# Utils Functions
import pandas as pd
import streamlit as st
import numpy as np
from src.iface_config import Config
from datetime import datetime
import requests
from bcb import sgs
from streamlit_echarts import st_echarts

class Utils:
    """Utils functions"""

    def __init__(self):
        
        self.config = Config()
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

    @st.cache_resource(show_spinner=False)
    def echart_dict(_self, data,
                    title: str = "",
                    label_format: str = "",
                    marker: bool = False,
                    smooth: bool = False,
                    mean: bool = False,
                    min_zoom = 0):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data.index.strftime("%d/%m/%Y").tolist()
        y_data = [round(value, 3) for value in data[data.columns[0]].tolist()]

        min_value = int(min(y_data) - (.5 * abs(min(y_data))))

        max_value = int(max(y_data) + (.5 * abs(max(y_data))))

        if -.50 < min(y_data) < 0:
            min_value -= 2

        options = {
            "grid": {
                "left": "4%", 
                "right": "3.5%", 
                # "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    }
                },
                "formatter": f"{{c}}{label_format}"
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": True},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": min_zoom, "end": 100},
                {"type": 'inside', "realtime": True, "start": min_zoom, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [{
                "type": "value",
                "axisLabel": {"formatter": f"{{value}}{label_format}"},
                "min": min_value,
                "max": max_value
            }],
            "series": [
                {
                    "type": "line",
                    "showSymbol": marker,
                    "smooth": smooth,
                    "lineStyle": {
                        "color": _self.config.base_color
                    },
                    "data": y_data
                }
            ]
        }

        if mean:
            options["series"][0]["markLine"] = {
                                            "data": [{"type": "average", "name": "Média"}],
                                                    "label": {
                                                    "position": "end",  
                                                    "offset": [-50, 20], 
                                                    "formatter": "{c}", 
        }
                                        }

        return options


    @st.cache_resource(show_spinner=False)
    def multiple_5series_echart(_self, data, title: str = ""):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data.index.strftime("%d/%m/%Y").tolist()

        y_data_1 = [round(value, 3) for value in data[data.columns[0]].tolist()]
        y_data_2 = [round(value, 3) for value in data[data.columns[1]].tolist()]
        y_data_3 = [round(value, 3) for value in data[data.columns[2]].tolist()]
        y_data_4 = [round(value, 3) for value in data[data.columns[3]].tolist()]
        y_data_5 = [round(value, 3) for value in data[data.columns[4]].tolist()]

        options = {

            "color": _self.config.multiple_color,
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "grid": {
                "left": "0%", 
                "right": "1%", 
                "containLabel": True
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    },
                    "formatter": f"{{c}}%"
                },
            },
            "legend": {
                "data": ["2 Anos", "5 Anos", "10 Anos", "20 Anos", "30 Anos"],
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {
                            "formatter": "{value}%"
                        }
            },
            "series": [
                {
                    "name": "2 Anos",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_1
                },
                {
                    "name": "5 Anos",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_2
                },
                {
                    "name": "10 Anos",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_3
                },
                {
                    "name": "20 Anos",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_4
                },
                {
                    "name": "30 Anos",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_5
                }
            ]
        }

        return options
    
    @st.cache_resource(show_spinner=False)
    def bar_chart_dict(_self, data, title, min_zoom: int = 0, label_format: str = "%"):
        """Renders Java Script Graphics"""

        x_data = data.index.strftime("%d/%m/%Y").tolist()
        y_data = [round(value, 3) for value in data[data.columns[0]].tolist()]

        min_value = int(min(y_data) - (.5 * abs(min(y_data))))
        max_value = int(max(y_data) + (.5 * abs(max(y_data))))

        if min_value == 0:
            min_value -= 5

        options = {
            "color": _self.config.base_color,
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                },
                "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    },
                "formatter": f"{{c}}{label_format}"
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": min_zoom, "end": 100},
                {"type": 'inside', "realtime": True, "start": min_zoom, "end": 100}
            ],
            "grid": {
                "left": "0%", 
                "right": "5%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "xAxis": [
                {
                    "type": "category",
                    "boundaryGap": True,
                    "data": x_data,
                    "axisTick": {
                        "alignWithLabel": True
                    }
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "axisLabel": {"formatter": f"{{value}}{label_format}"},
                    "min": min_value,
                    "max": max_value
                }
            ],
            "series": [
                {
                    "name": "",
                    "type": "bar",
                    "data": y_data,
                    "itemStyle": {
                        "barBorderRadius": [6, 6, 0, 0]
                    }
                }
            ]
        }

        return options
    
    @st.cache_resource(show_spinner=False)
    def simple_bar_chart_dict(_self, x, y, title):
        """Renders Java Script Graphics"""


        y = [round(value, 3) for value in y]


        options = {
            "color": _self.config.base_color,
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                },
                "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    },
                "formatter": "{c}%"
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "grid": {
                "left": "0%", 
                "right": "5%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "xAxis": [
                {
                    "type": "category",
                    "boundaryGap": True,
                    "data": x,
                    "axisTick": {
                        "alignWithLabel": True
                    }
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "axisLabel": {"formatter": f"{{value}}%"},
                    "min": 0,
                    "max": 100
                }
            ],
            "series": [
                {
                    "name": "",
                    "barWidth": '40%',
                    "type": "bar",
                    "data": y,
                    "itemStyle": {
                        "barBorderRadius": [6, 6, 0, 0]
                    }
                }
            ]
        }

        return options
    
    @st.cache_resource(show_spinner=False)
    def confint_chart(_self, data,
                      title: str = "",
                      label_format: str = "",
                      marker: bool = "%",
                      smooth: bool = False,
                      mean: bool = False):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data.index.strftime("%d/%m/%Y").tolist()
        y_data = [round(value, 3) for value in data[data.columns[0]].tolist()]
        lower_bound = np.array([round(value, 3) for value in data[data.columns[1]].tolist()])
        upper_bound = np.array([round(value, 3) for value in data[data.columns[2]].tolist()])


        min_value = int(min(y_data) - (.5 * abs(min(y_data))))
        max_value = int(max(y_data) + (.5 * abs(max(y_data))))

        option = {
            "color": _self.config.base_color,
            "title": {"text": title},
            "tooltip": {"trigger": "axis"},
            "backgroundColor": "#0E1117",
            "xAxis": {
                "type": "category",
                "data": x_data,
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "yAxis": {
                "type": "value"
                },
            "series": [
                {
                    "name": r"Limite Superior (68% de Confiança)",
                    "type": "line",
                    "data": upper_bound.tolist(),
                    "lineStyle": {"opacity": 0},
                    "areaStyle": {"color": "#ccc", "opacity": 0.2},
                    "stack": "confidence-band",
                    "symbol": "none",
                },
                {
                    "name": "Média",
                    "type": "line",
                    "data": y_data,
                    "showSymbol": False,
                },
                {
                    "name": r"Limite Inferior (68% de confiança)",
                    "type": "line",
                    "data": lower_bound.tolist(),
                    "lineStyle": {"opacity": 0},
                    "areaStyle": {"color": "#ccc", "opacity": 0.2},
                    "stack": "confidence-band",
                    "symbol": "none",
                }
            ],
        }

        return option
    

    @st.cache_data(show_spinner=False)
    def get_gdp(_self, country: str, ind, forward=False):
        """Gets IMF indicator"""

        url = f"{_self.config.vars.imf_gdp}/{ind}/"

        try:
            response = requests.get(url)
            if not response.ok:
                print(f"Error in API requisition: {response.status_code}")
            else:
                response = response.json()
                indicator = response["values"][ind]
                dates = [year for year in indicator[country].keys()]
                values = [value for value in indicator[country].values()]

                data = pd.DataFrame({"Date": dates,
                                     "values": values})
                data.set_index("Date", inplace=True)
                data.index = pd.to_datetime(data.index, format="%Y")
                if forward: 
                    data = data[(data.index.year >= _self.end.year)]
                else:
                    data = data[(data.index.year <= datetime.today().year) & (data.index.year >= _self.start.year)]
                
        except Exception as error:
            raise OSError(error) from error
        
        return data
    

    @st.cache_data(show_spinner=False)
    def get_bcb(_self, name, series: str):
        """Gets BCB Series"""

        try:
            
            data = sgs.get({name: series}, start=_self.start, end=_self.end)
                
        except Exception as error:
            raise OSError(error) from error
        
        return data
    

    def multiple_3series_echart(_self, data, title: str = ""):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data[data.columns[1]].tolist()

        y_data_1 = [round(value, 3) for value in data[data.columns[2]].tolist()]
        y_data_2 = [round(value, 3) for value in data[data.columns[3]].tolist()]
        y_data_3 = [round(value, 3) for value in data[data.columns[4]].tolist()]

        options = {

            "color": _self.config.multiple_color,
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "grid": {
                "left": "0%", 
                "right": "1%", 
                "containLabel": True
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    },
                    "formatter": f"{{c}}%"
                },
            },
            "legend": {
                "data": ["Cenário Positivo", "Cenário Neutro", "Cenário Negativo"],
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "animationDurationUpdate": 1000,
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {
                            "formatter": "{value}%"
                        }
            },
            "series": [
                {
                    "name": "Cenário Positivo",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": y_data_1
                },
                {
                    "name": "Cenário Neutro",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": y_data_2
                },
                {
                    "name": "Cenário Negativo",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": y_data_3
                },
            ]
        }

        return options
    

    def multiple_4series_echart(_self, data, curva_real, title: str = ""):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data[data.columns[1]].tolist()

        y_data_1 = [round(value, 3) for value in data[data.columns[2]].tolist()]
        y_data_2 = [round(value, 3) for value in data[data.columns[3]].tolist()]
        y_data_3 = [round(value, 3) for value in data[data.columns[4]].tolist()]

        curva_real = round(curva_real, 2).values.tolist()

        min_value = min([y_data_1, y_data_2, y_data_3])
        max_value = max([y_data_1, y_data_2, y_data_3])

        options = {

            "color": _self.config.multiple_color,
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "grid": {
                "left": "0%", 
                "right": "1%", 
                "containLabel": True
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    },
                    "formatter": f"{{c}}%"
                },
            },
            "legend": {
                "data": ["Positivo", "Neutro", "Negativo", "Curva DI"],
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "animationDurationUpdate": 1000,
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {
                            "formatter": "{value}%"
                        }
            },
            "series": [
                {
                    "name": "Positivo",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": y_data_1
                },
                {
                    "name": "Neutro",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": y_data_2
                },
                {
                    "name": "Negativo",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": y_data_3
                },
                {
                    "name": "Curva DI",
                    "type": "line",
                    "showSymbol": False,
                    "smooth": True,
                    "emphasis": {"focus": "series"},
                    "data": curva_real
                }
            ]
        }

        return options
    

    @st.cache_resource(show_spinner=False)
    def bonds_echart_dict(_self, data,
                    title: str = "",
                    label_format: str = "",
                    marker: bool = False,
                    smooth: bool = False,
                    mean: bool = False):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data[data.columns[0]].tolist()
        y_data = [round(value, 3) for value in data[data.columns[1]].tolist()]

        min_value = int(min(y_data) - (.5 * abs(min(y_data))))
        max_value = int(max(y_data) + (.5 * abs(max(y_data))))

        if -.50 < min(y_data) < 0:
            min_value -= 2

        options = {
            "grid": {
                "left": "0%", 
                "right": "1%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    }
                },
                "formatter": f"{{c}}{label_format}"
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": False},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [{
                "type": "value",
                "axisLabel": {"formatter": f"{{value}}{label_format}"},
                "min": min_value,
                "max": max_value
            }],
            "series": [
                {
                    "type": "line",
                    "showSymbol": marker,
                    "smooth": smooth,
                    "lineStyle": {
                        "color": _self.config.base_color
                    },
                    "data": y_data
                }
            ]
        }

        if mean:
            options["series"][0]["markLine"] = {
                                            "data": [{"type": "average", "name": "Média"}]
                                        }

        return options
    
    def multiple_interest(_self, data,
                    min_value: float,
                    max_value: float,
                    title: str = "",
                    label_format: str = "",
                    marker: bool = False,
                    smooth: bool = False,
                    mean: bool = False):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data[data.columns[0]].tolist()
        y_data_1 = [round(value, 3) for value in data[data.columns[1]].tolist()]
        y_data_2 = [round(value, 3) for value in data[data.columns[2]].tolist()]
        y_data_3 = [round(value, 3) for value in data[data.columns[3]].tolist()]
        y_data_4 = [round(value, 3) for value in data[data.columns[4]].tolist()]
        y_data_5 = [round(value, 3) for value in data[data.columns[5]].tolist()]

        if -.50 < min(y_data_5) < 0:
            min_value -= 2

        options = {
            "color": _self.config.multiple_color,
            "grid": {
                "left": "0%", 
                "right": "1%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765',
                    },
                    "formatter": f"{{c}}%"
                },
            },
            "legend": {
                "data": ["Atual", "1 mês", "3 meses", "6 meses", "1 ano"],
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": False},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [{
                "type": "value",
                "axisLabel": {"formatter": f"{{value}}{label_format}"},
                "min": min_value,
                "max": max_value
            }],
            "series": [
                {
                    "name": "Atual",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_1
                },
                {
                    "name": "1 mês",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_2
                },
                {
                    "name": "3 meses",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_3
                },
                {
                    "name": "6 meses",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_4
                },
                {
                    "name": "1 ano",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_5
                }
            ]
        }

        return options
    

    def multiple_interest_br(_self, data,
                    min_value: float,
                    max_value: float,
                    title: str = "",
                    label_format: str = "",
                    marker: bool = False,
                    smooth: bool = False,
                    mean: bool = False):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data[data.columns[0]].tolist()
        y_data_1 = [round(value, 3) for value in data[data.columns[1]].tolist()]
        y_data_2 = [round(value, 3) for value in data[data.columns[2]].tolist()]
        y_data_3 = [round(value, 3) for value in data[data.columns[3]].tolist()]
        y_data_4 = [round(value, 3) for value in data[data.columns[4]].tolist()]

        options = {
            "color": _self.config.multiple_color,
            "grid": {
                "left": "0%", 
                "right": "1%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765',
                    },
                    "formatter": f"{{c}}%"
                },
            },
            "legend": {
                "data": ["Atual", "1 mês", "3 meses", "6 meses", "1 ano"],
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": False},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [{
                "type": "value",
                "axisLabel": {"formatter": f"{{value}}{label_format}"},
                "min": min_value,
                "max": max_value
            }],
            "series": [
                {
                    "name": "Atual",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_1
                },
                {
                    "name": "1 mês",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_2
                },
                {
                    "name": "3 meses",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_3
                },
                {
                    "name": "6 meses",
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "data": y_data_4
                }
            ]
        }

        return options


    @st.cache_resource(show_spinner=False)
    def no_time_echart(_self, data,
                    title: str = "",
                    label_format: str = "",
                    marker: bool = False,
                    smooth: bool = False,
                    mean: bool = False,
                    column = 2):
        """Renders Java Script Graphics"""

        # considering that most of the graphs are time series
        x_data = data.index.tolist()
        y_data = [round(value, 3) for value in data[data.columns[column]].tolist()]

        min_value = int(min(y_data) - 1)

        max_value = int(max(y_data) + 1)

        if -.50 < min(y_data) < 0:
            min_value -= 2

        options = {
            "grid": {
                "left": "0%", 
                "right": "0%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    }
                },
                "formatter": f"{{c}}{label_format}"
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": False},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [{
                "type": "value",
                "axisLabel": {"formatter": f"{{value}}{label_format}"},
                "min": min_value,
                "max": max_value
            }],
            "series": [
                {
                    "type": "line",
                    "showSymbol": marker,
                    "smooth": smooth,
                    "lineStyle": {
                        "color": _self.config.base_color
                    },
                    "data": y_data
                }
            ]
        }

        if mean:
            options["series"][0]["markLine"] = {
                                            "data": [{"type": "average", "name": "Média"}],
                                                    "label": {
                                                    "position": "end",  
                                                    "offset": [-50, 20], 
                                                    "formatter": "{c}", 
        }
                                        }

        return options
    
    @st.cache_resource(show_spinner=False)
    def focus_echart(_self, data,
                    # min_value: float,
                    max_value: float,
                    title: str = "",
                    label_format: str = ""):
        """Renders Java Script Graphics"""


        anos = list(range(_self.end.year, _self.end.year + 5))
        x_data = data.index.strftime("%Y-%m-%d").tolist()
        
        y_data = [data[f"Mediana_{ano}"].tolist() for ano in anos]

        if np.min(data.values[data.values != None]) != 0:
            min_value = np.min(data.values[data.values != None])
        else:
            min_value = 0

        options = {
            "color": _self.config.multiple_color,
            "grid": {
                "left": "0%", 
                "right": "-11%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765',
                    },
                    "formatter": f"{{c}}%"
                },
            },
            "legend": {
                "data": [str(ano) for ano in anos],
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": False},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 90, "end": 100},
                {"type": 'inside', "realtime": True, "start": 90, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [
                {
                    "type": "value",
                    "axisLabel": {"formatter": f"{{value}}{label_format}"},
                    "min": min_value,
                    "max": max_value
                }
                for ano in anos
            ],
            "series": [
                {
                    "name": str(anos[i]),
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "connectNulls": True,
                    "data": y_data[i]
                } for i in range(5)
            ]
        }

        return options
    


    @st.cache_resource(show_spinner=False)
    def bar_line_chart_dict(_self, data, title, min_zoom: int = 0, label_format: str = "%"):
        """Renders Java Script Graphics"""

        y_acumulado = ((
            data
            .groupby(data.index.year)[data.columns[0]]
            .apply(lambda x: x.cumsum()).reset_index(level=0, drop=True)
        )/10).tolist()

        x_data = data.index.strftime("%d/%m/%Y").tolist()
        y_data = [round(value, 3) for value in data[data.columns[0]].tolist()]

        min_value = int(min(y_data) - (.5 * abs(min(y_data))))
        max_value = int(max(y_data) + (.5 * abs(max(y_data))))

        if min_value == 0:
            min_value -= 5

        options = {
            "color": [_self.config.base_color, "#2b58de"],
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "cross"
                },
                "animation": False,
                    "label": {
                        "backgroundColor": '#505765'
                    },
                "formatter": f"{{c}}{label_format}"
            },
            "legend": {
                "data": [
                {"name": "Fluxo", "icon": "rect"},
                {"name": "Acumulado no ano - base 10", "icon": "line"}
            ],
                "right": 140,
                "top": 10,
                "lineStyle": {
                    "color": "#2b58de"
            }
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "restore": {},
                    "saveAsImage": {}
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": min_zoom, "end": 100},
                {"type": 'inside', "realtime": True, "start": min_zoom, "end": 100}
            ],
            "grid": {
                "left": "0%", 
                "right": "5%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "xAxis": [
                {
                    "type": "category",
                    "boundaryGap": True,
                    "data": x_data,
                    "axisTick": {
                        "alignWithLabel": True
                    }
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "axisLabel": {"formatter": f"{{value}}{label_format}"},
                    "min": min_value,
                    "max": max_value
                }
            ],
            "series": [
                {
                    "name": "Fluxo",
                    "type": "bar",
                    "data": y_data,
                    "itemStyle": {
                        "barBorderRadius": [6, 6, 0, 0]
                    }
                },
                {   
                "name": "Acumulado no ano - base 10",
                "type": "line",
                "showSymbol": True,
                "marker": True,
                "lineStyle": {
                    "color": "#2b58de"
                },
                "data": y_acumulado
                }
            ]
        }

        return options
    

    @st.cache_resource(show_spinner=False)
    def multiple_pe_chart(_self, data,
                          legend: list,
                          max_value = None,
                          min_value = None,
                          title: str = "",
                          label_format: str = ""):
        """Renders Java Script Graphics"""

        x_data = data.index.strftime("%Y-%m-%d").tolist()        
        y_data = [data[col].tolist() for col in data.columns]

        if not max_value:
            max_value = 50

        options = {
            "color": _self.config.multiple_color,
            "grid": {
                "left": "2%", 
                "right": "2%", 
                "containLabel": True
            },
            "title": {
                "text": title,
                "textStyle": {"color": "#FFFFFF"}
            },
            "backgroundColor": "#0E1117",
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'cross',
                    "animation": False,
                    "label": {
                        "backgroundColor": '#505765',
                    },
                    "formatter": f"{{c}}"
                },
            },
            "legend": {
                "data": legend,
                "right": 140,
                "top": 10
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {"yAxisIndex": 'none'},
                    "dataView": {"readOnly": False},
                    "restore": {},
                }
            },
            "dataZoom": [
                {"show": True, "realtime": True, "start": 0, "end": 100},
                {"type": 'inside', "realtime": True, "start": 0, "end": 100}
            ],
            "xAxis": {
                "type": 'category',
                "data": x_data
            },
            "yAxis": [{
                "type": "value",
                "axisLabel": {"formatter": f"{{value}}{label_format}"},
                "min": min_value,
                "max": max_value
            }],
            "series": [
                {
                    "name": data.columns[i],
                    "type": "line",
                    "showSymbol": False,
                    "emphasis": {"focus": "series"},
                    "connectNulls": True,
                    "data": y_data[i]
                } for i in range(len(data.columns))
            ]
        }

        return options