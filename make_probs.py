'''
Created on 8 Feb 2010

@author: paul
'''
import copy
import cPickle
import random
import parse_semeval

def make_priors_freq(all_pairs,_n):
    """
    computes the prior probability of a given paraphrase occuring. This is simply
    a count of the number of times it occurs in the whole dataset. The
    paraphrase must have been produced by at least n annotators to count as a
    valid occurence for a given compound.
    """
    #parameter: paraphrase must have been mentioned by at least n annotators
    n=_n
    priors={}
    for pair in all_pairs:
        for p in pair.paraphrases:
            if p.freq<n: continue
            if p.name in priors:
                priors[p.name]+=(p.freq)
            else:
                priors[p.name]=(1.0)
    return priors


def make_priors(all_pairs, n):
    """
    computes the prior probability of a given paraphrase occuring. This is simply
    a count of the number of times it occurs in the whole dataset. The
    paraphrase must have been produced by at least n annotators to count as a
    valid occurence for a given compound.
    """
    #parameter: paraphrase must have been mentioned by at least n annotators

    priors={}
    for pair in all_pairs:
        for p in pair.paraphrases:
            if p.freq<n: continue
            if p.name in priors:
                priors[p.name]+=(1.0)
            else:
                priors[p.name]=(1.0)
    return priors


def make_prob_table(all_pairs,priors,n):
    """
    computes the conditional probability of a paraphrase, i.e. the probability
    of one paraphrase occurring in the same compound as another paraphrase.
    For two paraphrases A and B, the probability of A occurring given that B
    occurs for the same compound is a count of the number of times that A has
    occurred with B in all other compounds, divided by the number of times that
    B has occurred overall
    
    """
    
    #parameter: paraphrase must have been mentioned by at least n annotators
    cooc={}
    #initialize cooccurrence dictionary
    for x in priors.keys(): cooc[x]={}

    counter=0
    #for each paraphrase, count its cooccurrences with all other paraphrases
    for compound in all_pairs:
        counter+=1   
        #make a list of paraphrases for this compound
        currentParas=[]
        for x in compound.paraphrases:
            if x.freq<n: continue
            currentParas.append(x.name)
        i=0
        while(i<len(currentParas)):
            j=0
            a=currentParas[i]
            while(j<len(currentParas)):
                #don't count co-occurrence of paraphrase with itself
                if j==i:
                    j+=1
                    continue
                b=currentParas[j]
                if b in cooc[a]: cooc[a][b]+=1.0
                else: cooc[a][b]=1.0
                j+=1
            i+=1
            
    #probabilities are coocurrences divided by prior probability
    probs={}
    for x in cooc.keys(): probs[x]={}
    for a in cooc.keys():
        for b in cooc.keys():
            if b in cooc[a]:
                probs[a][b]=cooc[a][b]/ (priors[b])
            else:
                probs[a][b]=0.0
    return probs
