#!/usr/bin/env python2
# -*- coding: utf-8 -*-



import numpy as np
import re

def generate_deletes(string,max_distance):
    deletes = []
    queue = [string]
    for d in range(max_distance):
        temp_queue = []
        for word in queue:
            if len(word)>1:
                for c in range(len(word)):  # character index
                    word_minus_c = word[:c] + word[c+1:]
                    if word_minus_c not in deletes:
                        deletes.append(word_minus_c)
                    if word_minus_c not in temp_queue:
                        temp_queue.append(word_minus_c)
        queue = temp_queue
        
    return deletes

def levenshtein(string1, string2):
    
    if len(string1) < len(string2): return levenshtein(string2, string1)
    if len(string2) == 0:return len(string1)

    arr_string1 = np.array(list(string1))
    arr_string2 = np.array(list(string2))

    last_row = np.arange(arr_string2.size + 1)
    for s in arr_string1:
        current_row = last_row + 1

        current_row[1:] = np.minimum(current_row[1:],
                   np.add(last_row[:-1], arr_string2 != s))

        # Deletion (string2 grows shorter than string1):
        current_row[1:] = np.minimum(current_row[1:],
                current_row[0:-1] + 1)

        last_row = current_row

    return last_row[-1]

def read_corpus(path):
    f = open(path,'r')
    words = []
    for w in f.readlines():
        words.append(w.split()[0].lower())
    f.close()
    return words

def create_dictionary(fname):
    dictionary = []    
    with open(fname) as file:
        for line in file:
            # separate by words by non-alphabetical characters      
            words = re.findall('[a-z]+', line.lower())  
            for word in words:
                dictionary.append(word)
    return dictionary

def tweet_words(tweets):
    words = []
    for tweet in tweets:
        for w in re.findall('[a-z]+', tweet):
            words.append(w)
    return words


def correct_series(word,dict_corpus):
    #print(word)
    if word in dict_corpus: return word,True
    if len(word)==0: return "",True
    i = 2
    corrections = {}
    order = 0
    while(i<=len(word)):
        #print(i)
        if word[:i] in dict_corpus:
            correct,possible = correct_series(word[i:],dict_corpus)
            if possible:
                corrections[word[:i]+" "+correct]=(order,len(word[:i]+" "+correct))
                order += 1
        i = i + 1
    
    if len(corrections)==0:
        return "", False
    else:
        return sorted(corrections.items(), key=lambda term, val): (val[1], val[0]))[0][0],True

