from querydata import QueryData
from buildtime import buildTime

import tkinter as tk
from decimal import Decimal, getcontext, InvalidOperation

getcontext().prec = 10

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
    
    def validateNumber(self, number: tk.StringVar) -> Decimal | None:
        """
        验证输入的 tkinter 字符串值是否为数字

        Args:
            number (tk.StringVar): tkinter 字符串值

        Returns:
            Decimal | None | False: None 则带表输入空，可不作处理； False 则表示输入值不是数字； Decimal 则转为浮点数的结果
        """
        val = number.get().strip()
        if val in ('', '.', '-', '-.', '0.', '-0.'):
            return None
        try:
            return Decimal(val)
        except InvalidOperation:
            return False

    
    def onUpdateCalc(self, *args):
        """
        更新计算
        """
        errors = []

        # 验证名义尺寸
        norminalSize = self.validateNumber(self.norminalSizeVar)
        if norminalSize is None:
            errors.append('名义尺寸：未输完整')
        elif norminalSize is False:
            errors.append('名义尺寸：只能输入数字')

        # 验证上偏差
        upperDeviation = self.validateNumber(self.upperDeviationVar)
        if upperDeviation is None:
            errors.append('上偏差：未输完整')
        elif upperDeviation is False:
            errors.append('上偏差：只能输入数字')

        # 验证下偏差
        lowerDeviation = self.validateNumber(self.lowerDeviationVar)
        if lowerDeviation is None:
            errors.append('下偏差：未输完整')
        elif lowerDeviation is False:
            errors.append('下偏差：只能输入数字')

        # 如果有错误，显示并退出
        if errors:
            self.infoVar.set('；'.join(errors))
            return

        # 计算上下限和公差
        upperLimit = norminalSize + upperDeviation
        lowerLimit = norminalSize + lowerDeviation
        tolerance = upperDeviation - lowerDeviation

        itT1Z1 = self.queryData.queryItT1Z1(norminalSize, tolerance)
        if itT1Z1 is None:
            self.infoVar.set('轴孔公差等级过低或过高，仅适用于IT6-IT16公差等级尺寸')
            self.goNoGoGaugeClear()
            self.settingPlugGaugeClear()
            return

        it, t1, z1 = itT1Z1
        self.internationalToleranceGradeVar.set(f'IT{it}')

        feature = self.feature.get()
        self.infoVar.set('')

        def fmt(x):
            if isinstance(x, Decimal):
                s = format(x, 'f')
                if '.' in s:
                    s = s.rstrip('0').rstrip('.')
                return s
            elif x is None:
                return '—'
            return str(x)


        match feature:
            case 'shaft':
                goNorminalSize = upperLimit - z1 - t1 / 2
                goUpperDeviation = t1
                goLowerDeviation = Decimal('0')
                goWearLimit = upperLimit
                goRa = self.queryData.queryRa(feature, goNorminalSize, it)

                self.goGaugeNorminalSizeVar.set(fmt(goNorminalSize))
                self.goGaugeUpperDeviationVar.set(fmt(goUpperDeviation))
                self.goGaugeLowerDeviationVar.set(fmt(goLowerDeviation))
                self.goGaugeWearLimitVar.set(fmt(goWearLimit))
                self.goGaugeRaVar.set(fmt(goRa))

                noGoNorminalSize = lowerLimit
                noGoUpperDeviation = t1
                noGoLowerDeviation = Decimal('0')
                noGoRa = self.queryData.queryRa(feature, noGoNorminalSize, it)

                self.noGoGaugeNorminalSizeVar.set(fmt(noGoNorminalSize))
                self.noGoGaugeUpperDeviationVar.set(fmt(noGoUpperDeviation))
                self.noGoGaugeLowerDeviationVar.set(fmt(noGoLowerDeviation))
                self.noGoGaugeRaVar.set(fmt(noGoRa))

                goWearNorminalSize = upperLimit
                goWearUpperDeviation = Decimal('0')
                goWearLowerDeviation = -t1 / 2
                goWearRa = self.queryData.querySettingPlugGaugeRa(goWearNorminalSize, it)

                self.goWearSettingPlugGaugeNorminalSizeVar.set(fmt(goWearNorminalSize))
                self.goWearSettingPlugGaugeUpperDeviationVar.set(fmt(goWearUpperDeviation))
                self.goWearSettingPlugGaugeLowerDeviationVar.set(fmt(goWearLowerDeviation))
                self.goWearSettingPlugGaugeRaVar.set(fmt(goWearRa))

                goGoNorminalSize = upperLimit - z1
                goGoUpperDeviation = Decimal('0')
                goGoLowerDeviation = -t1 / 2
                goGoRa = self.queryData.querySettingPlugGaugeRa(goGoNorminalSize, it)

                self.goGoSettingPlugGaugeNorminalSizeVar.set(fmt(goGoNorminalSize))
                self.goGoSettingPlugGaugeUpperDeviationVar.set(fmt(goGoUpperDeviation))
                self.goGoSettingPlugGaugeLowerDeviationVar.set(fmt(goGoLowerDeviation))
                self.goGoSettingPlugGaugeRaVar.set(fmt(goGoRa))

                noGoGoLowerDeviation = -t1 / 2
                noGoGoUpperDeviation = Decimal('0')
                noGoGoNorminalSize = lowerLimit - noGoGoLowerDeviation
                noGoGoRa = self.queryData.querySettingPlugGaugeRa(noGoGoNorminalSize, it)

                self.noGoGoSettingPlugGaugeNorminalSizeVar.set(fmt(noGoGoNorminalSize))
                self.noGoGoSettingPlugGaugeUpperDeviationVar.set(fmt(noGoGoUpperDeviation))
                self.noGoGoSettingPlugGaugeLowerDeviationVar.set(fmt(noGoGoLowerDeviation))
                self.noGoGoSettingPlugGaugeRaVar.set(fmt(noGoGoRa))

            case 'hole':
                goNorminalSize = lowerLimit + z1 + t1 / 2
                goUpperDeviation = Decimal('0')
                goLowerDeviation = -t1
                goWearLimit = lowerLimit
                goRa = self.queryData.queryRa(feature, goNorminalSize, it)

                self.goGaugeNorminalSizeVar.set(fmt(goNorminalSize))
                self.goGaugeUpperDeviationVar.set(fmt(goUpperDeviation))
                self.goGaugeLowerDeviationVar.set(fmt(goLowerDeviation))
                self.goGaugeWearLimitVar.set(fmt(goWearLimit))
                self.goGaugeRaVar.set(fmt(goRa))

                noGoNorminalSize = upperLimit
                noGoUpperDeviation = Decimal('0')
                noGoLowerDeviation = -t1
                noGoRa = self.queryData.queryRa(feature, noGoNorminalSize, it)

                self.noGoGaugeNorminalSizeVar.set(fmt(noGoNorminalSize))
                self.noGoGaugeUpperDeviationVar.set(fmt(noGoUpperDeviation))
                self.noGoGaugeLowerDeviationVar.set(fmt(noGoLowerDeviation))
                self.noGoGaugeRaVar.set(fmt(noGoRa))

                self.settingPlugGaugeClear()

    def goNoGoGaugeClear(self):
        for var in [
            self.internationalToleranceGradeVar,
            self.goGaugeNorminalSizeVar, self.goGaugeUpperDeviationVar,
            self.goGaugeLowerDeviationVar, self.goGaugeWearLimitVar,
            self.goGaugeRaVar, self.noGoGaugeRaVar,
            self.noGoGaugeNorminalSizeVar, self.noGoGaugeUpperDeviationVar,
            self.noGoGaugeLowerDeviationVar
        ]:
            var.set('')

    def settingPlugGaugeClear(self):
        for var in [
            self.goGoSettingPlugGaugeNorminalSizeVar, self.goGoSettingPlugGaugeUpperDeviationVar,
            self.goGoSettingPlugGaugeLowerDeviationVar, self.goWearSettingPlugGaugeNorminalSizeVar,
            self.goWearSettingPlugGaugeUpperDeviationVar, self.goWearSettingPlugGaugeLowerDeviationVar,
            self.noGoGoSettingPlugGaugeNorminalSizeVar, self.noGoGoSettingPlugGaugeUpperDeviationVar,
            self.noGoGoSettingPlugGaugeLowerDeviationVar, self.goGoSettingPlugGaugeRaVar,
            self.goWearSettingPlugGaugeRaVar, self.noGoGoSettingPlugGaugeRaVar
        ]:
            var.set('')

    def goGaugeBoxUi(self):
        """
        通规尺寸
        """
        box = tk.LabelFrame(self, text='T 通规尺寸', padx=10, pady=10)
        labels = ['名义尺寸：', '上偏差：', '下偏差：', '磨损极限：', '粗糙度Ra']
        vars_ = [
            'goGaugeNorminalSizeVar', 'goGaugeUpperDeviationVar',
            'goGaugeLowerDeviationVar', 'goGaugeWearLimitVar', 'goGaugeRaVar'
        ]
        for i, text in enumerate(labels):
            tk.Label(box, text=text).grid(row=i, column=0, sticky=tk.W)
            setattr(self, vars_[i], tk.StringVar())
            tk.Entry(box, textvariable=getattr(self, vars_[i]), state='readonly').grid(row=i, column=1, sticky=tk.NSEW)
        return box

    def noGoGaugeBoxUi(self):
        """
        止规尺寸
        """
        box = tk.LabelFrame(self, text='Z 止规尺寸', padx=10, pady=10)
        labels = ['名义尺寸：', '上偏差：', '下偏差：', '粗糙度Ra']
        vars_ = [
            'noGoGaugeNorminalSizeVar', 'noGoGaugeUpperDeviationVar',
            'noGoGaugeLowerDeviationVar', 'noGoGaugeRaVar'
        ]
        for i, text in enumerate(labels):
            tk.Label(box, text=text).grid(row=i, column=0, sticky=tk.W)
            setattr(self, vars_[i], tk.StringVar())
            tk.Entry(box, textvariable=getattr(self, vars_[i]), state='readonly').grid(row=i, column=1, sticky=tk.NSEW)
        return box
    
    def goGoSettingPlugGaugeBoxUi(self):
        """
        “校通-通” 塞规
        """
        return self._createSettingPlugBox('TT “校通-通” 塞规尺寸', 'goGoSettingPlugGauge')
    
    def goWearSettingPlugGaugeBoxUi(self):
        """
        “校通-损” 塞规
        """
        return self._createSettingPlugBox('TS “校通-损” 塞规尺寸', 'goWearSettingPlugGauge')
    
    def noGoGoSettingPlugGaugeBoxUi(self):
        """
        “校止-通” 塞规
        """
        return self._createSettingPlugBox('ZT “校止-通” 塞规尺寸', 'noGoGoSettingPlugGauge')
    
    def _createSettingPlugBox(self, title, prefix):
        box = tk.LabelFrame(self, text=title, padx=10, pady=10)
        labels = ['名义尺寸', '上偏差', '下偏差', '粗糙度Ra']
        names = ["NorminalSizeVar", "UpperDeviationVar", "LowerDeviationVar", "RaVar"]
        for i, text in enumerate(labels):
            tk.Label(box, text=text).grid(row=i, column=0, sticky=tk.W)
            var = tk.StringVar()
            setattr(self, f"{prefix}{names[i]}", var)
            tk.Entry(box, textvariable=var, state="readonly").grid(row=i, column=1, sticky=tk.NSEW)

        return box
