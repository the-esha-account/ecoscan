import os, uuid, requests, psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import boto3
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
import numpy as np
from io import BytesIO
from PIL import Image
from flask import send_from_directory

print("🚀 Backend starting…")

load_dotenv(Path(__file__).parent / ".env")

PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# ---- DB ----
conn = psycopg2.connect(
    dbname="plant_scanner",
    user="esha",
    host="localhost"
)

def save_scan(name, confidence, image_url, season, location):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO plant_scans (plant_name, confidence, image_url, season, location)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, confidence, image_url, season, location)
    )
    conn.commit()
    cur.close()

# ---- S3 ----
USE_S3 = all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME])
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
) if USE_S3 else None

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ---- Winter model ----
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model

# --- Patch Dense to ignore old 'quantization_config' key ---
_original_dense_from_config = Dense.from_config
def dense_from_config_patched(config):
    config.pop("quantization_config", None)  # remove if present
    return _original_dense_from_config(config)
Dense.from_config = dense_from_config_patched

# --- Now safely load your model ---
MODEL_PATH = Path(__file__).parent / "models" / "winter_park_model.h5"
winter_park_model = load_model(MODEL_PATH) if MODEL_PATH.exists() else None
plant_classes = ["Carrot", "Cleaver", "English Ivy", "Fig Buttercup", "Garlic Mustard", "Honeysuckle", "Winter Creeper"]

app = Flask(__name__)
CORS(app)

def get_season_from_month(month):
    if month in [12,1,2]: return "winter"
    if month in [3,4,5]:  return "spring"
    if month in [6,7,8]:  return "summer"
    return "fall"

@app.route("/identify", methods=["POST"])
def identify():
    print("🖼 /identify called")

    # ---------- fields from frontend ----------
    season = request.form.get("season", "").lower()
    location = request.form.get("location", "").lower()

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()
    filename = f"{uuid.uuid4()}.jpg"

    # ---------- upload to S3 ----------
    if USE_S3:
        try:
            s3.put_object(Bucket=AWS_BUCKET_NAME, Key=filename, Body=image_bytes,
                        ContentType=image_file.content_type)
            image_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        except Exception as e:
            print("Error uploading to S3:", e)
            return jsonify({"error": "Failed to upload image"}), 500
    else:
        (UPLOAD_DIR / filename).write_bytes(image_bytes)
        image_url = request.host_url + f"uploads/{filename}"

    # ---------- Plant.id ----------
    try:
        r = requests.post(
            "https://api.plant.id/v2/identify",
            headers={"Api-Key": PLANT_ID_API_KEY},
            files={"images": image_bytes},
            data={"organs": ["leaf","flower"]}
        )
        data = r.json()

        if data.get("suggestions"):
            best = data["suggestions"][0]
            name = best["plant_name"]
            confidence = round(best["probability"] * 100, 2)
        else:
            name, confidence = "Unknown", 0

        print(f"🪴 Plant.id → {name} ({confidence}%)")

    except Exception as e:
        print("❌ Plant.id error:", e)
        name, confidence = "Error", 0

    # ---------- fallback winter model ----------
    if confidence < 50 and season == "winter" and location == "northeastern boston" and winter_park_model is not None:
        print("❄️ Using winter fallback model…")

        img = Image.open(BytesIO(image_bytes)).resize((224,224))
        x = keras_image.img_to_array(img) / 255.0
        x = np.expand_dims(x, 0)

        preds = winter_park_model.predict(x)
        idx = np.argmax(preds)
        confidence = float(np.max(preds) * 100)
        name = plant_classes[idx]

        print(f"🌲 Winter model → {name} ({confidence}%)")

    # ---------- save ----------
    save_scan(name, confidence, image_url, season, location)

    return jsonify({
        "name": name,
        "confidence": confidence,
        "image_url": image_url,
        "season": season,
        "location": location
    })

@app.route("/uploads/<path:name>")
def uploaded(name):
    return send_from_directory(UPLOAD_DIR, name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)