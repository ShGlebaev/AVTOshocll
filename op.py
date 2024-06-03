import tkinter as tk

root = tk.Tk()

menubar = tk.Menu(root)
root.config(menu=menubar)

submenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Подменю", menu=submenu)

submenu.add_command(label="Пункт 1", command=lambda: print("Выбран пункт 1"))
submenu.add_command(label="Пункт 2", command=lambda: print("Выбран пункт 2"))
submenu.add_command(label="Пункт 3", command=lambda: print("Выбран пункт 3"))

root.mainloop()
