import pandas as pd
import sqlite3


def connect_to_db():
    connection = sqlite3.connect("fysio.db")
    cursor = connection.cursor()
    return connection

def get_results_as_dataframe(results, headers):
    data = []
    for row in results:
        data.append(dict(zip(headers, row)))
    df = pd.DataFrame(data)
    return df


def get_min_year():
    connection = connect_to_db()
    query = """
    SELECT MIN(YEAR(date_column)) FROM articles;
    """
    cursor = connection.cursor()
    results = cursor.execute(query)
    min_year = results[0][0]
    return min_year

def get_max_year():
    connection = connect_to_db()
    query = """
    SELECT MAX(YEAR(date_column)) FROM articles;
    """
    max_year = results[0][0]
    cursor = connection.cursor()
    results = cursor.execute(query)
    return max_year

def perform_query(first_year_select=None, last_year_select=None, word_select=""):
    connection = connect_to_db()
    select_query = """
    SELECT date_column, page_number, text FROM articles
    WHERE 1=1
    """
   
    if first_year_select and last_year_select:
        select_query += f" AND YEAR(date_column) BETWEEN {first_year_select} AND {last_year_select}"
    elif first_year_select:
        select_query += f" AND YEAR(date_column) > {first_year_select}"
    elif last_year_select:
        select_query += f" AND YEAR(date_column) < {last_year_select}"
     
    if word_select:
        select_query += f" AND text LIKE '%{word_select}%'"
    headers = ["date", "page_number", "text"]
    cursor = connection.cursor()
    results = cursor.execute(select_query)
    df = get_results_as_dataframe(results, headers)
    return df

def delete_from_db():
    connection = connect_to_db()
    cursor = connection.cursor()
    query = "DELETE FROM articles"
    cursor.execute(query)
    connection.commit()