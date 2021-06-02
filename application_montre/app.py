import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas 
import os
import requests
import sqlite3
import plotly.graph_objects as go
import numpy as np
import datetime
from dash.dependencies import Input, Output
import json

def insert_data(db, insert_query, data):
    try:
        cursor.execute(insert_query, data)
        db.commit()
        print(cursor.rowcount)
        print("Insertion des données efféctuée")
    except:
        print("Une erreur est survenue lors de l'insertion")
        exit(1)


# insertion des données:
stations_data_insert='''INSERT INTO stations (Id_station, Name, latitude,longitude,location_date,location_success) VALUES(?,?,?,?,?,?)'''
measurements_data_insert ='''INSERT INTO measurements (Id_station,date_measurements, wind_heading,wind_speed_avg,wind_speed_min,wind_speed_max,status_date) VALUES(?,?,?,?,?,?,?)'''

db = sqlite3.connect('station_latest_measurements.db')      # connecter aux base de données
cursor = db.cursor()

nrow_measurements=cursor.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]        # trouver le numbres d'enregistrements dans le base de données
code_station=[410,307,113]
if nrow_measurements<12:
    for i in code_station:
        response = requests.get(f'http://api.pioupiou.fr/v1/live/{i}')
        response_info = response.json()
        data_station=[response_info['data']['id'],
                response_info['data']['meta']['name'],
                response_info['data']['location']['latitude'],
                response_info['data']['location']['longitude'],
                response_info['data']['location']['date'],
                response_info['data']['location']['success']]
        data_measurements=[response_info['data']['id'],
                response_info['data']['measurements']['date'],
                response_info['data']['measurements']['wind_heading'],
                response_info['data']['measurements']['wind_speed_avg'],
                response_info['data']['measurements']['wind_speed_max'],
                response_info['data']['measurements']['wind_speed_min'],
                response_info['data']['status']['date']]
        insert_data(db, measurements_data_insert, data_measurements)
elif nrow_measurements>=12:
    cursor.execute("DELETE FROM measurements WHERE Id_measurements BETWEEN  10 AND 12 ")     # delet les 3 encients mesuremnts
    cursor.execute("DELETE FROM sqlite_sequence WHERE seq BETWEEN  10 AND 12 ")
    db.commit()
    for i in code_station:
        response = requests.get(f'http://api.pioupiou.fr/v1/live/{i}')
        response_info = json.loads(response.text)
        data_station=[response_info['data']['id'],
                response_info['data']['meta']['name'],
                response_info['data']['location']['latitude'],
                response_info['data']['location']['longitude'],
                response_info['data']['location']['date'],
                response_info['data']['location']['success']]
        data_measurements=[response_info['data']['id'],
                response_info['data']['measurements']['date'],
                response_info['data']['measurements']['wind_heading'],
                response_info['data']['measurements']['wind_speed_avg'],
                response_info['data']['measurements']['wind_speed_max'],
                response_info['data']['measurements']['wind_speed_min'],
                response_info['data']['status']['date']]
        cursor.execute(measurements_data_insert,data_measurements)
        db.commit()
cursor.close()
db.close()


# visualisation des données:
db = sqlite3.connect('station_latest_measurements.db')      # connecter aux base de données
cursor = db.cursor()
df_station = pandas.read_sql_query("SELECT * FROM measurements ", db)
fig = px.line(df_station, x="date_measurements", y=["wind_speed_min","wind_speed_avg","wind_speed_max"], color="Id_station",
labels={"date_measurements": "Date measurements"},title=" les dernières mesures: wind speed (min-AVg-max Km/m)",hover_name="wind_speed_min",width=1600, height=700)
fig.update_traces(mode='markers+lines')
fig.update_layout(
    yaxis_title="Wind speed Km/h",
    legend_title="station code",
    margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor="LightSteelBlue",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="black"),
    legend=dict(
        title="code de station",
        traceorder="reversed",
        title_font_family="Times New Roman",
        font=dict(
            family="Balto",
            size=30,
            color="black"),       
        orientation="h",
        y=1, 
        yanchor="bottom",
        x=0.8,
        xanchor="left"))
cursor.close()
db.close()      
    



external_stylesheets = ['style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
    return html.Div([
        html.H1('The time is: ' + str(datetime.datetime.now())),
        html.Br(),
        dcc.Graph(
            id='live-update-graph',
            figure=fig
        )
        ])

app.layout = serve_layout


#@app.callback(Output('live-update-graph', 'figure'),
#              Input('interval-component', 'n_intervals'))








if __name__ == '__main__':
    app.run_server(debug=True)
