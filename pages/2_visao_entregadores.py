import folium
import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px

from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config(
    page_title='Visao Entregadores',
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

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:,['Time_taken(min)', 'Delivery_person_ID', 'City']]
    .groupby(['City', 'Delivery_person_ID'])
    .mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())
                
    df2_met1 = df2.loc[df2['City'] == 'Metropolitian' , :].head(10)
    df2_met2 = df2.loc[df2['City'] == 'Urban' , :].head(10)
    df2_met3 = df2.loc[df2['City'] == 'Semi-Urban' , :].head(10)

    df2_final = pd.concat([df2_met1,df2_met2,df2_met3], axis=0).reset_index(drop=True)
    return df2_final

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
st.header('Marketplace - Visão Entregadores')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('--------')

#Filtro de data
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Ate qual valor?', 
                  value=pd.datetime(2022, 4, 14), 
                  min_value=pd.datetime(2022, 2, 11),
                  max_value=pd.datetime(2022, 4, 6), 
                  format='DD-MM-YYYY')

st.sidebar.markdown('--------')

#Filtro de tipo de trafico
traffic_options = (st.sidebar.multiselect('Quais as condicoes do transito', options=(df1['Road_traffic_density'].unique()), default=['Low', 'High', 'Jam', 'Medium']))

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1: 
    with st.container():
        st.title('Metricas Gerais')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de Idade', maior_idade)
        
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de Idade', menor_idade)
        
        with col3:
            maior_condi = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condicao', maior_condi)

        with col4:
            menor_condi = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condicao', menor_condi)
    
    with st.container():
        st.markdown('------------')
        st.title('Avaliacoes')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Avaliacao media por entregador')
            delivery_mean = (df1[['Delivery_person_ID',                                         
                            'Delivery_person_Ratings']].groupby
                            (['Delivery_person_ID']).mean().reset_index())
            st.dataframe(delivery_mean)
            
        with col2:
            st.markdown('#### Avaliacao media por transito')
            df1_mean_std_traffic = (df1[['Delivery_person_Ratings',              
                                         'Road_traffic_density']]
                                         .groupby('Road_traffic_density')
                                         .agg({'Delivery_person_Ratings':['mean','std']}))
            
            df1_mean_std_traffic.columns = ['delivery_mean', 'delivery_std']
            df1_mean_std_traffic = df1_mean_std_traffic.reset_index()
            
            st.dataframe(df1_mean_std_traffic)
            
            st.markdown('#### Avaliacao media por condicoes climaticas')
            df1_mean_std_weather = (df1[['Delivery_person_Ratings',                      
                                        'Weatherconditions']]
                                        .groupby('Weatherconditions')
                                        .agg({'Delivery_person_Ratings':['mean','std']}))

            df1_mean_std_weather.columns = ['delivery_mean', 'delivery_std']
            df1_mean_std_weather = df1_mean_std_weather.reset_index()
            
            st.dataframe(df1_mean_std_weather)
    with st.container():
        st.markdown('------------')
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Top entregadores mais rapidos')
            df2_final = top_delivers(df1, top_asc=True)
            st.dataframe(df2_final)
        
        with col2:
            st.markdown('#### Top entregadores mais lentos')
            df2_final = top_delivers(df1, top_asc=False)
            st.dataframe(df2_final)