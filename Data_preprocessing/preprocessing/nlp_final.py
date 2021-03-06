# -*- coding: utf-8 -*-
"""NLP_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oyNaAOIUSJ4ZBL1K1ngw8_9boOr_cY-w
"""

!pip install transformers

!nvidia-smi

import torch
from transformers.file_utils import is_tf_available, is_torch_available, is_torch_tpu_available
from transformers import BertTokenizerFast, BertForSequenceClassification
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
import re
import nltk
from sklearn.preprocessing import LabelBinarizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
import string
import gensim
import gensim.downloader as gensim_api
from sklearn.model_selection import train_test_split

"""# Import data"""

data = pd.read_csv("review_cleaned.csv")

"""# Data overview"""

data.head(5)

data.shape

for col in data:
  print(len(data[col].unique()))

main_data = data[["text", "useful", "funny", "cool", "sum_ufc", "useful_label", "funny_label", "cool_label"]]

## if useful > 10:
##     useful_label =1
## else:
##     useful_label = 0
main_data.head()

## check missing values 
main_data.isna().sum()

## check outliers
sns.boxplot(x=main_data['useful'])

sns.boxplot(x=main_data['funny'])

sns.boxplot(x=main_data['cool'])

Q1 = main_data.useful.quantile(0.25)
Q3 = main_data.useful.quantile(0.75)
IQR = Q3 - Q1
print("IQR in useful column is ",IQR)
print("Number of outliers in useful column is ", main_data[(main_data.useful < (Q1 - 1.5 * IQR)) |(main_data.useful > (Q3 + 1.5 * IQR))].shape[0])

## make outliers to low or top range
main_data.loc[main_data["useful"] < (Q1 - 1.5 * IQR), "useful"] = (Q1 - 1.5 * IQR)
main_data.loc[main_data["useful"] > (Q3 + 1.5 * IQR), "useful"] = (Q3 + 1.5 * IQR)

Q1 = main_data.funny.quantile(0.25)
Q3 = main_data.funny.quantile(0.75)
IQR = Q3 - Q1
print("IQR in funny column is ",IQR)
print("Number of outliers in funny column is ", main_data[(main_data.funny < (Q1 - 1.5 * IQR)) |(main_data.funny > (Q3 + 1.5 * IQR))].shape[0])

## make outliers to low or top range
main_data.loc[main_data["funny"] < (Q1 - 1.5 * IQR), "funny"] = (Q1 - 1.5 * IQR)
main_data.loc[main_data["funny"] > (Q3 + 1.5 * IQR), "funny"] = (Q3 + 1.5 * IQR)

Q1 = main_data.cool.quantile(0.25)
Q3 = main_data.cool.quantile(0.75)
IQR = Q3 - Q1
print("IQR in cool column is ",IQR)
print("Number of outliers in cool column is ", main_data[(main_data.cool < (Q1 - 1.5 * IQR)) |(main_data.cool > (Q3 + 1.5 * IQR))].shape[0])

## make outliers to low or top range
main_data.loc[main_data["cool"] < (Q1 - 1.5 * IQR), "cool"] = (Q1 - 1.5 * IQR)
main_data.loc[main_data["cool"] > (Q3 + 1.5 * IQR), "cool"] = (Q3 + 1.5 * IQR)

## check outliers after cleaning
sns.boxplot(x=main_data['useful'])

## check outliers after cleaning
sns.boxplot(x=main_data['funny'])

## check outliers after cleaning
sns.boxplot(x=main_data['cool'])

"""# EDA"""

sns.countplot(
    x = "useful_label",
    data = main_data,
    order = [0,1]
)
plt.xlabel("useful_label")
plt.ylabel("count")
plt.title("Review Distribution Based on useful or not")

sns.countplot(
    x = "funny_label",
    data = main_data,
    order = [0,1]
)
plt.xlabel("funny_label")
plt.ylabel("count")
plt.title("Review Distribution Based on funny or not")

sns.countplot(
    x = "cool_label",
    data = main_data,
    order = [0,1]
)
plt.xlabel("funny_label")
plt.ylabel("count")
plt.title("Review Distribution Based on cool or not")

"""## check count distribution for each kind of reviews"""

sns.displot(main_data, x="useful", kde = True)

sns.displot(main_data, x="funny", kde = True)

sns.displot(main_data, x="cool", kde = True)

"""# Data preprocessing. """

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
stopwords = nltk.corpus.stopwords.words("english")
lemmatizer = WordNetLemmatizer()
def clean_text(texts):
  cleaned_text = texts.copy()
  for index, text in enumerate(texts):
    text = re.sub(r'@[\w]*','',text)
    text = re.sub(r'http[^ ]*','',text)
    text = re.sub(r'pic.[^ ]*','',text)
    text = re.sub(r'[^A-Za-z#]',' ',text)
    
    #lowercase
    text = text.lower()
    #tokenization
    text = nltk.word_tokenize(text)
    #remove stopwords
    text = [word for word in text if word not in stopwords]
    # lemmatizing
    text = [lemmatizer.lemmatize(word) for word in text]
    text = " ".join(text)
    cleaned_text[index] = text
  return cleaned_text
main_data["text"] = clean_text(main_data["text"])

"""# Data split"""

# randomly select 80% data as training set, 20% as testing data
training_set ,testing_set = train_test_split(main_data,test_size=0.2)

"""#Tfidf"""

tfidf = TfidfVectorizer(max_features = 3000)
training_set_tfidf = tfidf.fit_transform(training_set['text'].values.tolist())
testing_set_tfidf = tfidf.transform(testing_set['text'].values.tolist())

"""# Word2vec"""

embeddings = gensim_api.load("word2vec-google-news-300")

"""## training data embedding"""

docs_vectors = pd.DataFrame()
stopwords = nltk.corpus.stopwords.words("english")
for doc in training_set["text"]:
  temp = pd.DataFrame()
  for word in doc.split(" "):
    if word not in stopwords:
      try:
        word_vec = embeddings[word]
        temp = temp.append(pd.Series(word_vec), ignore_index = True)
      except:
        pass
  doc_vector = temp.mean()
  docs_vectors = docs_vectors.append(doc_vector, ignore_index = True)
docs_vectors.shape

pd.isnull(docs_vectors).sum().sum()
docs_vectors = docs_vectors.dropna()
training_set_embedding = docs_vectors

"""## testing data embedding"""

docs_vectors = pd.DataFrame()
stopwords = nltk.corpus.stopwords.words("english")
for doc in testing_set["text"]:
  temp = pd.DataFrame()
  for word in doc.split(" "):
    if word not in stopwords:
      try:
        word_vec = embeddings[word]
        temp = temp.append(pd.Series(word_vec), ignore_index = True)
      except:
        pass
  doc_vector = temp.mean()
  docs_vectors = docs_vectors.append(doc_vector, ignore_index = True)
docs_vectors.shape

pd.isnull(docs_vectors).sum().sum()
docs_vectors = docs_vectors.dropna()
testing_set_embedding = docs_vectors

np.save('main_data.npy', main_data)
np.save('training_set.npy', training_set)
np.save('testing_set.npy', testing_set)
np.save('training_set_tfidf.npy', training_set_tfidf)
np.save('testing_set_tfidf.npy', testing_set_tfidf)
np.save('training_set_embedding.npy', training_set_embedding)
np.save('testing_set_embedding.npy', testing_set_embedding)

## load npy data
## for example, main_data = np.load("main_data.npy", allow_pickle= True)
## Especiall, column names of main_data is ["text", "useful", "funny", "cool", "sum_ufc", "useful_label", "funny_label", "cool_label"]