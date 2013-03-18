'''
Created on 8 Feb 2010

@author: paul
'''
import copy
import cPickle
import random
import parse_semeval
import math
from parse_semeval import Paraphrase

def make_priors_freq(all_pairs):
    """
    computes the prior probability of a given paraphrase occuring. This is simply
    a count of the number of times it occurs in the whole dataset. The
    paraphrase must have been produced by at least n annotators to count as a
    valid occurence for a given compound.
    """
    priors={}
    for pair in all_pairs:
        for p in pair.paraphrases:
            if p.name in priors:
                priors[p.name]+=(p.freq)
            else:
                priors[p.name]=(p.freq)
    return priors


def make_priors(all_pairs):
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
            if p.name in priors:
                priors[p.name]+=(1.0)
            else:
                priors[p.name]=(1.0)
    return priors


def make_prob_table(all_pairs,priors):
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
            currentParas.append(x)
        i=0
        while(i<len(currentParas)):
            j=0
            a=currentParas[i].name
            while(j<len(currentParas)):
                #don't count co-occurrence of paraphrase with itself
                if j==i:
                    j+=1
                    continue
                b=currentParas[j]
                if b.name in cooc[a]: cooc[a][b.name]+=(1)
                else: cooc[a][b.name]=(1.0)
                j+=1
            i+=1
            
    #probabilities are coocurrences divided by prior probability
    probs={}
    for x in cooc.keys(): probs[x]={}
    for a in cooc.keys():
        for b in cooc.keys():
            if b in cooc[a]:
                probs[a][b]=(cooc[a][b]) / ( (priors[b]) * (priors[a]**0) ) 
                #print probs[a][b]
            else:
                probs[a][b]=0.0
    return probs


        
if __name__=="__main__":
    n=2
    out_file=open("/home/paul/mayThesis/semEvalTask9/SemEval2_task9_all_data_final/SemEval2_task9_scorer/out.txt",'w')
    train_file=open("/home/paul/mayThesis/semEvalTask9/combined.txt")
    test_file=open("/home/paul/mayThesis/semEvalTask9/testing.txt")
    test_file=open("/home/paul/mayThesis/semEvalTask9/testing.txt")
    test_pairs=parse_semeval.parse_file(test_file, n)
    all_pairs=parse_semeval.parse_file(train_file, n)
    priors=make_priors(all_pairs)
    probs=make_prob_table(all_pairs,priors)
    for pair in test_pairs:
        candidates=copy.copy(pair.paraphrases)
        for para in pair.paraphrases:
            for c in candidates:
                if para==c:continue
                para.score+=probs[para.name][c.name]
        pair.paraphrases=sorted(pair.paraphrases, key=lambda x: x.score, reverse=True)
        i=0
        for p in pair.paraphrases:
            i+=1
            out_file.write(str(i)+ " "+pair.n1 + " " + pair.n2 + " "+ p.name + " "+str(p.score) + "\n")
