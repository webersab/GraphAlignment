import vectorMap as vm

class Cluster:
    def __init__(self, predicates=None,vector=None, label=None,language=None, typePair=None):
        self.predicates = predicates
        self.vector = vector
        self.label = label
        self.language = language
        self.typePair = typePair
    
    def setTypePair(self,typePair):
        self.typePair = typePair
    
    # key of labelDict is in cluster label, value is a list of vectorMaps
    def fillLabelDict(self,G):
        labelDict={}
        for i in G.nodes.data():
            if i[1]['label'] not in labelDict:
                vectorMapList = []
                vector = i[1]['vector']
                vectorMap = vm.VectorMap()
                vectorMap.put(i[0],vector)
                vectorMapList.append(vectorMap)
                labelDict[i[1]['label']]=vectorMapList
            else:
                vectorMapList= labelDict[i[1]['label']]
                vector = i[1]['vector']
                vectorMap = vm.VectorMap()
                vectorMap.put(i[0],vector)
                vectorMapList.append(vectorMap)
                labelDict[i[1]['label']]=vectorMapList 
        return labelDict
    
    def collectTwinTuples(self,tup, listOfTuples):
        listOfDoubleTuples= [ (x,y) for x, y in listOfTuples if x  == tup[0] ]
        return listOfDoubleTuples
    
    def mergeTuples(self,listOfTuples):
        secondElement=0
        for i in listOfTuples:
            firstElement=i[0]
            secondElement=secondElement+i[1]
        return (firstElement, secondElement)
    
    def mergeVectors(self,listOfVectorMaps):
        listOfTuples = []
        for i in listOfVectorMaps:
            for key, value in i.items():
                listOfTuples.extend(value)
        newListOfTuples=[]
        for tup in listOfTuples[:]:
            a = self.collectTwinTuples(tup, listOfTuples)
            if len(a)>1:
                newTuple=self.mergeTuples(a)   
            else:
                newTuple=a
            if not isinstance(newTuple, list):
                newTuple=[newTuple]  
            newListOfTuples.extend(newTuple)
            #listOfTuples.remove(tup)
        newListOfTuples=list(set(newListOfTuples))
        return newListOfTuples
    
    def removeAllDuplicatesOfTuple(self, listOfTuples, tup):
        newListOfTuples=[tup]
        for j in listOfTuples:
            if j != tup:
                newListOfTuples.extend(j)
        return newListOfTuples
    
    def collectPredicates(self,listOfVectorMaps):
        listOfPredicates=[]
        for i in listOfVectorMaps:
            for key, value in i.items():
                listOfPredicates.append(key)
        return listOfPredicates
    
    def printClusterPredicates(self):
        print(self.predicates)
    
    def getClustersFromGraph(self,G, language):
        clusterList = []
        labelDict = self.fillLabelDict(G)
        for key, value in labelDict.items():
            clusterVector=self.mergeVectors(value)
            predicates=self.collectPredicates(value)
            cluster=Cluster(predicates,clusterVector,key,language)
            clusterList.append(cluster)
        return clusterList