import tkinter as tk, os

def runSingle():
    os.system(f"python \"{app_folder}/SnowMeltSingle.py\"")

def runForestVary():
    os.system(f"python \"{app_folder}/SnowMeltVaryForest.py\"")

def runFieldVary():
    os.system(f"python \"{app_folder}/SnowMeltVaryField.py\"")

def runAnalysis():
    os.system(f"python \"{app_folder}/SnowMeltAnalysis.py\"")

app_folder = os.path.dirname(os.path.realpath(__file__))
app_folder = app_folder.replace("\\", "/")
os.system("chcp 65001 > nul")

form = tk.Tk() #создание окна
#параметры окна
form.title("Расчет снеготаяния")
form.minsize(400, 300)
form.resizable(False, False)

#кнопки вызова форм
lbl2 = tk.Label(form)
lbl2.grid(row = 3, column = 0)
lbl3 = tk.Label(form)
lbl3.grid(row = 6, column = 0)

singleBtn = tk.Button(form, text="Одиночный расчет (без вариаций)", width=100, command=runSingle)
singleBtn.grid(row=9, column=2)

lbl4 = tk.Label(form)
lbl4.grid(row = 10, column = 0)

forestBtn = tk.Button(form, text="Вариация для леса", width=100, command=runForestVary)
forestBtn.grid(row=11, column=2)

lbl5 = tk.Label(form)
lbl5.grid(row = 12, column = 0)

fieldBtn = tk.Button(form, text="Вариация для поля", width=100, command=runFieldVary)
fieldBtn.grid(row=13, column=2)

lbl6 = tk.Label(form)
lbl6.grid(row = 14, column = 0)

analysisBtn = tk.Button(form, text="Анализ результатов", width=100, command=runAnalysis)
analysisBtn.grid(row=15, column=2)

#отображение окна и запуск приложения
form.mainloop()