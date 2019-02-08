#from main import intersection
import math
class VectorMap:
    def __init__(self):
        self.dict = {}
    
    def __iter__(self):
        return iter(self.dict)
    
    def keys(self):
        return self.dict.keys()
    
    def items(self):
        #for key, value in self.dict.items():
        return self.dict.items()
        #    return key, value
    
    def put(self,key, value):
        self.dict[key]=value
        return dict
    
    def get(self, key):
        return self.dict[key]
    
    def printVectorMap(self):
        for key, value in self.dict.items():
            print(str(key),str(value))
            
    def changeVectorsToOverlap(self,entitySet,intersection):
        #tMap maps the index of the entitySet to the index of the overlap set
        tMap=self.createTMap(entitySet,intersection)
        newVectorMap=VectorMap()
        for key,value in self.items():
            newVec=self.swap(value,tMap)
            if newVec!=[]:
                #newVectorMap[key]=newVec
                newVectorMap.put(key, newVec)
        return newVectorMap
    
    def createTMap(self,entitySet, intersection):
        tMap={}
        for i in entitySet:
            if i in intersection:
                tMap[entitySet.getIndex(i)]=intersection.index(i)
            else:
                tMap[entitySet.getIndex(i)]=None
        return tMap
    
    def swap(self,listOfTuples, tMap):
        newListOfTuples=[]
        for t in listOfTuples:
            if tMap.get(t[0])!=None:
                newListOfTuples.append((tMap.get(t[0]),t[1]))
        return newListOfTuples
    
    def calculatePredProb(self):
        predMap={}
        fullCountsMap={}
        for key, value in self.dict.items():
            count = 0
            for tu in value:
                count+=tu[1]
            fullCountsMap[key]=count
        
        #when the full counts map is done, calculate total number of pred
        numberOfAllPredicateOcurrences=0
        for value in fullCountsMap.values():
            numberOfAllPredicateOcurrences+=value
            
        #then fill pred map with percentages 
        for key,value in fullCountsMap.items():
            predMap[key]=value/numberOfAllPredicateOcurrences
              
        return predMap
    
    def calculteArgPairProb(self):
        pairMap={}
        fullCountsMap={}
        for value in self.dict.values():
            for tu in value:
                if tu[0] in fullCountsMap.keys():
                    fullCountsMap[tu[0]]+=tu[1]
                else:
                    fullCountsMap[tu[0]]=tu[1]
                    
        numberOfAllPairOcurrences=0
        for value in fullCountsMap.values():
            numberOfAllPairOcurrences+=value
            
        for key,value in fullCountsMap.items():
            pairMap[key]=value/numberOfAllPairOcurrences
            
        return pairMap
    
    def calculateTotalNumberOfRelations(self):
        for value in self.dict.values():
            count=0
            for tu in value:
                count+=tu[1]
        return count
    
    def changeVectorsToPmi(self):
        predMap=self.calculatePredProb()
        pairMap=self.calculteArgPairProb()
        #relMap={} maybe I dont need that? 
        totalNumberOfRelations=self.calculateTotalNumberOfRelations()
        
        newVectorMap=VectorMap()
        #walk trough old vector map and for each row put the new one in
        for key, value in self.dict.items():
            pPred=predMap[key]
            newListOfTuples=[]
            for tu in value:
                pArgPair=pairMap[tu[0]]
                pRel=tu[1]/totalNumberOfRelations
                PMI=math.log(pRel)-math.log(pPred)-math.log(pArgPair)
                newTuple=(tu[0],PMI)
                newListOfTuples.append(newTuple)
            newVectorMap.put(key, newListOfTuples)
        
        return newVectorMap
        
        
        
        
    
    