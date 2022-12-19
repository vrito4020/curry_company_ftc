import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    layout='wide')

image_path = (r'C:\Users\victo\repositorio')
image = Image.open(image_path + '\logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('--------')

st.write("# Curry Company Growth Dashboard")

st.markdown(""" 
    Growth DashBoard foi construído para acompanhar as métricas de crescimento da Empresa, dos Restaurantes e Entregadores.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento. 
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanis de crescimento 
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes 
""")