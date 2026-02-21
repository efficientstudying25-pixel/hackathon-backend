import os
import joblib
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from detection.scorer import calculate_risk
import logging

logging.basicConfig(level=logging.INFO)

print("THIS IS THE CORRECT APP FILE")

app = Flask(__name__)
CORS(app)

# Load ML Model
model = joblib.load("model/scam_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")


# ---------- CLEAN TEXT (for ML consistency) ----------
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())


# ---------- URL SUSPICION SCORE (Cyber Signal) ----------
def url_suspicion_score(message):
    message_lower = message.lower()

    suspicious_patterns = [
        "http://",
        "https://",
        ".xyz",
        ".top",
        ".click",
        "bit.ly",
        "tinyurl",
        "t.me",
        "wa.me"
    ]

    score = 0
    for pattern in suspicious_patterns:
        if pattern in message_lower:
            score += 20  # each suspicious URL adds risk

    return min(100, score)  # cap at 100


@app.route("/")
def home():
    return "Hello Nidhi Backend - LIVE!"


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
    if risk_level == "Low":
        return (
            "Yeh message safe lag raha hai. "
            "Isme koi major scam indicators detect nahi hue. "
            "Phir bhi unknown links ya personal details share karte waqt hamesha cautious rahein."
        )

    keywords_text = ", ".join(keywords) if keywords else "kuch suspicious patterns"

    return (
        f"Yeh message risky lag raha hai kyunki isme {keywords_text} jaise words detect hue hain. "
        f"Yeh patterns scams mein commonly use hote hain (urgency, financial ya authority triggers). "
        f"Kisi bhi unknown link par click na karein aur OTP ya personal details share na karein. "
        f"Risk level: {risk_level}."
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message = data["message"]

    # ---------- ML Probability ----------
    cleaned_message = clean_text(message)
    message_vector = vectorizer.transform([cleaned_message])
    ml_prob = model.predict_proba(message_vector)[0][1] * 100  # %

    # ---------- Behavioral Threat Score ----------
    behavior_score, flagged = calculate_risk(message)
    behavior_percent = min(100, behavior_score * 10)

    # ---------- URL Cyber Signal ----------
    url_score = url_suspicion_score(message)

    # ---------- 🔥 FINAL ENSEMBLE RISK FORMULA ----------
    # 60% ML + 30% Behavioral + 10% URL Risk
    final_risk_score = (
        (ml_prob * 0.6) +
        (behavior_percent * 0.3) +
        (url_score * 0.1)
    )

    # ---------- Risk Level Logic ----------
    if final_risk_score < 30:
        risk_level = "Low"
    elif final_risk_score < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Scam Type
    scam_type = detect_scam_type(flagged)

    # ---------- Smart Confidence (Hackathon-grade) ----------
    confidence = round(
        min(98, (ml_prob * 0.7) + (final_risk_score * 0.3)),
        2
    )

    logging.info(f"Message: {message}")
    logging.info(f"ML Prob: {ml_prob}")
    logging.info(f"Behavior Score: {behavior_percent}")
    logging.info(f"URL Score: {url_score}")
    logging.info(f"Final Risk Score: {final_risk_score}")

    response = {
        "risk_score": round(final_risk_score, 2),
        "risk_level": risk_level,
        "scam_type": scam_type,
        "flagged_keywords": flagged,
        "ml_probability": round(ml_prob, 2),
        "confidence_percent": confidence,
        "explanation": generate_explanation(message, flagged, final_risk_score, risk_level)
    }

    return jsonify(response)


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

    
