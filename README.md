# Project Summary

This trading bot reads weekly financial news for over 50+ top stocks by transaction volume and trades based on perceived sentiment. News sentiment is calculated with finBERT, a natural language model pre-trained on text from the financial domain. This trading bot considers both long and short positions (based on "positive" and "negative" sentiment, respectively) and distributes investments evenly among securities (a stronger perceived positive sentiment won't mean a larger investment in the security).

# Usage

1. Clone git repository ```bash git clone https://github.com/ethanrimes/News-Sentiment-Trading-Bot/```
2. Install dependencies ```bash pip install -r requirements.txt```
3. Set up Alpaca API key and API secret and replace the default values for ```bash API_KEY``` and ```bash API_SECRET```
4. Run the bot ```bash python tradingbot.py```

# Credits

- [FinBERT NLP model](https://huggingface.co/ProsusAI/finbert) - For providing the pre-trained model for news sentiment classification
- [Lumibot](https://lumibot.lumiwealth.com/) - For providing a lot of functionality that simplified the trading implementation
- [Alpaca API](https://docs.alpaca.markets/reference/) - For providing the functionality for obtaining the financial news, as well as the platform for the paper trading
- [Nicholas Renotte](https://github.com/nicknochnack) - For project inspiration
