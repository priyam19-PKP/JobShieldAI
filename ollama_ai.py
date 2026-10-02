import ollama

def get_heuristic_explanation(prediction):
    if "Fake" in prediction:
        return (
            "### 🔍 AI Forensic Security Assessment\n\n"
            "- **Verdict Analysis:** The ML classifier flagged high-probability vocabulary and structural signals common to fraudulent postings.\n"
            "- **Key Risk Factors:** Scammers often use unverified recruitment channels (Gmail, Telegram, WhatsApp), promise rapid hiring with no interview, or demand registration/hardware deposits.\n"
            "- **Candidate Advisory:** Never transfer funds, deposit checks for 'office equipment', or provide bank credentials. Always confirm openings on the company's verified careers page."
        )
    else:
        return (
            "### 🛡️ AI Forensic Security Assessment\n\n"
            "- **Verdict Analysis:** The ML classifier evaluated this listing as authentic. Language, compensation context, and skill criteria align with standard industry norms.\n"
            "- **Verification Advice:** Confirm that all recruiter communications originate from the organization's official corporate email domain.\n"
            "- **Safety Best Practice:** Even for authentic roles, standard employers will never ask for advance payments or sensitive government/financial IDs during initial interviews."
        )

def explain_prediction(job_description, prediction, use_llm=True):
    if not use_llm:
        return get_heuristic_explanation(prediction)

    # Concise prompt with truncated description for ultra-fast inference
    truncated_text = job_description[:700]
    prompt = f"""Fake job detection analysis.
Job Posting: {truncated_text}
Prediction: {prediction}

Provide:
1. Short reason why it is {prediction}.
2. Key warning sign or safe indicator.
3. 1 safety tip.
Keep strictly under 60 words."""

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_predict": 85,
                "temperature": 0.1
            }
        )
        return response["message"]["content"]
    except Exception as e:
        return get_heuristic_explanation(prediction)
