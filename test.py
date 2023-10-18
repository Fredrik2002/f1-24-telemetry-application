from tkinter import *
from tkinter import ttk

window = Tk()
window.geometry('400x600')
first_label = ttk.Label(text = "First label", background="red", anchor='center')
second_label = ttk.Label(text = "Label 2", background="blue")
last = ttk.Label(text = "Last of labels", background="green")
button = ttk.Button(text="Button")

first_label.pack(fill="x")
second_label.pack(expand=True, fill="none")
last.pack(expand=True, fill="both")
button.pack(fill="x")

window.mainloop()

