import ollama

def explain_prediction(job_description, prediction):

    prompt = f"""
You are an AI expert in fake job detection.

Job Description:
{job_description}

Machine Learning Prediction:
{prediction}

Explain:
1. Why the job is real or fake.
2. Mention warning signs.
3. Give safety advice.

Keep the answer under 150 words.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]