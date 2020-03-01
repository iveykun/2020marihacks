from rake_nltk import Rake
import nltk
from nltk import ne_chunk
from nltk.tokenize import word_tokenize
import random
r = Rake(min_length=2, max_length=3) # only takes terms with 2-3 words in them, ex. Thomas Edison, John F Kennedy

text = open(input())
temp = text.read()
textcopy = str(temp)

#text = 

keywords = r.extract_keywords_from_text(str(textcopy))  # finds keywords, usually a lot of words

lst = []
with_score = r.get_ranked_phrases()  # output the keywords you found


keywords

for word in with_score:
    lst.append(word)  # appends all keywords found to lst
lst = lst[0:50:2]   # removing half of them in steps of 2 to avoid having too many blanks in one sentence
#print(lst)

for thing in lst:
    textcopy = textcopy.replace(thing, ' _________ ')  # replacing the keywords with blanks
#textcopy.replace('thinking', '________')
f = open("printout.txt", "w+")
f.write(textcopy)  # writing final text to txt
f.close()
#print(textcopy)

'''

text = str(lst)
token = word_tokenize(text)
tags = nltk.pos_tag(token)
reg = "NP: {<DT>?<JJ>*<NN>}" 
a = nltk.RegexpParser(reg)
result = a.parse(tags)
print(result)
'''
