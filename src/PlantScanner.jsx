import { useState } from "react";
import "./App.css";
import logo from './images/logo.png';
import identifyimg from './images/identifyimg.png';
import fileimg from './images/fileimg.png';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5001";

export default function PlantScanner() {
  const [image, setImage] = useState(null);
  //const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [season, setSeason] = useState("");
  const [location, setLocation] = useState("");
  const [result, setResult] = useState({
  name: "Test Plant",
  confidence: 99
});

  const handleSubmit = async () => {
    if (!image) return;
    setLoading(true);

    const form = new FormData();
    form.append("image", image);
    form.append("season", season);
    form.append("location", location);

    try {
      const res = await fetch(`${API_URL}/identify`, {
        method: "POST",
        body: form
      });

      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
      setResult({ name: "Error", confidence: 0 });
    }

    setLoading(false);
  };

  return (
    //change href (of the logo & about) later to something else 
    <div>
      <header id="nav">
        <a href="#scan"><img id="logo" src={logo} /></a>
        <h1 id="brandname">EcoScan</h1>
        <nav id="navbar">
          <ul>
            <li>
              <a className="nav-link">About</a>
            </li>
            <li>
              <a href="#scan" className="nav-link">Scan</a>
            </li>
          </ul>
        </nav>
      </header>

      <section id="scan">
        <div id ="top-div">
          <div>
            <h1 id="youre-scanning">You're <br /> Scanning:</h1>

            <div className="dropdown-row">
              <select id="location-box" className="dropdown-box" value={location} onChange={e => setLocation(e.target.value)}>
                <option value="" disabled hidden>Set Location</option>
                <option value="northeastern boston">Northeastern Boston</option>
                <option value="other">Other</option>
              </select>

              <select id="season-box" className="dropdown-box" value={season} onChange={e => setSeason(e.target.value)}>
                <option value="" disabled hidden>Set Season</option>
                <option value="winter">Winter</option>
                <option value="spring">Spring</option>
                <option value="summer">Summer</option>
                <option value="fall">Fall</option>
              </select>
            </div>
          </div>

          <div>
            <h2>Browse Plants</h2>

            <div id = "rectangle"></div>
          </div>
        </div>

        {result && (
            <div className="results-container">
              <p className="results-text">
                <b>Plant</b>: {result.name}, <b>Confidence</b>: {result.confidence}%
              </p>
            </div>
          )}
        
        <div className="circle-button-row">

          <div className="button-container">
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={e => setImage(e.target.files[0])}
              style={{ display: "none" }}
            />
            <label htmlFor="file-input" className="circle-button" id="file-button" >
              <img id="fileimg" src={fileimg} />
            </label>
            <p className="button-text">
              {image ? "File Uploaded!" : "Choose File"}
            </p>
          </div>

          <div className="button-container">
            <button className="circle-button" id="identify-button" disabled={!image || loading} onClick={handleSubmit}>
              <img id="identifyimg" src={identifyimg} />
            </button>
            <p className="button-text">{loading ? "Identifying…" : "Identify Plant"}</p>
          </div>
          
        </div>

      </section>
    </div>
  );
}