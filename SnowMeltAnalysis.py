import tkinter as tk, os, pandas as pd, datetime as dt
from tkinter import filedialog as fd, messagebox as msg
from tkinter.messagebox import showinfo
from pathlib import Path
from simpledbf import Dbf5

def loadRealData():
    global realDataFile
    realDataFile = fd.askopenfilename(title = "Выберите файл с данными снегомерных маршрутов", \
        filetypes=[('Файлы XLSX', '*.xlsx')], initialdir = app_folder)

def directory_selector(windowTitle: str, selected: list):
    directory_path_string = fd.askdirectory(initialdir=app_folder, title=windowTitle)

    if len(directory_path_string) > 0:
        selected.append(directory_path_string)
        print ("Выбранные папки: ", selected)
        directory_selector('Выберите следующую папку или нажмите Отмена, чтобы закончить', selected)

    return selected

def calcError(folder, year, result_type):
    global realDataFile
    result_path = f"{folder}/{result_type}_group.dbf"
    result_frame = Dbf5(result_path).to_dataframe()
    real_frame = pd.read_excel(realDataFile)
    group_like = real_frame.columns.values[0]
    checkout_group = result_frame[(result_frame["GROUP_ID"].str.startswith(group_like))]

    sumReal = sumCalced = routeDays = error = 0
    for i in range(2,real_frame.shape[0]):
        row = real_frame.loc[[i]]
        date = pd.to_datetime(row[group_like], format='%Y-%m-%d %H:%M:%S')
        if (date.dt.year == int(year)).all():
            sumReal += row[2].values[0]
            calced = checkout_group[(pd.to_datetime(checkout_group["DATE"], format='%d.%m.%Y').dt.strftime('%d.%m.%Y') == pd.Timestamp(date.values[0]).to_pydatetime().strftime('%d.%m.%Y'))]["DS"].mean()
            sumCalced += calced
            error += (row[2].values[0] - calced) / row[2].values[0]
            routeDays += 1
        elif (date.dt.year > int(year)).all(): break
    
    error = error / routeDays
    return (sumReal, sumCalced, routeDays, error)

def calcMeltInfo(folder, result_type):
    global realDataFile
    result_path = f"{folder}/{result_type}_group.dbf"
    result_frame = Dbf5(result_path).to_dataframe()
    group_list = result_frame["GROUP_ID"].unique().tolist()

    has_group = result_frame
    no_group = pd.DataFrame()
    minstart_group = ""
    minend_group = ""
    maxstart_group = ""
    maxend_group = ""
    minstart_date = dt.datetime.now()
    minend_date = dt.datetime.now()
    maxstart_date = dt.datetime.now()
    maxend_date = dt.datetime.now()
    for i in range(0, len(group_list)):
        if i < len(group_list) - 1: no_group, has_group = [x for _, x in \
            has_group.groupby(has_group["GROUP_ID"] == group_list[i])]

        filtered = has_group[(has_group["H"] > 0)]
        if len(filtered) == 0:
            has_group = no_group
            continue
        min_row = filtered.iloc[0]
        start = pd.to_datetime(min_row["DATE"], format='%d.%m.%Y')
        max_row = filtered.iloc[-1]
        end = pd.to_datetime(max_row["DATE"], format='%d.%m.%Y')
        minstart_date = start if minstart_group == "" or start < minstart_date else minstart_date
        minend_date = end if minend_group == "" or end < minend_date else minend_date
        maxstart_date = start if maxstart_group == "" or start > maxstart_date else maxstart_date
        maxend_date = end if maxend_group == "" or end > maxend_date else maxend_date

        minstart_group = group_list[i] if minstart_date == start else minstart_group
        minend_group = group_list[i] if minend_date == end else minend_group
        maxstart_group = group_list[i] if maxstart_date == start else maxstart_group
        maxend_group = group_list[i] if maxend_date == end else maxend_group

        has_group = no_group
    return minstart_date, minstart_group, maxstart_group, minend_group, maxend_group, maxend_date

def loadData(folder, result_type):
    global dFrame
    if not Path(folder + "/results_" + result_type).exists():
        raise Exception (f"В папке нет данных по вариации коэффициента (путь к папке: {folder})")
    
    year = os.path.basename(folder)
    for subFolder in os.listdir(folder + "/results_" + result_type):
        try:
            convRes = float(subFolder.replace(",", "."))
        except Exception: continue
        subFolderFull = folder + "/results_" + result_type + "/" + subFolder
        if os.path.isdir(subFolderFull):
            if not Path(subFolderFull + "/les_group.dbf").exists() and not Path(subFolderFull + "/pole_group.dbf").exists():
                raise Exception(
                f"Для одного из коэффициентов нет данных расчетов по лесу и/или полю (путь к папке: {subFolderFull})"
                )
            coef = float(os.path.basename(subFolder).replace(",", "."))
            result_typeMorph = "les" if result_type == "forest" else "pole"
            sumReal, sumCalced, routeDays, error = calcError(subFolderFull, year, \
                result_typeMorph)
            minstart_date, minstart_group, maxstart_group, minend_group, maxend_group, maxend_date = \
                calcMeltInfo(subFolderFull, result_typeMorph)
            row = {"year": [year], "coef": [coef], "coefStr": [str(coef).replace(".", ",")], "sumReal": [sumReal], "sumCalced": [sumCalced], \
                "routeDays": [routeDays], "error": [error], "errorAbs": [abs(error)], "minStartDate": minstart_date, \
                "minStartGroup": minstart_group, "maxStartGroup": maxstart_group, "minEndGroup": minend_group, \
                "maxEndGroup": maxend_group, "maxEndDate": maxend_date}
            rowFrame = pd.DataFrame(row)
            dFrame = pd.concat([dFrame, rowFrame], axis = 0, ignore_index=True)

def collectDataset():
    global dFrame
    oldFrame = dFrame

    try:
        if realDataFile == "": loadRealData()
        if realDataFile == "": raise Exception("Сначала выберите файл с данными снегомерных маршрутов")
        foldersInit = []
        folders = directory_selector("Выберите папки с данными расчетов", foldersInit)
        result_type = msg.askyesno(title="Выберите тип ландшафта", \
            message="Будут проводиться расчеты для леса?")
        result_type = "forest" if result_type else "field"
        print("Итоговый выбор: ", folders)
        dFrame = pd.DataFrame(columns=["year", "coefStr", "sumReal", "sumCalced", "routeDays", "error", "errorAbs",\
            "minStartDate", "minStartGroup", "maxStartGroup", "minEndGroup", "maxEndGroup", "maxEndDate", "coef"])

        for folder in folders:
            try: loadData(folder, result_type)
            except Exception as e:
                showinfo(title="Ошибка агрегации", message=str(e))
                continue
            finally:
                print(f"{folder} done")

        print(dFrame)
        if (dFrame.size == 0): raise Exception("Ничего импортировать не удалось")
        else:
            saveFile = fd.asksaveasfilename(title="Выберите, куда сохранить датасет", \
                filetypes=[('Файлы CSV', '*.csv')])
            dFrame.to_csv(saveFile)

    except Exception as e:
        showinfo(title="Ошибка агрегации", message=str(e))
        dFrame = oldFrame


app_folder = os.path.dirname(os.path.realpath(__file__))
app_folder = app_folder.replace("\\", "/")
realDataFile = ""
dFrame = pd.DataFrame()
os.system("chcp 65001 > nul")

form = tk.Tk() #создание окна
#параметры окна
form.title("Расчет снеготаяния")
form.minsize(400, 300)
form.resizable(False, False)

lbl = tk.Label(form)
lbl.grid(row = 0, column = 0)
lbl1 = tk.Label(form)
lbl1.grid(row = 1, column = 0)
lbl2 = tk.Label(form)
lbl2.grid(row = 2, column = 0)
lbl3 = tk.Label(form)
lbl3.grid(row = 3, column = 0)

loadReal = tk.Button(form, text="Выбрать файл с данными снегомерных маршрутов", width=100, \
    command=loadRealData)
loadReal.grid(row = 4, column = 0)

lbl4 = tk.Label(form)
lbl4.grid(row = 5, column = 0)

collectData = tk.Button(form, text="Собрать данные расчетов в один датасет", width=100,\
    command=collectDataset)
collectData.grid(row = 6, column = 0)
form.mainloop()