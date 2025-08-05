from querydata import QueryData
from buildtime import buildTime

import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.queryData = QueryData()
        self.createWidgets()
        self.onUpdateCalc()

    def createWidgets(self):
        self.userInputBoxUi().grid(row=0, column=0, sticky=tk.NSEW)
        self.goGaugeBoxUi().grid(row=0, column=1, sticky=tk.NSEW)
        self.noGoGaugeBoxUi().grid(row=0, column=2, sticky=tk.NSEW)
        self.goGoSettingPlugGaugeBoxUi().grid(row=1, column=0, sticky=tk.NSEW)
        self.goWearSettingPlugGaugeBoxUi().grid(row=1, column=1, sticky=tk.NSEW)
        self.noGoGoSettingPlugGaugeBoxUi().grid(row=1, column=2, sticky=tk.NSEW)
        self.infoBoxUi().grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)
        tk.Label(self, text=f'{buildTime}').grid(row=3, column=0, columnspan=3, sticky=tk.W)
        tk.Label(self, text='IYATT-yx iyatt@iyatt.com').grid(row=4, column=0, columnspan=3, sticky=tk.W)
        tk.Label(self, text='计算依据《GB/T 1957-2006 光滑极限量规 技术条件》').grid(row=5, column=0, columnspan=3, sticky=tk.W)


    def infoBoxUi(self):
        """
        信息
        """
        infoBox = tk.LabelFrame(self, text='信息', padx=10, pady=10)

        self.infoVar = tk.StringVar()
        tk.Entry(infoBox, textvariable=self.infoVar, state='readonly').pack(fill=tk.BOTH)

        return infoBox

    def userInputBoxUi(self):
        """
        用户输入框 - 设计参数
        """
        userInputBox = tk.LabelFrame(self, text='设计参数', padx=10, pady=10)
        
        self.feature = tk.StringVar(value='shaft')
        tk.Radiobutton(userInputBox, text='轴尺寸', variable=self.feature, value='shaft', command=self.onUpdateCalc).grid(row=0, column=0, sticky=tk.NSEW)
        tk.Radiobutton(userInputBox, text='孔尺寸', variable=self.feature, value='hole', command=self.onUpdateCalc).grid(row=0, column=1, sticky=tk.NSEW)

        tk.Label(userInputBox, text='名义尺寸：').grid(row=1, column=0, sticky=tk.W)
        tk.Label(userInputBox, text='上偏差：').grid(row=2, column=0, sticky=tk.W)
        tk.Label(userInputBox, text='下偏差：').grid(row=3, column=0, sticky=tk.W)
        tk.Label(userInputBox, text='公差等级：').grid(row=4, column=0, sticky=tk.W)

        self.norminalSizeVar = tk.StringVar(value="20")
        self.upperDeviationVar = tk.StringVar(value="0.01")
        self.lowerDeviationVar = tk.StringVar(value="-0.01")
        self.internationalToleranceGradeVar = tk.StringVar()
        self.norminalSizeVar.trace_add('write', self.onUpdateCalc)
        self.upperDeviationVar.trace_add('write', self.onUpdateCalc)
        self.lowerDeviationVar.trace_add('write', self.onUpdateCalc)

        tk.Entry(userInputBox, textvariable=self.norminalSizeVar).grid(row=1, column=1, sticky=tk.NSEW)
        tk.Entry(userInputBox, textvariable=self.upperDeviationVar).grid(row=2, column=1, sticky=tk.NSEW)
        tk.Entry(userInputBox, textvariable=self.lowerDeviationVar).grid(row=3, column=1, sticky=tk.NSEW)
        tk.Entry(userInputBox, textvariable=self.internationalToleranceGradeVar, state='readonly').grid(row=4, column=1, sticky=tk.NSEW)

        return userInputBox
    
    def validateNumber(self, number: tk.StringVar) -> float | None:
        """
        验证输入的 tkinter 字符串值是否为数字

        Args:
            number (tk.StringVar): tkinter 字符串值

        Returns:
            float | None | bool: None 则带表输入空，可不作处理； False 则表示输入值不是数字； float 则转为浮点数的结果
        """
        number = number.get()
        if number in ('', '.', '-', '-.', '0.', '-0.'):
            return None
        try:
            return float(number)
        except ValueError:
            return (None, None)
    
    def onUpdateCalc(self, *args):
        """
        更新计算
        """
        # 检查用户输入值
        ####################
        errorString = None

        norminalSize = self.validateNumber(self.norminalSizeVar)
        if norminalSize is None:
            errorString = '名义尺寸：未输完整'
        elif norminalSize == (None, None):
            errorString = '名义尺寸：只能输入数字'
        else:
            self.infoVar.set('')
        
        upperDeviation = self.validateNumber(self.upperDeviationVar)
        if upperDeviation is None:
            errorString = '上偏差：未输完整'
        elif upperDeviation == (None, None):
            errorString = '上偏差：只能输入数字'
        else:
            self.infoVar.set('')
        
        lowerDeviation = self.validateNumber(self.lowerDeviationVar)
        if lowerDeviation is None:
            errorString = '下偏差：未输完整'
        elif lowerDeviation == (None, None):
            errorString = '下偏差：只能输入数字'
        else:
            self.infoVar.set('')

        if errorString is not None:
            self.infoVar.set(errorString)
            return

        # 准备计算数据
        ###############
        # 计算轴/孔上极限
        upperLimit = norminalSize + upperDeviation
        # 计算轴/孔下极限
        lowerLimit = norminalSize + lowerDeviation
        # 计算公差
        tolerance = upperDeviation - lowerDeviation
        # 查询轴孔公差等级、量规公差、量规通端公差带中值与孔轴最大实体尺寸的差值
        itT1Z1 = self.queryData.queryItT1Z1(norminalSize, tolerance)
        if itT1Z1 is None:
            self.infoVar.set('轴孔公差等级过低或过高，仅适用于IT6-IT16公差等级尺寸')
            self.goNoGoGaugeClear()
            self.settingPlugGaugeClear()
            return
        it, t1, z1 = itT1Z1
        
        # 显示公差等级
        self.internationalToleranceGradeVar.set(f'IT{it}')

        # 轴孔类型
        feature = self.feature.get()
        # 显示量规尺寸、粗糙度
        match feature:
            case 'shaft':
                """轴"""
                # 计算通端
                goNorminalSize = upperLimit - z1 - t1 / 2
                goUpperDeviation = t1
                goLowerDeviation = 0
                goWearLimit = upperLimit
                goRa = self.queryData.queryRa(feature, goNorminalSize, it)
                # 显示通端
                self.goGaugeNorminalSizeVar.set(goNorminalSize)
                self.goGaugeUpperDeviationVar.set(goUpperDeviation)
                self.goGaugeLowerDeviationVar.set(goLowerDeviation)
                self.goGaugeWearLimitVar.set(goWearLimit)
                self.goGaugeRaVar.set(goRa)

                # 计算止端
                noGoNorminalSize = lowerLimit
                noGoUpperDeviation = t1
                noGoLowerDeviation = 0
                noGoRa = self.queryData.queryRa(feature, noGoNorminalSize, it)
                # 显示止端
                self.noGoGaugeNorminalSizeVar.set(noGoNorminalSize)
                self.noGoGaugeUpperDeviationVar.set(noGoUpperDeviation)
                self.noGoGaugeLowerDeviationVar.set(noGoLowerDeviation)
                self.noGoGaugeRaVar.set(noGoRa)

                # 计算 校通-损
                goWearNorminalSize = upperLimit
                goWearUpperDeviation = 0
                goWearLowerDeviation = -t1 / 2
                goWearRa = self.queryData.querySettingPlugGaugeRa(goWearNorminalSize, it)
                # 显示 校通-损
                self.goWearSettingPlugGaugeNorminalSizeVar.set(goWearNorminalSize)
                self.goWearSettingPlugGaugeUpperDeviationVar.set(goWearUpperDeviation)
                self.goWearSettingPlugGaugeLowerDeviationVar.set(goWearLowerDeviation)
                self.goWearSettingPlugGaugeRaVar.set(goWearRa)

                # 计算 校通-通
                goGoNorminalSize = upperLimit - z1
                goGoUpperDeviation = 0
                goGoLowerDeviation = -t1 / 2
                goGoRa = self.queryData.querySettingPlugGaugeRa(goGoNorminalSize, it)
                # 显示 校通-通
                self.goGoSettingPlugGaugeNorminalSizeVar.set(goGoNorminalSize)
                self.goGoSettingPlugGaugeUpperDeviationVar.set(goGoUpperDeviation)
                self.goGoSettingPlugGaugeLowerDeviationVar.set(goGoLowerDeviation)
                self.goGoSettingPlugGaugeRaVar.set(goGoRa)

                # 计算 校止-通
                noGoGoLowerDeviation = -t1 / 2
                noGoGoUpperDeviation = 0
                noGoGoNorminalSize = lowerLimit - noGoGoLowerDeviation
                noGoGoRa = self.queryData.querySettingPlugGaugeRa(noGoGoNorminalSize, it)
                # 显示 校止-通
                self.noGoGoSettingPlugGaugeNorminalSizeVar.set(noGoGoNorminalSize)
                self.noGoGoSettingPlugGaugeUpperDeviationVar.set(noGoGoUpperDeviation)
                self.noGoGoSettingPlugGaugeLowerDeviationVar.set(noGoGoLowerDeviation)
                self.noGoGoSettingPlugGaugeRaVar.set(noGoGoRa)

            case 'hole':
                """孔"""
                # 计算通端
                goNorminalSize = lowerLimit + z1 + t1 / 2
                goUpperDeviation = 0
                goLowerDeviation = -t1
                goWearLimit = lowerLimit
                goRa = self.queryData.queryRa(feature, goNorminalSize, it)
                # 显示通端
                self.goGaugeNorminalSizeVar.set(goNorminalSize)
                self.goGaugeUpperDeviationVar.set(goUpperDeviation)
                self.goGaugeLowerDeviationVar.set(goLowerDeviation)
                self.goGaugeWearLimitVar.set(goWearLimit)
                self.goGaugeRaVar.set(goRa)

                # 计算止端
                noGoNorminalSize = upperLimit
                noGoUpperDeviation = 0
                noGoLowerDeviation = -t1
                noGoRa = self.queryData.queryRa(feature, noGoNorminalSize, it)
                # 显示止端
                self.noGoGaugeNorminalSizeVar.set(noGoNorminalSize)
                self.noGoGaugeUpperDeviationVar.set(noGoUpperDeviation)
                self.noGoGaugeLowerDeviationVar.set(noGoLowerDeviation)
                self.noGoGaugeRaVar.set(noGoRa)

                # 清空校规
                self.settingPlugGaugeClear()

    def goNoGoGaugeClear(self):
        self.internationalToleranceGradeVar.set(0)
        self.goGaugeNorminalSizeVar.set(0)
        self.goGaugeUpperDeviationVar.set(0)
        self.goGaugeLowerDeviationVar.set(0)
        self.goGaugeWearLimitVar.set(0)
        self.goGaugeRaVar.set(0)
        self.noGoGaugeRaVar.set(0)
        self.noGoGaugeNorminalSizeVar.set(0)
        self.noGoGaugeUpperDeviationVar.set(0)
        self.noGoGaugeLowerDeviationVar.set(0)

    def settingPlugGaugeClear(self):
        self.goGoSettingPlugGaugeNorminalSizeVar.set(0)
        self.goGoSettingPlugGaugeUpperDeviationVar.set(0)
        self.goGoSettingPlugGaugeLowerDeviationVar.set(0)
        self.goWearSettingPlugGaugeNorminalSizeVar.set(0)
        self.goWearSettingPlugGaugeUpperDeviationVar.set(0)
        self.goWearSettingPlugGaugeLowerDeviationVar.set(0)
        self.noGoGoSettingPlugGaugeNorminalSizeVar.set(0)
        self.noGoGoSettingPlugGaugeUpperDeviationVar.set(0)
        self.noGoGoSettingPlugGaugeLowerDeviationVar.set(0)
        self.goGoSettingPlugGaugeRaVar.set(0)
        self.goWearSettingPlugGaugeRaVar.set(0)
        self.noGoGoSettingPlugGaugeRaVar.set(0)
    
    def goGaugeBoxUi(self):
        """
        通规尺寸
        """
        goGaugeBox = tk.LabelFrame(self, text='T 通规尺寸', padx=10, pady=10)

        tk.Label(goGaugeBox, text='名义尺寸：').grid(row=0, column=0, sticky=tk.W)
        tk.Label(goGaugeBox, text='上偏差：').grid(row=1, column=0, sticky=tk.W)
        tk.Label(goGaugeBox, text='下偏差：').grid(row=2, column=0, sticky=tk.W)
        tk.Label(goGaugeBox, text='磨损极限：').grid(row=3, column=0, sticky=tk.W)
        tk.Label(goGaugeBox, text='粗糙度Ra').grid(row=4, column=0, sticky=tk.W)

        self.goGaugeNorminalSizeVar = tk.DoubleVar()
        self.goGaugeUpperDeviationVar = tk.DoubleVar()
        self.goGaugeLowerDeviationVar = tk.DoubleVar()
        self.goGaugeWearLimitVar = tk.DoubleVar()
        self.goGaugeRaVar = tk.DoubleVar()

        tk.Entry(goGaugeBox, textvariable=self.goGaugeNorminalSizeVar, state='readonly').grid(row=0, column=1, sticky=tk.NSEW)
        tk.Entry(goGaugeBox, textvariable=self.goGaugeUpperDeviationVar, state='readonly').grid(row=1, column=1, sticky=tk.NSEW)
        tk.Entry(goGaugeBox, textvariable=self.goGaugeLowerDeviationVar, state='readonly').grid(row=2, column=1, sticky=tk.NSEW)
        tk.Entry(goGaugeBox, textvariable=self.goGaugeWearLimitVar, state='readonly').grid(row=3, column=1, sticky=tk.NSEW)
        tk.Entry(goGaugeBox, textvariable=self.goGaugeRaVar, state='readonly').grid(row=4, column=1, sticky=tk.NSEW)

        return goGaugeBox

    def noGoGaugeBoxUi(self):
        """
        止规尺寸
        """
        noGoGaugeBox = tk.LabelFrame(self, text='Z 止规尺寸', padx=10, pady=10)

        tk.Label(noGoGaugeBox, text='名义尺寸：').grid(row=0, column=0, sticky=tk.W)
        tk.Label(noGoGaugeBox, text='上偏差：').grid(row=1, column=0, sticky=tk.W)
        tk.Label(noGoGaugeBox, text='下偏差：').grid(row=2, column=0, sticky=tk.W)
        tk.Label(noGoGaugeBox, text='粗糙度Ra').grid(row=3, column=0, sticky=tk.W)

        self.noGoGaugeNorminalSizeVar = tk.DoubleVar()
        self.noGoGaugeUpperDeviationVar = tk.DoubleVar()
        self.noGoGaugeLowerDeviationVar = tk.DoubleVar()
        self.noGoGaugeRaVar = tk.DoubleVar()

        tk.Entry(noGoGaugeBox, textvariable=self.noGoGaugeNorminalSizeVar, state='readonly').grid(row=0, column=1, sticky=tk.NSEW)
        tk.Entry(noGoGaugeBox, textvariable=self.noGoGaugeUpperDeviationVar, state='readonly').grid(row=1, column=1, sticky=tk.NSEW)
        tk.Entry(noGoGaugeBox, textvariable=self.noGoGaugeLowerDeviationVar, state='readonly').grid(row=2, column=1, sticky=tk.NSEW)
        tk.Entry(noGoGaugeBox, textvariable=self.noGoGaugeRaVar, state='readonly').grid(row=3, column=1, sticky=tk.NSEW)

        return noGoGaugeBox
    
    def goGoSettingPlugGaugeBoxUi(self):
        """
        “校通-通” 塞规
        """
        goGoSettingPlugGaugeBox = tk.LabelFrame(self, text='TT “校通-通” 塞规尺寸', padx=10, pady=10)

        tk.Label(goGoSettingPlugGaugeBox, text='名义尺寸').grid(row=0, column=0, sticky=tk.W)
        tk.Label(goGoSettingPlugGaugeBox, text='上偏差').grid(row=1, column=0, sticky=tk.W)
        tk.Label(goGoSettingPlugGaugeBox, text='下偏差').grid(row=2, column=0, sticky=tk.W)
        tk.Label(goGoSettingPlugGaugeBox, text='粗糙度Ra').grid(row=3, column=0, sticky=tk.W)

        self.goGoSettingPlugGaugeNorminalSizeVar = tk.DoubleVar()
        self.goGoSettingPlugGaugeUpperDeviationVar = tk.DoubleVar()
        self.goGoSettingPlugGaugeLowerDeviationVar = tk.DoubleVar()
        self.goGoSettingPlugGaugeRaVar = tk.DoubleVar()

        tk.Entry(goGoSettingPlugGaugeBox, textvariable=self.goGoSettingPlugGaugeNorminalSizeVar, state='readonly').grid(row=0, column=1, sticky=tk.NSEW)
        tk.Entry(goGoSettingPlugGaugeBox, textvariable=self.goGoSettingPlugGaugeUpperDeviationVar, state='readonly').grid(row=1, column=1, sticky=tk.NSEW)
        tk.Entry(goGoSettingPlugGaugeBox, textvariable=self.goGoSettingPlugGaugeLowerDeviationVar, state='readonly').grid(row=2, column=1, sticky=tk.NSEW)
        tk.Entry(goGoSettingPlugGaugeBox, textvariable=self.goGoSettingPlugGaugeRaVar, state='readonly').grid(row=3, column=1, sticky=tk.NSEW)

        return goGoSettingPlugGaugeBox
    
    def goWearSettingPlugGaugeBoxUi(self):
        """
        “校通-损” 塞规
        """
        goWearSettingPlugGaugeBox = tk.LabelFrame(self, text='TS “校通-损” 塞规尺寸', padx=10, pady=10)

        tk.Label(goWearSettingPlugGaugeBox, text='名义尺寸').grid(row=0, column=0, sticky=tk.W)
        tk.Label(goWearSettingPlugGaugeBox, text='上偏差').grid(row=1, column=0, sticky=tk.W)
        tk.Label(goWearSettingPlugGaugeBox, text='下偏差').grid(row=2, column=0, sticky=tk.W)
        tk.Label(goWearSettingPlugGaugeBox, text='粗糙度Ra').grid(row=3, column=0, sticky=tk.W)

        self.goWearSettingPlugGaugeNorminalSizeVar = tk.DoubleVar()
        self.goWearSettingPlugGaugeUpperDeviationVar = tk.DoubleVar()
        self.goWearSettingPlugGaugeLowerDeviationVar = tk.DoubleVar()
        self.goWearSettingPlugGaugeRaVar = tk.DoubleVar()

        tk.Entry(goWearSettingPlugGaugeBox, textvariable=self.goWearSettingPlugGaugeNorminalSizeVar, state='readonly').grid(row=0, column=1, sticky=tk.NSEW)
        tk.Entry(goWearSettingPlugGaugeBox, textvariable=self.goWearSettingPlugGaugeUpperDeviationVar, state='readonly').grid(row=1, column=1, sticky=tk.NSEW)
        tk.Entry(goWearSettingPlugGaugeBox, textvariable=self.goWearSettingPlugGaugeLowerDeviationVar, state='readonly').grid(row=2, column=1, sticky=tk.NSEW)
        tk.Entry(goWearSettingPlugGaugeBox, textvariable=self.goWearSettingPlugGaugeRaVar, state='readonly').grid(row=3, column=1, sticky=tk.NSEW)

        return goWearSettingPlugGaugeBox
    
    def noGoGoSettingPlugGaugeBoxUi(self):
        """
        “校止-通” 塞规
        """
        noGoGoSettingPlugGaugeBox = tk.LabelFrame(self, text='ZT “校止-通” 塞规尺寸', padx=10, pady=10)

        tk.Label(noGoGoSettingPlugGaugeBox, text='名义尺寸').grid(row=0, column=0, sticky=tk.W)
        tk.Label(noGoGoSettingPlugGaugeBox, text='上偏差').grid(row=1, column=0, sticky=tk.W)
        tk.Label(noGoGoSettingPlugGaugeBox, text='下偏差').grid(row=2, column=0, sticky=tk.W)
        tk.Label(noGoGoSettingPlugGaugeBox, text='粗糙度Ra').grid(row=3, column=0, sticky=tk.W)

        self.noGoGoSettingPlugGaugeNorminalSizeVar = tk.DoubleVar()
        self.noGoGoSettingPlugGaugeUpperDeviationVar = tk.DoubleVar()
        self.noGoGoSettingPlugGaugeLowerDeviationVar = tk.DoubleVar()
        self.noGoGoSettingPlugGaugeRaVar = tk.DoubleVar()

        tk.Entry(noGoGoSettingPlugGaugeBox, textvariable=self.noGoGoSettingPlugGaugeNorminalSizeVar, state='readonly').grid(row=0, column=1, sticky=tk.NSEW)
        tk.Entry(noGoGoSettingPlugGaugeBox, textvariable=self.noGoGoSettingPlugGaugeUpperDeviationVar, state='readonly').grid(row=1, column=1, sticky=tk.NSEW)
        tk.Entry(noGoGoSettingPlugGaugeBox, textvariable=self.noGoGoSettingPlugGaugeLowerDeviationVar, state='readonly').grid(row=2, column=1, sticky=tk.NSEW)
        tk.Entry(noGoGoSettingPlugGaugeBox, textvariable=self.noGoGoSettingPlugGaugeRaVar, state='readonly').grid(row=3, column=1, sticky=tk.NSEW)

        return noGoGoSettingPlugGaugeBox

def test():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    test()