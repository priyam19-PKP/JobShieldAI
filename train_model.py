import pandas as pd

# Load dataset
df = pd.read_csv("dataset/fake_job_postings.csv")

print("Dataset Loaded Successfully!")
print("Shape:", df.shape)

# Create a combined text column
df["text"] = (
    df["title"].fillna("") + " " +
    df["company_profile"].fillna("") + " " +
    df["description"].fillna("") + " " +
    df["requirements"].fillna("")
)

print("\nCombined text created successfully!")
print(df["text"].head())

# Target variable
y = df["fraudulent"]

print("\nTarget Distribution:")
print(y.value_counts())
# ===========================================
# TF-IDF Vectorization
# ===========================================

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X = vectorizer.fit_transform(df["text"])

print("\nTF-IDF Vectorization Completed!")

print("Feature Matrix Shape:", X.shape)
# ===========================================
# Train-Test Split
# ===========================================

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTrain-Test Split Completed!")

print("Training Data :", X_train.shape)
print("Testing Data  :", X_test.shape)
# ===========================================
# Logistic Regression
# ===========================================

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Create model
lr_model = LogisticRegression(max_iter=1000)

# Train model
lr_model.fit(X_train, y_train)

# Predict
y_pred = lr_model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("LOGISTIC REGRESSION RESULTS")
print("==============================")

print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
# ===========================================
# Random Forest
# ===========================================

from sklearn.ensemble import RandomForestClassifier

# Create model
rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train model
rf_model.fit(X_train, y_train)

# Predict
rf_pred = rf_model.predict(X_test)

# Accuracy
rf_accuracy = accuracy_score(y_test, rf_pred)

print("\n==============================")
print("RANDOM FOREST RESULTS")
print("==============================")

print("Accuracy:", round(rf_accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, rf_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, rf_pred))
# ===========================================
# XGBoost
# ===========================================

from xgboost import XGBClassifier

xgb_model = XGBClassifier(
    random_state=42,
    eval_metric="logloss"
)

# Train
xgb_model.fit(X_train, y_train)

# Predict
xgb_pred = xgb_model.predict(X_test)

# Accuracy
xgb_accuracy = accuracy_score(y_test, xgb_pred)

print("\n==============================")
print("XGBOOST RESULTS")
print("==============================")

print("Accuracy:", round(xgb_accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, xgb_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, xgb_pred))
print("\n==============================")
print("MODEL COMPARISON")
print("==============================")

print(f"Logistic Regression : {accuracy*100:.2f}%")
print(f"Random Forest       : {rf_accuracy*100:.2f}%")
print(f"XGBoost             : {xgb_accuracy*100:.2f}%")
# ===========================================
# Save Model and Vectorizer
# ===========================================

import joblib

joblib.dump(xgb_model, "models/jobshield_model.pkl")
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")

print("\n✅ Model and TF-IDF Vectorizer Saved Successfully!")
