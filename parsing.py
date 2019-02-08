import re 
import pickle
from linker import Linker
from tqdm import tqdm

class Parsing:
    
    def extractEntities(self,string):
        entity = re.search('(.*): \d', string)
        entity=entity.group(1)
        return entity
    
    def extractPredicate(self,string,typePair):
        predicate = re.search('predicate: (.*)'+typePair+'.*', string)
        predicate=predicate.group(1)
        return predicate
    
    def extractCount(self,string):
        count=re.search('.*: (.*).*', string)
        count=count.group(1)
        return int(float(count))
    
    def parse(self, fileName,entitySet,vectorMap,typePair):
        #unpickling dict for cheap link
        #with open("/group/project/s1782911/graphAlignmentOutputData/entityDictionary.dat", "rb") as r:
            #entDict=pickle.load(r)
        print("parsing")
        with open(fileName) as f:
            for line in f:
                if 'inv idx' in line:
                    break
                elif 'predicate' in line:
                    predicate=self.extractPredicate(line,typePair)
                    currentVector = []
                    vectorMap.put(predicate,currentVector)
                elif ': ' in line and 'num preds' not in line:
                    #if linking:extract single words
                    #if linking: link single words
                    #if linking: concatenate the entity links
                    
                    entities=self.extractEntities(line)
                    
                    l = Linker()
                    #entities=l.cheapLink(origEntities, entDict)
                    count=self.extractCount(line)
                    index = entitySet.getIndex(entities)
                    pair = (index,count)
                    currentVector.append(pair)
        print("done parsing")
        return vectorMap, entitySet


