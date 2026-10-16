import customtkinter
import tkinter as tk
import datetime
import pandas as pd
import pickle

customtkinter.set_appearance_mode("dark")  # Режимы: system (по умолчанию), light, dark
customtkinter.set_default_color_theme("blue")  # Темы: blue (по умолчанию), dark-blue, green

class MyFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = tk.Canvas(self, width=752, height=484, background='white', highlightthickness=0)
        self.canvas.pack(side="left")

        # TODO: Код, который растягивает панели x и у в соответствии с размером окна
        self.master.bind("<Configure>", self.update_canvas_size)

        # TODO: Растягиваем панель x (с датами) под размер окна
        self.date_canvas = tk.Canvas(self, height=32, background='#6B6B6B', highlightthickness=1)
        self.date_canvas.pack(side="bottom", fill="x")  # Используем fill="x" для растяжения по горизонтали

        # TODO: Растягиваем панель y (с ценами) под размер окна
        self.scale_canvas = tk.Canvas(self, width=40, background='#6B6B6B', highlightthickness=1)
        self.scale_canvas.pack(side="left", fill="y")  # Используем fill="y" для растяжения по вертикали

        # TODO: Привязываем маленькую угловую панель в зависимости от размера окна
        self.box_canvas = tk.Canvas(self, width=40, height=32, background='#6B6B6B', highlightthickness=1)
        self.box_canvas.place(x=0, rely=1.0, anchor="sw")  # Устанавливаем anchor="sw" для привязки к нижнему углу

        self.update_canvas_size(None)  # Вызываем один раз для инициализации положения и размеров

        # TODO: Записываем None в координату start_y, пока она не меняется (пока мы не двигали холст мышкой):
        self.start_y = None

        # TODO: Запуск всех функций:
        self.bind()
        self.mouse_cross()
        self.draw_graph()
        self.draw_y_price()
        self.draw_x_date()
        self.zoom_data()
        self.draw_corner_panel()

    # TODO: Функция для обновления размера холста
    def update_canvas_size(self, event):
        new_width = self.winfo_width() - 0
        new_height = self.winfo_height() - 0

        # Обновить размер холста
        self.canvas.config(width=new_width, height=new_height)

        # Рассчитать новое положение по оси y для date_canvas (ось x)
        date_canvas_y = new_height - self.date_canvas.winfo_height()

        # Установить ширину и переместить self.date_canvas (ось x) в новое положение
        self.date_canvas.config(width=new_width)
        self.date_canvas.place(x=41, y=date_canvas_y)

        # Установка высоты для scale_canvas (ось y)
        self.scale_canvas.config(height=new_height)

    # TODO: Привязка первой кнопки мыши для перетаскивания графика:
    def bind(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    # TODO: Функция для создания перекрестия мыши и привязки к движению мыши:
    def mouse_cross(self):
        # Создаём перекрестие мыши:
        self.horizontal_line = self.canvas.create_line(0, 0, 0, 0, fill="#F0F0F0")
        self.vertical_line = self.canvas.create_line(0, 0, 0, 0, fill="#F0F0F0")

        # Добавляем привязку функции для отображения перекрестия и цены на мышке:
        self.canvas.bind("<Motion>", self.draw_crosshair_and_price)

        # Добавляем привязку функции для скрытия перекрестия и цены на мышке:
        self.canvas.bind("<Leave>", self.hide_rosshair_and_price)

    # TODO: Функция, которая отвечает за создание перекрестия и цены на мышке:
    def draw_crosshair_and_price(self, event):
        x, y = event.x, event.y

        # Рисуем перекрестие мыши (и устанавливаем длину линий по ширине и высоте):
        self.canvas.coords(self.horizontal_line, -2000, y, 2000, y)
        self.canvas.coords(self.vertical_line, x, -1000, x, 1000)

        # Динамический удаляем ценовую метку при движении мыши:
        self.canvas.delete("price_label")

        # Нарисовать цену на перекрестии мыши (чтобы цена соответствовала движению мыши):
        self.price_crosshair = "{:.0f}".format(self.high_price - (y - self.candle_y) / self.k * self.price_range)
        self.price_label = self.canvas.create_text(x, y - 10, text=self.price_crosshair, tags=("price_label",), fill="#BDBDBD",
                                         font=("Arial", "7", "bold"))

        # Условие, которое перерисовывает ценовую метку, когда мы двигаем график мышкой вверх или вниз:
        if self.start_y is not None:
            self.canvas.delete("price_label")
            self.price_crosshair = "{:.0f}".format(self.high_price - (y - self.move_price) / self.k * self.price_range)
            self.price_label = self.canvas.create_text(x, y - 10, text=self.price_crosshair, tags=("price_label",), fill="#BDBDBD",
                                             font=("Arial", "7", "bold"))

        '''Далее часть кода, которая рисует динамическую ценовую метку на оси Y (цены), которая меняется при движении мыши:'''

        # Получение x, y-координат положения мыши:
        x, y = 38, event.y

        # Преобразуем координату y в значение цены, используя текущий ценовой диапазон и позицию candle_y
        price = (self.high_price - (y - self.candle_y) / self.k * self.price_range)

        # Динамический удаляем все существующие ценовые метки и прямоугольники при движении мыши:
        self.scale_canvas.delete("price_label2")
        self.scale_canvas.delete("price_rect")

        # Создаём прямоугольник под меткой цены на оси y:
        rect_y1 = y - 8
        rect_y2 = rect_y1 + 16
        self.scale_canvas.create_rectangle(2, rect_y1, 39, rect_y2, fill="#E3E3E3", outline="#4F4F4F", width=1, tags=("price_rect",))

        # Создаём метку с ценой на оси y:
        self.price_crosshair = "{:.0f}".format((self.high_price - (y - self.candle_y) / self.k * self.price_range))
        self.price_label2 = self.scale_canvas.create_text(x, y, text=self.price_crosshair, tags=("price_label2",),
                                                         fill="#4F4F4F", font=("Arial", "10", "bold"), anchor="e")


        '''Далее часть кода, которая рисует динамическую метку с датой на оси X (даты), которая меняется при движении мыши:'''

        # Получение x, y-координат положения мыши:
        x, y = event.x, 30

        # Динамический удаляем все существующие метки и прямоугольник при движении мыши:
        self.date_canvas.delete("date_label")
        self.date_canvas.delete("date_rect")

        # Создаём прямоугольник под меткой даты на оси X:
        rect_x1 = x - 67
        rect_x2 = rect_x1 + 56
        self.date_canvas.create_rectangle(rect_x1, 2, rect_x2, 31, fill="#CBCDCB", outline="#4F4F4F", width=1, tags=("date_rect",))

        # Обновление текста в прямоугольнике даты (рассчитываем дату в прямоугольнике метки на оси X с датами):
        rect_x_center = (rect_x1 + rect_x2) / 2
        date_idx = int((rect_x_center - 20) / 30)  # 30 - ширина свечи
        if date_idx >= 0 and date_idx < len(self.df):
            date_str = self.df.iloc[date_idx]['date'].strftime('%d-%m-%Y')
            self.date_canvas.delete("date_label")
            self.date_canvas.create_text(rect_x_center, 16, text=date_str, tags=("date_label",), fill="#4F4F4F",
                                         font=("Arial", "7", "bold"))
        else:
            self.date_canvas.delete("date_rect")

    # TODO: Функция, которая отвечает за исчезновение перекрестия мыши и цены, когда она выходит за границы холста:
    def hide_rosshair_and_price(self, event):

        #Исчезновение перекрестия мыши:
        self.canvas.coords(self.horizontal_line, 0, 0, 0, 0)
        self.canvas.coords(self.vertical_line, 0, 0, 0, 0)

        # Исчезновение цены:
        self.canvas.coords(self.price_label, 0, 0)

        # Исчезновение метки на оси Y (цена):
        self.scale_canvas.delete("price_label2", "price_rect")

        # Исчезновение метки на оси X (даты):
        self.date_canvas.delete("date_rect", "date_label")

    # TODO: Функция для создания свечного графика:
    def draw_graph(self):
        # Считываем датафрейм:
        with open('dataframe.pkl', 'rb') as file:
            self.df = pickle.load(file)

        # Обрезаем ненужные столбцы из датафрейма:
        self.df = self.df.iloc[:, :6]

        # Присваиваем имена столбцам:
        self.df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        # Обрезаем строки до нужного количества (указываем количество свечей):
        self.df = self.df.head(21)

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
        candle_width = 30

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
        distance_candles = 22

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

            self.canvas.create_rectangle(candle_x, self.candle_y + candle_open, candle_x + candle_width, self.candle_y + candle_close,
                                         outline=candle_color, width=candle_outline_width, fill=candle_color)

        self.canvas.place(x=2, y=2)

    # TODO: Функция для создания оси y (ось с ценами):
    def draw_y_price(self):
        # Добавляем левую панель для шкалы цен (ось y):
        self.scale_canvas = tk.Canvas(self, width=41, height=452, background='#6B6B6B', highlightthickness=1)
        self.scale_canvas.place(x=0, y=0)  # Устанавливаем положение в точке (0, 0)

        # Рисуем шкалу цен (ось y):
        self.scale_step = self.price_range / 20
        for i in range(-1, 40):
            price = self.low_price + self.scale_step * i
            y_pos = self.candle_y + self.k - (price - self.low_price) / self.price_range * self.k
            rounded_price = round(price)
            self.scale_canvas.create_text(37, y_pos, text=str(rounded_price), fill="white", font=("Arial", "9", "bold"),
                                          anchor="e")

        # self.scale_canvas.place(x=0, y=2)

    # TODO: Функция для создания оси x (ось с датами):
    def draw_x_date(self):
        # Добавляем нижнюю панель для дат (ось x):
        self.date_canvas = tk.Canvas(self, width=715, height=32, background='#6B6B6B', highlightthickness=1)
        self.date_canvas.pack(side="bottom")

        # Пишем даты по оси x:
        start_date = self.df['date'].min().date()
        end_date = self.df['date'].max().date()
        num_dates = 12  # количество дат для отображения
        days_between_dates = (end_date - start_date).days
        days_per_interval = days_between_dates // (num_dates - 1)
        date_width = self.date_canvas.winfo_reqwidth() / num_dates  # вычислить ширину каждой метки даты
        for i in range(num_dates):
            date_label = start_date + datetime.timedelta(days=(i * days_per_interval))
            x = i * date_width
            self.date_canvas.create_text(x + date_width / 2, 16, text=date_label.strftime('%d.%m.%Y'), fill="white",
                                         font=("Arial", "7", "bold"))

        self.date_canvas.place(x=41, y=456)

    # TODO: Функция для создания маленькой угловой панели:
    def draw_corner_panel(self):
        # Создаём маленькую угловую панель (квадрат в самом углу):
        self.box_canvas = tk.Canvas(self, width=40, height=32, background='#6B6B6B', highlightthickness=1)
        self.box_canvas.place(x=0, rely=1.0, anchor="sw")

    # TODO: Функции с данными для зуммирования:
    def zoom_data(self):
        # Данные для приближения и отдаления шкалы y при прокрутке колёсиком:
        self.scale_step = self.price_range / 8
        self.scale_y_offset = self.candle_y
        self.scale_height = self.k

        # Приближение и отдаление колёсиком мыши:
        self.canvas.bind_all("<MouseWheel>", self.zoom)

    # TODO: Функция обратного вызова для настройки масштаба холста по событию колеса мыши:
    def zoom(self, event):
        # Получить текущий коэффициент масштабирования (положительный для увеличения, отрицательный для уменьшения)
        # (можно регулировать скорость прокрутки)
        zoom_factor = 1.1 if event.delta > 0 else 1 / 1.1
        if event.delta > 0:
            zoom_factor_date1 = 1.1
            zoom_factor_date2 = 1
        else:
            zoom_factor_date1 = 0.9
            zoom_factor_date2 = 1

        # Обновление высоты и смещения по оси y:
        self.scale_height *= zoom_factor
        self.scale_y_offset = event.y - (event.y - self.scale_y_offset) * zoom_factor

        # Рассчитываем новые размеры свечи:
        candle_width = 30 * zoom_factor

        # Обновление позиций элементов на холсте:
        self.canvas.scale("all", event.x, event.y, zoom_factor, zoom_factor)
        self.date_canvas.scale("all", event.x, event.y, zoom_factor_date1, zoom_factor_date2)
        self.scale_canvas.delete("all")

        for i in range(-1, 40):
            self.scale_step = self.price_range / 30
            price = self.low_price + self.scale_step * i
            y = self.scale_y_offset + self.scale_height - (price - self.low_price) / self.price_range * self.scale_height
            rounded_price = round(price)
            self.scale_canvas.create_text(37, y, text=str(rounded_price), fill="white",
                                          font=("Arial", "9", "bold"), anchor="e")

        self.canvas.place(x=2, y=2)
        self.scale_canvas.place(x=0, y=2)

    # TODO: Функция старта перемещения графика кнопкой мыши:
    def start_drag(self, event):
        # Записываем текущее положение мыши в переменные start_x и start_y:
        self.start_x = event.x
        self.start_y = event.y

        # Меняем координаты сдвига свечей по высоте (self.candle_y) после перемещения графика мышкой:
        self.update_start_y = self.start_y
        self.start_position = self.candle_y

        '''Я пропустил ошибку. Исправить эту ошибку потом (ошибка связвна с расчётом цены на перекрестии)!:'''
        try:
         self.start_position = self.shift
        except:
            pass

    # TODO: Функция перемещения графика и осей x и y левой кнопкой мыши:
    def on_drag(self, event):
        # Вычислить разницу в положении мыши:
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        # Переместить график и оси:
        self.canvas.move("all", dx, dy)
        self.scale_canvas.move("all", 0, dy)
        self.date_canvas.move("all", dx, 0)

        # Обновить начальную позицию для следующего события перетаскивания:
        self.start_x = event.x
        self.start_y = event.y

        # Формула, которая рассчитывает новые координаты сдвига свечей по высоте (self.candle_y), после перетасквания:
        self.shift = self.start_position - (self.update_start_y - self.start_y)
        self.move_price = self.shift

    # TODO: Функция останавливающая перемещение:
    def stop_drag(self, event):
        # пока ничего не делать
        pass

    # TODO: Функции, которые сбрасывает состояние графика после зуммирования или перемещения:
    def reset_graph(self):
        # Очищаем все панели:
        self.canvas.delete("all")
        self.scale_canvas.delete("all")
        self.date_canvas.delete("all")

        # Перезапускаем все функции:
        self.bind()
        self.mouse_cross()
        self.draw_graph()
        self.draw_y_price()
        self.draw_x_date()
        self.zoom_data()
        self.draw_corner_panel()

        self.start_y = None

    def change_data(self):
        # Очищаем все панели:
        self.canvas.delete("all")
        self.scale_canvas.delete("all")
        self.date_canvas.delete("all")

        # Перезапускаем все функции:
        self.bind()
        self.mouse_cross()
        from change_data import draw_graph2
        draw_graph2(self)
        self.draw_y_price()
        self.draw_x_date()
        self.zoom_data()
        self.draw_corner_panel()

        self.start_y = None

    def change_data_log(self):
        # Очищаем все панели:
        self.canvas.delete("all")
        self.scale_canvas.delete("all")
        self.date_canvas.delete("all")

        # Перезапускаем все функции:
        self.bind()
        self.mouse_cross()
        from change_data_log import draw_graph_log
        draw_graph_log(self)
        self.draw_y_price()
        self.draw_x_date()
        self.zoom_data()
        self.draw_corner_panel()

        self.start_y = None

    def change_data_line(self):
        # Очищаем все панели:
        self.canvas.delete("all")
        self.scale_canvas.delete("all")
        self.date_canvas.delete("all")

        # Перезапускаем все функции:
        self.bind()
        self.mouse_cross()
        from change_data_line import draw_graph_line
        draw_graph_line(self)
        self.draw_y_price()
        self.draw_x_date()
        self.zoom_data()
        self.draw_corner_panel()

        self.start_y = None

    def change_data_log_line(self):
        # Очищаем все панели:
        self.canvas.delete("all")
        self.scale_canvas.delete("all")
        self.date_canvas.delete("all")

        # Перезапускаем все функции:
        self.bind()
        self.mouse_cross()
        from change_data_log_line import draw_graph_log_line
        draw_graph_log_line(self)
        self.draw_y_price()
        self.draw_x_date()
        self.zoom_data()
        self.draw_corner_panel()

        self.start_y = None

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # TODO: Условия для позиций on и off переключателей CTkSwitch (функции "switch_callback"):
        self.is_on1 = False
        self.is_on2 = False

        self.geometry("800x600")
        self.title("Свечной график")
        self.minsize(800, 600)
        self.grid_rowconfigure(0, weight=1)  # настроить систему сетки
        self.grid_columnconfigure(0, weight=2)

        self.my_frame = MyFrame(master=self, border_width=0, fg_color=("white"), height=800, width=800)
        self.my_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

        # TODO: Расположение, команды и текст для меню с выбором опций, а также текстовая метка над меню:
        self.appearance_mode_label = customtkinter.CTkLabel(master=self, text="Выбор режима:", text_color="#7a848d")
        self.appearance_mode_label.grid(row=1, column=0, padx=20, pady=0, ipadx=0, ipady=0, sticky="sw")

        # TODO: Переключатель выбора режима отображения графика (переключатель 1):
        self.switch = customtkinter.CTkSwitch(master=self, command=self.switch_callback1, text="Логарифм. график", text_color="#7a848d")
        self.switch.grid(row=1, column=0, padx=140, pady=1, ipadx=0, ipady=0, sticky="sw")

        # TODO: Переключатель выбора режима отображения графика (переключатель 2):
        self.switch = customtkinter.CTkSwitch(master=self, command=self.switch_callback2, text="Линейный график", text_color="#7a848d")
        self.switch.grid(row=1, column=0, columnspan=3, padx=310, ipadx=0, pady=1, ipady=0, sticky="sw")

        # TODO: Выпадающий список с выборами вариантов графика:
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(master=self,
                                                                       values=["График 1 (двадцать свечей)", "График 2 (расширенные данные)", "График 3 (логарифмический график)"],
                                                                       command=self.change_appearance_mode_event, fg_color="#343638",
                                                                       button_color="#565b5e", button_hover_color="#7a848d",
                                                                       dropdown_fg_color="#333333", dropdown_hover_color="#474747")
        self.appearance_mode_optionemenu.grid(row=2, column=0, padx=20, pady=15, ipadx=0, ipady=0, sticky="ew")


        # TODO: Расположение, команды и текст для синей кнопки "Сбросить":
        self.button = customtkinter.CTkButton(master=self, command=self.button_callback, text="Сбросить")
        self.button.grid(row=2, column=1, padx=20, pady=15, ipadx=0, ipady=0, sticky="ew")

    # TODO: Функция для кнопки сброса состояния графиков CTkButton (условие сответствует выбранному полю в меню CTkOptionMenu):
    def button_callback(self):
        if self.appearance_mode_optionemenu.get() == "График 2 (расширенные данные)":
            self.my_frame.change_data()
        elif self.appearance_mode_optionemenu.get() == "График 1 (двадцать свечей)":
              self.my_frame.reset_graph()
        elif self.appearance_mode_optionemenu.get() == "График 3 (логарифмический график)":
              self.my_frame.change_data_log()

    # TODO: Функция для выбора из списка CTkOptionMenu:
    def change_appearance_mode_event(self, values):
        if values == "График 2 (расширенные данные)":
            self.my_frame.change_data()
        elif values in ["График 1 (двадцать свечей)"]:
            self.my_frame.reset_graph()
        elif values in ["График 3 (логарифмический график)"]:
            self.my_frame.change_data_log()

    # TODO: Функция для переключателя CTkSwitch (Логарифмический график):
    def switch_callback1(self):
        if self.is_on1 == False and self.is_on2 == False:
            self.my_frame.change_data_log()
            self.is_on1 = True

        elif self.is_on1 == True and self.is_on2 == False:
            self.my_frame.change_data()
            self.is_on1 = False

        elif self.is_on1 == True and self.is_on2 == True:
            self.my_frame.change_data_line()
            self.is_on1 = True

        elif self.is_on1 == False and self.is_on2 == True:
            self.my_frame.change_data_log_line()
            self.is_on1 = True

        # else:
        #     self.my_frame.change_data()
        #     self.is_on1 = False

    # TODO: Функция для переключателя CTkSwitch (Линейный график):
    def switch_callback2(self):
        if self.is_on1 == False and self.is_on2 == False:
            self.my_frame.change_data_line()
            self.is_on2 = True

        elif self.is_on1 == True and self.is_on2 == False:
            self.my_frame.change_data_log_line()
            self.is_on2 = True

        elif self.is_on1 == True and self.is_on2 == True:
            self.my_frame.change_data_log()
            self.is_on2 = False

        elif self.is_on1 == False and self.is_on2 == True:
            self.my_frame.change_data()
            self.is_on2 = False

        elif self.appearance_mode_optionemenu.get() == "График 2 (расширенные данные)" and self.is_on2 == False:
            self.my_frame.change_data_line()
            self.is_on2 = True
        # else:
        #     self.my_frame.change_data()
        #     self.is_on2 = False

app = App()
app.mainloop()