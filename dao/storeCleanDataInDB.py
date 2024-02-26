import sqlite3
import os
import csv

# Directory path containing the CSV files
csv_directory = 'data/csv_files/cleaned_csv_files2/'

def store_clean_csv_files(filename):
    # Iterate over each file in the directory
    connection = sqlite3.connect("fysio.db")
    # for filename in os.listdir(csv_directory):
    #     if filename.endswith('.csv'):
    file_path = os.path.join(csv_directory, filename)
    date_str = filename.split('.')[0]  # Extract the date string from the filename

    # Extract the year, month, and day from the date string
    year, month, day = date_str.split('-')

    # Format the date as 'YYYY-MM-DD' for MySQL
    formatted_date = f"{year}-{month}-{day}"
    formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"


    # Prepare the SQL query to insert data
    insert_query = f"INSERT INTO articles (date_column, page_number, text) VALUES"

    # Open the CSV file with the correct encoding
    with open(file_path, 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row

        # Iterate over each row in the CSV file
        for row in reader:
            # Extract the row values and trim any leading/trailing whitespace
            page_number = row[0].strip()
            text = row[1].strip()

            # Execute the SQL query to insert the row into the table
            # cursor = db.connection.cursor()
            cursor = connection.cursor()

            query = insert_query + '(\'' + formatted_date + '\',\'' + page_number + '\',\'' +  text + '\')'
            cursor.execute(query)

            cursor.close()
            connection.commit()