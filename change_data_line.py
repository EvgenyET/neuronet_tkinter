import datetime
import pandas as pd
import pickle

# Функция выбора расширенных данных из датафрейма Биткоина (выбор всех данных):

def draw_graph_line(self):
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

    # Create a line for the graph
    x_values = []
    y_values = []
    for i, row in self.df.iterrows():
        x_value = i * candle_width + pos_x + candle_width / 2
        y_value = (self.df['high'].max() - row['close']) / price_range * self.k + self.candle_y
        x_values.append(x_value)
        y_values.append(y_value)

    for i in range(1, len(x_values)):
        self.canvas.create_line(x_values[i - 1], y_values[i - 1], x_values[i], y_values[i], fill='blue')

    self.canvas.place(x=2, y=2)