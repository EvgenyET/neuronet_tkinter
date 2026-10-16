import math
import pandas as pd
import pickle

# Функция выбора расширенных данных из датафрейма Биткоина (выбор всех данных):

def draw_graph_log(self):
    with open('dataframe.pkl', 'rb') as file:
        self.df = pickle.load(file)

    self.df = self.df.iloc[:, :6]

    self.df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

    self.df = self.df.head(2221)

    self.df = self.df.rename(
        columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                 'Volume': 'volume'})
    self.df['date'] = pd.to_datetime(self.df['date'], unit='ms')
    for col in self.df.columns[1:]:
        self.df[col] = pd.to_numeric(self.df[col])

    print(self.df)

    self.high_price = self.df['high'].max()
    self.low_price = self.df['low'].min()

    self.price_range = self.high_price - self.low_price

    candle_width = 1

    candle_outline_width = 1

    start_date = self.df['date'].min().date()
    price_range = self.df['high'].max() - self.df['low'].min()

    self.candle_y = 0

    self.k = 1620

    distance_candles = 0

    pos_x = 50

    for i, row in self.df.iterrows():
        candle_date = row['date'].date()
        days_since_start = (candle_date - start_date).days
        candle_x = ((days_since_start / 12) * distance_candles + i * candle_width) + pos_x
        candle_color = 'red' if row['open'] > row['close'] else 'green'

        candle_top = (math.log10(self.high_price) - math.log10(row['high'])) / math.log10(self.price_range) * self.k
        candle_bottom = (math.log10(self.high_price) - math.log10(row['low'])) / math.log10(self.price_range) * self.k
        candle_open = (math.log10(self.high_price) - math.log10(row['open'])) / math.log10(self.price_range) * self.k
        candle_close = (math.log10(self.high_price) - math.log10(row['close'])) / math.log10(self.price_range) * self.k

        self.canvas.create_line(candle_x + candle_width / 2, self.candle_y + candle_top,
                                candle_x + candle_width / 2, self.candle_y + candle_bottom,
                                width=candle_outline_width, fill=candle_color)

        self.canvas.create_rectangle(candle_x, self.candle_y + candle_open, candle_x + candle_width,
                                     self.candle_y + candle_close,
                                     outline=candle_color, width=candle_outline_width, fill=candle_color)

    self.canvas.place(x=2, y=2)