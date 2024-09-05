from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Tuple

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

def estimate_sentiment(news: List[str], threshold: float = 0.7) -> Tuple[float, str]:
    if news:
        # Tokenize the input headlines
        tokens = tokenizer(news, return_tensors="pt", padding=True).to(device)
        
        # Get the model output (logits)
        logits = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])["logits"]
        
        # Convert logits to probabilities
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        weighted_sum = torch.zeros(3).to(device)  # 3 for [positive, negative, neutral]
        total_weight = 0.0
        
        # Loop over each headline's probabilities
        for prob in probabilities:
            max_prob = torch.max(prob).item()  # Get the highest probability
            sentiment_idx = torch.argmax(prob).item()  # Get the index of the predicted sentiment
            
            # If the sentiment is positive (index 0) or negative (index 1), and meets threshold
            if sentiment_idx in [0, 1] and max_prob >= threshold:
                weighted_sum += prob * max_prob  # Weight the probabilities by the confidence
                total_weight += max_prob
        
        # Normalize the weighted sum by the total weight
        if total_weight > 0:
            avg_probabilities = weighted_sum / total_weight
            max_prob = torch.max(avg_probabilities).item()
            sentiment = labels[torch.argmax(avg_probabilities).item()]
            return max_prob, sentiment
        else:
            return 0, "neutral"  # If no positive/negative sentiment passed the threshold
    else:
        return 0, labels[-1]  # Return neutral for empty news list

if __name__ == "__main__":
    # Example usage
    headlines = ['markets responded negatively to the news!', 'traders were displeased!']
    probability, sentiment = estimate_sentiment(headlines, threshold=0.7)
    
    # print(f"Overall Sentiment: Probability = {probability:.4f}, Sentiment = {sentiment}")