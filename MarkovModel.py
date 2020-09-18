import string
import random
import math
import re

def tokenize(text):
    separatedText = ""
    for character in text:
        if character in string.punctuation:
            output = " %s " % character
        else:
            output = character
        separatedText += output
    return separatedText.split()

def ngrams(n, tokens):
    ngrams = []
    tokens.append('<END>')
    currTuple = (('<START>',)) * (n - 1)
    for token in tokens:
        ngrams.append((currTuple, token))
        if n == 1:
            currTuple = ()
        else:
            currTuple = currTuple[1:] + (token,)
    return ngrams

class NgramModel(object):

    def __init__(self, n):
        self.n = n
        self.ngramsCount = {}
        self.contextCount = {}

    def update(self, sentence):
        tokens = tokenize(sentence)
        ngramsList = ngrams(self.n, tokens)
        for ngram in ngramsList:
            if ngram in self.ngramsCount:
                self.ngramsCount[ngram] += 1
            else:
                self.ngramsCount[ngram] = 1
            if ngram[0] in self.contextCount:
                self.contextCount[ngram[0]] += 1
            else:
                self.contextCount[ngram[0]] = 1

    def prob(self, context, token):
        contextCount = self.contextCount[context]
        if (context, token) in self.ngramsCount.keys():
            tokenCount = self.ngramsCount[(context, token)]
            return tokenCount / contextCount
        return 0.0

    def random_token(self, context):
        r = random.random()
        prob = 0
        tokens = sorted([key[1] for key in self.ngramsCount.keys() if context == key[0]])
        for token in tokens:
            prob += self.prob(context, token)
            if prob > r:
                return token

    def random_text(self, token_count):
        startTuple = (('<START>',))
        context = startTuple * (self.n - 1)
        sentence = ""
        count = 0
        while token_count > count:
            key = self.random_token(context)
            if count == 0:
                sentence = key
            else:
                sentence = sentence + " " + key
            if self.n > 1:
                context = (context[1:], key)
                context = context[0] + (context[1],)
            if key == "<END>":
                startTuple = (('<START>',))
                context = startTuple * (self.n - 1)
            count += 1
        sentence = re.sub(r'\s([?.!:,;\-"\'\)/](?:\s|$))', r'\1', sentence)
        sentence = re.sub(r'\samp;', '', sentence)
        if sentence[0:5] == 'http:':
            sentence = self.random_text(token_count)
        sentence = sentence.split(' http')
        return sentence[0]

    def perplexity(self, sentence):
        perplexity = 0
        tokens = tokenize(sentence)
        ngramsList = ngrams(self.n, tokens)
        for ngram in ngramsList:
            perplexity += math.log(self.prob(ngram[0], ngram[1]))
        perplexity = 1 / math.exp(perplexity)
        return math.pow(perplexity, 1 / (len(tokens)))

def create_ngram_model(n, path):
    model = NgramModel(n)
    file = open(path, 'r')
    lines = file.readlines()
    for line in lines:
        model.update(line)
    return model
