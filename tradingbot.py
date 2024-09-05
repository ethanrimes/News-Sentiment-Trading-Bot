from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime 
from alpaca_trade_api import REST 
from timedelta import Timedelta 
from finbert_utils import estimate_sentiment
from alpaca_trade_api.rest import APIError


API_KEY = # Your API key
API_SECRET = # Your API secret
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY, 
    "API_SECRET": API_SECRET, 
    "PAPER": True
}

class MLTrader(Strategy): 
    def initialize(self): 
        self.symbols = ['NVDA','TSLA','AAPL','AMZN','MSFT','META','AMD','SMCI','LLY',\
                        'AVGO','GOOG','ASTS','XOM','COST','FYBR','KO','MCK','JPM','INTC',\
                            'DELL','APLD','DAL','DLTR','VZ','MRK','CVX','CRWD','UNH','COIN','PYPL','MU','ORCL',\
                                'AMAT','NFLX','BAC','V','F','MA','PAYC','DG','PLTR','PG','PEP','MSTR',\
                                    'EW','BA','T','PLTR','CRM','WMT','QCOM','CAT','CI','WFC','PFE','UPS','HD','ABBV','UNP','GS','X','TMUS',\
                                        'CMCSA','PM','CSCO','HPE','UBER','MARA','DE','COP','DIS','GE','GM','PANW','NU','ODFL']
        self.sleeptime = "7D"
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def get_dates(self): 
        today = self.get_datetime()
        week_prior = today - Timedelta(days=7)
        return today.strftime('%Y-%m-%d'), week_prior.strftime('%Y-%m-%d')

    def get_sentiment(self): 
        today, week_prior = self.get_dates()
        organizer = {}
        nonzero_positions = 0
        for symbol in self.symbols:
            news = self.api.get_news(symbol=symbol, 
                                    start=week_prior, 
                                    end=today,
                                    limit=50)
             
            headlines = [ev.__dict__["_raw"]["headline"] for ev in news]
            probability, sentiment = estimate_sentiment(headlines)
            organizer[symbol] = (probability, sentiment)
            if sentiment != "neutral" and probability > 0.66:
                nonzero_positions += 1

        return nonzero_positions, organizer
    
    def on_bot_crash(self, error):
        self.sell_all()
        self.log_message(error)

    def on_trading_iteration(self):
        nonzero_positions, sentiments = self.get_sentiment()
        
        if nonzero_positions > 0:
            position_value = self.get_portfolio_value() / nonzero_positions
            for ticker,tup in sentiments.items():
                position = None
                try: 
                    position = self.api.get_position(ticker)
                except APIError as e:
                    position = None
                pos_q = int(0 if position is None else position.qty)
                probability,sentiment = tup
                last_price = self.api.get_latest_trade(ticker).p
                target_q, order =  int(position_value/last_price), ""

                if sentiment == "positive" and probability > 0.66:
                    qty = abs(target_q - pos_q)
                    if target_q < pos_q:
                        order = self.create_order(ticker, qty, "sell", type="bracket", 
                        take_profit_price=last_price*.8, 
                        stop_loss_price=last_price*1.05
                    )
                    else:
                        order = self.create_order(ticker, qty, "buy", type="bracket", 
                            take_profit_price=last_price*1.20, 
                            stop_loss_price=last_price*.95
                        )

                elif sentiment == "negative" and probability > 0.66:
                    qty = abs(target_q + pos_q)
                    if pos_q < -1*target_q:
                        order = self.create_order(ticker, qty, "buy", type="bracket", 
                                take_profit_price=last_price*1.20, 
                                stop_loss_price=last_price*.95
                            )
                    else:
                        order = self.create_order(ticker, qty, "sell", type="bracket", 
                        take_profit_price=last_price*.8, 
                        stop_loss_price=last_price*1.05
                    )
                if order != "":
                    self.submit_order(order)

start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31) 
broker = Alpaca(ALPACA_CREDS) 
strategy = MLTrader(name='news_sentiment_bot', broker=broker)
strategy.backtest(
    YahooDataBacktesting, 
    start_date, 
    end_date
)


# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()