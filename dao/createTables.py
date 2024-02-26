import sqlite3

def create_tables():
  connection = sqlite3.connect("fysio.db")
  cursor = connection.cursor()
  create_articles_table_query = "CREATE TABLE IF NOT EXISTS articles (date_column TEXT, page_number INTEGER, text BLOB);"
  cursor.execute(create_articles_table_query)
