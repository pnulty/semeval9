'''
Created on 10 Dec 2009

@author: paul
'''
'''
Created on 23 Nov 2009

@author: paul
'''
import math
import sys
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn
from nltk import WordNetLemmatizer
wnl=WordNetLemmatizer()

class Web1TSearch:
    """An interface using an index to search the Web1T Corpus quickly"""
    def __init__(self,path="/home/paul/thesis/corpora/web1T/clean/"):
        """Looks for the indexes and loads them"""
        self.path=path
        print path
        print self.path
        print "Loading index..."
        try:
            self.indexes=[]
            self.indexes.append(open(self.path+"indexes/index3.txt").readlines())
            self.indexes.append(open(self.path+"indexes/index4.txt").readlines())
            self.indexes.append(open(self.path+"indexes/index5.txt").readlines())
        except:
            print "Couldn't find the index files at: "+self.path 

    def __getIndexPosition(self,n1):
        """"Looks up the position of n1 in the corpus using the index. Returns
        a list of strings of the form filename%byteoffset"""
        pos=[]
        for i in self.indexes:
            for line in i:
                line=line.split()
                if line[0]==n1:
                    pos.append(line[1])
        return pos


    def plural(self,word):
        """simple rules to return the plural of an English word"""
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word[-1] in 'sx' or word[-2:] in ['sh', 'ch']:
            return word + 'es'
        elif word.endswith('an'):
            return word[:-2] + 'en'
        return word + 's'
    
    def getLines(self,x):
        """Finds and returns all lines that begin with x
            singular or plural form. Returns a dictionary in the
            form pattern:frequency """
        
        results={}
        forms=[x]#,self.plural(x)]  
        for f in forms:
            n1=f
            print "getting "+ n1
            pos=self.__getIndexPosition(n1)
            for p in pos:
                p=p.split("%")
                file=open(self.path+p[0][0:3]+"s/"+p[0])
                offset=p[1]
                file.seek(int(offset))
                line=file.readline()
                line=line.split()      
                while((line[0])==n1):    
                    pat=line[1:-1]
                    freq=int(line[-1])
                    pat='_'.join(pat)
                    if pat in results:results[pat]+=freq
                    else: results[pat]=freq                        
                    line=file.readline()
                    line=line.split()
                    if len(line)<3:
                        break
                file.close()
                #sortedResults=sorted(results.iteritems(), key=lambda (k,v): (v,k),reverse=True)
        return results
    
    def getNgrams(self,x,y):
        """Finds and returns all ngrams that begin with x and end with y in 
            singular or plural form. Returns a dictionary in the
            form pattern:frequency """
        results={}
        forms=[(x,y),(self.plural(x),y),(x,self.plural(y)),(self.plural(x),self.plural(y))]  
        for f in forms:
            n1=f[0]
            n2=f[1]
            pos=self.__getIndexPosition(n1)
            for p in pos:
                p=p.split("%")
                file=open(self.path+p[0][0:3]+"s/"+p[0])
                offset=p[1]
                file.seek(int(offset))
                line=file.readline()
                line=line.split()
                while((line[0])==n1):
                    if (line[-2])==n2: 
                        pat=line[1:-2]
                        freq=int(line[-1])
                        pat='_'.join(pat)
                        if pat in results:results[pat]+=freq
                        else: results[pat]=freq                        
                    line=file.readline()
                    line=line.split()
                    if len(line)<3:
                        break
                file.close()
                #sortedResults=sorted(results.iteritems(), key=lambda (k,v): (v,k),reverse=True)
        return results
    
    def reducePats(self, pats,head,mod):
        """merges semantically identical patterns by removing determiners,conjunctions
            and adjectives"""
        validPos=['VB','VBD','VBG','VBN','VBP','VBZ','IN',]
        newPats={}
        sortedResults={}
        st=0
        for p in pats.keys():
            st+=1
            s= "We look at the "+head+" "+p.replace('_',' ')+" "+mod
            s= pos_tag(word_tokenize(s))
            s=s[5:]
            for w in s:
                if w[1].startswith('NN')or w[1].startswith('CC')or w[1].startswith('P') : continue
            temp=""
            for w in s:
                if w[1] in validPos:
                    if wnl.lemmatize(w[0],wn.VERB):
                        temp=temp+wnl.lemmatize(w[0],wn.VERB)+"_"
                    else:
                        temp=temp+w[0]+'_'                    
            temp=temp.rstrip('_')
            temp=temp.replace(' ','_')
            if temp in newPats: newPats[temp]+=math.log(pats[p])
            else: newPats[temp]=math.log(pats[p])
            #sortedResults=sorted(newPats.iteritems(), key=lambda (k,v): (v,k),reverse=True)
        return newPats
    
if __name__ == '__main__':
    w=Web1TSearch()
    mod=sys.argv[1]
    head=sys.argv[2]
    r= w.getNgrams(head,mod)
    r= w.reducePats(r,head,mod)
    sortedResults=sorted(r.iteritems(), key=lambda (k,v): (v,k),reverse=True)
    for s in sortedResults: print s
