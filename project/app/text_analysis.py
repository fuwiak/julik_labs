import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import text as sql_text

def analyze_text(text: str) -> str:
    """
    Анализ текста по ключевым словам. Возвращает строку-результат: "Учёба", "Отзывы", "Спам" или "Не определено".
    Для упрощения пример читает keywords.json из текущей директории.
    """
    with open("keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)

    kw_study = keywords.get("study", [])
    kw_reviews = keywords.get("reviews", [])
    kw_spam = keywords.get("spam", [])

    text_lower = text.lower()

    if any(kw in text_lower for kw in kw_study):
        return "Учёба"
    elif any(kw in text_lower for kw in kw_reviews):
        return "Отзывы"
    elif any(kw in text_lower for kw in kw_spam):
        return "Спам"
    else:
        return "Не определено"
