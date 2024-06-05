from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog
from tkinter import ttk
import sqlite3 as sq
from io import BytesIO

import PIL
from PIL import ImageTk, Image

from tkcalendar import *

current_user = None

with sq.connect("databaz") as db:
    c = db.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS people (
    ID INTEGER,
    password TEXT,
    photo BLOB,
    F TEXT,
    I TEXT,
    O TEXT,
    POST TEXT
    ) """)

with sq.connect("databaz") as db:
    c = db.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS time (
    name_ex TEXT,
    date INTEGER
    ) """)


def login_screan(root):
    clear_screen(root)
    Label(root, text="Авторизация").pack()
    Label(root, text="Введите ID:").pack()
    ID_entry = Entry(root)
    ID_entry.pack()
    Label(root, text="Пароль:").pack()
    password_entry = Entry(root, show="*")
    password_entry.pack()
    togle = Button(root, text="Показать", command=lambda: toggle_password(password_entry, togle))
    togle.place(x=265, y=80)
    Button(root, text="Войти", command=lambda: login(root, ID_entry.get(), password_entry.get())).pack()


def toggle_password(password_entry, togle):
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


def login(root, ID_entry, password_entry):
    global current_user
    if not ID_entry or not password_entry:
        mb.showerror("Ошибка", "Вы не ввели логин или пароль!")
    else:
        with sq.connect("databaz") as db:
            c = db.cursor()
            c.execute("SELECT * FROM people WHERE ID=? AND password=?", (ID_entry, password_entry))
            user = c.fetchone()
            if user:
                current_user = {
                    'ID': user[0],
                    'password': user[1],
                    'F': user[2],
                    'I': user[3],
                    'O': user[4],
                    'POST': determine_user_post(user[0])
                }
                main_screen(root)
                mb.showinfo("Авторизация", "Авторизация прошла успешно")
            else:
                mb.showerror("Ошибка", "Неверный ID или пароль")


def determine_user_post(ID):
    first_digit = int(str(ID)[0])
    if first_digit == 1:
        return "Администратор"
    elif first_digit == 2:
        return "Преподаватель"
    elif first_digit == 3:
        return "Преподаватель-методист"
    elif first_digit == 4:
        return "Студент"
    else:
        return "Неизвестно"


def main_screen(root):
    clear_screen(root)
    if current_user:
        first_digit = int(str(current_user['ID'])[0])
        if first_digit == 1:
            admin_screan(root)
        elif first_digit == 2:
            teacher_screan(root)
        elif first_digit == 3:
            instructor_screan(root)
        elif first_digit == 4:
            student_screan(root)
        else:
            Label(root, text="Неизвестная роль").pack()
    else:
        Label(root, text="Неизвестная роль").pack()


def add_user(id, password, surname, name, patronymic, post, photo_path):
    with sq.connect("databaz") as db:
        c = db.cursor()

        # Загрузка фотографии из файла
        with open(photo_path, 'rb') as file:
            photo_data = file.read()

        # Вставка данных пользователя в базу данных
        c.execute("INSERT INTO people (ID, password, F, I, O, POST, photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (id, password, surname, name, patronymic, post, photo_data))
        db.commit()


def user_add():
    second = Toplevel()
    Label(second, text="Добавление пользователя").pack()

    Label(second, text="ID:").pack()
    id_entry = Entry(second)
    id_entry.pack()

    Label(second, text="Пароль:").pack()
    password_entry = Entry(second)
    password_entry.pack()

    Label(second, text="Фамилия:").pack()
    surname_entry = Entry(second)
    surname_entry.pack()

    Label(second, text="Имя:").pack()
    name_entry = Entry(second)
    name_entry.pack()

    Label(second, text="Отчество:").pack()
    patronymic_entry = Entry(second)
    patronymic_entry.pack()

    Label(second, text="Фотография:").pack()
    photo_entry = Entry(second)
    photo_entry.pack()
    photo_btn = Button(second, text="...", command=lambda: select_file(photo_entry))
    photo_btn.place(x=137, y=239)

    Label(second, text="Должность:").pack()
    post_combobox = ttk.Combobox(second, values=["Администратор", "Преподаватель", "Преподаватель-инструктор", "Студент"])
    post_combobox.pack()

    Button(second, text="Добавить", command=lambda: add_user(id_entry.get(), password_entry.get(), surname_entry.get(),
                                                           name_entry.get(),
                                    patronymic_entry.get(), post_combobox.get(), photo_entry.get())).pack()


def select_file(photo_entry):
    file_path = filedialog.askopenfilename()

    photo_entry.delete(0, 'end')
    photo_entry.insert(0, file_path)


def show_users():
    users_window = Toplevel()
    users_window.geometry('400x250')  # Задаем меньший размер окна

    # Создаем Treeview с настройкой ширины столбцов
    users_tree = ttk.Treeview(users_window, columns=("ID", "Фамилия", "Имя"), show='headings')
    users_tree.column("ID", width=50)  # Задаем ширину столбца
    users_tree.column("Фамилия", width=150)
    users_tree.column("Имя", width=150)
    users_tree.heading("ID", text="ID")
    users_tree.heading("Фамилия", text="Фамилия")
    users_tree.heading("Имя", text="Имя")

    # Заполняем данными
    with sq.connect("databaz") as db:
        c = db.cursor()
        c.execute("SELECT * FROM people")
        users = c.fetchall()
        for user in users:
            users_tree.insert("", "end", values=(user[0], user[2], user[3]))

    users_tree.pack()  # Позволяем этому виджету заполнить все доступное пространство

    # Функция для удаления выбранного пользователя
    def delete_selected_user():
        selected_item = users_tree.selection()[0]  # Получаем выбранный элемент
        user_details = users_tree.item(selected_item)['values']  # Получаем детали пользователя
        user_id = user_details[0]  # Получаем ID пользователя

        # Создаем окно подтверждения
        confirm_window = Toplevel(users_window)
        confirm_window.title("Подтверждение удаления")
        confirm_window.geometry("300x150")

        Label(confirm_window, text=f"Вы точно хотите удалить следующую запись?\nID: {user_id}\nФамилия: {user_details[1]}\nИмя: {user_details[2]}").pack(pady=10)

        def confirm_delete():
            users_tree.delete(selected_item)  # Удаляем элемент из Treeview
            with sq.connect("databaz") as db:  # Удаляем пользователя из базы данных
                c = db.cursor()
                c.execute("DELETE FROM people WHERE ID=?", (user_id,))
                db.commit()
            confirm_window.destroy()

        Button(confirm_window, text="Удалить", command=confirm_delete).pack(side=LEFT, padx=20, pady=10)
        Button(confirm_window, text="Отмена", command=confirm_window.destroy).pack(side=RIGHT, padx=20, pady=10)

    delete_button = Button(users_window, text="Удалить", command=delete_selected_user)
    delete_button.pack()


def admin_screan(root):
    clear_screen(root)
    root.title("Меню администратора")
    Label(root, text="Профиль администратора").pack()

    with sq.connect("databaz") as db:
        c = db.cursor()
        c.execute("SELECT F, I, O, photo FROM people WHERE ID = ?", (current_user['ID'],))
        user_info = c.fetchone()

    full_name = f"{user_info[0]} {user_info[1]} {user_info[2]}"

    try:
        photo = Image.open(BytesIO(user_info[3]))
    except PIL.UnidentifiedImageError:
        print("Unable to open image")
        photo = None

    Label(root, text=f"Добро пожаловать, {full_name}!").pack()

    if photo is not None:
        photo_frame = Frame(root)
        photo_frame.pack()
        photo_label = Label(photo_frame)
        photo_label.pack()
        photo_image = ImageTk.PhotoImage(photo)
        photo_label.config(image=photo_image)
        photo_label.image = photo_image

    menu_admin = Menu(root)
    root.config(menu=menu_admin)
    submenu_admin = Menu(menu_admin, tearoff=0)
    menu_admin.add_cascade(label='Управление пользователями', menu=submenu_admin)
    submenu_admin.add_command(label='Добавить пользователя', command=user_add)
    submenu_admin.add_command(label='Удалить пользователя', command=show_users)
    menu_admin.add_command(label='Календарь', command=open_calendar)
    menu_admin.add_command(label='Памятка', command=the_memo)

    # Добавляем кнопку выхода из аккаунта
    logout_button = Button(root, text="Выйти", command=lambda: logout(root))
    logout_button.place(relx=1.0, rely=0.0, anchor='ne')


def open_calendar():
    calendar_window = Toplevel()
    calendar_window.title("Календарь")
    #calendar_window.geometry("250x400")

    cal = Calendar(calendar_window, selectmode='day', locale='ru_RU')
    cal.pack()

    event_text = Text(calendar_window, height=10, width=40)
    event_text.pack()

    Button(calendar_window, text="Назначить экзамен", command=lambda: open_event_window(event_text)).pack()
    Button(calendar_window, text="Обновить", command=lambda: display(event_text)).pack()


def the_memo(file_path='Meno.txt'):
    meno_scrin = Toplevel()
    meno_scrin.title("Памятка")
    Label(meno_scrin, text="Памятка по добовлению пользователей").pack()
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            text = file.read()
        text_field = Text(meno_scrin)
        text_field.insert('1.0', text)
        text_field.configure(state='disabled')
        text_field.pack()
    except IOError as e:
        print(f"Ошибка при чтении файла: {e}")
    #Button(meno_scrin, text="Вернуться", command=back).place(relx=1.0, rely=0.0, anchor='ne')


def back():
    clear_screen(root)
    admin_screan(root)


def open_event_window(event_type):
    event_window = Toplevel()
    event_window.title(event_type)

    Label(event_window, text="Год:").pack()
    year_entry = Entry(event_window)
    year_entry.pack()

    Label(event_window, text="Месяц:").pack()
    month_entry = Entry(event_window)
    month_entry.pack()

    Label(event_window, text="День:").pack()
    day_entry = Entry(event_window)
    day_entry.pack()

    Label(event_window, text="Час:").pack()
    hour_entry = Entry(event_window)
    hour_entry.pack()

    Label(event_window, text="Минуты:").pack()
    minutes_entry = Entry(event_window)
    minutes_entry.pack()

    Label(event_window, text="Тип экзамена:").pack()
    nameex_combobox = ttk.Combobox(event_window, values=[
        "1. Экзамен в ГАИ",
        "2. Первая контрольная точка",
        "3. Вторая контрольная точка",
        "4. Третья контрольная точка",
        "5. Внутренний экзамен"
    ])
    nameex_combobox.pack()

    def add_date():
        year = year_entry.get()
        month = month_entry.get()
        day = day_entry.get()
        hour = hour_entry.get()
        minutes = minutes_entry.get()
        nameex = nameex_combobox.get()

        # Проверка заполнения всех полей
        if not year or not month or not day or not hour or not minutes or not nameex:
            mb.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Обработка значений для получения формата YYYYMMDDHHMM
        date = year + month + day + hour + minutes

        with sq.connect("databaz") as db:
            c = db.cursor()
            c.execute("INSERT INTO time (name_ex, date) VALUES (?, ?)",
                      (nameex, date))

        mb.showinfo("Успех", "Данные успешно добавлены.")
        display(event_text)
    Button(event_window, text="Добавить", command=add_date).pack()


def display(event_text):
    # Очистка текстового поля
    event_text.delete(1.0, END)

    # Извлечение данных из базы данных
    conn = sq.connect("databaz")
    c = conn.cursor()
    c.execute("SELECT name_ex, date FROM time")
    rows = c.fetchall()
    for row in rows:
        name_ex = row[0]
        date = str(row[1])  # Преобразование date в строку

        # Форматирование даты и времени
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        hour = date[8:10]
        minutes = date[10:12]

        formatted_date = f"{day}.{month}.{year} {hour}:{minutes}"

        # Добавление данных в текстовое поле
        event_text.insert(END, f"{formatted_date}: {name_ex}\n")


def teacher_screan(root):
    clear_screen(root)
    Label(root, text="Профиль преподавателя").pack()

    with sq.connect("databaz") as db:
        c = db.cursor()
        c.execute("SELECT F, I, O, photo FROM people WHERE ID = ?", (current_user['ID'],))
        user_info = c.fetchone()

    full_name = f"{user_info[0]} {user_info[1]} {user_info[2]}"

    try:
        photo = Image.open(BytesIO(user_info[3]))
    except PIL.UnidentifiedImageError:
        print("Unable to open image")
        photo = None

    Label(root, text=f"Добро пожаловать, {full_name}!").pack()

    if photo is not None:
        photo_frame = Frame(root)
        photo_frame.pack()
        photo_label = Label(photo_frame)
        photo_label.pack()
        photo_image = ImageTk.PhotoImage(photo)
        photo_label.config(image=photo_image)
        photo_label.image = photo_image

    # Добавляем кнопку выхода из аккаунта
    logout_button = Button(root, text="Выйти", command=lambda: logout(root))
    logout_button.place(relx=1.0, rely=0.0, anchor='ne')


def instructor_screan(root):
    clear_screen(root)
    Label(root, text="Профиль преподавателя-инструктора").pack()

    with sq.connect("databaz") as db:
        c = db.cursor()
        c.execute("SELECT F, I, O, photo FROM people WHERE ID = ?", (current_user['ID'],))
        user_info = c.fetchone()

    full_name = f"{user_info[0]} {user_info[1]} {user_info[2]}"

    try:
        photo = Image.open(BytesIO(user_info[3]))
    except PIL.UnidentifiedImageError:
        print("Unable to open image")
        photo = None

    Label(root, text=f"Добро пожаловать, {full_name}!").pack()

    if photo is not None:
        photo_frame = Frame(root)
        photo_frame.pack()
        photo_label = Label(photo_frame)
        photo_label.pack()
        photo_image = ImageTk.PhotoImage(photo)
        photo_label.config(image=photo_image)
        photo_label.image = photo_image

    # Добавляем кнопку выхода из аккаунта
    logout_button = Button(root, text="Выйти", command=lambda: logout(root))
    logout_button.place(relx=1.0, rely=0.0, anchor='ne')


def student_screan(root):
    clear_screen(root)
    Label(root, text="Профиль студента").pack()

    with sq.connect("databaz") as db:
        c = db.cursor()
        c.execute("SELECT F, I, O, photo FROM people WHERE ID = ?", (current_user['ID'],))
        user_info = c.fetchone()

    full_name = f"{user_info[0]} {user_info[1]} {user_info[2]}"

    try:
        photo = Image.open(BytesIO(user_info[3]))
    except PIL.UnidentifiedImageError:
        print("Unable to open image")
        photo = None

    Label(root, text=f"Добро пожаловать, {full_name}!").pack()

    if photo is not None:
        photo_frame = Frame(root)
        photo_frame.pack()
        photo_label = Label(photo_frame)
        photo_label.pack()
        photo_image = ImageTk.PhotoImage(photo)
        photo_label.config(image=photo_image)
        photo_label.image = photo_image

    # Добавляем кнопку выхода из аккаунта
    logout_button = Button(root, text="Выйти", command=lambda: logout(root))
    logout_button.place(relx=1.0, rely=0.0, anchor='ne')


def logout(root):
    global current_user
    current_user = None
    login_screan(root)


def clear_screen(root):
    for widget in root.winfo_children():
        widget.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title('Авторизация')
    root.geometry('400x300')
    root.iconbitmap('Автошколакамикадзе.ico')
    login_screan(root)

    root.mainloop()
