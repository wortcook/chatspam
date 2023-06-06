# THIS CODE COPIED FROM "SOMEWHERE" I CAN'T REMEMBER FROM WHERE
# NOW, SO PLEASE CONTACT ME IF YOU ARE THE OWNER OF THIS CODE OR
# CAN POINT ME TO THE ORIGINAL SOURCE SO I CAN ATTRIBUTE IT PROPERLY.
#
# COMMENTS AUTO-TRANSLATED FROM TURKISH USING CHATGPT
#
# We include the necessary libraries in our project.
import pandas as pd
import re
import numpy as np
import math

# We calculate our class ratios.
# EX: N = 4 Yes = 3 No = 1
# P(Yes) = 3/4, P(No) = 1/4
def labelPredictions(Y):
    # We define an empty dictionary to hold our key-value pairs.
    labels = {}
    
    # We find out our total example count.
    total = len(Y)
    
    # We go through each class column and get their counts.
    for label in Y:            
        if label in labels:
            labels[label] += 1
        else:
            labels[label] = 1
    
    # We calculate the ratio of each label.
    for i in labels:
        val = labels[i]

        labels[i] = val / total;

    return labels

# We get the words in the given string sentence,
# changing the letters to lowercase.
def split_words(sentence):
    words = re.sub("[^\w]", " ",  sentence).split()
    words = list(map(lambda x:x.lower(),words))

    return words

# We get the words in the given sentence in a unique way,
# along with how many times the same word was used in the sentence.
def split_words_unique(sentence):
    words = split_words(sentence)

    _words = {}

    for w in words:
        if w not in _words:
            _words[w] = 1
        else:
            _words[w] += 1

    return _words

# We calculate the Vocabulary value.
def calculateVocabulary(X):
    amount = 0
    stack = []

    for sentence in X:
        words = split_words(sentence)
        

        for w in words:
            if w not in stack:
                stack.append(w)
                amount += 1

    return amount

# We calculate the word count.
def determineWordsCount(X):
    count = 0

    for sentence in X:
        words = split_words(sentence)

        for w in words:
            count += 1

    return count

# We get the word count in a specific class.
# EX: P(Chinese|Yes) = 5 , P(Tokyo|Yes) = 0
def getWordCountInClass(payload,word,c):
    df = dataFrameForClass(payload,c)

    sentences = df[payload['f_text']]

    count = 0

    for sentence in sentences:
        words = split_words(sentence)

        for w in words:
            if w == word:
                count += 1

    return count

# We get the data frame for a specific class.
# EX: It will return a data frame with only the text and label for the 'Yes' class.
def dataFrameForClass(payload,c):
    return payload['X'].loc[payload['X'][payload['f_label']] == c]

# It gives the word count for a specific class.
def getWordsCount(payload,c):
    df = dataFrameForClass(payload,c)

    return determineWordsCount(df[payload['f_text']])

# We set our model and return the necessary parameters as a list.
def fit(X,Y,f_text = 'text',f_label = 'label'):

    payload = {};
    
    # We get our total class count.
    payload['classes'] = set(Y)
    # We get our class ratios.
    # P(Sport) = 2 / 5 P(Not Sport) = 3 / 5
    payload['predictions'] = labelPredictions(Y)
    # We get the Vocabulary value.
    payload['vocabulary'] = calculateVocabulary(X[f_text])
    
    # We save other data models to our data list for future use.
    payload['X'] = X
    payload['Y'] = Y
    payload['f_text'] = f_text
    payload['f_label'] = f_label

    return payload

# We perform the prediction operations.
def predict(payload,text):
    # We get the unique words in the sentence.
    words = split_words_unique(text)
    
    m_estimate = {}
    
    # We calculate the M-Estimate.
    for c in payload['classes']:
        n = getWordsCount(payload,c)

        m_estimate[c] = {}

        for word in words:
            force = words[word]

            n_c = getWordCountInClass(payload,word,c)

            # P(d|c) = (n_c + 1) / (n + vocabulary)
            _estimate = (n_c + 1) / (n + payload['vocabulary'])
            
            _estimate = math.pow(_estimate,force)

            m_estimate[c][word] = _estimate

    tags = {}
    
    # We calculate and transfer to the 'tags' object for each calculated class value.
    # EX: P(d|Yes) = 0,0003 --- P(d|No) = 0,0001
    for c in payload['predictions']:
        p = payload['predictions'][c]

        m = np.prod(list(m_estimate[c].values()))

        final = m * p

        tags[c] = final
        
    print(tags)
    
        
    # Finally, we return the label with the highest value among the found tags.
    # In this way, our label value is revealed.
    return max(tags,key= lambda x: tags[x])
