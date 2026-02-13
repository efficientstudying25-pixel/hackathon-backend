import re

def calculate_risk(message):
    keywords = {
        # 🔴 High Risk (8–10)
        "otp": 10,
        "share otp": 10,
        "send otp": 10,
        "cvv": 10,
        "confirm pin": 10,
        "enter pin": 10,
        "verification code": 9,
        "6 digit code": 9,
        "account blocked": 9,
        "account suspended": 9,
        "account locked": 9,
        "update kyc": 9,
        "click link": 9,
        "verify now": 9,
        "pan suspended": 9,
        "aadhaar suspended": 9,
        "credit card blocked": 9,
        "debit card blocked": 9,
        "scan qr": 9,
        "remote access": 9,
        "anydesk": 9,
        "teamviewer": 9,
        "screen share": 9,

        # 🟠 Medium Risk (5–7)
        "lottery": 7,
        "winner": 7,
        "prize": 7,
        "investment": 7,
        "guaranteed return": 7,
        "double money": 7,
        "loan approved": 6,
        "refund": 6,
        "urgent": 6,
        "work from home": 6,
        "parcel on hold": 6,
        "customs duty": 6,
        "electricity disconnect": 6,
        "police case": 6,
        "legal notice": 6,
        "registration fee": 6,
        "processing fee": 6,
        "approve upi": 6,
        "collect request": 6,
        "bank manager": 6,
        "rbi notice": 6,

        # 🟢 Low Risk (1–4)
        "update": 4,
        "verify": 4,
        "bank": 4,
        "account": 3,
        "offer": 3,
        "limited time": 3,
        "today only": 3,
        "cashback": 3,
        "reward": 3,
        "email verify": 3,
        "password update": 4,
        "security alert": 4,
        "unusual activity": 4,
        "login now": 4,
        "reset password": 4
    }

    score = 0
    flagged = []

    message_lower = message.lower()

    for word, weight in keywords.items():
        if re.search(r"\b" + re.escape(word) + r"\b", message_lower):
            score += weight
            flagged.append(word)

    return score, flagged
