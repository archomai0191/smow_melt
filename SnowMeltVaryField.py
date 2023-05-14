#Модуль, содержащий описание формы с вариацией коэффициента водного эквивалента снега для поля

import tkinter as tk, FormDataClass as fdc, math, datetime as dt, SnowMeltLogic as sml, os
from tkinter import filedialog as fd
from tkinter.ttk import Checkbutton
from tkinter.messagebox import showinfo

def heightClicked(): #обработчик для checkbox-a "Высота"
    forestCoefEntry.configure(state = "normal" if heightChk_state.get() else "disabled")
    fieldCoefEntry.configure(state = "normal" if heightChk_state.get() else "disabled")

def expClicked(): #обработчик для checkbox-a "Экспозиция"
    southEntry.configure(state = "normal" if expChk_state.get() else "disabled")
    westEntry.configure(state = "normal" if expChk_state.get() else "disabled")
    eastEntry.configure(state = "normal" if expChk_state.get() else "disabled")
    northEntry.configure(state = "normal" if expChk_state.get() else "disabled")
    plainEntry.configure(state = "normal" if expChk_state.get() else "disabled")

def forestClicked(): #обработчик для checkbox-a "Изменить водный эквивалент снега для леса"
    snowForestDefEntry.set("2")
    snowForestCoefEntry.configure(state = "normal" if snowForestChk_state.get() else "disabled")

def pickFile(): #обработчик для кнопки "Выбрать файл"
    filetypes = [('Файлы DBF', '*.dbf')]
    filename = fd.askopenfilename(title = "Выберите файл", initialdir = "/", filetypes = filetypes)
    pathLbl.configure(text = filename if filename != "" else "Файл с данными о точках не выбран")

def parseEntry(elem, message): #преобразование строки в вещественное число
    try:
        res = float(elem.get().replace(",", ".")) #замена запятой на точку и преобразование к вещественному числу
        return res
    except: #преобразовать не удалось => было введено не число, сообщаем об этом
        showinfo(title = "Ошибка в параметрах", message = message)
        return float('NaN')

def run(): #обработчик для кнопки "Расчет"
    #чтение и проверка временного промежутка
    startTime = sml.parseDt(startEntry, True, "Неверный формат для начала временного промежутка")
    endTime = sml.parseDt(endEntry, False, "Неверный формат для конца временного промежутка")
    if startTime is None or endTime is None: return
    if startTime > endTime:
        showinfo(title = "Ошибка в параметрах", message = 
            "Начало временного промежутка не может наступить позже, чем его конец")
        return

    #чтение и проверка порога высоты и коэффициентов водного эквивалента снега
    heightTh = parseEntry(heightEntry, "В качестве порога высоты введено не число")
    wEqForest = parseEntry(snowForestCoefEntry, "В качестве водного эквивалента снега для леса введено не число")
    wEqFieldMin = parseEntry(snowFieldLowBorder,
        "В качестве нижней границы водного эквивалента снега для леса введено не число")
    wEqFieldMax = parseEntry(snowFieldHighBorder,
        "В качестве верхней границы водного эквивалента снега для леса введено не число")
    step = parseEntry(snowFieldStep, "В качестве шага введено не число")
    if math.isnan(heightTh) or math.isnan(wEqForest) or math.isnan(wEqFieldMin) or math.isnan(wEqFieldMax) \
        or math.isnan(step): return
    
    if (step > 0 and wEqFieldMin > wEqFieldMax) or (step < 0 and wEqFieldMin < wEqFieldMax):
        showinfo(title = "Ошибка в параметрах", message = "Неверный дипазон вариации коэффициента")
        return
    if (step == 0):
        showinfo(title = "Ошибка в параметрах", message = "Шаг не может быть равным 0")
        return
    
    if not heightChk_state.get():
        #если высота не учитывается, высотные коэффициенты имеют значения по умолчанию
        forestCoef = 0.9739
        fieldCoef = 0.9739
    else: #иначе - проверка этих коэффициентов
        forestCoef = parseEntry(forestCoefEntry, "В качестве высотного коэффициента для леса введено не число")
        fieldCoef = parseEntry(fieldCoefEntry, "В качестве высотного коэффициента для поля введено не число")
        if math.isnan(forestCoef) or math.isnan(fieldCoef): return
    
    if not expChk_state.get():
        #если экспозиция не учитывается, экспозиционные коэффициенты имеют значения по умолчанию
        sCoef = 1
        nCoef = 1
        wCoef = 1
        eCoef =  1
        pCoef = 1
    else: #иначе - проверка этих коэффициентов
        sCoef = parseEntry(southEntry, "В качестве экспозиционного коэффициента для юга введено не число")
        nCoef = parseEntry(northEntry, "В качестве экспозиционного коэффициента для севера введено не число")
        wCoef = parseEntry(westEntry, "В качестве экспозиционного коэффициента для запада введено не число")
        eCoef = parseEntry(eastEntry, "В качестве экспозиционного коэффициента для востока введено не число")
        pCoef = parseEntry(plainEntry, "В качестве экспозиционного коэффициента для равнины введено не число")
        if math.isnan(sCoef) or math.isnan(nCoef) or math.isnan(wCoef) or math.isnan(eCoef) \
            or math.isnan(pCoef): return

    if pathLbl.cget("text") == "Файл с данными о точках не выбран":
        showinfo(title = "Ошибка в параметрах", message = "Сначала выберите файл")
        return
    
    app_folder = os.path.dirname(os.path.realpath(__file__))
    app_folder = app_folder.replace("\\", "/")
    if not os.path.exists(app_folder + "/results_field"): os.mkdir(app_folder + "/results_field")

    wEqField = wEqFieldMin
    while wEqField < wEqFieldMax:
        #запуск расчетов
        data = fdc.FormData(pathLbl.cget("text"), startTime, endTime, heightTh, heightChk_state.get(), expChk_state.get(),
            wEqField, wEqForest, forestCoef, fieldCoef, sCoef, nCoef, wCoef, eCoef, pCoef)
        try:
            sml.run(data)
            if not os.path.exists(app_folder + "/results_field/" + str(wEqField).replace(".", ",")):
                os.mkdir(app_folder + "/results_field/" + str(wEqField).replace(".", ","))
            
            folder, name = os.path.split(data.file)
            os.replace(folder + "/les_group.dbf", app_folder + "/results_field/" + 
                str(wEqField).replace(".", ",") + "/les_group.dbf")
            os.replace(folder + "/pole_group.dbf", app_folder + "/results_field/" +
                str(wEqField).replace(".", ",") + "/pole_group.dbf")

        except Exception as e:
            showinfo(title = "Ошибка при расчетах", message = str(e))
        finally: wEqField += step

form = tk.Tk() #создание окна
#параметры окна
form.title("Расчет снеготаяния")
form.minsize(400, 400)
form.resizable(False, False)

#временной промежуток, для которого ведутся расчеты
startLbl = tk.Label(form, text = "Период с")
startLbl.grid(column = 0, row = 0, sticky = "W")
startEntry = tk.Entry(form)
startEntry.grid(column = 1, row = 0, padx = 10)
endLbl = tk.Label(form, text = "по")
endLbl.grid(column = 2, row = 0)
endEntry = tk.Entry(form)
endEntry.grid(column = 3, row = 0, padx = 10)

#порог высоты
heightLbl = tk.Label(form, text = "Порог высоты")
heightLbl.grid(column = 0, row = 1, pady = 10, sticky = "W")
heightEntry = tk.Entry(form, width = 10)
heightEntry.grid(column = 1, row = 1)

#высота
heightChk_state = tk.BooleanVar()
heightChk_state.set(True)
heightChk = Checkbutton(form, text = "Высота", var = heightChk_state, command = heightClicked)
heightChk.grid(column = 0, row = 3, pady = 10, sticky = "W")
forestCoefLbl = tk.Label(form, text = "Коэф. для леса")
forestCoefLbl.grid(column = 1, row = 3)
forestCoefEntry = tk.Entry(form, width = 10)
forestCoefEntry.grid(column = 2, row = 3)
fieldCoefLbl = tk.Label(form, text = "Коэф. для поля")
fieldCoefLbl.grid(column = 1, row = 4)
fieldCoefEntry = tk.Entry(form, width = 10)
fieldCoefEntry.grid(column = 2, row = 4)

#экспозиция
expChk_state = tk.BooleanVar()
expChk_state.set(True)
expChk = Checkbutton(form, text = "Экспозиция", var = expChk_state, command = expClicked)
expChk.grid(column = 0, row = 5, pady = 10, sticky = "W")
southLbl = tk.Label(form, text = "Юг")
southLbl.grid(column = 1, row = 5)
southEntry = tk.Entry(form, width = 10)
southEntry.grid(column = 2, row = 5)
westLbl = tk.Label(form, text = "Запад")
westLbl.grid(column = 1, row = 6)
westEntry = tk.Entry(form, width = 10)
westEntry.grid(column = 2, row = 6)
northLbl = tk.Label(form, text = "Север")
northLbl.grid(column = 1, row = 7, pady = 10)
northEntry = tk.Entry(form, width = 10)
northEntry.grid(column = 2, row = 7)
eastLbl = tk.Label(form, text = "Восток")
eastLbl.grid(column = 1, row = 8)
eastEntry = tk.Entry(form, width = 10)
eastEntry.grid(column = 2, row = 8)
plainLbl = tk.Label(form, text = "Равнина")
plainLbl.grid(column = 1, row = 9, pady = 10)
plainEntry = tk.Entry(form, width = 10)
plainEntry.grid(column = 2, row = 9)

#коэффициенты водного эквивалента снега
snowForestChk_state = tk.BooleanVar()
snowForestChk_state.set(True)
snowForestChk = Checkbutton(form, text = "Изменить водный эквивалент снега для леса", var = snowForestChk_state,
    command = forestClicked)
snowForestChk.grid(column = 0, row = 10, sticky = "W")
snowForestDefEntry = tk.StringVar()
snowForestDefEntry.set("2")
snowForestCoefEntry = tk.Entry(form, width = 10, textvariable = snowForestDefEntry)
snowForestCoefEntry.grid(column = 2, row = 10)
snowForestLbl = tk.Label(form, text = "Границы изменения водного эквивалента снега для поля")
snowForestLbl.grid(column = 0, row = 11, sticky = "W")
snowFieldLowBorder = tk.Entry(form, width = 10)
snowFieldLowBorder.grid(column = 1, row = 11)
snowFieldHighBorder = tk.Entry(form, width = 10)
snowFieldHighBorder.grid(column = 2, row = 11)
snowFieldStepLbl = tk.Label(form, text = "Шаг")
snowFieldStepLbl.grid(column = 3, row = 11)
snowFieldStep = tk.Entry(form, width = 10)
snowFieldStep.grid(column = 4, row = 11)

#путь к файлу с данными о точках
pathLbl = tk.Label(form, text = "Файл с данными о точках не выбран")
pathLbl.grid(column = 0, row = 12, sticky = "W")

#выбор файла и начало расчетов
fileBtn = tk.Button(form, text = "Выбрать файл", width = 20, command = pickFile)
fileBtn.grid(column = 0, row = 13, padx = 20, pady = 10)
runBtn = tk.Button(form, text = "Расчет", width = 20, command = run)
runBtn.grid(column = 1, row = 13)

#отображение окна и запуск приложения
form.mainloop()
