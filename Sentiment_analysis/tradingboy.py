from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta
from finebert_util import estimate_sentiment
# Import writer class from csv module
from csv import writer


API_KEY = "PKZ1B4QS69E8RXEEEPUH"
API_SECRET = "bx9TcOQJGS3XewrpuGUJgb3ffxjyPMYwd3tDKTru"
BASE_URL="https://paper-api.alpaca.markets/v2"

ALPACA_CREDS={
    "API_KEY":API_KEY,
    "API_SECRET":API_SECRET,
    "PAPER":True
}

class MLTrader(Strategy):
    def initialize(self, symbol: str = "SPY", cash_at_risk:float=.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk= cash_at_risk
        self.api = REST(base_url = BASE_URL, key_id = API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        try:
            quantity = round(cash * self.cash_at_risk / last_price, 0 )
        except:
            quantity = 0
            last_price = 0
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        past = today - Timedelta(days = 3)
        return today.strftime('%Y-%m-%d'), past.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, past = self.get_dates()
        news = self.api.get_news(symbol = self.symbol, start= past, end = today)
        news  = [ev.__dict__["_raw"]["headline"] for ev in news]
        with open("news.csv", "a") as file:
            file.write("\n")
            file.write(today)
            for row in news:
                file.write("\n")
                file.write("\n")
                file.write(row)
            file.close()

        probability, sentiment = estimate_sentiment(news)
        return today, probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        today, probability, sentiment = self.get_sentiment()
        List = [today, probability, sentiment]
        with open('event.csv', 'a') as f_object:
            # Pass this file object to csv.writer()
            # and get a writer object
            writer_object = writer(f_object)

            # Pass the list as an argument into
            # the writerow()
            writer_object.writerow(List)

            # Close the file object
            f_object.close()
        # if cash > last_price:
        #     if sentiment == "positive" and probability > .9:
        #         if self.last_trade == "sell":
        #             self.sell_all()
        #         order = self.create_order(
        #                 self.symbol, 
        #                 quantity,
        #                 "buy",
        #                 type = "bracket",
        #                 take_profit_price = last_price * 1.20,
        #                 stop_loss_price = last_price* .95
        #             )
        #         self.submit_order(order)
        #         self.last_trade = "buy"
        #     elif sentiment == "negative" and probability> .8:
        #         if self.last_trade == "buy":
        #             self.sell_all()
        #         order = self.create_order(
        #             self.symbol, 
        #             quantity,
        #             "sell",
        #             type = "bracket",
        #             take_profit_price = last_price * .8,
        #             stop_loss_price = last_price *1.05
        #         )
        #         self.submit_order(order)
        #         self.last_trade = "sell"
start_date = datetime(2024, 5, 20)
end_date = datetime(2024, 5, 25)

broker = Alpaca(ALPACA_CREDS)
strategy= MLTrader(name = "mlstrat", broker=broker, parameters={"symbol":"PANW", "cash_at_risk":.5})
strategy.backtest(
    YahooDataBacktesting, 
    start_date, 
    end_date, 
    parameters={"symbol":"PANW", "cash_at_risk":.5}
)
