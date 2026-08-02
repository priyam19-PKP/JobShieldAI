from ollama_ai import explain_prediction

result = explain_prediction(
    job_description="Software Engineer at Google. 5 years experience. Official website careers.google.com",
    prediction="Real"
)

print(result)