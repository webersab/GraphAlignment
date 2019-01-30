

import sys
from parsing import Parsing
import datetime
import os
from tqdm import tqdm
#import pprint
#from Cython.Compiler.ExprNodes import inc_dec_constructor

#reload(sys)  
#sys.setdefaultencoding('utf8')

class Preprocess:

    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
    
    def removeRareEntities(self,filePath):
        inFile = open(filePath,'r')
        occurenceCountDict={}
        p = Parsing()
        for line in inFile:
            if 'inv idx' in line:
                break
            elif ': ' in line and 'num preds' not in line and 'predicate' not in line and line!="":
                entities=p.extractEntities(line)
                if entities in occurenceCountDict:
                    oldCount=occurenceCountDict[entities]
                    newCount=oldCount+1
                    occurenceCountDict[entities]=newCount
                else:
                    occurenceCountDict[entities]=1
        rareEntitiesList=[]
        for key,value in occurenceCountDict.items():
            if value<3:
                rareEntitiesList.append(key)
    
        orig_stdout = sys.stdout
        f = open('GermanLoc#LocNoRareEntities.txt', 'w')
        sys.stdout = f
    
        inFile2 = open(filePath,'r')
        for line in inFile2:
            if 'inv idx' in line:
                break
            elif ': ' in line and 'num preds' not in line and 'predicate' not in line and line!="":
                entities = p.extractEntities(line)
                if entities in rareEntitiesList:
                    continue
                else:
                    print(line.rstrip())
            else:
                print(line.rstrip())
        sys.stdout = orig_stdout
        f.close()  
        
    def fillPredicateMap(self,predicate,nounPair,predicateMap):
        internalPredicateMap={}
        if predicate in predicateMap:
            internalMap=predicateMap.get(predicate)
            internalMap["count"]+=1
            if nounPair in internalMap:
                internalMap[nounPair]+=1
            else:
                internalMap[nounPair]=1
        else:
            predicateMap[predicate]=internalPredicateMap
            internalPredicateMap["count"]=1
            internalPredicateMap[nounPair]=1
        return predicateMap
        
    def fillNounPairMap(self,predicate,nounPair,nounPairMap):
        internalNounPairMap={}
        if nounPair in nounPairMap:
            internalMap=nounPairMap.get(nounPair)
            internalMap["count"]+=1
            if predicate in internalMap:
                internalMap[predicate]+=1
            else:
                internalMap[predicate]=1
        else:
            nounPairMap[nounPair]=internalNounPairMap
            internalNounPairMap["count"]=1
            internalNounPairMap[predicate]=1
        return nounPairMap
                
        
    def generate_input(self,inFileName, outFileName,typePair):
        inFile = open(inFileName,'r')
        predicateMap={}
        nounPairMap={}
        for line in tqdm(inFile,total=582924893,unit="lines"):
            if ("(" in line): 
                predicate=self.find_between(line,"(",")"+typePair)
                nounPair=self.find_between(line,"("+predicate+")"+typePair+"::","|||")
                # fill predicate map
                if predicate != "":
                    predicateMap=self.fillPredicateMap(predicate,nounPair,predicateMap)
                #fill noun pair map
                if nounPair != "":
                    nounPairMap=self.fillNounPairMap(predicate,nounPair,nounPairMap)
        print("Size of nounPairMap",sys.getsizeof(nounPairMap))
        print("Size of predicateMap",sys.getsizeof(predicateMap))
        
        
        #Printing happens here
        orig_stdout = sys.stdout
        f = open(outFileName, 'a')
        sys.stdout = f
        print("types: "+typePair+", num preds: "+str(len(predicateMap.keys())))
        
        #make sure that rare predicates are kicked out.
        dontList=[] 
        for key, value in predicateMap.items():
            if int(value["count"])<3:
                dontList.append(key) 
            else:
                print("predicate: ("+key+")"+typePair)
                for k, v in value.items():
                    if k != "count":
                        k=k.replace("::","#")
                        print(k+": "+str(v))
                print("\n")
        
        for key, value in nounPairMap.items():
            k = key
            k=k.replace("::","#")
            if set(value.keys()).intersection(set(dontList))!=None:
                for i in set(value.keys()).intersection(set(dontList)):
                    value["count"]=value["count"]-1
                    del value[i]
            elif int(value["count"])!=0:
                print("inv idx of "+k+" :"+str(value["count"]))
                for x,y in value.items():
                    if x != "count":
                        print("(" + x +")"+typePair)
        sys.stdout = orig_stdout
        f.close()            
           
        
        
if __name__ == "__main__":
#Find the predicates
    print("Hello preprocessor!")
    print("begin: ",datetime.datetime.now())
    p=Preprocess()
    
    p.generate_input("/disk/scratch_big/sweber/pipelineOutputTyped/all.txt", "/disk/scratch_big/sweber/germanPERSON#PERSONfull.txt","#PERSON#PERSON")
         
    print("end : ",datetime.datetime.now())

    
