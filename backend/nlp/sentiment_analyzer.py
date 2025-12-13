# backend/nlp/sentiment_analyzer.py
from transformers import pipeline
import torch

# Load sentiment analysis model (using a lightweight model)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0 if torch.cuda.is_available() else -1
)

def analyze_sentiment(reviews):
    """
    Analyze sentiment of reviews and return overall sentiment score
    Returns: (reviews_with_sentiment, overall_sentiment_score, sentiment_breakdown)
    """
    if not reviews:
        return reviews, 0.0, {"positive": 0, "negative": 0, "neutral": 0}
    
    texts = [r["text"] for r in reviews]
    
    # Batch sentiment analysis
    sentiments = sentiment_analyzer(texts, truncation=True, max_length=512)
    
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for i, sentiment in enumerate(sentiments):
        label = sentiment['label']  # POSITIVE or NEGATIVE
        score = sentiment['score']  # confidence
        
        # Add sentiment to review
        reviews[i]["sentiment"] = label
        reviews[i]["sentiment_score"] = round(score, 3)
        
        # Count sentiments
        if label == "POSITIVE" and score > 0.6:
            positive_count += 1
        elif label == "NEGATIVE" and score > 0.6:
            negative_count += 1
        else:
            neutral_count += 1
    
    # Calculate overall sentiment score (-1 to 1, where 1 is most positive)
    total = len(reviews)
    overall_score = round((positive_count - negative_count) / total, 3) if total > 0 else 0.0
    
    sentiment_breakdown = {
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count
    }
    
    return reviews, overall_score, sentiment_breakdown