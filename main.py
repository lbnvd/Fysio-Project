import dash
from dash import html, dcc, Input, Output
import flask
from flask import render_template, redirect
import json
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import matplotlib.pyplot as plt
from threading import Thread
from wordcloud import WordCloud

import nltk

from dao.createTables import create_tables
create_tables()

from dao.storeCleanDataInDB import store_clean_csv_files
from dao.fct_queries import perform_query, delete_from_db
from models.extract_text.pdfToCsv import convert
from data.csv_files.cleanCsv import clean_csv_files
from models.machine_learning import top_words


hostname = '0.0.0.0'
port = 8050

result_folder = "data/result_files/"
pdf_folder = "data/pdf_files/"
csv_folder = "data/csv_files/csv/"
clean_folder = "data/csv_files/cleaned_csv_files2/"
pictures_folder = "assets/pictures/"

import os

for path in [pdf_folder, csv_folder, clean_folder, pictures_folder, result_folder]:
    if not os.path.exists(path):
        os.makedirs(path)

def show_files(folder):
    return [{'label': x, 'value': x} for x in os.listdir(folder)]

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

global status
status = '0 not started'

flask_app = flask.Flask(__name__, template_folder='pages', static_folder='assets')
dash_app = dash.Dash(__name__, server=flask_app, title='Results', routes_pathname_prefix='/visualisation/', assets_url_path='/')
dash_app._favicon = ("assets/favicon.ico")

def make_layout():
    return html.Div(id="_dash-app-content", children=[
    html.Div(id="dash_container", children=[
        html.Div(id="links", children=[
            html.A(href="/", children=html.Img(src=r'assets/favicon.ico')),
            html.A(href="/", children=html.Div("Home", className="dash_link btn btn-secondary")),
            html.A(href="/files", children=html.Div("PDF", className="dash_link btn btn-secondary")),
            html.A(href="/visualisation", children=html.Div("Results", className="dash_link btn btn-secondary")),
        ]),
        html.Iframe(src="/progress"),
    ]),
    html.Div(id="_pages_content", children=[
        html.Div(className="page_title", children=[
            html.H3("Results"),
        ]),
        html.Div(id="visualization_container", children=[
            html.Div(className="visualization_containers", children=[
                html.H4("features cleaning"),
                html.Div(id="plot_models_wordcloud", children=[
                    dcc.Dropdown(id="wordcloud_selector", options=show_files(pictures_folder)),
                ]),
                html.Div(id="plot_models_wordcloud_container")
            ]),
            html.Div(className="visualization_containers", children=[
                html.H4("analysis"),
                html.Div(id="plot_models_analysis", children=[
                    dcc.Dropdown(id="analysis_selector", options=show_files(result_folder))
                ]),
                html.Div(id="plot_models_analysis_container")
            ]),
            html.Div(className="visualization_containers", children=[
                html.H4("clusters in time"),
                html.Div(id="plot_models_time_clusters", children=[
                    dcc.Input(id="time_clusters_input", placeholder='Enter a cluster name', type='text',value=''),
            ]),
                html.Div(id="plot_models_time_clusters_container", children=[]),
            ]),
        ])
    ])
])

dash_app.layout = make_layout
         
@dash_app.callback(Output("plot_models_wordcloud_container", "children"), 
                    Input("wordcloud_selector", "value"))
def get_wordcloud(path):
    if path == None:
        return ''
    fig = px.imshow(np.array(Image.open(pictures_folder + path)))
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    return dcc.Graph(figure=fig)

@dash_app.callback(Output("plot_models_analysis_container", "children"), Input("analysis_selector", "value"))
def get_analysis(path):
    if path == None:
        return ''
    df_preclean = pd.read_csv(result_folder + path, nrows=50)
    fig = px.pie(df_preclean, names='_word_', values='_count_',hole=0.3)

    return dcc.Graph(figure=fig)

@dash_app.callback(Output("plot_models_time_clusters_container", "children"),
                   Input("time_clusters_input", "value"))
def show_clusters_dates(cluster_names):
    if cluster_names == None or cluster_names == '':
        return ''
    clusters = cluster_names.split(',')
    for cluster in clusters:
        if cluster == '': cluster = ' '
    df_ready = pd.DataFrame()
    for file in os.listdir(clean_folder):
        df_temp = pd.read_csv(clean_folder + file)
        df_temp['date'] = file[:10]
        df_temp['date'] = pd.to_datetime(df_temp['date'], format='%Y-%m-%d')
        df_temp['clusters'] = df_temp['text'].str.findall('|'.join(clusters)).apply(set).str.join(', ')
        df_ready = pd.concat([df_ready, df_temp], ignore_index=True)
    df_ready = df_ready[df_ready['text'].str.contains(('|'.join(clusters)))]
    df_ready['text'] = df_ready['text'].apply(lambda x: x[:25] + '<br>' + x[25:50] + '<br>' + x[50:75] + '<br>' + x[75:100] + '<br>' + x[100:] if len(x) > 100 else x[:25] + '<br>' + x[25:] if len(x) > 25 else x)
    df_ready.index = range(len(df_ready.index))
    fig = px.scatter(df_ready, x='date', color='clusters', custom_data=['page_number', 'text'])
    fig.update_traces(
        hovertemplate="<br>".join([
            "date: %{x}",
            "page_number: %{customdata[0]}",
            "text: %{customdata[1]}"
        ])
    )
    fig.update_traces(marker=dict(size=3),
                    selector=dict(mode='markers'))
    

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=6,
    ))
    return dcc.Graph(figure=fig)
                     
                     
def make_wordcloud():
    # wordcloud after data cleaning
    text_full_postclean = ''
    for file in os.scandir(clean_folder):
        df_postclean = pd.read_csv(file)
        text_postclean = ''
        for row_text in df_postclean['text']:
            text_postclean = text_postclean + ' ' + str(row_text)
        wordcloud_postclean = WordCloud(width=400,height=320,background_color='white',max_font_size=40).generate(text_postclean)
        plt.imshow(wordcloud_postclean, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad = 0)
        # df_postclean_full.append(df_postclean, ignore_index=True)
        plt.savefig(pictures_folder + str(file.name) + '.png')
        text_full_postclean = text_full_postclean + str(text_postclean)
    wordcloud_postclean = WordCloud(width=400,height=320,background_color='white',max_font_size=40).generate(text_full_postclean)
    plt.figure()
    plt.imshow(wordcloud_postclean, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad = 0)
    plt.savefig(pictures_folder + 'data_selection.png')


def start_extracting():
    global status
    status = '2 starting data extraction'
    files = os.listdir(pdf_folder)
    i = 1
    length = len(files)
    for file in files:
        convert(file)
        i+=1
        status = '2 starting data extraction' + '(' + str(i) +'/' + str(length) + ')'
    start_cleaning()

def start_cleaning():
    global status
    status = '4 starting data cleaning'
    files = os.listdir(csv_folder)
    i = 1
    length = len(files)
    for file in files:
        clean_csv_files(file)
        status = '4 starting data cleaning' + '(' + str(i) +'/' + str(length) + ')'
    status = '6 data cleaned'


    # make the wordclouds
    make_wordcloud()

    status = '8 starting model\'s training'
    length = len(os.listdir(clean_folder))
    i=1
    for file in os.listdir(clean_folder):
        status = '8 processing file: ' + file +  '(' + str(i) +'/' + str(length) + ')'
        i+=1
        results = top_words(file, 3, 3)
        clusters = pd.DataFrame()
        for cluster in results:
            clusters = pd.concat([clusters, cluster])
        clusters.to_csv(result_folder + file[:10] + '_results.csv', index=True)
    status = '0 finished'

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/files', methods=['GET','POST'])
def get_files():
    feedback = ''
    if flask.request.method == "POST":
        files =  flask.request.files.getlist("file")
        i = 0
        for file in files:
            if file.filename == '' or not file.filename.endswith(".pdf"):
                return render_template('files.html', data=["select a pdf file"])
            i+=1
            filename = file.filename
            file.save(os.path.join(pdf_folder + filename))
        thread_extracting = Thread(target=start_extracting)
        thread_extracting.start()
        feedback = str(i) + ' file(s) uploaded'
    files = []
    for file in os.listdir(pdf_folder):
          files.append(file)
    if files == []: files = ["No files uploaded."]
    return render_template('files.html', data=files, feedback=feedback)

@flask_app.route('/file', methods=['POST'])
def remove_files():
    if flask.request.method == "POST":
        global status
        file = flask.request.form['file']
        if file == 'store to database':
            delete_from_db()
            i = 1
            length = len(os.listdir(clean_folder))
            for file in os.listdir(clean_folder):
                i += 1
                status = '0 storing file ' + '(' + str(i) + '/' + str(length) + ')'
                store_clean_csv_files(file)
            status = '0 files stored in database'
        elif file == 'import from database':
            status = '0 importing from database'
            # store clean csv files from database
            df = perform_query(first_year_select=None, last_year_select=None, word_select="")
            if len(df) > 0:
                date_tmp = df.iloc[0]['date']
                df_rdy = pd.DataFrame(columns=df.columns)
                for i, value in df.iterrows():
                    if value['date'] != date_tmp:
                        df_rdy.to_csv(clean_folder + date_tmp + '.csv', index=False)
                        date_tmp = value['date']
                        df_rdy = pd.DataFrame(columns=df.columns)
                    else:
                        df_tmp = pd.DataFrame([[value['date'], value['page_number'], value['text']]], columns=['date', 'page_number', 'text'])
                        df_rdy = pd.concat([df_rdy, df_tmp], ignore_index=True)
                df_rdy = pd.concat([df_rdy, df_tmp], ignore_index=True)
                df_rdy.to_csv(clean_folder + date_tmp + '.csv', index=False)
                start_cleaning()
                status = '0 files imported from database'
            else:
                status = '0 database empty'
        elif file == 'remove all files':
            status = '0 system cleaned'
            for path in [pdf_folder, csv_folder, clean_folder, pictures_folder, result_folder]:
                for filename in os.listdir(path):
                    os.remove(path + '/' + filename)
        else:
            file = file[7:]
            os.remove(os.path.join(pdf_folder + file))
        return redirect('/files')

@flask_app.route('/visualisation')
def get_dash():
    return dash_app.index()


@flask_app.route('/progress', methods=['GET'])
def get_status():
  return render_template('status.html')

@flask_app.route('/status', methods=['GET'])
def set_status():
  statusList = {'status':status}
  return json.dumps(statusList)


if __name__ == '__main__':
	flask_app.run(debug=False, host=hostname, port=port)