import json
from typing import Literal

class QueryData:
    def __init__(self):
        # 零件公称尺寸和量规T1、Z1参数
        # 数据整理为下面格式：
        # [
        #     ((公称尺寸范围下限, 公称尺寸范围上限): ((公差值, T1, Z1), (公差值, T1, Z1), ...)),
        #     ((公称尺寸范围下限, 公称尺寸范围上限): ((公差值, T1, Z1), (公差值, T1, Z1), ...)},
        #     ...
        # ]
        self.norminalTolT1Z1Data = [
            (
                tuple(norminalData['norminalRange']),
                tuple(
                    (
                    tolT1Z1['tol'],
                    QueryData.ItLevels[i],
                    tolT1Z1['T1'],
                    tolT1Z1['Z1']) 
                    for i, tolT1Z1 in enumerate(norminalData['tolT1Z1s'])
                )
            )
            for norminalData in json.loads(QueryData.norminalTolT1Z1Json)
        ]

        # 量规公称尺寸、零件公差等级和量规粗糙度
        # 数据整理为下面格式：
        # {
        # {
        #    "hole": {
        #           (零件公差等级范围下限, 零件公差等级范围上限): (((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ...),
        #           (零件公差等级范围下限, 零件公差等级范围上限): (((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ...),
        #           ...
        #       }
        #    "shaft": {
        #           (零件公差等级范围下限, 零件公差等级范围上限): (((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ...),
        #           ...
        #       }
        # }
        self.gaugeNorminalItRaData = {
            feature: {
                tuple(item['IT']): tuple(
                    (tuple(nr['nominal']), nr['Ra'])
                    for nr in item['nominalRa']
                )
                for item in norminalRa
            }
            for feature, norminalRa in json.loads(QueryData.gaugeNorminalItRaJson).items()
        }

        # 校规公称尺寸、零件公差等级和量规粗糙度
        # 数据整理为下面格式：
        # {
        #       (零件公差等级范围下限, 零件公差等级范围上限): (((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ...),
        #       (零件公差等级范围下限, 零件公差等级范围上限): (((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ((量规公称尺寸范围下限， 量规公称尺寸范围上限), 粗糙度), ...),
        #       ...
        # }
        self.settingPlugGaugeNorminalItRaData = {
            tuple(item['IT']): tuple(
                (tuple(nr['nominal']), nr['Ra'])
                for nr in item['nominalRa']
            )
            for item in json.loads(QueryData.settingPlugGaugeNorminalItRaJson)
        }

    def queryRa(self, feature: Literal['hole', 'shaft'], gaugeNorminal: float, it: Literal[6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]):
        """
        根据量规公称尺寸和零件公差等级查询粗糙度。
        
        Args:
            feature (str): 零件特征，取值：'hole' 或 'shaft'
            gaugeNorminal (float): 量规公称尺寸，单位：mm，范围大于 0 至 500
            it (int): 零件公差等级，IT6-IT16

        Returns:
            float: 粗糙度，单位：μm
        """
        for itRange, norminalRaList in self.gaugeNorminalItRaData[feature].items():
            if itRange[0] <= it <= itRange[1]:
                for (norminalMin, norminalMax), ra in norminalRaList:
                    if norminalMin < gaugeNorminal <= norminalMax:
                        return ra
        return None
    
    def querySettingPlugGaugeRa(self, gaugeNorminal: float, it: Literal[6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]):
        """
        根据校规量规公称尺寸和零件公差等级查询粗糙度。

        Args:
            gaugeNorminal (float): 校规量规公称尺寸，单位：mm，范围大于 0 至 500
            it (int): 零件公差等级，IT6-IT16

        Returns:
            float: 粗糙度，单位：μm
        """
        for itRange, norminalList in self.settingPlugGaugeNorminalItRaData.items():
            if itRange[0] <= it <= itRange[1]:
                for (norminalMin, norminalMax), ra in norminalList:
                    if norminalMin < gaugeNorminal <= norminalMax:
                        return ra
        return None

    def queryItT1Z1(self, norminalSize: float, tolerance: float):
        """
        根据零件尺寸查询其公差等级及量规通止端尺寸参数。
        
        Args:
            norminalSize (float): 零件尺寸，单位：mm，大于 0 至 500
            tolerance (float): 零件公差，单位：mm

        Returns:
            tuple: (IT, T1, Z1)，单位：mm。IT 尺寸公差等级；T1：工作量规尺寸公差；Z1：通端工作量规尺寸公差带的中心线至工作最大实体尺寸之间的距离。
        """
        tolerance *= 1000
        print(f'norminalSize: {norminalSize}, tolerance: {tolerance}')
        for (sizeMin, sizeMax), tolT1Z1List in self.norminalTolT1Z1Data:
            if sizeMin < norminalSize <= sizeMax:
                print(f'sizeMin: {sizeMin}, sizeMax: {sizeMax}')
                candidates = [(tol, it, t1, t2) for tol, it, t1, t2 in tolT1Z1List if tol <= tolerance]
                if not candidates:
                    return None
                print(candidates)
                best = max(candidates, key=lambda x: x[0])
                print(best)
                return best[1], best[2] / 1000, best[3] / 1000
        return None

    # 公差等级 IT6-IT16
    ItLevels = [i for i in range(6, 17)]

    # 《GB/T 1957-2006》 表 A.1
    # 校规公称尺寸、零件公差等级和量规粗糙度表
    settingPlugGaugeNorminalItRaJson = '''
        [
            {
                "IT": [6, 9],
                "nominalRa": [
                    {"nominal": [0, 120], "Ra": 0.05},
                    {"nominal": [120, 315], "Ra": 0.1},
                    {"nominal": [315, 500], "Ra": 0.2}
                ]
            },
            {
                "IT": [10, 12],
                "nominalRa": [
                    {"nominal": [0, 120], "Ra": 0.1},
                    {"nominal": [120, 315], "Ra": 0.2},
                    {"nominal": [315, 500], "Ra": 0.4}
                ]
            },
            {
                "IT": [13, 16],
                "nominalRa": [
                    {"nominal": [0, 120], "Ra": 0.2},
                    {"nominal": [120, 315], "Ra": 0.4},
                    {"nominal": [315, 500], "Ra": 0.4}
                ]
            }
        ]
    '''

    # 《GB/T 1957-2006》 表 4
    # 量规公称尺寸、零件公差等级和量规粗糙度表
    gaugeNorminalItRaJson = '''
        {
            "hole": [
                {
                    "IT": [6, 6],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.05},
                        {"nominal": [120, 315], "Ra": 0.1},
                        {"nominal": [315, 500], "Ra": 0.2}
                    ]
                },
                {
                    "IT": [7, 9],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.1},
                        {"nominal": [120, 315], "Ra": 0.2},
                        {"nominal": [315, 500], "Ra": 0.4}
                    ]
                },
                {
                    "IT": [10, 12],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.2},
                        {"nominal": [120, 315], "Ra": 0.4},
                        {"nominal": [315, 500], "Ra": 0.8}
                    ]
                },
                {
                    "IT": [13, 16],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.4},
                        {"nominal": [120, 315], "Ra": 0.8},
                        {"nominal": [315, 500], "Ra": 0.8}
                    ]
                }
            ],
            "shaft": [
                {
                    "IT": [6, 9],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.1},
                        {"nominal": [120, 315], "Ra": 0.2},
                        {"nominal": [315, 500], "Ra": 0.4}
                    ]
                },
                {
                    "IT": [10, 12],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.2},
                        {"nominal": [120, 315], "Ra": 0.4},
                        {"nominal": [315, 500], "Ra": 0.8}
                    ]
                },
                {
                    "IT": [13, 16],
                    "nominalRa": [
                        {"nominal": [0, 120], "Ra": 0.4},
                        {"nominal": [120, 315], "Ra": 0.8},
                        {"nominal": [315, 500], "Ra": 0.8}
                    ]
                }
            ]
        }
    '''

    # 《GB/T 1957-2006》 表 3
    # 零件尺寸和量规 T1、Z1 参数表
    norminalTolT1Z1Json = '''
        [
            {
                "norminalRange": [0, 3],
                "tolT1Z1s": [
                    {"tol": 6, "T1": 1, "Z1": 1},
                    {"tol": 10, "T1": 1.2, "Z1": 1.6},
                    {"tol": 14, "T1": 1.6, "Z1": 2},
                    {"tol": 25, "T1": 2, "Z1": 3},
                    {"tol": 40, "T1": 2.4, "Z1": 4},
                    {"tol": 60, "T1": 3, "Z1": 6},
                    {"tol": 100, "T1": 4, "Z1": 9},
                    {"tol": 140, "T1": 6, "Z1": 14},
                    {"tol": 250, "T1": 9, "Z1": 20},
                    {"tol": 400, "T1": 14, "Z1": 30},
                    {"tol": 600, "T1": 20, "Z1": 40}
                ]
            },
            {
                "norminalRange": [3, 6],
                "tolT1Z1s": [
                    {"tol": 8, "T1": 1.2, "Z1": 1.4},
                    {"tol": 12, "T1": 1.4, "Z1": 2},
                    {"tol": 18, "T1": 2, "Z1": 2.6},
                    {"tol": 30, "T1": 2.4, "Z1": 4},
                    {"tol": 48, "T1": 3, "Z1": 5},
                    {"tol": 75, "T1": 4, "Z1": 8},
                    {"tol": 120, "T1": 5, "Z1": 11},
                    {"tol": 180, "T1": 7, "Z1": 16},
                    {"tol": 300, "T1": 11, "Z1": 25},
                    {"tol": 480, "T1": 16, "Z1": 35},
                    {"tol": 750, "T1": 25, "Z1": 50}
                ]
            },
            {
                "norminalRange": [6, 10],
                "tolT1Z1s": [
                    {"tol": 9, "T1": 1.4, "Z1": 1.6},
                    {"tol": 15, "T1": 1.8, "Z1": 2.4},
                    {"tol": 22, "T1": 2.4, "Z1": 3.2},
                    {"tol": 36, "T1": 2.8, "Z1": 5},
                    {"tol": 58, "T1": 3.6, "Z1": 6},
                    {"tol": 90, "T1": 5, "Z1": 9},
                    {"tol": 150, "T1": 6, "Z1": 13},
                    {"tol": 220, "T1": 8, "Z1": 20},
                    {"tol": 360, "T1": 13, "Z1": 30},
                    {"tol": 580, "T1": 20, "Z1": 40},
                    {"tol": 900, "T1": 30, "Z1": 60}
                ]
            },
            {
                "norminalRange": [10, 18],
                "tolT1Z1s": [
                    {"tol": 11, "T1": 1.6, "Z1": 2},
                    {"tol": 18, "T1": 2, "Z1": 2.8},
                    {"tol": 27, "T1": 2.8, "Z1": 4},
                    {"tol": 43, "T1": 3.4, "Z1": 6},
                    {"tol": 70, "T1": 4, "Z1": 8},
                    {"tol": 110, "T1": 6, "Z1": 11},
                    {"tol": 180, "T1": 7, "Z1": 15},
                    {"tol": 270, "T1": 10, "Z1": 24},
                    {"tol": 430, "T1": 15, "Z1": 35},
                    {"tol": 700, "T1": 24, "Z1": 50},
                    {"tol": 1100, "T1": 35, "Z1": 75}
                ]
            },
            {
                "norminalRange": [18, 30],
                "tolT1Z1s": [
                    {"tol": 13, "T1": 2, "Z1": 2.4},
                    {"tol": 21, "T1": 2.4, "Z1": 3.4},
                    {"tol": 33, "T1": 3.4, "Z1": 5},
                    {"tol": 52, "T1": 4, "Z1": 7},
                    {"tol": 84, "T1": 5, "Z1": 9},
                    {"tol": 130, "T1": 7, "Z1": 13},
                    {"tol": 210, "T1": 8, "Z1": 18},
                    {"tol": 330, "T1": 12, "Z1": 28},
                    {"tol": 520, "T1": 18, "Z1": 40},
                    {"tol": 840, "T1": 28, "Z1": 60},
                    {"tol": 1300, "T1": 40, "Z1": 90}
                ]
            },
            {
                "norminalRange": [30, 50],
                "tolT1Z1s": [
                    {"tol": 16, "T1": 2.4, "Z1": 2.8},
                    {"tol": 25, "T1": 3, "Z1": 4},
                    {"tol": 39, "T1": 4, "Z1": 6},
                    {"tol": 62, "T1": 5, "Z1": 8},
                    {"tol": 100, "T1": 6, "Z1": 11},
                    {"tol": 160, "T1": 8, "Z1": 16},
                    {"tol": 250, "T1": 10, "Z1": 22},
                    {"tol": 390, "T1": 14, "Z1": 34},
                    {"tol": 620, "T1": 22, "Z1": 50},
                    {"tol": 840, "T1": 28, "Z1": 60},
                    {"tol": 1300, "T1": 40, "Z1": 90}
                ]
            },
            {
                "norminalRange": [50, 80],
                "tolT1Z1s": [
                    {"tol": 19, "T1": 2.8, "Z1": 3.4},
                    {"tol": 30, "T1": 3.6, "Z1": 4.6},
                    {"tol": 46, "T1": 4.6, "Z1": 7},
                    {"tol": 74, "T1": 6, "Z1": 9},
                    {"tol": 120, "T1": 7, "Z1": 13},
                    {"tol": 190, "T1": 9, "Z1": 19},
                    {"tol": 300, "T1": 12, "Z1": 26},
                    {"tol": 460, "T1": 16, "Z1": 40},
                    {"tol": 740, "T1": 26, "Z1": 60},
                    {"tol": 1200, "T1": 40, "Z1": 90},
                    {"tol": 1900, "T1": 60, "Z1": 130}
                ]
            },
            {
                "norminalRange": [80, 120],
                "tolT1Z1s": [
                    {"tol": 22, "T1": 3.2, "Z1": 3.8},
                    {"tol": 35, "T1": 4.2, "Z1": 5.4},
                    {"tol": 54, "T1": 5.4, "Z1": 8},
                    {"tol": 87, "T1": 7, "Z1": 10},
                    {"tol": 140, "T1": 8, "Z1": 15},
                    {"tol": 220, "T1": 10, "Z1": 22},
                    {"tol": 350, "T1": 14, "Z1": 30},
                    {"tol": 540, "T1": 20, "Z1": 46},
                    {"tol": 870, "T1": 30, "Z1": 70},
                    {"tol": 1400, "T1": 46, "Z1": 100},
                    {"tol": 2200, "T1": 70, "Z1": 150}
                ]
            },
            {
                "norminalRange": [120, 180],
                "tolT1Z1s": [
                    {"tol": 25, "T1": 3.8, "Z1": 4.4},
                    {"tol": 40, "T1": 4.8, "Z1": 6},
                    {"tol": 63, "T1": 6, "Z1": 9},
                    {"tol": 100, "T1": 8, "Z1": 12},
                    {"tol": 160, "T1": 9, "Z1": 18},
                    {"tol": 250, "T1": 12, "Z1": 25},
                    {"tol": 400, "T1": 16, "Z1": 35},
                    {"tol": 630, "T1": 22, "Z1": 52},
                    {"tol": 1000, "T1": 35, "Z1": 80},
                    {"tol": 1600, "T1": 52, "Z1": 120},
                    {"tol": 2500, "T1": 80, "Z1": 180}
                ]
            },
            {
                "norminalRange": [180, 250],
                "tolT1Z1s": [
                    {"tol": 29, "T1": 4.4, "Z1": 5},
                    {"tol": 46, "T1": 5.4, "Z1": 7},
                    {"tol": 72, "T1": 7, "Z1": 10},
                    {"tol": 115, "T1": 9, "Z1": 14},
                    {"tol": 185, "T1": 10, "Z1": 20},
                    {"tol": 290, "T1": 14, "Z1": 29},
                    {"tol": 460, "T1": 18, "Z1": 40},
                    {"tol": 720, "T1": 26, "Z1": 60},
                    {"tol": 1150, "T1": 40, "Z1": 90},
                    {"tol": 1850, "T1": 60, "Z1": 130},
                    {"tol": 2900, "T1": 90, "Z1": 200}
                ]
            },
            {
                "norminalRange": [250, 315],
                "tolT1Z1s": [
                    {"tol": 32, "T1": 4.8, "Z1": 5.6},
                    {"tol": 52, "T1": 6, "Z1": 8},
                    {"tol": 81, "T1": 8, "Z1": 11},
                    {"tol": 130, "T1": 10, "Z1": 16},
                    {"tol": 210, "T1": 12, "Z1": 22},
                    {"tol": 320, "T1": 16, "Z1": 32},
                    {"tol": 520, "T1": 20, "Z1": 45},
                    {"tol": 810, "T1": 28, "Z1": 66},
                    {"tol": 1300, "T1": 45, "Z1": 100},
                    {"tol": 2100, "T1": 66, "Z1": 50},
                    {"tol": 3200, "T1": 100, "Z1": 220}
                ]
            },
            {
                "norminalRange": [315, 400],
                "tolT1Z1s": [
                    {"tol": 36, "T1": 5.4, "Z1": 6.2},
                    {"tol": 57, "T1": 7, "Z1": 9},
                    {"tol": 89, "T1": 9, "Z1": 12},
                    {"tol": 140, "T1": 11, "Z1": 18},
                    {"tol": 230, "T1": 14, "Z1": 25},
                    {"tol": 360, "T1": 18, "Z1": 36},
                    {"tol": 570, "T1": 22, "Z1": 50},
                    {"tol": 890, "T1": 32, "Z1": 74},
                    {"tol": 1400, "T1": 50, "Z1": 110},
                    {"tol": 2300, "T1": 74, "Z1": 170},
                    {"tol": 3600, "T1": 110, "Z1": 250}
                ]
            },
            {
                "norminalRange": [400, 500],
                "tolT1Z1s": [
                    {"tol": 40, "T1": 6, "Z1": 7},
                    {"tol": 63, "T1": 8, "Z1": 10},
                    {"tol": 97, "T1": 10, "Z1": 14},
                    {"tol": 155, "T1": 12, "Z1": 20},
                    {"tol": 250, "T1": 16, "Z1": 28},
                    {"tol": 400, "T1": 20, "Z1": 40},
                    {"tol": 630, "T1": 24, "Z1": 55},
                    {"tol": 970, "T1": 36, "Z1": 80},
                    {"tol": 1550, "T1": 55, "Z1": 120},
                    {"tol": 2500, "T1": 80, "Z1": 190},
                    {"tol": 4000, "T1": 120, "Z1": 280}
                ]
            }
        ]
    '''
