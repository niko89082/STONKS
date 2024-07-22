#Import the libraries
import math
from lumibot.brokers import Alpaca
from alpaca_trade_api import REST
# import pandas_datareader as web
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM # Long Short-Term Memory layer
import keras
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from timeit import default_timer as timer
plt.style.use('fivethirtyeight')
import csv




class Machine:
    def __init__(self, days:int, base, key, sec, stock ="MSFT",days_trend=45):
        self.start = (datetime.now() - timedelta(days)).strftime("%Y-%m-01") 
        self.end = datetime.now().strftime("%Y-%m-%d") 
        STOCK=stock.capitalize
        self.stock = yf.Ticker(STOCK)
        self.days_trend=days_trend
        self.df = self.get_stock_data()
        self.days = days
        self.api = REST(base_url = base, key_id = key, secret_key=sec)

    def report(self, results, n_top=3):
        for i in range(1, n_top + 1):
            candidates = np.flatnonzero(results['rank_test_score'] == i)
            for candidate in candidates:
                print("Model with rank: {0}".format(i))
                print("Mean validation score: {0:.3f} (std: {1:.3f})"
                    .format(np.sqrt(-results['mean_test_score'][candidate]),
                            results['std_test_score'][candidate]))
                print("Parameters: {0}".format(results['params'][candidate]))
                print("")

    def get_stock_data(self):
        start = (datetime.now() - timedelta(self.days)).strftime("%Y-%m-01") 
        end = datetime.now().strftime("%Y-%m-%d") 
        bars = self.api.get_bars(self.stock, "1D", start, end)
        bar = bars.__dict__["_raw"]

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(bar)

        # Rename columns to more readable names if desired
        df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low', 'n': 'number_of_trades', 'o': 'open', 't': 'timestamp', 'v': 'volume', 'vw': 'volume_weighted_average_price'}, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.rename(columns={'t': 'timestamp'}, inplace=True)
        df.set_index('timestamp', inplace=True)
        return df

    class TimingCallback(keras.callbacks.Callback):
        def __init__(self, logs={}):
            self.logs=[]
        def on_epoch_begin(self, epoch, logs={}):
            self.starttime = timer()
        def on_epoch_end(self, epoch, logs={}):
            self.logs.append(timer()-self.starttime)
            
    
    def get_financial_data(stock, sample_start_date, sample_stop_date):
        pass
    
    def y_predictor(self, data, sell, buy):
        percent = (data["close"]-data["open"])/data["close"]
        if (percent> buy):
            return [1,0,0]## buy
        elif (percent< sell):
            return[0,0,1]##sell
        else:
            return [0,1,0]##hold



    def data(self):
        ########################
        #
        #
        #       TODO:
        #      REDO DATA SO IT WORKS WITH ALPACA INSTEAD OF YAHOO
        #
        #
        ########################




        data = self.df.filter(["close","high","low", "open", "volume"])
        dataset = data.values
        #Get /Compute the number of rows to train the model on
        training_data_len = math.ceil( len(dataset) * .8 ) 

        #price scaler
        close = np.array([[C] for C  in dataset[0:, 0]])
        scalerP = self.scalerP = MinMaxScaler(feature_range=(0, 1))
        scaled_price_close = scalerP.fit_transform(close)

        prices = np.array([[O,H,L,V] for O,H,L,V  in dataset[0:, 1:5]])
        scalerPs = self.scalerPs = MinMaxScaler(feature_range=(0, 1))
        scaled_prices = scalerPs.fit_transform(prices)

        self.train_data = np.append(scaled_price_close,scaled_prices,axis=1)
        x_train=[]
        y_train = []
        for i in range(self.days_trend,training_data_len):
            x_train.append([self.train_data[i-self.days_trend: i, 0:]])
            y_train.append(self.train_data[i ,0])
        return x_train, y_train
    
    def generate(self):
        x_train, y_train = self.data()
        self.model = Sequential()
        self.model.add(LSTM(units=113, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
        self.model.add(LSTM(units=100, return_sequences=False))
        self.model.add(Dense(units=50))
        self.model.add(Dense(units=25))
        self.model.add(Dense(units=1))


        #Compile the model
        self.model.compile(optimizer='adam', loss='mean_squared_error')

        # Display a model summary
        self.model.summary()

        # model.save('my_stock_model.h5')
        self.model.save('my_model1.keras')

    def train(self):
        try:
            self.model
        except:
            self.generate()
        #Train the model
        cb = self.TimingCallback()
        self.model.fit(self.x_train, self.y_train, batch_size=1, epochs=20, workers=1, callbacks=[cb])
        # print(cb.logs)
        print("{} Seconds".format(sum(cb.logs)))
    
    def test(self):
        pass
        ######################TODO: redo for alpaca
        #test_data = self.train_data[self.days - n_days_to_trend: , : ]
        # # print(train_data[training_data_len - n_days_to_trend])
        # # print(test_data[0])
        # #Create the x_test and y_test data sets
        # x_test = []
        # y_test =  close[training_data_len:, : ] #Get all of the rows from index 1603 to the rest and all of the columns (in this case it's only column 'Close'), so 2003 - 1603 = 400 rows of data
        # for i in range(self.days_trend,len(test_data)):
        #     x_test.append(test_data[i-self.days_trend:i, : ])
        #call self.rmse and plug in the x and y values

    def prediction(self, predict_x):
        predictions = self.model.predict(predict_x)
        predictions = self.scalerP.inverse_transform(predictions)#Undo scaling
        return predictions
    
    def rmse(self, x_test, y_test):
        y_prediction = self.prediction(x_test)
        rmse=np.sqrt(np.mean(((y_prediction - y_test)**2)))
        return rmse