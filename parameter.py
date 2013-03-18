'''
Created on 8 Feb 2010

@author: paul
'''
import copy
import cPickle
import random
import parse_semeval
from parse_semeval import Paraphrase

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
                if b.name in cooc[a]: cooc[a][b.name]+=(b.freq/80.0)
                else: cooc[a][b.name]=(1.0/80.0)
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

def get_results(testing, m):

    for pair in testing:
        gold_paras=[]
        for p in pair.paraphrases:
            gold_paras.append(p)
    
        if len(gold_paras)>2:
            subs=random.sample(gold_paras,3)
        else:
            errcount+=1
            print "List too short error."
            continue
        base=[]

        for t in totals:
            if Paraphrase(t[0]) not in subs:
                base.append(Paraphrase(t[0]))
            if len(base)==m: break
        # a list of all paraphrases, to be ordered by score for this compound
        results=[]
        
        for p in probs.keys():
            x=Paraphrase(p.strip())
            x.score=0.0
            #the seed paraphrases are not allowed in predictions
            if not x in subs: results.append(x)
            
        for p in results:
            for s in subs:
                try:
                    p.score+=probs[p.name][s.name]
                    nonerrcount+=1
                    #print "done"
                except KeyError:
                    errcount+=1
                    #print errcount
                    #print "Key Error"
        results.sort(key= lambda para: para.score, reverse=True)
        score=0.0
        basescore=0.0
        for b in base[0:m]:
            if b in gold_paras:basescore+=1.0    
        for r in results[0:m]:
            if r in gold_paras:score+=1.0
        total+=(score/float(m))
        basetotal+=(basescore/float(m))
    acc=total/len(testing)
    print "predictions:"
    print total/len(testing)
    print
    baseacc=basetotal/len(testing)
    print "baseline:"
    print basetotal/len(testing)
    
    print errcount
    print nonerrcount
    results=[acc,baseacc]
    return results
        
if __name__=="__main__":  
    n=3
    data_file=open("/home/paul/mayThesis/semEvalTask9/combined.txt")
    all_pairs=parse_semeval.parse_file(data_file, n)
    cross_validate(all_pairs,22)