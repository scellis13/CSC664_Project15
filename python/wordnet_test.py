from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import requests
import sys
import json
from bs4 import BeautifulSoup
import math
import time
import threading
from googleapiclient.discovery import build

#***Uncomment lines below for server-side calling
searchQuery = sys.argv[1]
name = sys.argv[2]
synset_option = int(sys.argv[3])
searchQueryChoice = int(sys.argv[4])
tokenChoice = int(sys.argv[5])
#***Uncomment lines above for server-side calling

#***Uncomment lines below to test manual Search Queries without the Server request
# searchQuery = "Study that Pitbulls are Genetically Fighting Dogs"
# name = "Testing Synset"
# synset_option = 5
# searchQueryChoice = 1
# tokenChoice = 1
#***Uncomment lines above to test manual Search Queries without the Server request

#Start Environment Variables
fileName = "queryFiles/"+name+".txt"
minRead = 0
maxRead = 25000
threadCount = 3
end = 10
json_file_data = {}
stop_words = set(stopwords.words("english")) #list of stop words by default from NLTK
ps = PorterStemmer()
#End of Environment Variables



#*************FUNCTIONS**************#
def tokenizeAndFilter(text):
    ##Step 1: Tokenize
    queryTokens_step1 = []
    queryTokens_step2 = []
    queryTokens_step3 = []
    
    queryTokens_step1 = word_tokenize(text)

    ##Step 2: Stop Words
    for token in queryTokens_step1:
        if token not in stop_words:
            queryTokens_step2.append(token)

    ##Step 3: Stemming
    for token in queryTokens_step2:
        queryTokens_step3.append(ps.stem(token))
    
    return queryTokens_step3
            
def count_tokens(thread, start, title, url, textList, tokenList):
    global total_count

    json_file_data[start] = []
    json_file_data[start].append(json.loads('{ "url":"'+url+'", "title":"'+title+'"}'))
    for word in tokenList:
        count = textList.count(word)
        if word in total_count:
            total_count[word] = total_count[word] + count
        else:
            total_count[word] = count
        if count > 0:
            word_frequency[word] = word_frequency[word] + 1
        json_string = '{ "word":"'+word+'", "count":"'+str(count)+'"}'
        json_object = json.loads(json_string)
        json_file_data[start].append(json_object)

def writeFile(end):
    json_file_data[end] = []

    global total_count
    for key, value in total_count.items():
        
        idf = 0
        if word_frequency[key] != 0:
            idf = math.log((end/(word_frequency[key])), 2)
            
        json_string = '{ "main_word":"'+key+'", "total_count":"'+str(value)+'", "df":"'+str(word_frequency[key])+'","idf":"'+str(idf)+'"}'
        json_object = json.loads(json_string)
        json_file_data[end].append(json_object)
        
    with open(fileName, 'w+', encoding='utf-8') as outfile:
        json.dump(json_file_data, outfile, ensure_ascii=False, indent=4)
#**********END OF FUNCTIONS**********#







#**********START OF DYNAMIC CODE**********#
        
#Determine synset query variation, and tokens.
synsetTokenString = ""
unfilteredTokens = word_tokenize(searchQuery)
##hypernyms == abstract elements
##hyponyms == specific alternative elements
if synset_option != 0:
    for token in unfilteredTokens:
        if token not in stop_words:
            synArray = wordnet.synsets(token)
            if len(synArray) > 0:
                #print("Synset for: " + token + " : " + str(synArray))
                if (synset_option == 1 or synset_option == 5):
                    hypernyms = synArray[0].hypernyms()
                    #print("\tHypernyms for: " + str(synArray[0].name()) + " : " + str(hypernyms))
                    if len(hypernyms) > 0:
                        hypernym = str(hypernyms[0].lemmas()[0].name())
                        #print("\t\tWord to tokenize: " + hypernym)
                        synsetTokenString += hypernym + " "
                if (synset_option == 2 or synset_option == 5):
                    hyponyms = synArray[0].hyponyms()
                    #print("\tHyponyms for: " + str(synArray[0].name()) + " : " + str(hyponyms))
                    if len(hyponyms) > 0:
                        hyponym = str(hyponyms[0].lemmas()[0].name())
                        #print("\t\tHyponym to Tokenize: " + hyponym)
                        synsetTokenString += hyponym + " "
                if (synset_option == 3 or synset_option == 5):
                    holonyms = synArray[0].part_holonyms()
                    #print("\tholonyms for: " + str(synArray[0].name()) + " : " + str(holonyms))
                    if len(holonyms) > 0:
                        holonym = str(holonyms[0].lemmas()[0].name())
                        #print("\t\tHolonym to Tokenize: " + holonym)
                        synsetTokenString += holonym + " "
                if (synset_option == 4 or synset_option == 5):
                    meronyms = synArray[0].part_meronyms()
                    #print("\tmeronyms for: " + str(synArray[0].name()) + " : " + str(meronyms))
                    if len(meronyms) > 0:
                        meronym = str(meronyms[0].lemmas()[0].name())
                        #print("\t\tmeronym to Tokenize: " + meronym)
                        synsetTokenString += meronym + " "

if ((searchQueryChoice == 0) and (tokenChoice == 1)): #Default Web Search with Synset Tokens Only
    filteredTokens = tokenizeAndFilter(synsetTokenString)
elif searchQueryChoice == 0 and tokenChoice == 2: #Default Web Search with Combined Tokens
    filteredTokens = tokenizeAndFilter(searchQuery + " " + synsetTokenString)
elif searchQueryChoice == 1 and tokenChoice == 0: #Synset Web Search with Default Tokens Only
    filteredTokens = tokenizeAndFilter(searchQuery)
    searchQuery = synsetTokenString
elif searchQueryChoice == 1 and tokenChoice == 1: #Synset Web Search with Synset Tokens Only
    filteredTokens = tokenizeAndFilter(synsetTokenString)
    searchQuery = synsetTokenString
elif searchQueryChoice == 1 and tokenChoice == 2: #Synset Web Search with Combined Tokens
    filteredTokens = tokenizeAndFilter(searchQuery + " " + synsetTokenString)
    searchQuery = synsetTokenString
elif searchQueryChoice == 2 and tokenChoice == 0: #Combined Web Search with Default Tokens Only
    filteredTokens = tokenizeAndFilter(searchQuery)
    searchQuery = searchQuery + " " + synsetTokenString
elif searchQueryChoice == 2 and tokenChoice == 1: #Combined Web Search with Synset Tokens Only
    filteredTokens = tokenizeAndFilter(synsetTokenString)
    searchQuery = searchQuery + " " + synsetTokenString
elif searchQueryChoice == 2 and tokenChoice == 2: #Combined Web Search with Combined Tokens
    filteredTokens = tokenizeAndFilter(searchQuery + " " + synsetTokenString)
    searchQuery = searchQuery + " " + synsetTokenString
else: #Default Web Search with Default Tokens Only
    filteredTokens = tokenizeAndFilter(searchQuery)

print("Searching Google with Query: " + searchQuery)
print("Comparing Tokens with: " + str(filteredTokens))

total_count = {}
word_frequency = {}
for word in filteredTokens:
    word_frequency[word] = 0





#***Uncomment lines below for using Google API to Searching URLs
my_api_key = 'AIzaSyCkvdms4HfQEI22KhWMLooaZOjTMi6Xryg'
my_cse_id = '63cba334e2fb168d2'

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

data = google_search(searchQuery, my_api_key, my_cse_id, start=1)
end = len(data)
#***Uncomment lines above for using Google API for Searching URLs

#Lines below store manual data and conduct '10' requests
# for startCount in range(1, 100, 10):
#     results = google_search(searchQuery, my_api_key, my_cse_id, start=startCount)
#     
#     with open('manualData.txt', 'a+', encoding='utf-8') as outfile:
#         json.dump(results, outfile, ensure_ascii=False, indent=4)
#Lines above store manual data and conduct '10' requests

# ***Uncomment lines below for using manual data file
# data = []
# with open('manualData.txt') as json_file:
#     data = json.load(json_file)
# Uncomment lines above for using manual data file

def func(start):
    for i in range(start, end, threadCount):
        print("Thread["+str(i)+"] reading url: " + data[i]['link'])
        print("Thread["+str(i)+"] reading title: " + data[i]['title'])
        print("Thread["+str(i)+"] reading snippet: " + data[i]['snippet'])
        url = data[i]['link']
        try:
            res = requests.get(url)
            count_tokens(start, i, data[start]['title'],url,tokenizeAndFilter(data[i]['title']+data[i]['snippet']+" "+res.text[minRead:maxRead]), filteredTokens)        
        except:
            count_tokens(start, i, data[start]['title'],url,tokenizeAndFilter(data[i]['title']+data[i]['snippet']), filteredTokens)        

threadArr = []

startingTime = time.time()
print("Starting @ ", startingTime)

for i in range(0, threadCount):
    x = threading.Thread(target=func, args=(i,))
    threadArr.append(x)
    x.start()
    
for i in range(0, threadCount):
    threadArr[i].join()

endingTime = time.time()
print("Ending @ ", endingTime)
print("Total thread time: ", endingTime - startingTime)

writeFile(end)

#print("Total Documents: ", end)
#for key, value in word_frequency.items():
    #print("IDF (", key, "): ", value, " : log(total/doc freq) = ", math.log((end/value), 2))
    
print("Exiting...")
sys.exit(0)



