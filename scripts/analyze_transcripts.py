# scripts/analyze_transcripts.py
import pandas as pd
from textblob import TextBlob
from collections import Counter, defaultdict
import json
import os
import re

# Define themes using YOUR critical vocabulary
THEMES = {
    "coding-support": ["github", "python", "script", "function", "json", "dataset", "library","loop","array"],
    "identity-reflexivity": ["identity", "self", "gender", "values", "subjectivity", "pronouns"],
    "pedagogy": ["class", "project", "readings", "learn", "understand", "explain", "assignment", "design"],
    "embodiment": ["body", "drawing", "art", "material", "senses", "touch", "hand", "paper", "therapeutic", "physical"],
    "ai-theory": ["machine", "agency", "chatbot", "authority", "LLM", "posthuman", "situated", "agential", "model","generation","sustainability"]
}

def classify_theme(text: str) -> str:
    text_lower = text.lower()
    matches = []
    for theme, keywords in THEMES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            matches.append((score, theme))
    return max(matches, key=lambda x: x[0])[1] if matches else "other"

df = pd.read_csv("assets/cleaned_chatgpt_history.csv")
df = df.dropna(subset=["content"])
df["content"] = df["content"].astype(str)

# keep messages by role for separate + combined analysis
all_messages = []

for _, row in df.iterrows():
    text = row["content"]
    role = row["role"]
    sentiment = TextBlob(text).sentiment.polarity
    # Apply theme classification to BOTH user and assistant
    theme = classify_theme(text)
    
    msg = {
        "role": role,
        "conversation_title": row["conversation_title"],
        "timestamp": row["timestamp"],
        "text": text,
        "sentiment": round(sentiment, 3),
        "theme": theme,
        "word_count": len(text.split())
    }
    all_messages.append(msg)

# Split for analysis
user_msgs = [m for m in all_messages if m["role"] == "user"]
assistant_msgs = [m for m in all_messages if m["role"] == "assistant"]

# --- Aggregations ---
def get_theme_counts(msgs):
    return dict(Counter(m["theme"] for m in msgs))

def get_top_words(msgs, n=20):
    all_text = " ".join(m["text"].lower() for m in msgs)
    words = re.findall(r"\b[a-zA-Z]{3,}\b", all_text)
    return Counter(words).most_common(n)

output = {
    "metadata": {
        "total_user": len(user_msgs),
        "total_assistant": len(assistant_msgs),
    },
    "user": {
        "theme_distribution": get_theme_counts(user_msgs),
        "avg_sentiment": sum(m["sentiment"] for m in user_msgs) / len(user_msgs) if user_msgs else 0,
        "top_words": get_top_words(user_msgs),
        "samples_by_theme": {theme: [m for m in user_msgs if m["theme"] == theme][:2] for theme in set(m["theme"] for m in user_msgs)}
    },
    "assistant": {
        "theme_distribution": get_theme_counts(assistant_msgs),
        "avg_sentiment": sum(m["sentiment"] for m in assistant_msgs) / len(assistant_msgs) if assistant_msgs else 0,
        "top_words": get_top_words(assistant_msgs),
        "samples_by_theme": {theme: [m for m in assistant_msgs if m["theme"] == theme][:2] for theme in set(m["theme"] for m in assistant_msgs)}
    }
}

with open("assets/chatgpt-analysis.json", "w") as f:
    json.dump(output, f, indent=2)
