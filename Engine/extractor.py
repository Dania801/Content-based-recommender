import sys
import pandas as pd
import numpy as np
import string
import matplotlib.pylab as plot
from preprocessor import preprocessDataset, plotStats, tokenizeClasses
from collections import Counter
import pickle



def computeLikeFreq(data):
    userLikes = data.UserLike
    plotStats(data, 'UserLike', 'user_likes_freq', False)
    userLikesDict = Counter(userLikes)
    return userLikesDict

def classesJointFreq(data):
    classes = data.Classes
    classesArr = []
    for i, entry in enumerate(classes):
        for j, token in enumerate(entry):
            classesArr.append(token)
    distinctClasses = list(set(classesArr))
    columns = ['Classes', 'UserLike']
    dataset = data[columns]
    classesDict = {}
    for j, token in enumerate(distinctClasses):
        tokenArray = np.array([0,0,0,0,0])
        for i, entry in dataset.iterrows():
            if token in entry['Classes'] and entry['UserLike'] == 1:
                tokenArray[0]+=1
            if token in entry['Classes'] and entry['UserLike'] == 2:
                tokenArray[1]+=1
            if token in entry['Classes'] and entry['UserLike'] == 3:
                tokenArray[2]+=1
            if token in entry['Classes'] and entry['UserLike'] == 4:
                tokenArray[3]+=1
            if token in entry['Classes'] and entry['UserLike'] == 5:
                tokenArray[4]+=1
        classesDict[token] = tokenArray
        tokenArray = np.array([0,0,0,0,0])
        print ('{0}- {1}'.format(j, token))
    with open('../Data/joint_freq.pickle', 'wb') as handle:
        pickle.dump(classesDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    

def dataWithConditionalProb(dataset):
    likesFreq = computeLikeFreq(dataset)
    with open('../Data/joint_freq.pickle', 'rb') as handle:
        jointFreq = pickle.load(handle)
    columns = ['Classes', 'UserLike']
    data = dataset[columns]
    conditionalFreqs = []
    entryProbability = 1
    for i, entry in data.iterrows():
        for token in entry['Classes']:
            prob = jointFreq[token][entry['UserLike']-1] / likesFreq[entry['UserLike']]
            entryProbability *= prob
        conditionalFreqs.append(entryProbability)
        entryProbability = 1
    dataset['ConditionalFreq'] = conditionalFreqs
    return dataset

def dataWithMeanConditionalProb(data):
    likesFreq = computeLikeFreq(data)
    with open('../Data/joint_freq.pickle', 'rb') as handle:
        jointFreq = pickle.load(handle)
    columns = ['Classes', 'ConditionalFreq', 'UserLike']
    dataset = data[columns]
    meanConditionalFreq = []
    probSum = 0
    for i, entry in dataset.iterrows():
        for token in entry['Classes']:
            prob = jointFreq[token][entry['UserLike']-1] / likesFreq[entry['UserLike']]
            probSum += prob
        meanConditionalFreq.append(probSum/len(entry['Classes']))
        probSum = 0
    data['MeanConditionalFreq'] = meanConditionalFreq
    return data


def addExtractedFeatures():
    data = preprocessDataset()
    data = dataWithConditionalProb(data)
    data = dataWithMeanConditionalProb(data)
    data.to_csv('../Data/all_features.csv')
    return data

# print (addExtractedFeatures())