from rake_nltk import Rake
import nltk
from nltk import ne_chunk
from nltk.tokenize import word_tokenize
import random
def dt(txt):  # remember to add quotes ex: dt('corona.txt')
    r = Rake(min_length=2, max_length=3) # only takes terms with 2-3 words in them, ex. Thomas Edison, John F Kennedy
    text = open(str(txt))
    #text = open(input())
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
    dic = {}
    for count, thing in enumerate(lst):
        dic[count] = thing
        replace = ' _________{}{}{} '.format('[', count, '] ') 
        textcopy = textcopy.replace(thing, replace)  # replacing the keywords with blanks
    #textcopy.replace('thinking', '________')
    f = open("printout.txt", "w+")
    f.write(textcopy)  # writing final text to txt
    
    f.write('\n')
    f.write('\n')
    f.write('answers:')
    f.write('\n')
    for item in dic.items():
        f.write(str(item))
        f.write('\n')
    
    f.close()
    #print(textcopy)
    # reveal('abilities', 18, dic)  # you need to put them in this order 
    return dic

def reveal(answer, num, dic):  # get answer, tells if it's right
    real = dic.get(num)
    if answer in real:
        print("Correct! The answer is ", real)
    else:
        print("Wrong! The answer is ", real)
    
# dt('corona.txt')
