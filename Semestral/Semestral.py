#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Anel Vásquez anel.vasquez@utp.ac.pa
#Vladimir Saenz vladimir.saenz@utp.ac.pa
#Hugo Zamorano hugo.zamorano@utp.ac.pa


# In[1]:


import psycopg2
import pandas as pd

from datetime import date
import os

import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np 
import re
import seaborn as sns
from shapely.geometry import Point, Polygon
from shapely.geometry import MultiPolygon
import folium


# In[4]:


conn = psycopg2.connect(host = "ec2-18-235-4-83.compute-1.amazonaws.com", dbname = "ddkspvhu6eifu0", user = "udxqmonmankkgv", password = "4ab607087038ffcf0478ca0c11b86a453d8e0470a34bfed09b1bc223de7ab72a", port = "5432")


# In[5]:


cur = conn.cursor()


# In[6]:


sql = "select * from tb_covid"
data = pd.read_sql_query(sql,conn)


# In[7]:


data = pd.DataFrame(data)
data = data.drop(index=0)


# Cambiamos la columna datecovid a formato date

# In[8]:


pd.to_datetime(data["datecovid"])


# In[9]:


data.info()


# Establecemos la columna de fechas (datecovid) para poder trabajar con los dias de la semana 

# In[10]:


data["datecovid"] = data["datecovid"].map(lambda x: date.fromisoformat(x))


# In[11]:


data["weekday"] = data["datecovid"].map(lambda x: x.weekday())
w_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
data["weekday"] = [w_list[idx] for idx in data["weekday"]]


# In[12]:


data.head()


# creamos latitud y longitud con el centroide como columnas
# 

# In[13]:


def cut_long(point):
    long, _ = point[6:-1].split(" ")
    return float(long)

def cut_lat(point):
    _, lat = point[6:-1].split(" ")
    return float(lat)


# In[14]:


data["long"] = data["centroid"].map(cut_long)
data["lat"] = data["centroid"].map(cut_lat)


# In[15]:


data.head()


# In[16]:


data_aux = data[~data[["airportname"]].duplicated()].reset_index(drop=True)
data_aux


# Preparamos un dataset para la visualizacion de los paises y ciudades donde se presentan los datos

# In[17]:


data_frame_geometry = data_aux[['airportname', 'city', 'sate','iso_3166_2', 'country', 'long', 'lat']]


# In[18]:


def visualize_airport_map(df,  zoom):
    lat_map=30.038557
    lon_map=31.231781
    f = folium.Figure(width=1000, height=500)
    m = folium.Map([lat_map,lon_map], zoom_start=zoom).add_to(f)
        
    for i in range(0,len(df)):
        folium.Marker(location=[df["lat"][i],df["long"][i]],icon=folium.Icon(icon_color='white',icon ='plane')).add_to(m)
        
    return m


# In[156]:


mapa_ap = visualize_airport_map(data_aux,2)


# In[157]:


mapa_ap


# Como la mayoria de los datos se encuentran en america, vamos a ver cuantos hay en total con un grafico circular

# In[20]:


df_Country_count = pd.DataFrame(data["country"].value_counts())
#df_Country_count
g = df_Country_count.plot.pie(y='country', figsize=(7, 7))
g.set_title("records for each country")


# Esto muestra que hay alrededor de 250 puntos de datos en cada aeropuerto, excepto en el Aeropuerto Internacional de Santiago y el Aeropuerto Internacional de Edmonton.

# In[21]:


plt.figure(figsize=(20,6))
fig1 = sns.countplot(x = 'airportname', data = data , palette='plasma')
fig1.set_xticklabels(fig1.get_xticklabels(), rotation=90)
fig1.set_title("Count for various Airports")
plt.show();


# Esto muestra que todas las ciudades tienen recuentos más o menos iguales en los datos, excepto Nueva York. La razón más probable sería que tiene más aeropuertos. 

# In[22]:


plt.figure(figsize=(20,6))
fig2 = sns.countplot(x = 'city', data = data , palette='rainbow_r')
fig2.set_xticklabels(fig2.get_xticklabels(), rotation=90)
fig2.set_title("Count for various City")
plt.show();


# Aquí, todos los estados tienen el mismo recuento de datos, excepto Alberta, Quebec, California y Nueva York. Una vez más, la razón más probable debe ser el número de aeropuertos.

# In[23]:


plt.figure(figsize=(20,6))
fig3 = sns.countplot(x = 'sate', data = data , palette='cividis')
fig3.set_xticklabels(fig3.get_xticklabels(), rotation=90)
fig3.set_title("Count for various State")
plt.show();


# Los puntos de datos máximos son para EE. UU. Seguido de Canadá. Esto se debe a que el número de aeropuertos en EE. UU. Y Canadá es probablemente mayor que el de Australia y Chile. 

# In[24]:


plt.figure(figsize=(8,4))
fig4 = sns.countplot(x = 'country', data = data , palette='plasma')
fig4.set_xticklabels(fig4.get_xticklabels())
fig4.set_title("Count for various Country")
plt.show();


# In[25]:


data.groupby("country")[['sate','city','airportname']].nunique()


# In[ ]:





# # Distribución del porcentaje de referencia

# In[26]:


data["percentofbaseline"]=pd.DataFrame(data["percentofbaseline"], dtype='int')


# In[27]:


sns.kdeplot(data['percentofbaseline'],shade=True, color="cyan")
plt.title("Distribucion de datos de referencia")
plt.show();


# # Distribucion para chile 

# In[28]:


data_chile = data[data['country']=='Chile']


# In[29]:


sns.kdeplot(data_chile['percentofbaseline'],shade=True, color="red")
plt.title("Distribucion de datos de referencia de Chile")
plt.show();


# # Distribucion para USA

# In[30]:


data_USA = data[data['country']=='United States of America (the)']
sns.kdeplot(data_USA['percentofbaseline'],shade=True, color="blue")
plt.title("Distribucion de datos de referencia de USA")
plt.show();


# # Distribucion para Canada

# In[31]:


data_Canada = data[data['country']=='Canada']
sns.kdeplot(data_Canada['percentofbaseline'],shade=True, color="green")
plt.title("Distribucion de datos de referencia de Canada")
plt.show();


# # Distribucion para Australia

# In[32]:


data_Australia = data[data['country']=='Australia']
sns.kdeplot(data_Australia['percentofbaseline'],shade=True, color="yellow")
plt.title("Distribucion de datos de referencia de Australia")
plt.show();


# # Movimiento durante los meses

# In[33]:


df_month_count = pd.DataFrame(data["datecovid"].map(lambda d: d.month).value_counts())
df_month_count = df_month_count.reset_index()
df_month_count = df_month_count.rename(columns={"datecovid":"count", "index":"month"})
g = sns.barplot(data=df_month_count.reset_index(), y="count", x="month")
g.set_xticklabels(g.get_xticklabels(), rotation=90)
g.set_title("Registro por cada mes")


# # Movimiento durante las semanas

# In[34]:


df_weekday_count = pd.DataFrame(data["weekday"].value_counts())
g = df_weekday_count.plot.pie(y='weekday', figsize=(7, 7))
g.set_title("Registo por semana")


# # Dashboard

# In[75]:


from jupyter_dash import JupyterDash


# In[73]:


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go 
from dash.dependencies import Input, Output

from gevent import pywsgi


# In[168]:


app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='Analisis de Trafico aereo durante el Covid-19'),
    html.Div(children='' 'Mapa de las zonas estudiadas'),
    dcc.Graph(
        id='mapa',
        figure={
            'data': mapa_ap
        }
    )
])


# In[170]:


if __name__=='__main__':
    app.run_server(debug=False)

