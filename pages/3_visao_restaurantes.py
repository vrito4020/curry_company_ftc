import folium
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config(
    page_title='Visao Restaurante',
    layout='wide')
#------------------------
# Funcoes
#------------------------
def clean_code(df1):
    #Limpando e converteendo coluna Delivery_person_Age para int 
    linhas_limpas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Limpando coluna Road_traffic_density
    linhas_limpas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()

    #Limpando coluna City
    linhas_limpas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()

    #Limpando a coluna Festival
    linhas_limpas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_limpas, :].copy()

    #Converter linhas rating para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #Converter Order_date para datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #convert multiple_deliveries to int
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

def distance(df1):
    colas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',                                                      'Delivery_location_longitude']
    df1['distance'] = (df1.loc[:, colas].apply(lambda x: haversine((x['Restaurant_latitude'],                                           x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1))
            
    dist_mean = np.round(df1['distance'].mean(), 2)
    return dist_mean

def avg_std_time(df1, yn, op):
    """ Esta funcao calcula o tempo medio e o desvio padrao do tempo de entrega.
        Parametros:
            Input:
                -df: Data frame com os dados para os calculos
                -yn: Se vai ou nao vai ocorrer com festival
                    'Yes ': tem festival
                    'No ' : nao tem festival
                -op: Tipo de operacao que precisa ser calculado
                    'fest_mean': Calcula o tempo medio
                    'fest_std' : Calcula o desvio padrao
            Output:
                Dataframe com duas colunas e uma linha
     """
    df_filt = df1.loc[:, ['Festival', 'Time_taken(min)']].groupby(['Festival']).agg({'Time_taken(min)':                                                                                                                ['mean','std']})
    df_filt.columns = ['fest_mean', 'fest_std']

    df_filt = df_filt.reset_index()
    df_filt = np.round(df_filt.loc[df_filt['Festival'] == yn, op], 2)
    return df_filt

def temp_entreg_city(df1):
    colas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = (df1.loc[:, colas].apply(lambda x: haversine((x['Restaurant_latitude'],
                                                                    x['Restaurant_longitude']),                    
                                                                   (x['Delivery_location_latitude'],
                                                                    x['Delivery_location_longitude'])), axis=1))

    City_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

    fig = go.Figure(data=[go.Pie(labels=City_distance['City'],values=City_distance['distance'], pull=[0, 0.1, 0])])
    return fig

def time_city(df1):
    mean_std_time = (df1.loc[:, ['City', 'Time_taken(min)']]
    .groupby(['City']).agg({'Time_taken(min)':['mean', 'std']}))
                
    mean_std_time.columns = ['time_mean', 'time_std']
    mean_std_time = mean_std_time.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=mean_std_time['City'], y=mean_std_time['time_mean'],
                                    error_y=dict(type='data', array=mean_std_time['time_std'])))
 
    fig.update_layout(barmode='group')
    return fig

def city_time_road(df1):
    mean_std = (df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
    .groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']}))
    mean_std.columns = ['time_mean', 'time_std']
    mean_std = mean_std.reset_index()

    fig = px.sunburst(mean_std, path=['City', 'Road_traffic_density'], values='time_mean',
                                  color='time_std', color_continuous_scale='RdBu', 
                                  color_continuous_midpoint=np.average(mean_std['time_std']))
    return fig

def dristri_dist(df1):
    mean_std = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
    .groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean', 'std']}))
        
    mean_std.columns = ['time_mean', 'time_std']
    mean_std = mean_std.reset_index()
    return mean_std
#------------------------
# Inicio do Codigo
#------------------------
df = pd.read_csv('dataset/train.csv')

df1 = df.copy()

df1 = clean_code(df1)

#2.0: Visão -- dos -- Entregadores

#======================
#Barra lateral
#======================
st.header('Marketplace - Visão Restaurantes')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('--------')

#Filtro de data
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Ate qual valor?', 
                  value=pd.to_datetime(2022, 4, 14), 
                  min_value=pd.to_datetime(2022, 2, 11),
                  max_value=pd.to_datetime(2022, 4, 6), 
                  format='DD-MM-YYYY')

st.sidebar.markdown('--------')

#Filtro de tipo de trafico
traffic_options = st.sidebar.multiselect('Quais as condicoes do transito', options=(df1['Road_traffic_density'].unique()), default=(df1['Road_traffic_density'].unique()))

st.sidebar.markdown('--------')
#Filtro de temporal
weather_options = st.sidebar.multiselect('Quais as condicoes do clima', options=(df1['Weatherconditions'].unique()), default=(df1['Weatherconditions'].unique()))

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas2 = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas2, :]

linhas_selecionadas3 = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas3, :]

#======================
#Layout no Streamlit
#======================

tab1, tab2, tab3 = st.tabs(['Visao Gerencial', '_', '_'])

with tab1:
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            entreg_unique = len(df1['Delivery_person_ID'].unique())
            col1.metric('Entregadores', entreg_unique)
        
        with col2:
            dist_mean = distance(df1)
            col2.metric('Distancia media', dist_mean)
        
        with col3:
            df_filt = avg_std_time(df1, yn='Yes ', op='fest_mean')
            col3.metric('Tempo medio entrega com festival', df_filt)
        
        with col4:
            df_filt = avg_std_time(df1, yn='Yes ', op='fest_std')
            col4.metric('Desvio padrao de entregas medio com festival', df_filt)
        
        with col5:
            df_filt = avg_std_time(df1, yn='No ', op='fest_mean')
            col5.metric('Tempo medio entrega com festival', df_filt)
            
        with col6:
            df_filt = avg_std_time(df1, yn='No ', op='fest_std')
            col6.metric('Desvio padrao de entregas medio com festival', df_filt)
        
    with st.container():
        st.markdown('--------')
        st.title('Tempo medio de entrega por cidade')
        fig = temp_entreg_city(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        st.markdown('--------')
        st.title('Distribuicao do Tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            fig = time_city(df1)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = city_time_road(df1)
            st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        st.markdown('--------')
        st.title('Distribuicao da Distancia')
        mean_std = dristri_dist(df1)
        st.dataframe(mean_std)
