import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

# Gerando dados fictícios
np.random.seed(42)
num_points = 50
x_data = pd.date_range("2024-01-01", periods=num_points).strftime("%Y-%m-%d").tolist()
y_data = np.linspace(50, 100, num_points) + np.random.normal(0, 5, num_points)

# Criando intervalos de confiança
confidence_interval = 8  # Ajuste para alterar o intervalo
lower_bound = y_data - confidence_interval
upper_bound = y_data + confidence_interval

# Criando o gráfico ECharts
option = {
    "title": {"text": "Gráfico com Intervalo de Confiança"},
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": x_data,
        "axisLabel": {"rotate": 45},  # Rotaciona os labels do eixo X
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "name": "Limite Inferior",
            "type": "line",
            "data": lower_bound.tolist(),
            "lineStyle": {"opacity": 0},  # Oculta a linha
            "stack": "confidence-band",
            "symbol": "none",
        },
        {
            "name": "Limite Superior",
            "type": "line",
            "data": (upper_bound - lower_bound).tolist(),
            "lineStyle": {"opacity": 0},  # Oculta a linha
            "areaStyle": {"color": "#ccc", "opacity": 0.5},  # Área sombreada
            "stack": "confidence-band",
            "symbol": "none",
        },
        {
            "name": "Média",
            "type": "line",
            "data": y_data.tolist(),
            "itemStyle": {"color": "#FF5733"},
            "showSymbol": False,
        },
    ],
}

# Exibindo no Streamlit
st_echarts(options=option, height="500px", theme="dark")
