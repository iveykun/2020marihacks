from rake_nltk import Rake
import nltk
from nltk import ne_chunk
from nltk.tokenize import word_tokenize
import random
r = Rake(min_length=2, max_length=3)

text = open(input())
temp = text.read()
textcopy = str(temp)

#text = 

keywords = r.extract_keywords_from_text(str(textcopy))

lst = []
with_score = r.get_ranked_phrases()


keywords

for word in with_score:
    lst.append(word)
lst = lst[0:50:2]
print(lst)

for thing in lst:
    textcopy = textcopy.replace(thing, ' _________ ')
#textcopy.replace('thinking', '________')
f = open("printout.txt", "w+")
f.write(textcopy)
f.close()
print(textcopy)
'''

text = str(lst)
token = word_tokenize(text)
tags = nltk.pos_tag(token)
reg = "NP: {<DT>?<JJ>*<NN>}" 
a = nltk.RegexpParser(reg)
result = a.parse(tags)
print(result)
'''
