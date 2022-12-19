import folium
import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px

from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config(
    page_title='Visao Empresa',
    layout='wide')

#--------------------------
# Funções
#--------------------------
def clean_code(df1):
    #Limpando e convertendo coluna Delivery_person_Age para int 
    linhas_limpas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Limpando os NaN da coluna Road_traffic_density
    linhas_limpas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()

    #Limpando os NaN da coluna City
    linhas_limpas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()

    #Convertendo as linhas rating para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #Convertendo Order_date para datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #convertendo todas as 
    linhas_limpas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #removendo os espaços da linhas do data frame
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    #tirando os (min) da coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1[ 'Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1[ 'Time_taken(min)'].astype(int)
    
    return df1

def order_metric(df1):              
    #Seleção de linhas
    data_bar = df1[['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    
    #desenhar o grafico de barras
    fig = px.bar(data_bar, x='Order_Date', y='ID')
    return fig

def traffic_order_share(df1):
    data_traf = df1[['Road_traffic_density', 'ID']].groupby(['Road_traffic_density']).count().reset_index()

    data_traf = data_traf.loc[data_traf['Road_traffic_density'] != 'NaN', :]
    data_traf['entregas_per'] = data_traf['ID'] / data_traf['ID'].sum()

    fig2 = px.pie(data_traf, values='entregas_per', names='Road_traffic_density')
                
    return fig2

def traffic_order_city(df1):
    data_aux = (df1.loc[:,['City', 'Road_traffic_density', 'ID']]
    .groupby(['City', 'Road_traffic_density'])
    .count().reset_index())
    #data_aux = data_aux.loc[data_aux['City'] != 'NaN',:]
    #data_aux = data_aux.loc[data_aux['Road_traffic_density'] != 'NaN',:]

    fig3 = px.scatter(data_aux,x='City', y='Road_traffic_density', size='ID', color='City')
    return fig3

def order_by_week(df1):
    #Criacao coluna week_of_year
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    #Agrupamento das linhas 
    data_line = df1[['week_of_year', 'ID']].groupby(['week_of_year']).count().reset_index()

    #Grafico de vizualizacao
    fig4 = px.line(data_line, x='week_of_year', y='ID')
    return fig4

def order_share_by_week(df1):
    #Groupby para as 
    df_aux01 = df1[['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux02 = df1[['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig5 = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig5

def country_maps(df1):
    data_plot = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',                                                                     'Delivery_location_longitude']].groupby(['City',                                                                                 'Road_traffic_density']).median().reset_index()
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    folium_static(map_)
#--------------------------
# Inicio do Código


df = pd.read_csv('dataset/train.csv')
df1 = df.copy()
df1 = clean_code(df1)
#1.0: Visão -- da -- Empresa

#======================
#Barra lateral
#======================
st.header('Marketplace - Visão Empresa')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('--------')

#filtro de data
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Ate qual valor?', 
                  value=pd.datetime(2022, 4, 14), 
                  min_value=pd.datetime(2022, 2, 11),
                  max_value=pd.datetime(2022, 4, 6), 
                  format='DD-MM-YYYY')

st.sidebar.markdown('--------')

#filtro de tipo de trafico
traffic_options = (st.sidebar.multiselect('Quais as condicoes do transito', options=(df1['Road_traffic_density'].unique()), default=['Low', 'High', 'Jam', 'Medium']))

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas2 = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas2, :]
#======================
#Layout no Streamlit
#======================
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])

with tab1:
    with st.container():
        st.markdown("# Orders By Day")
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig2 = traffic_order_share(df1)
            st.plotly_chart(fig2, use_container_width=True)
                       
        with col2:
            st.header('Traffic Order City')
            fig3 = traffic_order_city(df1)
            st.plotly_chart(fig3, use_container_width=True)
                      
with tab2:
    with st.container():
        st.header('Order By Week')
        fig4 = order_by_week(df1)
        st.plotly_chart(fig4, use_container_width=True)
        
    
    with st.container():
        st.header('Order Share By Week')
        fig5 = order_share_by_week(df1)
        st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.header('Country Maps')
    country_maps(df1)
    