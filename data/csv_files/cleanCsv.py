import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.snowball import DutchStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

# Provides a way of interacting with the operating system
import os



def clean_text(text_d):
    #check if the input is a string 
    if type(text_d) == str:
        # convert to lowercase
        text_d = text_d.lower()
        # remove email addresses
        text_d = re.sub(r'\S+@\S+(?:\.\S+)+', '', text_d)
        # remove http URLs
        text_d = re.sub(r'http\S+', '', text_d)
        # remove www URLs
        text_d = re.sub(r'www.\S+', '', text_d)
        # remove literral character: numbers/punctuation/special characters
        text_d = re.sub(r'[^a-zA-Z0-9\s]', '', text_d)
        text_d = re.sub(r'\w*\d\w*', '', text_d)

        # remove leading and trailing whitespace
        text_d = text_d.strip()
        # remove consecutive whitespace (tabs/newlines)
        text_d = re.sub(r'\s+', ' ', text_d) 
        
        # allow to apply techniques/perf
        words = word_tokenize(text_d)
        found_stopwords = ['fysiopraxis', 'fysio', 'praxis', 'fysiotherapie', 'therapie', 'fysiotherapeut', 'therapeut', 'patient', 
                           'jar', 'jaargang', 'januari' ,'februari' ,'maart' ,'april' ,'mei' , 'juni' ,
                           'juli' ,'augustus' ,'september' ,'oktober' ,'november' ,'december', 
                           'nederland', 'artikel', 'email', ]
        words = [word for word in words if word not in found_stopwords]
        # remove stopwords
        dutch_stopwords = set(stopwords.words('dutch'))
        words = [word for word in words if word not in dutch_stopwords]
        # apply both stemming and lemmatization using a lambda function
        stemmer = DutchStemmer()
        lemmatizer = WordNetLemmatizer()
        # map() applies lambda() to each word and returns a new sequence
        # lambda() takes a word and applies stemm&lemm methods [lambda arg: exprss]
        words = map(lambda word: stemmer.stem(lemmatizer.lemmatize(word)), words)
        # convert the map objct to a list
        words = list(words)
        # check if words is not empty
        text_d = ' '.join(words)
        if not text_d or len(text_d) < 1:
            text_d = "N"
    else:
        text_d = "N"        

    return text_d


# Set the directory path
csv_folder = "data/csv_files/csv/"
clean_folder ="data/csv_files/cleaned_csv_files2"
# Iterate through all files in the directory 
# Perfom text cleaning on any CSV files found
def clean_csv_files(file):
    # Load the CSV file
    # Joins dir path with file var to create new path that points to CSV in the dir
    file_path = os.path.join(csv_folder, file)
    df = pd.read_csv(file_path)

    df_ready = pd.DataFrame(columns=['page_number', 'text'])
    # Explode the text data
    for index, row in df.iterrows():
        # tokenize the string into individuals words
        page_number = int(row['page_number'])
        text = sent_tokenize(row['text'])
        # text = row['text'].split(' ')
        for elt in text:
            elt = elt[:100]
            df_ready.loc[len(df_ready.index)] = [page_number, elt]
    df_ready = df
    # Clean the 'text_d' column using the function
    df_ready["text"] = df_ready["text"].apply(clean_text)
    df_ready = df_ready[df_ready['text'] != 'N']
    df_ready = df_ready[df_ready['page_number'] > 5]

    # Save the new df to a new CSV file with the same name as the original file with _cleaned add
    output_file = file.replace(".csv", "_cleaned.csv")
    output_file_path = os.path.join(clean_folder , file)
    df_ready.to_csv(output_file_path, index=False)
