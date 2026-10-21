
CREATE TABLE plant_scans (
    id SERIAL PRIMARY KEY,
    plant_name TEXT,
    confidence DOUBLE PRECISION,
    image_url TEXT,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    season VARCHAR(10),
    location VARCHAR(50)
);
