# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 16:05:45 2023

@author: Arpit Soni
"""

import json
import string
import random
import nltk
import numpy as num
from nltk.stem import WordNetLemmatizer
import tensorflow as tf 
from tensorflow.keras import Sequential 
from tensorflow.keras.layers import Dense, Dropout

nltk.download("punkt")
nltk.download("wordnet")
nltk.download('omw-1.4')

lm = WordNetLemmatizer() # for getting words
# lists
classes = []
newWords = []
documentX = []
documentY = []

data_file=open('intents.json').read()
intents_data=json.loads(data_file)

# Each intent is tokenized into words and the patterns and their associated tags are added to their respective lists.
for intent in intents_data["intents"]:
    for pattern in intent["patterns"]:
        tokens = nltk.word_tokenize(pattern)
        newWords.extend(tokens)
        documentX.append(pattern)
        documentY.append(intent["tag"])
    
    
    if intent["tag"] not in classes:# add unexisting tags to their respective classes
        classes.append(intent["tag"])

newWords = [lm.lemmatize(word.lower()) for word in newWords if word not in string.punctuation] # set words to lowercase if not in punctuation
newWords = sorted(set(newWords))# sorting words
classes = sorted(set(classes))# sorting classes

trainingData = [] # training list array
outEmpty = [0] * len(classes)
# BOW model
for idx, doc in enumerate(documentX):
    bagOfwords = []
    text = lm.lemmatize(doc.lower())
    for word in newWords:
        bagOfwords.append(1) if word in text else bagOfwords.append(0)
    
    outputRow = list(outEmpty)
    outputRow[classes.index(documentY[idx])] = 1
    trainingData.append([bagOfwords, outputRow])

random.shuffle(trainingData)
trainingData = num.array(trainingData, dtype=object)# coverting our data into an array afterv shuffling

x = num.array(list(trainingData[:, 0]))# first trainig phase
y = num.array(list(trainingData[:, 1]))# second training phase

# defining some parameters
iShape = (len(x[0]),)
oShape = len(y[0])

# the deep learning model
model = Sequential()
model.add(Dense(128, input_shape=iShape, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.3))
model.add(Dense(oShape, activation = "softmax"))
model_tf = tf.keras.optimizers.Adam(learning_rate=0.01, decay=1e-6)
model.compile(loss='categorical_crossentropy',
              optimizer=model_tf,
              metrics=["accuracy"])
print(model.summary())
model.fit(x, y, epochs=200, verbose=1)

def ourText(text): 
  newtkns = nltk.word_tokenize(text)
  newtkns = [lm.lemmatize(word) for word in newtkns]
  return newtkns

def wordBag(text, vocab): 
  newtkns = ourText(text)
  bagOwords = [0] * len(vocab)
  for w in newtkns: 
    for idx, word in enumerate(vocab):
      if word == w: 
        bagOwords[idx] = 1
  return num.array(bagOwords)

def pred_class(text, vocab, labels): 
  bagOwords = wordBag(text, vocab)
  ourResult = model.predict(num.array([bagOwords]))[0]
  newThresh = 0.2
  yp = [[idx, res] for idx, res in enumerate(ourResult) if res > newThresh]

  yp.sort(key=lambda x: x[1], reverse=True)
  newList = []
  for r in yp:
    newList.append(labels[r[0]])
  return newList

def getRes(firstlist, fJson): 
  tag = firstlist[0]
  listOfIntents = fJson["intents"]
  for i in listOfIntents: 
    if i["tag"] == tag:
      ourResult = random.choice(i["responses"])
      break
  return ourResult

while True:
    newMessage = input("Type in: ")
    intents = pred_class(newMessage, newWords, classes)
    ourResult = getRes(intents, intents_data)
    print("Bot: ", ourResult)