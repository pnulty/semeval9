import parse_semeval
import cPickle
import random
from predict import make_priors
from predict import make_prob_table
from parse_semeval import Paraphrase
f=open("/home/paul/mayThesis/semEvalTask9/combined.txt")

all_pairs=parse_semeval.parse_file(f,3)
n=3
print "making prior probaility table..."
priors=make_priors(all_pairs)
print "making prob table"
probs=make_prob_table(all_pairs, priors)
print len(priors)

again='y'
while(again!='n'):
    print "done. enter paraphrase"
    inp="."
    seeds=[]
    while(inp):
        inp=raw_input()
        if inp in priors:
            seeds.append(Paraphrase(inp))
        else:
            print "not found"
    
    print "working..."
    for pair in all_pairs:
        paras=[]
        for p in pair.paraphrases:
            if p.freq < n : continue
            paras.append(p)
        results=[]
        
        for p in probs.keys():
            x=Paraphrase(p.strip())
            x.score=0.0
            #the seed paraphrases are not allowed in predictions
            if not x in seeds: results.append(x)
            
        for p in results:
            for s in seeds:
                try:
                    p.score+=probs[p.name][s.name]
                    #print "done"
                except KeyError:
                    pass
                    print "Key Error"
        results.sort(key= lambda para: para.score, reverse=True)
    
    for r in results[0:10]:
        print r.name
    print "\n\n gain?"
    again=raw_input()