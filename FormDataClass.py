#Класс, содержащий в себе данные с формы
class FormData():
    def __init__(self, filename, startT, endT, heightTh, hCheck, eCheck, wEqField, wEqForest,
                 forestCoef, fieldCoef, sCoef, nCoef, wCoef, eCoef, pCoef):
        self.file = filename #имя входного файла
        self.sTime = startT #начало временного промежутка
        self.eTime = endT #конец временного промежутка
        self.hThresh = heightTh #порог высоты
        self.hCheck = hCheck #флаг учета высоты
        self.eCheck = eCheck #флаг учета экспозиции
        self.wEqField = wEqField #водный эквивалент снега для поля
        self.wEqForest = wEqForest #водный эквивалент снега для леса
        self.forestCoef = forestCoef #высотный коэффициент для леса
        self.fieldCoef = fieldCoef #высотный коэффициент для поля
        self.sCoef = sCoef #экспозиционный коэффициент для юга
        self.nCoef = nCoef #экспозиционный коэффициент для севера
        self.wCoef = wCoef #экспозиционный коэффициент для запада
        self.eCoef =  eCoef #экспозиционный коэффициент для востока
        self.pCoef = pCoef #экспозиционный коэффициент для равнины