import pandas as pd
import os
from PyPDF2 import PdfReader
from pyparsing import Any, Literal
import re

# Define the path to your folder with PDF files
pdf_folder = "data/pdf_files"
csv_folder = "data/csv_files/csv"

def path_maker(file_name: Any , pdf_folder: Literal ):
    file_path = os.path.join(pdf_folder, file_name)
    return file_path

def extract_year_month(text):
    # List of month names and numbers
    maanden = {"januari": "01", "februari": "02", "maart": "03", "april": "04", "mei": "05", "juni": "06", "juli": "07", "augustus": "08", "september": "09", "oktober": "10", "november": "11", "december": "12",
               "jan": "01", "feb": "02", "mrt": "03", "apr": "04", "mei": "05", "jun": "06", "jul": "07", "aug": "08", "sept": "09", "okt": "10", "nov": "11", "dec": "12",
               "01": "01", "02": "02", "03": "03", "04": "04", "05": "05", "06": "06", "07": "07", "08": "08", "09": "09", "10": "10", "11": "11", "12": "12"}

    # Create a regular expression pattern that matches any of the month names or numbers
    month_pattern = re.compile("|".join(maanden), re.IGNORECASE)

    year_pattern = re.compile(r"(\d{4})")
    
    month_match = month_pattern.search(text)
    year_match = year_pattern.search(text)

    if month_match and year_match:
        month = month_match.group(0).lower()  # The month is the first group in the match
        year = year_match.group(1)    # The year is the first group in the match
        # Convert the month from a word to a number using the dictionary
        month_number = maanden.get(month)
        return year, month_number
    else:
        return None, None  # If no match is found, return None for both year and month


def convert(file):
    file_path = path_maker(file, pdf_folder)
    return exract_pdf_text(file_path, csv_folder)


def exract_pdf_text(file_path: Any , csv_folder: Any):
    df = pd.DataFrame(columns=['page_number', 'text'])
    page_nu = 0
    pdf = PdfReader(file_path)
    page_first = pdf.pages[0].extract_text()
    year, month = extract_year_month( page_first.replace('\n', ' '))

    for page in pdf.pages:
        page_nu += 1
        text = page.extract_text().replace('\n', ' ').replace('\r', ' ')
        dct = {'page_number': page_nu, 'text': text}
        df = pd.concat([df, pd.DataFrame({k:[v] for k,v in dct.items()})], ignore_index=True)
    
    csv_file = str(year) + '-' + str(month) + '-' + '01.csv'
    saveData(df, csv_file, csv_folder) 
    return csv_file

def saveData(df: pd.DataFrame , file_name: Any , file_path: Any):
    csv_file_name = os.path.basename(file_name).replace('.pdf', '.csv')
    csv_file_path = os.path.join(file_path, csv_file_name)
    df.to_csv(csv_file_path, index=False)




def getName(list_text1 , list_text2 ):
     # Convert the lists to sets
    set_text1 = set(list_text1)
    set_text2 = set(list_text2)
             
    temp = [x for x in set_text1 if x in set_text2 and  12 > len(x) > 10 and x == 'FysioPraxis'  ]
    for x in temp:
        if x == 'FysioPraxis':
            return x
        else:
            return 'unknown'
        


def pdf_detils_name(text):
    lowercase_list = text.lower().replace('\n' , ' ') .replace('•', ' ').replace('/', ' ')
    maanden = ["ebruar" , "maar",  "januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
    tm = lowercase_list.split()
    filtered_months = [w for w in tm if w in maanden]
    if not filtered_months:
        return find_and_replace_missing_months(tm, maanden)	
    else:
        filtered_months[0].replace('maar', 'maart').replace('ebruar', 'februari')
    tn = text.lower().replace('•', ',').replace('\n' , ',').split(',')
    pattern = r'\d+'
    filtered_number = [w for w in tn if w if 'nr' in w or 'nummer' in w ][0].strip().replace('nr', 'nr-').replace('nummer', 'nr-').replace(' ', '')
    
    filtered_jaar = [w for w in tn if w if 'jaar' in w or 'jaargang' in w and  re.search(pattern, w)][0].split()
    filtered_jaar = [d for d in filtered_jaar if re.search(pattern, d)][0]
    string = filtered_months[0].replace('maar', 'maart').replace('ebruar', 'februari') + '_' +  filtered_number + '_jaargang-' + filtered_jaar
    return string


def find_and_replace_missing_months(words, months):
    corrected_words = []
    for word in words:
        if len(word) > 1:
            if word[:-1] in months:
                corrected_words.append(word[:-1])
            elif word[1:] in months:
                corrected_words.append(word[1:])
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
    return corrected_words