from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import sqlite3 as sq


current_user = None

with sq.connect("databaz") as db:
    c = db.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS people (
    ID INTEGER,
    password TEXT,
    F TEXT,
    I TEXT,
    O TEXT,
    POST TEXT
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


def add_user(id, password, surname, name, patronymic, post):
    with sq.connect("databaz") as db:
        c = db.cursor()
        c.execute("INSERT INTO people (ID, password, F, I, O, POST) VALUES (?, ?, ?, ?, ?, ?)", (id, password, surname, name, patronymic, post))
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

    Label(second, text="Роль:").pack()
    post_combobox = ttk.Combobox(second, values=["Администратор", "Преподаватель", "Преподаватель-методист", "Студент"])
    post_combobox.pack()

    Button(second, text="Добавить", command=lambda: add_user(id_entry.get(), password_entry.get(), surname_entry.get(),
                                                           name_entry.get(),
                                    patronymic_entry.get(), post_combobox.get())).pack()


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
        selected_item = users_tree.selection()[0]  # получаем выбранный элемент
        user_id = users_tree.item(selected_item)['values'][0]  # получаем ID пользователя
        users_tree.delete(selected_item)  # удаляем элемент из Treeview
        with sq.connect("databaz") as db:  # удаляем пользователя из базы данных
            c = db.cursor()
            c.execute("DELETE FROM people WHERE ID=?", (user_id,))
            db.commit()

    delete_button = Button(users_window, text="Удалить", command=delete_selected_user)
    delete_button.pack()


def admin_screan(root):
    clear_screen(root)
    Label(root, text="Профиль администратора").pack()

    menu_admin = Menu(root)
    root.config(menu=menu_admin)
    submenu_admin = Menu(menu_admin, tearoff=0)
    menu_admin.add_cascade(label='Управление пользователями', menu=submenu_admin)
    submenu_admin.add_command(label='Добавить пользователя', command=user_add)
    submenu_admin.add_command(label='Удалить пользователя', command=show_users)


def teacher_screan(root):
    clear_screen(root)
    Label(root, text="Профиль преподавателя").pack()

    # Добавляем кнопку выхода из аккаунта
    logout_button = Button(root, text="Выйти", command=lambda: logout(root))
    logout_button.place(relx=1.0, rely=0.0, anchor='ne')


def instructor_screan(root):
    clear_screen(root)
    Label(root, text="Профиль преподавателя-методиста").pack()

    # Добавляем кнопку выхода из аккаунта
    logout_button = Button(root, text="Выйти", command=lambda: logout(root))
    logout_button.place(relx=1.0, rely=0.0, anchor='ne')


def student_screan(root):
    clear_screen(root)
    Label(root, text="Профиль студента").pack()

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
