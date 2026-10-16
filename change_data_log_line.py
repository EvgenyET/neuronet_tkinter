import math
import pandas as pd
import pickle

# Функция выбора расширенных данных из датафрейма Биткоина (выбор всех данных):

def draw_graph_log_line(self):
    with open('dataframe.pkl', 'rb') as file:
        self.df = pickle.load(file)

    self.df = self.df.iloc[:, :6]

    self.df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

    self.df = self.df.head(2221)

    self.df = self.df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                            'Volume': 'volume'})
    self.df['date'] = pd.to_datetime(self.df['date'], unit='ms')
    for col in self.df.columns[1:]:
        self.df[col] = pd.to_numeric(self.df[col])

    self.high_price = self.df['high'].max()
    self.low_price = self.df['low'].min()

    self.price_range = self.high_price - self.low_price

    candle_width = 1

    candle_outline_width = 1

    start_date = self.df['date'].min().date()
    price_range = self.df['high'].max() - self.df['low'].min()

    self.candle_y = 490

    self.k = 490

    distance_candles = 0

    pos_x = 50

    # Create a list of x and y values for each data point
    data_points = []
    for i, row in self.df.iterrows():
        candle_date = row['date'].date()
        days_since_start = (candle_date - start_date).days
        x = ((days_since_start / 12) * distance_candles + i * candle_width) + pos_x

        # Use log base 10 to convert the y-value to a logarithmic scale
        y = -1 * (math.log10(row['close']) - math.log10(self.low_price)) / (math.log10(self.high_price) - math.log10(self.low_price)) * self.k

        data_points.append((x, y))

    # Draw a line connecting the data points
    for i in range(len(data_points) - 1):
        x1, y1 = data_points[i]
        x2, y2 = data_points[i+1]
        self.canvas.create_line(x1, self.candle_y + y1, x2, self.candle_y + y2, width=candle_outline_width, fill='blue')

    self.canvas.place(x=2, y=2)