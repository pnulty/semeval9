'''
Created on 8 Feb 2010

@author: paul
'''
import random
import ngrams
class NounPair:
    def __init__(self,n1,n2):
        self.n1=n1
        self.n2=n2
    def __eq__(self,other):
        return (self.n1==other.n1 and self.n2==other.n2)

class Paraphrase:
    def __init__(self,name,freq=0.0):
        self.name=name
        self.freq=freq
        self.score=0.0
    def __eq__(self,other):
        return self.name==other.name

def parse_file(file,n):
    '''reads the data file and makes a list of NounPair objects with
    paraphrase objects as attributes. Paraphrases with frequencies of less than
    n are excluded'''
    lines=file.readlines()
    examples=[]
    old=""
    for line in lines:
        line=line.split('\t')
        if len(line)<2:continue
        cur=line[0].replace(' ','_')
        if not old==cur: # then we've reached the next pairs
            this_pair= NounPair(line[0].split()[0],line[0].split()[1])
            examples.append(this_pair)
            this_pair.paraphrases=[]
        freq=line[2]
        if len(line)>2: freq=int(line[2])
        tmp=Paraphrase(line[1].strip(),freq)
        if tmp.freq < n: continue
        this_pair.paraphrases.append( tmp )
        old=line[0].replace(' ','_')
    return examples

if __name__=="__main__":
    path='/home/paul/mayThesis/semEvalTask9/all.txt'
    data=open(path)
    print parse_file(data)