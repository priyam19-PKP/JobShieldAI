import joblib

# Load saved model and vectorizer
model = joblib.load("models/jobshield_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")


def predict_job(job_description):
    # Convert text to TF-IDF
    text_vector = vectorizer.transform([job_description])

    # Predict
    prediction = model.predict(text_vector)[0]

    # Prediction probability
    probability = model.predict_proba(text_vector)[0]

    confidence = max(probability) * 100

    if prediction == 1:
        result = "Fake Job"
    else:
        result = "Real Job"

    return result, confidence


# Test Prediction
if __name__ == "__main__":

    sample = """
    We are looking for a software developer.
    Salary: $120000 per year.
    Experience: 2 years.
    Company: Google.
    """

    result, confidence = predict_job(sample)

    print("Prediction:", result)
    print("Confidence:", round(confidence, 2), "%")