def analyze_text(text: str) -> str:
    # Пример: определяем тональность отзыва (позитив/негатив) по наличию слов
    negative_words = ["bad", "terrible", "worse"]
    positive_words = ["good", "great", "excellent"]

    text_lower = text.lower()
    score = 0
    for w in positive_words:
        if w in text_lower:
            score += 1
    for w in negative_words:
        if w in text_lower:
            score -= 1

    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    else:
        return "neutral"
