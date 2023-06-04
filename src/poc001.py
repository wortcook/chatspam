# Gerekli kütüphaneleri projemize dahil ediyoruz.
import pandas as pd
import re
import numpy as np
import math

# Class oranlarımızı hesaplıyoruz
# ÖRN N = 4 Yes = 3 No = 1
# P(Yes) = 3/4, P(No) = 1/4
def labelPredictions(Y):
    # Key-value şeklinde tanımlamak için boş bir list tanımlıyoruz
    labels = {}
    
    # Toplam example sayımızı öğreniyoruz
    total = len(Y)
    
    # Her sınıf stününü gezip sayılarını alıyoruz
    for label in Y:            
        if label in labels:
            labels[label] += 1
        else:
            labels[label] = 1
    
    # Her label'in oranını hesaplıyoruz.
    for i in labels:
        val = labels[i]

        labels[i] = val / total;

    return labels

# Parametre olarak alınınan string cümlenin içindeki kelimelerin
# harflerini küçülterek alıyoruz.
def split_words(sentence):
    words = re.sub("[^\w]", " ",  sentence).split()
    words = list(map(lambda x:x.lower(),words))

    return words

# Parametre olarak alınan cümlenin içindeki kelimeri
# benzersiz bir şekilde alıp yine aynı kelimenin
# cümle içinde kaç defa kullanıldığı bilgisi ile birlikte alıyoruz.
def split_words_unique(sentence):
    words = split_words(sentence)

    _words = {}

    for w in words:
        if w not in _words:
            _words[w] = 1
        else:
            _words[w] += 1

    return _words

# Vocabulary değerini hesaplıyoruz
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

# Kelime sayısını hesaplıyoruz
def determineWordsCount(X):
    count = 0

    for sentence in X:
        words = split_words(sentence)

        for w in words:
            count += 1

    return count

# Sınıf içindeki kelime sayısını alıyoruz
# ÖRN: P(Chinese|Yes) = 5 , P(Tokyo|Yes) = 0
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

# Belirli bir sınıfa ait data frame alıyoruz.
# ÖRN: Sadece 'Yes' sınıfına ait text ve label data frame dönecektir.
def dataFrameForClass(payload,c):
    return payload['X'].loc[payload['X'][payload['f_label']] == c]

# Spesifik olarak belirlnen sınıfa ait kelime sayısın verir.
def getWordsCount(payload,c):
    df = dataFrameForClass(payload,c)

    return determineWordsCount(df[payload['f_text']])

# Mödelimizi ayarlıyoruz ve gerekli parametreleri bir
# list olarak geri alıyoruz
def fit(X,Y,f_text = 'text',f_label = 'label'):

    payload = {};
    
    # Toplam sınıf sayımızı alıyoruz
    payload['classes'] = set(Y)
    # Class oranlarımızı alıyoruz
    # P(Sport) = 2 / 5 P(Not Sport) = 3 / 5
    payload['predictions'] = labelPredictions(Y)
    # Vocabulary değerini alıyoruz
    payload['vocabulary'] = calculateVocabulary(X[f_text])
    
    # Diğer veri modellerini kullanmak için
    # veri listimize kaydediyoruz
    payload['X'] = X
    payload['Y'] = Y
    payload['f_text'] = f_text
    payload['f_label'] = f_label

    return payload

# Tahminleme işlemlerini gerçekleştiriyoruz
def predict(payload,text):
    # Cümle içindeki benzersiz kelimeleri alıyoruz
    words = split_words_unique(text)
    
    m_estimate = {}
    
    # M-Estimate hesaplaması yapıyoruz
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
    
    # Hesaplanan herbir class değerlerine göre hesaplama yapıp bunu
    # 'tags' objesine aktarıyoruz
    # ÖRN: P(d|Yes) = 0,0003 --- P(d|No) = 0,0001
    for c in payload['predictions']:
        p = payload['predictions'][c]

        m = np.prod(list(m_estimate[c].values()))

        final = m * p

        tags[c] = final
        
    print(tags)
    
        
    # Son olarak bulunan etiketlerin arasında
    # en yüksek değere sahip etiketi geriye dönderiyoruz.
    # Bu şekilde label değerimiz ortaya çıkmış oluyor
    return max(tags,key= lambda x: tags[x])
            

df = pd.read_csv('../data/spam_ham_prompts.csv')

print(df)

payload = fit(df,df['label'])

label = predict(payload,"I am going hiking in the morning, what would you recommend I bring?")

print(label)

df = pd.read_csv('../data/test_prompts.csv')

idx = 0

for text in df['text']:
    label = predict(payload,text)

    print("=====================================")
    print(idx)
    print(text)
    print(df['label'][idx])
    print(label)

    idx += 1


# payload = fit(df,df['label'])

# label = predict(payload,"Chinese Chinese Chinese Tokyo Japan")

# print(label)