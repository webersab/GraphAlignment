#from main import intersection
class VectorMap:
    def __init__(self):
        self.dict = {}
    
    def __iter__(self):
        return iter(self.dict)
    
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
        tMap=self.createTMap(entitySet,intersection)
        newVectorMap={}
        for key,value in self.items():
            newVec=self.swap(value,tMap)
            if newVec!=[]:
                newVectorMap[key]=newVec
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
        
        
    
    