def calculate_risk_score(result, warnings):

    score = 0

    if "Fake" in result:
        score += 50

    score += (len(warnings) - 1) * 8

    score = max(0, min(score, 100))

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level