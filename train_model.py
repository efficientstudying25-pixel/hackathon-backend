import pandas as pd
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

df_original = pd.read_excel("data/scam_binary.xlsx")

df_new = pd.read_excel("data/VoiceGuard_2000_HighRisk_Dominant (1).xlsx")
df_new = df_new.rename(columns={"Message": "message"})
df_new["label"] = 1
df_new = df_new[["message", "label"]]

# Sample 500 records to maintain class balance with the original dataset
df_new = df_new.sample(n=500, random_state=42)

df = pd.concat([df_original, df_new], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

def clean_text(text):
    text = str(text).lower()

    # Remove the synthetic "high risk alert #X:" pattern
    text = re.sub(r'high risk alert #\d+:\s*', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

df["message"] = df["message"].apply(clean_text)

X = df["message"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

vectorizer = TfidfVectorizer(stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(class_weight="balanced")
model.fit(X_train_vec, y_train)

y_pred = model.predict(X_test_vec)

print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

joblib.dump(model, "model/scam_model.pkl")
joblib.dump(vectorizer, "model/vectorizer.pkl")