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

def get_results(training,testing, m):
    print "bulding probability table..."
    priors=make_priors_freq(training)
    probs=make_prob_table(training, priors)
    print "done."
    total=0.0
    basetotal=0.0
    rand_basetotal=0.0
    errcount=0
    nonerrcount=0
    #baseline of most frequent  overall paraphrases
    totals=sorted(priors.items(), key=lambda x: x[1], reverse=True)
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
            
        rand_base=[]
        i=0
        while(i<3):
            p=Paraphrase(random.choice(priors.keys()))
            if p not in subs:
                rand_base.append(p)
                i+=1
                
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
            p.score=priors[p.name]
            for s in subs:
                try:
                    p.score=p.score*probs[p.name][s.name]
                    nonerrcount+=1
                    #print "done"
                except KeyError:
                    errcount+=1
                    #print errcount
                    #print "Key Error"
        results.sort(key= lambda para: para.score, reverse=True)
        score=0.0
        basescore=0.0
        rand_basescore=0.0
        for p in rand_base[0:m]:
            if p in gold_paras:rand_basescore+=1.0   
        for b in base[0:m]:
            if b in gold_paras:basescore+=1.0    
        for r in results[0:m]:
            if r in gold_paras:score+=1.0
        total+=(score/float(m))
        basetotal+=(basescore/float(m))
        rand_basetotal+=(rand_basescore/float(m))
    acc=total/len(testing)
    print "predictions:"
    print total/len(testing)
    print
    baseacc=basetotal/len(testing)
    print "most frequent baseline:"
    print basetotal/len(testing)
    
    rand_baseacc=rand_basetotal/len(testing)
    print "random baseline:"
    print rand_basetotal/len(testing)
    
    print errcount
    print nonerrcount
    results=[acc,baseacc, rand_baseacc]
    return results


def cross_validate(dataset, k):
    
    fold_size=len(dataset)/k
    folds=[]
    start=0
    end=fold_size-1
    #split the dataset into k folds. the folds will be of equal size, examples
    #that don't fit into the last fold are excluded
    while(end<len(dataset)):
        folds.append(dataset[start:end])
        start+=fold_size
        end+=fold_size
        
    i=0
    total_acc=0.0
    total_base=0.0
    total_rand_base=0.0
    while(i<len(folds)):
        print "testing on fold %i" % i
        training=[]
        testing=[]
        testing=folds[i]
        print len(folds)
        j=0
        while(j<len(folds)):
            if j!=i: training.extend(folds[j])
            j+=1
        print len(training)
        result=get_results(training, testing, 1)
        accuracy=result[0]
        baseline=result[1]
        total_acc+=accuracy
        total_base+=baseline
        total_rand_base+=result[2]
        print len(training)
        print len(testing)
        print "accuracy %s" % accuracy
        print "baseline %s" % baseline
        i+=1
    print "***********"
    print "acc: %f" % (total_acc/k)
    print "base: %f" % (total_base/k)
    print "rand_base: %f" % (total_rand_base/k)
    print "***********"
        
if __name__=="__main__":
    n=2
    data_file=open("/home/paul/mayThesis/semEvalTask9/combined.txt")
    all_pairs=parse_semeval.parse_file(data_file, n)
    pri=make_priors(all_pairs)
    pro=make_prob_table(all_pairs, pri)
    x=["enclose", "contain", "hold", "be filled with"]
    y=["enclose", "contain", "hold", "be filled with"]
    for p in x:
        print "*********************"
        print pri[p]
        sum=0.0
        for p2 in y:
            print p
            print p2
            try:
                print pro[p][p2]
                sum+=pro[p][p2]
            except:
                print "x"
        print sum