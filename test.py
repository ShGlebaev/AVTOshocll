from tkinter import *

# Создаем главное окно
root = Tk()
root.title("Пример с изображением в кнопке")
root.geometry("300x200")

# Загружаем изображение
img = PhotoImage(file="закрыть.png")

# Создаем кнопку с изображением
btn = Button(root, image=img, background="blue")
btn.pack()

# Запускаем главный цикл приложения
root.mainloop()
