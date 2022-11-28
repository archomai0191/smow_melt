from math import floor
import os, dbf, shutil, numpy, RecordClasses as rc, xlrd, datetime as dt, numpy as np
from tkinter.messagebox import showinfo

def parseDt(elem, isstart, message): #преобразование строки в datetime
    try:
        res = dt.datetime.strptime(elem.get(), "%d.%m.%Y") #попытка чтения в формате дд.мм.гггг
        return elem.get()
    except:
        try:
            res = dt.datetime.strptime(elem.get(), "%Y") #попытка чтения в формате гггг
            #установка даты 1 января, если читаем начало промежутка, иначе - 31 декабря
            if isstart: res = res.replace(month = 1, day = 1)
            else: res = res.replace(month = 12, day = 31)
            day = res.day
            month = res.month
            year = res.year
            resStr = ("0" if day < 10 else "") + str(day) + "." + ("0" if month < 10 else "") + str(month) + "." + str(year)
            return resStr
        except: #была введена не дата - сообщаем об этом
            showinfo(title = "Ошибка в параметрах", message = message)
            return None

def global_init(): #инициализация глобальных переменных
    global fl,exsp, AllCountDayL, AllCountDayP, AllResL, AllResP, station_height, StartR, StartRow, Spmax,\
        Slmax, DataMaxL, DataMaxP, RecCount, CountDayL, CountDayP, ResP, ResL, InputMas, PrMas, l,\
        PnLes, PnPole, station_height
    fl = exsp = AllCountDayL = AllCountDayP = StartR = RecCount = CountDayL = CountDayP = 0
    AllResL = [rc.Trec3() for i in range(0, 2001)]
    AllResP = [rc.Trec3() for i in range(0, 2001)]
    ResL = [rc.Trec3() for i in range(0, 1001)]
    ResP = [rc.Trec3() for i in range(0, 1001)]
    InputMas = [rc.Trec() for i in range(0, 1001)]
    PrMas = [rc.Trec2() for i in range (0, 301)]
    station_height = Spmax = Slmax = l = station_height = 0.0
    StartRow = 2
    PnLes = np.array([[0.03,0], [0.06,0.08], [0.09,0.45], [0.13,0.87], [0.15,0.92], [0.22,0.85], [0.3, 0.53],
        [0.38,0.18], [0.45,0.06], [0.6, 0.02], [0.66, 0]])
    PnPole = np.array([[0.02,0.05], [0.04,0.45], [0.06,0.87], [0.08,0.92], [0.1, 0.9], [0.15,0.74], [0.2, 0.47], 
        [0.25,0.21], [0.3, 0.13], [0.4, 0.05], [0.5, 0.01], [0.6, 0]])
    DataMaxP = DataMaxL = ""

def splitCode(code): #возвращение части кода
    findings = []
    for i in range (0, 7):
        pos = code.find("_")
        findings.append(code[0:pos] if pos != -1 else code)
        code = code[pos + 1:]
    return findings

def getL(bass_id): #поиск залесенности
    app_folder = os.path.dirname(os.path.realpath(__file__))
    app_folder = app_folder.replace("\\", "/")
    workbook = xlrd.open_workbook(app_folder + "/abd/bass_1000.xls")
    sheet = workbook.sheet_by_index(0)
    i = 1
    #поиск нужного бассейна
    while(i < sheet.nrows and sheet.cell_value(rowx = i, colx = 0)!= '' and 
        int(sheet.cell_value(rowx = i, colx = 0)) != bass_id): i += 1
    if i >= sheet.nrows: raise Exception("Бассейн не найден")
    st = sheet.cell_value(rowx = i, colx = 3)
    if st == '' or float(st) == -999: raise Exception("Нет данных по залесенности")
    return float(st)

def getFileName(station_id): #поиск файла метеостанции
    app_folder = os.path.dirname(os.path.realpath(__file__))
    app_folder = app_folder.replace("\\", "/")
    workbook = xlrd.open_workbook(app_folder + "/abd/meteostation_1000.xls")
    sheet = workbook.sheet_by_index(0)
    i = 1
    while(i < sheet.nrows and sheet.cell_value(rowx = i, colx = 0)!= '' and 
        int(sheet.cell_value(rowx = i, colx = 0)) != station_id): i += 1
    if i >= sheet.nrows: raise Exception("Файл метеостанции не найден")
    height = float(sheet.cell_value(rowx = i, colx = 3))
    return sheet.cell_value(rowx = i, colx = 2).strip(), height

def dateFromXls(sheet, row, col):
    year, month, day, hour, minute, nearest_second = xlrd.xldate_as_tuple\
        (sheet.cell_value(rowx = row, colx = col), 0)
    return ("0" if day < 10 else "") + str(day) + "." + ("0" if month < 10 else "") + str(month) + "." + str(year)

def importData(data, station_id1, station_id2, station_id3, bass_id, height): #скачивание информации из файла
    global station_height, StartR, AllCountDayL, AllCountDayP, Spmax, Slmax, DataMaxP, DataMaxL, \
        RecCount, CountDayL, CountDayP, ResP, ResL, l
    pr = 0.0
    flag = filename = ""
    row = col = sdvig = row3 = 0
    l = round(getL(bass_id), 2)
    #открывает файл с температурой
    app_folder = os.path.dirname(os.path.realpath(__file__))
    app_folder = app_folder.replace("\\", "/")
    temperature, station_height = getFileName(station_id2)
    temperature = "/" + temperature.replace("\\", "/")
    workbook = xlrd.open_workbook(app_folder + temperature)
    workbook2 = workbook3 = workbook
    sheet = workbook.sheet_by_index(0)
    sheet2 = sheet3 = sheet
    if (station_id2 != station_id1):
        #открывает файл с осадками
        osadki, pr = getFileName(station_id1)
        osadki = "/" + osadki.replace("\\", "/")
        workbook2 = xlrd.open_workbook(app_folder + osadki)
        sheet2 = workbook2.sheet_by_index(0)
    
    StartR = StartRow
    AllCountDayP = 0
    AllCountDayL = 0
    #поиск нужного года
    Date = dateFromXls(sheet, StartR, 1)
    if Date == '' : Date = dateFromXls(sheet, StartR, 3)
    while StartR < sheet.nrows and dt.datetime.strptime(Date, "%d.%m.%Y") < dt.datetime.strptime(data.sTime, "%d.%m.%Y") \
        and sheet.cell_value(rowx = StartR, colx = 1) != "" \
        and sheet.cell_value(rowx = StartR + 1, colx = 1) != "":
            while StartR < sheet.nrows and sheet.cell_value(rowx = StartR, colx = 2) != "": StartR += 1
            StartR += 1
            if StartR < sheet.nrows: Date = dateFromXls(sheet, StartR, 1)
    if StartR >= sheet.nrows: raise Exception("Данных для введенного промежутка нет")

    while StartR < sheet.nrows and sheet.cell_value(rowx = StartR, colx = 2) != "" and \
        dt.datetime.strptime(dateFromXls(sheet, StartR, 1), "%d.%m.%Y") \
        <= dt.datetime.strptime(data.eTime, "%d.%m.%Y"):
            row = StartR + 1
            flag = "1"
            sdvig = row if station_id2 == station_id1 else StartRow + 1
            #ищет нужную строку в файле с осадками
            while sheet2.cell_value(rowx = sdvig, colx = 2) != sheet.cell_value(rowx = row, colx = 2)\
                and sheet2.cell_value(rowx = sdvig, colx = 2) != ""\
                and sheet2.cell_value(rowx = sdvig + 1, colx = 2) != "":
                    while sheet2.cell_value(rowx = sdvig, colx = 2) != "" and \
                        sheet2.cell_value(rowx = sdvig, colx = 2) != sheet.cell_value(rowx = row, colx = 2):
                            sdvig += 1
                    if sheet2.cell_value(rowx = sdvig, colx = 2) == "": sdvig += 2
            sdvig -= row
            if station_id3 == station_id1 :
                sheet3 = sheet
                #row3 = row - 1
            if station_id3 == station_id2 :
                sheet3 = sheet2
                #row3 = row - 1 + sdvig

            if station_id3 != station_id2 and station_id3 != station_id2:
            #открывает файл с снегозапасом
                filename, pr = getFileName(station_id3)
                filename = app_folder + "/" + filename.replace("\\", "/")
                workbook3 = xlrd.open_workbook(filename)
                sheet3 = workbook3.sheet_by_index(0)
            
            row3 = StartRow
            # поиск нужного года
            Date = dateFromXls(sheet3, row3, 1)
            while dt.datetime.strptime(Date, "%d.%m.%Y") < dt.datetime.strptime(data.sTime, "%d.%m.%Y")\
                and str(sheet3.cell_value(rowx = row3, colx = 1)).strip() != ""\
                and str(sheet3.cell_value(rowx = row3 + 2, colx = 1)).strip() != "":
                    row3= row3+1
                    while str(sheet3.cell_value(rowx = row3, colx = 2)).strip() != "": row3 += 1
                    row3 = row3+1
                    Date = dateFromXls(sheet3, row3, 1)
            #считывание данных о дате и максимальном снегозапасе
            if str(sheet3.cell_value(rowx = row3, colx = 0)).strip() != "" and \
                sheet3.cell_value(rowx = row3, colx = 0) != -999:
                    Spmax = sheet3.cell_value(rowx = row3, colx = 0)
            else: raise Exception('Нет данных по снегозапасам в поле. Файл ' + filename)
            DataMaxP = dateFromXls(sheet3, row3, 1)

            if str(sheet3.cell_value(rowx = row3, colx = 2)).strip() != "" and \
                sheet3.cell_value(rowx = row3, colx = 2) != -999:
                    Slmax = sheet3.cell_value(rowx = row3, colx = 2)
            else: raise Exception('Нет данных по снегозапасам в лесу. Файл ' + filename)
            DataMaxL = dateFromXls(sheet3, row3, 3)

            #считывание данных из файлов
            while row < sheet.nrows and flag != "":
                if str(sheet2.cell_value(row + sdvig, 1)).strip() !='' :
                    InputMas[row-StartR-1].temp = sheet2.cell_value(row + sdvig, 1)
                else: InputMas[row-StartR-1].temp = -999

                if str(sheet.cell_value(row, 0)).strip() != "": 
                    InputMas[row-StartR-1].osadki = sheet.cell_value(row, 0)
                else: InputMas[row-StartR-1].osadki = -999

                InputMas[row-StartR-1].time = dateFromXls(sheet, row, 2)
                row += 1
                if row < sheet.nrows: flag = str(sheet.cell_value(row, 2)).strip()
            RecCount = row - StartR - 2
            StartR = row + 1
            #выполнение расчета
            calc(height, data)

            #запись результатов в массив за все года (поле)
            for i in range (0, CountDayP):
                AllCountDayP += 1
                AllResP[AllCountDayP].time = ResP[i].time
                AllResP[AllCountDayP].Xmm = ResP[i].Xmm
                AllResP[AllCountDayP].Smax = ResP[i].Smax
                AllResP[AllCountDayP].Sproc = ResP[i].Sproc
                AllResP[AllCountDayP].dS = ResP[i].dS

            #запись результатов в массив за все года (лес)
            for i in range (0, CountDayL):
                AllCountDayL += 1
                AllResL[AllCountDayL].time = ResL[i].time
                AllResL[AllCountDayL].Xmm = ResL[i].Xmm
                AllResL[AllCountDayL].Smax = ResL[i].Smax
                AllResL[AllCountDayL].Sproc = ResL[i].Sproc
                AllResL[AllCountDayL].dS = ResL[i].dS

def exportGroup(code, les, pole): #запись результата в файлы
    if fl == 1: #лес
        for i in range(1, AllCountDayL):
            AllResL[i].Sproc = round(AllResL[i].Sproc, 4);
            AllResL[i].Xmm = round(AllResL[i].Xmm, 4);
            AllResL[i].dS = round(AllResL[i].dS, 4);
            AllResL[i].Smax = round(AllResL[i].Smax, 4);
            rec = (code, AllResL[i].time, AllResL[i].Xmm, AllResL[i].Smax, AllResL[i].Sproc, AllResL[i].dS, 
                    code.strip() + "_" + AllResL[i].time)
            les.append(rec)
    
    if fl == 0: #поле
        for i in range(1, AllCountDayP + 1):
            AllResP[i].Sproc = round(AllResP[i].Sproc, 4);
            AllResP[i].Xmm = round(AllResP[i].Xmm, 4);
            AllResP[i].dS = round(AllResP[i].dS, 4);
            AllResP[i].Smax = round(AllResP[i].Smax, 4);
            rec = (code, AllResP[i].time, AllResP[i].Xmm, AllResP[i].Smax, AllResP[i].Sproc, AllResP[i].dS, 
                    code.strip() + "_" + AllResP[i].time)
            pole.append(rec)

def run(data): #инициализация расчетов
    global_init()
    global fl, exsp
    station_id1 = station_id2 = station_id3 = bass_id = count = 0
    code = OldCode = ""
    height = 0.0
    folder, name = os.path.split(data.file)
    app_folder = os.path.dirname(os.path.realpath(__file__))
    app_folder = app_folder.replace("\\", "/")
    path_les = app_folder + "/dbf/LesPole/les_group.dbf"
    path_pole = app_folder + "/dbf/LesPole/pole_group.dbf"
    shutil.copyfile(path_les, folder + "/les_group.dbf")
    shutil.copyfile(path_pole, folder + "/pole_group.dbf")
    points_dbf = dbf.Table(data.file)
    les_dbf = dbf.Table(folder + "/les_group.dbf")
    pole_dbf = dbf.Table(folder + "/pole_group.dbf")
    points_dbf = points_dbf.open(mode = dbf.READ_WRITE)
    pole_dbf = pole_dbf.open(mode = dbf.READ_WRITE)
    les_dbf = les_dbf.open(mode = dbf.READ_WRITE)

    try:
        print ("Работаем с базой данных с точками...")
        print("started at", dt.datetime.now())
        records = numpy.array([r.merge.strip() for r in points_dbf])
        records = numpy.array(sorted(set(records)))
        print("ended at", dt.datetime.now())

        print("Проводим расчеты...")
        for record in records:
            print("progress ", count * 100 / len(records), "%")
            code = record #запоминание кодовой строки
            params = splitCode(code)
            bass_id = int(params[0])#запоминание номера бассейна
            station_id1 = int(params[2])#запоминание номера станции с данными по температуре
            station_id2 = int(params[3])#запоминание номера станции с данными по осадкам
            station_id3 = int(params[4])#запоминание номера станции с данными по снегозапасу
            height = float(params[5])#запоминание высоты точки
            fl = int(params[1])#запоминание флага лес-поле
            exsp = int(params[6])#запоминание экспозиции склона

            if station_id1 == 6 and station_id2 == 6 and station_id3 == 6: height+= 1
            if code != OldCode:
                importData(data, station_id1, station_id2, station_id3, bass_id, height) #считывание данных и выполнение расчета
                OldCode = code
                exportGroup(code, les_dbf, pole_dbf)
            count += 1
        print("ended at", dt.datetime.now())
    except: raise
    finally:
        points_dbf.close()
        pole_dbf.close()
        les_dbf.close()

def calc(height, data): #выполнение расчета
    global CountDay, CountDayP, CountDayL, station_height, exsp, RecCount, fl, Spmax, Slmax, DataMaxP, DataMaxL, l
    i = CountDay = CountDayP = CountDayL = 0
    dSl = dSlN = Sl = Slmaxr = dSp = dSpN = Hl = LamL = alfL = SumT = Tp_ = Tp = LamP = Spmaxr = Hp = Sp = SumX = alfP = 0.0
    OldDay = InputMas[i].time
    FlagTp = False
    nOs = nT = ifest = 0

    while i <= RecCount: #записываем данные в промежуточный массив
        nOs = 0
        nT = 0
        SumX = 0.0
        SumT = 0.0

        if InputMas[i].osadki != -999:
            nOs += 1
            SumX += InputMas[i].osadki

        if InputMas[i].temp != -999:
            nT += 1
            SumT += InputMas[i].temp

        nOs = nOs if nOs != 0 else 1
        nT = nT if nT != 0 else 1
        PrMas[CountDay].time = OldDay
        PrMas[CountDay].XmmW = SumX * (4.9204 * SumT + 34.601) / 100.0
        if PrMas[CountDay].XmmW < 0: PrMas[CountDay].XmmW = 0
        if PrMas[CountDay].XmmW > SumX: PrMas[CountDay].XmmW = SumX
        PrMas[CountDay].XmmT = (SumX) - PrMas[CountDay].XmmW
        PrMas[CountDay].temp = SumT
        CountDay += 1
        i += 1
        OldDay = InputMas[i].time

    if fl == 0 and Spmax > 0: #счет для поля
        CountDay -= 1
        LamP = 1.25
        Spmaxr = salSpMax(Spmax, height, data)
        Sp = Spmaxr
        alfP = 1.5
        Hp = 0
        FlagTp = True
        Tp = 0
        Tp_ = 0
        CountDayP = 0
        Tp = 0 #сумма положительных температур
        Tp_ = 0 #сумма отрицательных температур
        ifest = 0
        
        while PrMas[ifest].time != DataMaxP and ifest <= CountDay: #поиск даты максимального снегозапаса
            writeToResP((1-l) * Spmaxr, (1-l) * Spmaxr, 100, 0, PrMas[ifest].time, CountDayP)
            CountDayP += 1
            ifest += 1

        for i in range (ifest, CountDay + 1):
            if PrMas[i].temp > 0.0:
                Tp += PrMas[i].temp
                Tp_ = 0
            if PrMas[i].temp < 0 and PrMas[i-1].temp < 0: Tp_ += PrMas[i].temp
            elif (PrMas[i].temp < 0): Tp_ = PrMas[i].temp
            if (Tp+Tp_) < 0: Tp = 0 #обнуление суммы положительных темп., если она меньше суммы отриц. темп.

            Sp += PrMas[i].XmmT * (1 - l)
            if FlagTp: dSp = Sp *(1 - l)
            if Tp >= 0.2 * Spmaxr / data.wEqField: #проверка, началось ли таяние
                if FlagTp:
                    dSpN = dSp
                    FlagTp = False
                else: LamP = 0.0024 * dSp / dSpN * 100 + 1.0008 #нахождение коэф. лямбда

                alfP = alpha(Tp, Spmaxr, l, True) #нахождение коэф. альфа
                #нахождение слоя стаявшего снега
                Hp = LamP * alfP * PrMas[i].temp + PrMas[i].XmmW * (1-l)
                Hp = salH(Hp, data)
                if Hp < 0: Hp = 0
                if dSp > 0 and Tp >= 0.2 * Spmaxr / data.wEqField and alfP != 0:
                    #запись данных в массив результатов
                    ResP[CountDayP].time  = PrMas[i].time
                    if dSp-Hp <0:ResP[CountDayP].Xmm  = dSp
                    else: ResP[CountDayP].Xmm  = Hp
                    ResP[CountDayP].Smax = (1-l) * Spmaxr
                    ResP[CountDayP].dS  = dSp
                    ResP[CountDayP].Sproc  = dSp / dSpN * 100
                    CountDayP += 1
                else:
                    #запись данных после окончания снеготаяния
                    if dSp < 0:
                        writeToResP((1 - l)*Spmaxr, 0, 0, 0, PrMas[i].time, CountDayP)
                        CountDayP  = CountDayP+1
                if Hp> PrMas[i].XmmW * (1-l): Hp  = Hp-PrMas[i].XmmT*(1-l)
                dSp += round(-Hp+PrMas[i].XmmT*(1-l), 14)

            else:
                if not FlagTp: writeToResP((1-l)*Spmaxr, dSp, dSp/dSpN*100, 0, PrMas[i].time, CountDayP)
                else: writeToResP((1-l)*Spmaxr, (1-l)*Spmaxr, 100, 0, PrMas[i].time, CountDayP)
                CountDayP += 1

    if fl == 1 and Slmax > 0:#счет для леса
        Hp  = 0
        Slmaxr  = salSlMax(Slmax, height, data)
        Sl  = Slmaxr
        alfL  = 1.23
        LamL  = 1.43
        FlagTp  = True
        CountDayL  = 0
        Tp  = 0
        Tp_  = 0
        ifest  = 0

        while PrMas[ifest].time != DataMaxL and ifest <= CountDay: 
            writeToResL(l*Slmaxr, l*Slmaxr, 100, 0, PrMas[ifest].time, CountDayL)
            CountDayL += 1
            ifest += 1

        for i in range (ifest, CountDay + 1):
            if PrMas[i].temp> 0:
                Tp  = Tp+PrMas[i].temp
                Tp_  = 0
            if PrMas[i].temp < 0 and PrMas[i-1].temp<0: Tp_  = Tp_+PrMas[i].temp
            elif PrMas[i].temp < 0: Tp_  = PrMas[i].temp
            if (Tp+Tp_) < 0: Tp  = 0
            Sl  = Sl+PrMas[i].XmmT*l
            if FlagTp: dSl  = Sl*l
            if Tp >=(0.3*Slmaxr/data.wEqForest):
                if FlagTp:
                    dSlN  = dSl
                    FlagTp  = False
                else: LamL  = 0.0044*dSl/dSlN*100+1.0064

                alfL  = alpha(Tp, Slmaxr, l, False)
                Hl =  LamL*alfL*PrMas[i].temp+PrMas[i].XmmW*l
                Hl  = salH(Hl, data)
                if Hl<0: Hl  = 0
                if (dSl>0) and (Tp >=(0.3*Slmaxr/data.wEqForest)) and (alfL!=0):
                    ResL[CountDayL].time  = PrMas[i].time
                    if (dSl-Hl)<0: ResL[CountDayL].Xmm  = dSl
                    else: ResL[CountDayL].Xmm  = Hl
                    ResL[CountDayL].Smax  = l*Slmaxr
                    ResL[CountDayL].dS  = dSl
                    ResL[CountDayL].Sproc  = dSl/dSlN*100
                    CountDayL  = CountDayL+1
                if dSl<0:
                    writeToResL(l*Slmaxr, 0, 0, 0, PrMas[i].time, CountDayL)
                    CountDayL  = CountDayL+1
                if Hl>(PrMas[i].XmmW*l): Hl  = Hl-PrMas[i].XmmW*l  
                dSl  = dSl-Hl+PrMas[i].XmmT*l
            else:
                if not(FlagTp): writeToResL(l*Slmaxr, dSl, dSl/dSlN*100, 0, PrMas[i].time, CountDayL)
                else: writeToResL(l*Slmaxr, l*Slmaxr, 100, 0, PrMas[i].time, CountDayL)
                CountDayL  = CountDayL+1

def salSlMax(slMax, height, data): #пересчет максимального снегозапаса с учетом поправочных коэф-тов по высоте для поля
    return data.forestCoef * (height - station_height) + slMax if data.hThresh <= height and data.hCheck else slMax

def salSpMax(spMax, height, data): #пересчет максимального снегозапаса с учетом попроавочных коэф-тов по высоте для леса
    return data.fieldCoef * (height - station_height) + spMax if data.hThresh <= height and data.hCheck else spMax

def writeToResL(Smax, dS, Sproc, Xmm, time, CountDayl): #запись в массив ResL
    ResL[CountDayl].Smax = Smax
    ResL[CountDayl].dS = dS
    ResL[CountDayl].Sproc = Sproc
    ResL[CountDayl].Xmm = Xmm
    ResL[CountDayl].time = time

def writeToResP(Smax, dS, Sproc, Xmm, time, CountDayP): #запись в массив ResP
    ResP[CountDayP].Smax = Smax
    ResP[CountDayP].dS = dS
    ResP[CountDayP].Sproc = Sproc
    ResP[CountDayP].Xmm = Xmm
    ResP[CountDayP].time = time

def alpha (sumT, sMax, L, flagPole): #вычисление коэффициента альфа
    i = 0
    k = P = 0.0
    if flagPole:
        k = sumT / sMax
        while i < 12 and k >= PnPole[i,0]: i += 1
        if i >= 12: return P
        P = PnPole[i-1,1]+(PnPole[i,1]-PnPole[i-1,1])*(k-PnPole[i-1,0])/(PnPole[i,0]-PnPole[i-1,0])
        return 6.25 * (1 - L) * P
    else:
        k = 0.6 * sumT / sMax
        while i < 11 and k >= PnLes[i, 0]: i += 1
        if i >= 11: return P
        P = PnLes[i-1,1]+(PnLes[i,1]-PnLes[i-1,1])*(k-PnLes[i-1,0])/(PnLes[i,0]-PnLes[i-1,0])
        return 2.86 * L * P

def salH (h, data): #пересчет слоя стаявшего снега с учетом поправочных коэф-тов по экспозиции
    if data.eCheck:
        if exsp == 1: h *= data.nCoef
        elif exsp == 2: h *= data.eCoef
        elif exsp == 3: h *= data.sCoef
        elif exsp == 4: h *= data.wCoef
        elif exsp == -1: h *= data.pCoef
    return h