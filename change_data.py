import datetime
import pandas as pd
import pickle

# Функция выбора расширенных данных из датафрейма Биткоина (выбор всех данных):

def draw_graph2(self):
    # Считываем датафрейм:
    with open('dataframe.pkl', 'rb') as file:
        self.df = pickle.load(file)

    # Обрезаем ненужные столбцы из датафрейма:
    self.df = self.df.iloc[:, :6]

    # Присваиваем имена столбцам:
    self.df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

    # Обрезаем строки до нужного количества (указываем количество свечей):
    self.df = self.df.head(2221)

    self.df = self.df.rename(
        columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                 'Volume': 'volume'})
    self.df['date'] = pd.to_datetime(self.df['date'], unit='ms')
    for col in self.df.columns[1:]:
        self.df[col] = pd.to_numeric(self.df[col])

    print(self.df)

    # Определяем максимальную и минимальную цены из датафрейма:
    self.high_price = self.df['high'].max()
    self.low_price = self.df['low'].min()

    # Разница между максимальной и минимальной ценой:
    self.price_range = self.high_price - self.low_price

    # Указываем размер свечи (толщина свечи):
    candle_width = 1

    # Толщина контура свечи:
    candle_outline_width = 1

    # Привязываем свечи к датам по оси x:
    start_date = self.df['date'].min().date()
    price_range = self.df['high'].max() - self.df['low'].min()

    # Сдвиг свечей по высоте:
    self.candle_y = 100

    # Коэффициент k (удлиняет свечи):
    self.k = 320

    # Расстояние между свечами:
    distance_candles = 0

    # Сдвиг графика по оси x:
    pos_x = 50

    for i, row in self.df.iterrows():
        candle_date = row['date'].date()
        days_since_start = (candle_date - start_date).days
        candle_x = ((days_since_start / 12) * distance_candles + i * candle_width) + pos_x
        candle_color = 'red' if row['open'] > row['close'] else 'green'

        candle_top = (self.df['high'].max() - row['high']) / price_range * self.k
        candle_bottom = (self.df['high'].max() - row['low']) / price_range * self.k
        candle_open = (self.df['high'].max() - row['open']) / price_range * self.k
        candle_close = (self.df['high'].max() - row['close']) / price_range * self.k

        self.canvas.create_line(candle_x + candle_width / 2, self.candle_y + candle_top,
                                candle_x + candle_width / 2, self.candle_y + candle_bottom,
                                width=candle_outline_width, fill=candle_color)

        self.canvas.create_rectangle(candle_x, self.candle_y + candle_open, candle_x + candle_width,
                                     self.candle_y + candle_close,
                                     outline=candle_color, width=candle_outline_width, fill=candle_color)

    self.canvas.place(x=2, y=2)