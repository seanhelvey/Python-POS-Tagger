#! /usr/bin/env python

#before running the file, make sure path to traningFile, developmentFile are correct here:
trainingFile = "/Users/seanhelvey/Desktop/HelveySean_Assignment_4/training.pos"
developmentFile = "/Users/seanhelvey/Desktop/HelveySean_Assignment_4/development.text"

import copy
import collections

class bigram(object):
    def __init__(self):
        self.priorWord = ''
        self.priorTag = ''
        self.currentWord = ''
        self.currentTag = ''

        self.transition = ()
        self.emission = ()

        self.wordCount = 0
        self.tagCount = 0
        self.priorTagCount = 0
        self.transCount = 0
        self.emitCount = 0

        self.possTags = []

        self.transProb = 0
        self.emishProb = 0
        self.finalProb = 0
        
    def scoreCalc(self):
        self.transProb = self.transCount/float(self.priorTagCount)
        self.emishProb = self.emitCount/float(self.tagCount)
        self.finalProb = self.transProb * self.emishProb

class sentences(object):
    def __init__(self):
        self.list = []

        self.sentsMax = 0

    def addWord(self,gram):
        for sentence in self.list:
            sentence.bigrams.append(gram)

    def addSentence(self):
        sent = sentence()
        self.list.append(sent)
    
    def replicate(self,gram):

        holdList = []
        for s in self.list:
            c = sentence()
            c = copy.deepcopy(s)

            c.bigrams.pop()
            c.bigrams.append(gram)

            holdList.append(c)

        self.list = self.list[:] + holdList[:]

class sentence(object):
    def __init__(self):
        self.bigrams = []
        self.score = 0
        self.max = 0
        
    def sentScore(self):
        switch = 0
        for gram in self.bigrams:
            if switch == 0:
                self.score = gram.finalProb
                switch = 1
            else:
                self.score = self.score * float(gram.finalProb)

#open trainingFile for read
file=open(trainingFile,'r')

#list of bigrams for aggregating data
theBigrams = []

#dictionairies for counting
wordDic = collections.defaultdict(int)
tagDic = collections.defaultdict(int)
transDic = collections.defaultdict(int)
emitDic = collections.defaultdict(int)
possDic1 = collections.defaultdict(list)
possDic2 = collections.defaultdict(int)

#last pos -> most likely pos
lastDic = collections.defaultdict(str)

#variables to store for the next iteration
lastWord = ''
lastTag = ''
lastTagCount = 0

#FIRST PASS~~~~~~
#parsing input data
#aggregating dictionairies
file.seek(0)
for line in file:
    
    gram = bigram()
    thisLine = line.split()
    listLen = len(thisLine)

    #assign PRIOR word and tag to gram
    gram.priorWord = lastWord
    gram.priorTag = lastTag
    gram.priorTagCount = lastTagCount

    #if the current line contains a word and a tag
    if listLen > 1:
        
        #assign CURRENT word and tag to gram
        gram.currentWord = thisLine[0]
        gram.currentTag = thisLine[1]
        
        #and add to dictionairy -> list
        possDic1[gram.currentWord].append(gram.currentTag)
        
    else:
        gram.currentWord = ''
        gram.currentTag = ''

    #store transition & emission
    gram.transition = (gram.priorTag,gram.currentTag)
    gram.emission = (gram.currentTag,gram.currentWord)

    #increment dictionairies
    transDic[gram.transition] += 1
    emitDic[gram.emission] += 1
    wordDic[gram.currentWord] += 1
    tagDic[gram.currentTag] += 1
    possDic2[gram.currentWord] += 1
    
    #add the gram to our list
    theBigrams.append(gram)

    #set temp variables for next gram
    lastWord = gram.currentWord
    lastTag = gram.currentTag
    lastTagCount = gram.tagCount


#Uniqify thingys in possDic1
for thingy in possDic1:
    possDic1[thingy]=list(set(possDic1[thingy]))

copyTagDic = copy.deepcopy(tagDic)
copyTransDic = copy.deepcopy(transDic)

#lastDic will have tag -> tag+1 in strings
for tag in copyTagDic:
    lastDic[tag] = ""

#Counting total transitions from tag
for trans in transDic:
    copyTagDic[trans[0]] += 1

#Taking transDic from count to prob
for trans in transDic:
    copyTransDic[trans] = transDic[trans]/ float(copyTagDic[trans[0]])

#Setting copyTagDic back to zero
for tag in copyTagDic:
    copyTagDic[tag] = 0

#Setting max
for item in copyTransDic:
    if copyTagDic[item[0]] < copyTransDic[item]:
        copyTagDic[item[0]] = copyTransDic[item]

#Storing in lastDic
for item in copyTransDic:
    if copyTagDic[item[0]] == copyTransDic[item]:

        #mapping tag -> tag + 1
        lastDic[item[0]] = item[1]

gramDic = collections.defaultdict(bigram)

#COUNTING~~~~~~~~~~~~~
#We want the data from the dictionairies
#stored locally with each bigram object
for item in theBigrams:

    item.wordCount = wordDic[item.currentWord]
    item.tagCount = tagDic[item.currentTag]
    item.priorTagCount = tagDic[item.priorTag]    
    item.transCount = transDic[item.transition]

    if item.emission[0] == item.currentTag and item.emission[1] == item.currentWord:
        item.emitCount = emitDic[item.emission]

    item.possTags = possDic1[item.currentWord]

    item.scoreCalc()
    gramDic[(item.currentWord,item.currentTag)] = item

#SECOND PASS~~~~~~~~
#Building up lists of possible word combinations or "sentences"
#Computing likelihood of each tag sequence

file=open(developmentFile,'r')

sentsList = []
newSents = 1
sentsListNum = 0
theLastTag = ''
for word in file:

    wordList = word.split()
    currentTag = ''

    if len(wordList) > 0:
        theWord = wordList[0]
        tags = possDic1[theWord]

        if newSents == 1:
            newSents = 0
            sents = sentences()
            sents.addSentence()
    
        if len(tags) >= 1:

            tagMax = 0
            for tag in tags:
                gram = gramDic[(theWord,tag)]
                currentTag = tag
                
                if gram.finalProb >= tagMax:
                    tagMax = gram.finalProb                    

            for tag in tags:
                gram = gramDic[(theWord,tag)]
                
                if gram.finalProb == tagMax:
                    sents.addWord(gram)

        else:
            if len(tags) == 0:
                gram = bigram()
                gram.currentWord = theWord
                gram.currentTag = lastDic[theLastTag]
                gram.finalProb = .0001
                gramDic[(gram.currentWord,gram.currentTag)] = gram

            else:
                gram = gramDic[(theWord,tags[0])]
                currentTag = tags[0]

            sents.addWord(gram)

    else:
        newSents = 1
        sentsList.append(sents)
        sentsListNum = sentsListNum + 1

    theLastTag = currentTag

#Find max
for sents in sentsList:
    for sent in sents.list:
        sent.sentScore()
        if sent.score > sents.sentsMax:
            sents.sentsMax = sent.score


outfile = open("out.txt","w")

#Write output
for sents in sentsList:
    num = 0
    for sent in sents.list:
        if sent.score == sents.sentsMax and num == 0:
            for gram in sent.bigrams:
                outfile.write(str(gram.currentWord)+"\t"+str(gram.currentTag)+"\n")
            num += 1
            outfile.write("\n")

outfile.write("\n")
