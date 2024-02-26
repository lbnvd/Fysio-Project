import os
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster

#to bypass limits when trying to plot the tree
import sys
sys.setrecursionlimit(100000)
def text_from_csv():
    #getting the path of all the csv files and creating variables for later
    folder = "data/csv_files/csv"
    csv_Files = [f.path for f in os.scandir(folder) if f.is_dir() or f.is_file()]
    list = []
    L = []

    #we fit transform for all the csv to adapt it to each of them
    for csv_path in csv_Files:
        
        df = pd.read_csv(csv_path, header=None , names=["year","page","text"])
        list_row = df['text'].values.tolist()
        
        date = df["year"]
        dates = date[1]
        L.append([dates,list_row])

    
    #we created a matrix with the date and text on each row, we sort it by date(years)
    L.sort()
    previous_date = 0
    #concatenate the text by years
    for date_text in L:
        current_date = date_text[0]
        if current_date == previous_date:
            list[len(list)-1] = list[len(list)-1] + date_text[1]
        else:
            list.append(date_text[1])
        previous_date = date_text[0]
    #return the list of concatenated text by years

    return list

clean_folder = "data/csv_files/cleaned_csv_files2/"


def top_words(file, range_Top_Words,number_of_clust):
    #The parameters are very important to filter out words 
    #(max_df=maximu proportion of apearence|min_df=minimum number of "lines" to appear into)
    vectorizer = TfidfVectorizer(max_df=0.5,min_df=5)
    results = []
    df = pd.read_csv(clean_folder + file)
    #.values.astype('U')
    tfidf_matrix = vectorizer.fit_transform(df['text'])
    df_dtm = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    ##Hierarchy clustering parts (ML)

    clust = linkage(df_dtm, method="ward", metric="euclidean")
    clustering = fcluster(clust, number_of_clust, 'maxclust')
    
    df_dtm['_cluster_'] = clustering
    #print(df_dtm['_cluster_'].value_counts())
    df_dtm.index.name = '_article_'
    #capture the cluster info into the database and rank the number of words
    df_word_count = df_dtm.groupby('_cluster_').sum().reset_index().melt(id_vars=['_cluster_'], var_name='_word_', value_name='_count_')

    for k in range(1,number_of_clust+1):
        words_1 = df_word_count[df_word_count._cluster_==k].sort_values(by=['_count_'], ascending=False).head(range_Top_Words)
        results.append(words_1)
    return results
