import os, uvicorn
from flask import Flask, request, jsonify
from flask_cors import CORS
from detection.scorer import calculate_risk
import logging
logging.basicConfig(level=logging.INFO)


print("THIS IS THE CORRECT APP FILE")

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello Nidhi Backend"

@app.route("/test")
def test():
    return "TEST ROUTE WORKING"
def detect_scam_type(flagged_keywords):
    text = " ".join(flagged_keywords).lower()

    if any(k in text for k in ["otp", "cvv", "pin"]):
        return "OTP / Banking Scam"

    if any(k in text for k in ["kyc", "aadhaar", "pan"]):
        return "KYC Update Scam"

    if any(k in text for k in ["lottery", "winner", "prize"]):
        return "Lottery Scam"

    if any(k in text for k in ["job", "work from home", "registration fee"]):
        return "Job Scam"

    if any(k in text for k in ["investment", "double money", "guaranteed"]):
        return "Investment Scam"

    if any(k in text for k in ["anydesk", "teamviewer", "remote access"]):
        return "Remote Access Scam"

    return "Suspicious Message"
def generate_explanation(message, keywords, score, risk_level):
    keywords_text = ", ".join(keywords) if keywords else "no major keywords"

    explanation = (
        f"Yeh message risky lag raha hai kyunki isme {keywords_text} jaise words detect hue hain. "
        f"Aise words scams mein common hote hain. "
        f"Aap kisi bhi link par click na karein aur OTP ya personal details share na karein. "
        f"Risk level: {risk_level}."
    )

    return explanation

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message = data["message"]

    score, flagged = calculate_risk(message)

    # Risk Level
    if score <= 3:
        risk_level = "Low"
    elif score <= 7:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Detect Scam Type
    scam_type = detect_scam_type(flagged)

    # Confidence Logic
    confidence = min(95, 40 + score * 5)

    logging.info(f"Message received: {message}")
    logging.info(f"Score: {score}, Risk Level: {risk_level}")

    response = {
        "risk_score": score,
        "risk_level": risk_level,
        "scam_type": scam_type,
        "flagged_keywords": flagged,
        "explanation": generate_explanation(message, flagged, score, risk_level),
        "confidence_percent": confidence
    }

    return jsonify(response)


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
