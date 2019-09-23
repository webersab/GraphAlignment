#standard
import codecs
import csv
import sys
from nltk.parse import DependencyGraph
#from theano.gof.lazylinker_c import actual_version
import itertools
#from dask.tests.test_distributed import cluster
sys.path.append("/disk/scratch_big/sweber/udpipe-1.1.0-bin")
#sys.path.append("/afs/inf.ed.ac.uk/user/s17/s1782911")
import pickle
#custom
import udpipe_model as udp
import datetime
from tqdm import tqdm
import pprint
from generalEntityTyping import GeneralEntityTyping
import socket
from pygermanet.germanet import load_germanet
import os
from itertools import chain
import numpy
import random
import time


#this method is fully taken from Lianes pipeline
def get_negation( dt, i, neg):
    """
    Check to see if the predicate is negated
    Look for the POS-tag "PTKNEG" and dependency "advmod"
    """
    if 'advmod' in dt.nodes[i]['deps']:
        # Check for negations at sub-level
        l = dt.nodes[i]['deps']['advmod']
        for n in l:
            if dt.nodes[n]['tag'] == 'PTKNEG':
                neg = True
        for n in l:
            neg = get_negation(dt, n, neg)
    return neg

def checkClusters(pred1,pred2,cluster,listOfFoundClusters):
    pred1C=0
    pred2C=0
    predicateSet=set()
    #if pred1!="sein" and pred2!="sein" and pred1!="sagen" and pred2!="sagen" and pred1!="gehen" and pred2!="gehen" and pred1!="haben" and pred2!="haben" :
    for predicate in cluster.predicates:
        if ("("+pred1 in str(predicate)):
            pred1C+=1 
            predicateSet.add(predicate)
        if ("("+pred2 in str(predicate)):
            pred2C+=1
            predicateSet.add(predicate)
    if (pred1C>0)and(pred2C>0):
        listOfFoundClusters.append(cluster)
        print(pred1,pred2,"in",cluster.typePair)
        return predicateSet,listOfFoundClusters
    else:
        return predicateSet,listOfFoundClusters


def controlForEntailmentSim(entailedPredicatesMap,foundEntailment,row,counterMap, mapOffalsePositives, mapOffalseNegatives):
    if foundEntailment:
        if row[0]=="entailment":   
            counterMap["truePositives"]+=1
            counterMap["entCounter"]+=1
            counterMap["hitcounter"]+=1
            counterMap["totalcounter"]+=1
        else:
            counterMap["falsePositives"]+=1
            counterMap["entCounter"]+=1
            counterMap["totalcounter"]+=1

            innerMap={}
            sentences=row[1]+row[2]
            predicates=[]
            sims=[]
            for key, value in entailedPredicatesMap:
                predicates.append(key)
                sims.append(value)
            innerMap["sentences"]=sentences
            innerMap["predicates"]=predicates
            innerMap["sims"]=sims
            mapOffalsePositives[counterMap["falsePositives"]]=innerMap
    else:
        if row[0]=="neutral":
            counterMap["trueNegatives"]+=1
            counterMap["hitcounter"]+=1
            counterMap["neuCounter"]+=1
            counterMap["totalcounter"]+=1
        else:
            counterMap["falseNegatives"]+=1
            counterMap["neuCounter"]+=1
            counterMap["totalcounter"]+=1
            
            innerMap2={}
            sentences=row[1]+row[2]
            predicates=[]
            sims=[]
            for key, value in entailedPredicatesMap:
                predicates.append(key)
                sims.append(value)
            
            innerMap2["sims"]= sims
            innerMap2["sentences"]=sentences
            innerMap2["predicates"]=predicates
            #innerMap2["parse"]=showDependencyParse(model, [row[1],row[2]])

            mapOffalseNegatives[counterMap["falseNegatives"]]=innerMap2
            
    return counterMap, mapOffalsePositives, mapOffalseNegatives
    
def controlForEntailment(listOfFoundClusters,row,firstPredicates,secondPredicates,mapOffalsePositives,mapOffalseNegatives,counterMap,typePairList,predicateSet):
    
    if len(listOfFoundClusters)>0:
        if row[0]=="entailment":   
            counterMap["truePositives"]+=1
            counterMap["entCounter"]+=1
            counterMap["hitcounter"]+=1
            counterMap["totalcounter"]+=1
        else:
            counterMap["falsePositives"]+=1
            counterMap["entCounter"]+=1
            counterMap["totalcounter"]+=1

            innerMap={}
            sentences=row[1]+row[2]
            firstPredicatesKeys=list(firstPredicates.keys())
            firstPredicatesKeys.extend(list(secondPredicates.keys()))
            predicates=(",".join(firstPredicatesKeys))
            s=""
            numberOfClusters=0
            numberOfPredicates=0
            for cluster in listOfFoundClusters:
                s+="||"
                numberOfClusters+=1
                for predicate in cluster.predicates:
                    s+=str(predicate) 
                    numberOfPredicates+=1
            innerMap["predicates in same cluster"]=str(predicateSet)
            innerMap["predicates per cluster"]=numberOfPredicates/numberOfClusters
            innerMap["sentences"]=sentences
            innerMap["predicates"]=predicates
            innerMap["numberofclusters"]=len(listOfFoundClusters)
            innerMap["TypePairList"]=set(typePairList)
            mapOffalsePositives[counterMap["falsePositives"]]=innerMap
    else:
        if row[0]=="neutral":
            counterMap["trueNegatives"]+=1
            counterMap["hitcounter"]+=1
            counterMap["neuCounter"]+=1
            counterMap["totalcounter"]+=1
        else:
            counterMap["falseNegatives"]+=1
            counterMap["neuCounter"]+=1
            counterMap["totalcounter"]+=1
            
            innerMap2={}
            sentences=row[1]+row[2]
            firstPredicatesKeys=list(firstPredicates.keys())
            firstPredicatesKeys.extend(list(secondPredicates.keys()))
            predicates=(",".join(firstPredicatesKeys))
            
            innerMap2["TypePairlist"]= set(typePairList)
            innerMap2["sentences"]=sentences
            innerMap2["predicates"]=predicates
            #innerMap2["parse"]=showDependencyParse(model, [row[1],row[2]])

            mapOffalseNegatives[counterMap["falseNegatives"]]=innerMap2

    return counterMap, mapOffalsePositives, mapOffalseNegatives

def controlForEntailmentInLevy(listOfFoundClusters,line,firstPredicates,secondPredicates,mapOffalsePositives,mapOffalseNegatives,counterMap,typePairList,predicateSet):
    
    if len(listOfFoundClusters)>0:
        if line[2]=="y":  
            print("HIT!") 
            counterMap["truePositives"]+=1
            counterMap["entCounter"]+=1
            counterMap["hitcounter"]+=1
            counterMap["totalcounter"]+=1
        else:
            counterMap["falsePositives"]+=1
            counterMap["entCounter"]+=1
            counterMap["totalcounter"]+=1

            innerMap={}
            sentences=line[0]+line[1]
            firstPredicatesKeys=list(firstPredicates.keys())
            firstPredicatesKeys.extend(list(secondPredicates.keys()))
            predicates=(",".join(firstPredicatesKeys))
            s=""
            numberOfClusters=0
            numberOfPredicates=0
            for cluster in listOfFoundClusters:
                s+="||"
                numberOfClusters+=1
                for predicate in cluster.predicates:
                    s+=str(predicate) 
                    numberOfPredicates+=1
            innerMap["predicates in same cluster"]=str(predicateSet)
            innerMap["predicates per cluster"]=numberOfPredicates/numberOfClusters
            innerMap["sentences"]=sentences
            innerMap["predicates"]=predicates
            innerMap["numberofclusters"]=len(listOfFoundClusters)
            innerMap["TypePairList"]=set(typePairList)
            mapOffalsePositives[counterMap["falsePositives"]]=innerMap
    else:
        if line[2]=="n":
            counterMap["trueNegatives"]+=1
            counterMap["hitcounter"]+=1
            counterMap["neuCounter"]+=1
            counterMap["totalcounter"]+=1
        else:
            counterMap["falseNegatives"]+=1
            counterMap["neuCounter"]+=1
            counterMap["totalcounter"]+=1
            
            innerMap2={}
            sentences=line[0]+line[1]
            firstPredicatesKeys=list(firstPredicates.keys())
            firstPredicatesKeys.extend(list(secondPredicates.keys()))
            predicates=(",".join(firstPredicatesKeys))
            
            innerMap2["TypePairlist"]= set(typePairList)
            innerMap2["sentences"]=sentences
            innerMap2["predicates"]=predicates
            #innerMap2["parse"]=showDependencyParse(model, [row[1],row[2]])

            mapOffalseNegatives[counterMap["falseNegatives"]]=innerMap2

    return counterMap, mapOffalsePositives, mapOffalseNegatives

def getSimilarities(typePair):
    
    if socket.gethostname()=="pataphysique.inf.ed.ac.uk":
        outputFolder="/disk/scratch_big/sweber/similarityTables/"
    elif socket.gethostname()=="ebirah.inf.ed.ac.uk":
        outputFolder="/group/project/s1782911/similarityTables/"
    elif socket.gethostname()=="darkstar.inf.ed.ac.uk":
        outputFolder="/disk/data/darkstar2/s1782911/similarityTables/"  
        
    type1=typePair[0]
    type2=typePair[1] 
        
    similaritiesPickleAddress= outputFolder+"german#"+type1+"#"+type2+"Similarities.dat"
    indexMapPickleAddress=outputFolder+"german#"+type1+"#"+type2+"reversedIndexMap.dat"
    similarities=[]
    reversedIndexMap={}
    
    try:
        with open(similaritiesPickleAddress, "rb") as f:
            similarities=pickle.load(f)
    except FileNotFoundError:
        print("Missing ")
    except EOFError:
        print("empty")

        
    try:
        with open(indexMapPickleAddress, "rb") as g:
            reversedIndexMap=pickle.load(g)
    except FileNotFoundError:
        print("Missing ")
    except EOFError:
        print("empty")
    
    return similarities, reversedIndexMap

def whereAmI():
    if socket.gethostname()=="pataphysique.inf.ed.ac.uk":
        return "/disk/scratch_big/sweber/outputPickles/"
    elif socket.gethostname()=="ebirah.inf.ed.ac.uk":
        return "/group/project/s1782911/outputPickles/"
    elif socket.gethostname()=="darkstar.inf.ed.ac.uk":
        return "/disk/data/darkstar2/s1782911/outputPickles/"
    
 
def getRightClusterList(typePair):
    clusterList=[]
    
    outputFolder=whereAmI()
       
    if typePair[0] == "NoSubj":
        type1="MISC"
    else:
        type1=typePair[0]
    if typePair[1]=="NoObj":
        type2="MISC"
    else:
        type2=typePair[1]
    
    pickleAddress=outputFolder+"german2#"+type1+"#"+type2+"2Clustered.dat" 
    #unpickle cluster list
    with open(pickleAddress, "rb") as f:
        clusterList=pickle.load(f)
    
    for cluster in clusterList:
        cluster.setTypePair(typePair)
    
    return clusterList
    
def decideCluster(typePairList):
    containsNull=False
    containsActual=False
    for i in typePairList:
        if i[0]=="noSubj" and i[1]=="noObj":
            containsNull=True
        if i[0].isupper() and i[1].isupper():
            containsActual=True
            actual=i
    if containsNull and containsActual:
        return actual
    else:
        return None
        

def testGermanSimilarities(xnliSlice,threshold):
    mapOffalsePositives={}
    mapOffalseNegatives={}
    score=0
    
    counterMap={
    "hitcounter":0,
    "totalcounter":0,
    "truePositives":0,
    "trueNegatives":0,
    "falsePositives":0,
    "falseNegatives":0,
    "entCounter":0,
    "neuCounter":0}
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(xnliSlice) as fd:
        rd = csv.reader(fd, delimiter="\t")
        for row in tqdm(rd,total=1660):
            # get all predicates and their possible type pairs from the sentences
            firstPredicates=extractPredicateFromSentence(model,row[1])
            secondPredicates=extractPredicateFromSentence(model,row[2])
            foundEntailment=False
            entailedPredicatesMap={}
            valueList1=list(firstPredicates.values())
            valueList2=list(secondPredicates.values())
            overlapOfTypes = [value for value in valueList1 if value in valueList2]
            typeSet=set()
            typeSet=list(chain.from_iterable(overlapOfTypes))
            if len(typeSet)>0:
                for typePair in typeSet:
                    similarities, reversedIndexMap = getSimilarities(typePair)
                    for pred1 in firstPredicates.keys():
                        for pred2 in secondPredicates.keys():
                            if ".2)" not in pred1:
                                pred1="("+pred1+".1,"+pred1+".2)"
                            if ".2)" not in pred2:
                                pred2="("+pred2+".1,"+pred2+".2)"
                            #print("predicates ",pred1,pred2)
                            if pred1 in str(reversedIndexMap.keys()) and pred2 in str(reversedIndexMap.keys()):
                                index1=reversedIndexMap[pred1]
                                index2=reversedIndexMap[pred2]
                                sim=similarities[index1][index2]
                                #print("sim ",sim)
                                if sim>threshold:
                                    foundEntailment=True
                                    entailedPredicatesMap[(pred1,pred2)]=sim
            counterMap, mapOffalsePositives, mapOffalseNegatives = controlForEntailmentSim(entailedPredicatesMap,foundEntailment, 
                                                                                           row,counterMap, mapOffalsePositives, mapOffalseNegatives)
                    
    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))  
    return score,mapOffalsePositives, mapOffalseNegatives         
 
    
def testGermanClusters(xnliSlice):

    mapOffalsePositives={}
    mapOffalseNegatives={}
    score=0
    
    counterMap={
    "hitcounter":0,
    "totalcounter":0,
    "truePositives":0,
    "trueNegatives":0,
    "falsePositives":0,
    "falseNegatives":0,
    "entCounter":0,
    "neuCounter":0}
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    sillyBaselineHits=0
    
    with open(xnliSlice) as fd:
        rd = csv.reader(fd, delimiter="\t")
        for row in tqdm(rd,total=1660):
            listOfFoundClusters=[]
            typePairList=[]
            #each predicate has a list of type pairs
            firstPredicates=extractPredicateFromSentence(model,row[1])
            secondPredicates=extractPredicateFromSentence(model,row[2])
            
            ##Pseudocode for silly baseline
            lst3 = [value for value in firstPredicates if value in secondPredicates] 
            if lst3!=[]:
                sillyBaselineHits+=1 
            
            totalPredicateSet=set()
            #for each combination of predictates from sentence one and two
            for pred1 in firstPredicates.keys():
                for pred2 in secondPredicates.keys():
                    #determine which cluster to pick dependent on predicate types
                    overlapOfTypes = [value for value in firstPredicates[pred1] if value in secondPredicates[pred2]] 
                    #typePairList.append(firstPredicates[pred1])
                    #typePairList.append("|")
                    #typePairList.append(secondPredicates[pred2])
                    typePairList=overlapOfTypes
                    if len(overlapOfTypes)>0:
                        #retrieve right cluster list
                        for typePair in set(overlapOfTypes):
                            clusterList=getRightClusterList(typePair)
                            for cluster in clusterList:
                                if len(cluster.predicates)<21:
                                    predicateSet,listOfFoundClusters=checkClusters(pred1,pred2,cluster,listOfFoundClusters)
                                    if predicateSet != set():
                                        for p in predicateSet:
                                            totalPredicateSet.add(p)
            counterMap, mapOffalsePositives, mapOffalseNegatives = controlForEntailment(listOfFoundClusters,row,firstPredicates,secondPredicates,
                                                                                           mapOffalsePositives,mapOffalseNegatives,counterMap, typePairList,totalPredicateSet)
            
    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))
        sillyBaselineScore=sillyBaselineHits/counterMap["totalcounter"]
        print(" silly score: ", str(sillyBaselineScore))

    return score,mapOffalsePositives, mapOffalseNegatives

def dependency_parse_to_graph(filename):
    """
    Read dependency parser output from file and construct graph
    """
    data = ''
    dtree = []
    with open(filename, 'r') as f:
        for line in f:
            if line[0] != '#':
                if 'root' in line:
                    elements = line.split('\t')
                    if elements[7] == 'root':
                        elements[7] = 'ROOT'
                        line = '\t'.join(elements)
                data += line
                if line == '\n':
                    dg = DependencyGraph(data)
                    dtree.append(dg)
                    data = ''
    return dtree


def parseToArray(testFile):
    array=[]
    with open(testFile) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            array.append(row)
    return array

def getTypePairforPredicate(d,predicate):
    subj=""
    obj=""
    
    #print(predicate)
    for i in d.nodes:
        if d.nodes[i]['lemma']==predicate:
            #print(d.nodes[i]['deps'])
            deps=d.nodes[i]['deps']
            if 'nsubj' in deps.keys():
                subjAddress=d.nodes[i]['deps']['nsubj']
                subj=d.nodes[subjAddress[0]]['lemma']
            elif 'nsubj:pass' in deps.keys() :
                subjAddress=d.nodes[i]['deps']['nsubj:pass']
                subj=d.nodes[subjAddress[0]]['lemma']
            elif 'csubj' in deps.keys() :
                subjAddress=d.nodes[i]['deps']['csubj']
                subj=d.nodes[subjAddress[0]]['lemma']
            elif 'dep' in deps.keys():
                subjAddress=d.nodes[i]['deps']['dep']
                subj=d.nodes[subjAddress[0]]['lemma']
            else:
                subj=""
            
            if 'obj' in deps.keys():
                objAddress=d.nodes[i]['deps']['obj']
                obj=d.nodes[objAddress[0]]['lemma']
            elif 'obl' in deps.keys():
                objAddress=d.nodes[i]['deps']['obl']
                obj=d.nodes[objAddress[0]]['lemma']
            #elif 'iobj' in deps.keys():
                #objAddress=d.nodes[i]['deps']['obl']
                #obj=d.nodes[objAddress[0]]['lemma']
    #print(subj,obj)            
    G = GeneralEntityTyping() 
    gn = load_germanet()         
    if subj!="":
        subjType=G.typeEntity(subj,gn)
    else:
        subjType="NoSubj"
    
    if obj!="":
        objType=G.typeEntity(obj,gn)
    else:
        objType="NoObj"
    #print(subjType,objType)
    return (subjType,objType)

def getAllTypePairsOfSentence(d): 
    G = GeneralEntityTyping() 
    gn = load_germanet() 
    typeList=[]
    foundEvent=False
    for j in d.nodes: 
        if d.nodes[j]['ctag']=='NOUN' or d.nodes[j]['ctag']=='PRON': 
            word=d.nodes[j]['lemma']
            time.sleep(.300)
            typ=G.typeEntity(word,gn)
            #stupid hack to make up for not having EventXEvent graph
            if typ=='EVENT' and not foundEvent: 
                typeList.append(typ)
                foundEvent=True
            elif typ!='EVENT':
                typeList.append(typ)        
    typeList=list(itertools.combinations(typeList,2))
    return typeList

def treeToPredMapSimple(d):
    mapOfPredicates={}
    typePairList=getAllTypePairsOfSentence(d)
    for i in d.nodes:
        if d.nodes[i]['ctag']=='VERB' or  d.nodes[i]['tag']=='VVPP':
            predicate=d.nodes[i]['lemma']
            if get_negation(d, i, False):
                predicate="NEG_"+predicate
            mapOfPredicates[predicate]=typePairList
    return mapOfPredicates

def treeToPredMap(d):
    #in the simplest case root is predicate
    mapOfPredicates={}
    root=d.nodes[0]['deps']['ROOT'][0]
    predicate=d.nodes[root]['lemma']
    if get_negation(d, root, False):
        predicate="NEG_"+predicate
    typePair=getTypePairforPredicate(d,predicate)
    mapOfPredicates[predicate]=typePair
    #other cases
    #if d.nodes[root]['ctag'] != 'VERB':
    for n in d.nodes:
        #adj or noun plus 'be'
        if d.nodes[n]['ctag']=='VERB' and (d.nodes[n]['lemma']=='sein'):
            predicate=d.nodes[root]['word']
            predicate=predicate+'.sein'
            if get_negation(d, root, False) and not ("NEG_" in predicate):
                predicate="NEG_"+predicate
            if predicate not in mapOfPredicates.keys():
                typePair=getTypePairforPredicate(d,predicate)
                mapOfPredicates[predicate]=typePair
        elif d.nodes[n]['ctag']=='VERB' and (d.nodes[n]['lemma']!='sein'):
            if get_negation(d, root, False) and not ("NEG_" in predicate):
                predicate="NEG_"+predicate
            if predicate not in mapOfPredicates.keys():
                typePair=getTypePairforPredicate(d,predicate)
                mapOfPredicates[predicate]=typePair
                
    return mapOfPredicates

def showDependencyParse(model, sentences):
    strArray=[]
    for sentence in sentences:
        sent = model.tokenize(sentence)
        for s in sent:
            model.tag(s)
            model.parse(s)
        conllu = model.write(sent, "conllu")
        #print(conllu)
        """
        outfile = "conllOut.txt"
        with codecs.open(outfile, 'w', 'utf-8') as o:
            o.write(conllu)
        #print("wrote conllu file")
        
        #predicateList=[]
        dtree = dependency_parse_to_graph("conllOut.txt")
        #i=0

        for d in dtree:
            dt=d.tree()
            stri=dt.pprint()
            strArray.append(stri)
        """
    return strArray
    

def extractPredicateFromSentence(model, sentence):
    sent = model.tokenize(sentence)
    for s in sent:
        model.tag(s)
        model.parse(s)
    conllu = model.write(sent, "conllu")
    ran=random.randint(1,50000)
    outfile = "conllOut"+str(ran)+".txt"
    with codecs.open(outfile, 'w', 'utf-8') as o:
        o.write(conllu)
    #print("wrote conllu file")
    
    #predicateList=[]
    predicateMap={}
    dtree = dependency_parse_to_graph("conllOut"+str(ran)+".txt")
    i=0
    for d in dtree:
        predicateMap=treeToPredMapSimple(d)
    #print("done extracting predicates") 
    os.remove("conllOut"+str(ran)+".txt")
    #pp = pprint.PrettyPrinter()
    #pp.pprint(predicateMap)
    return predicateMap

def extractPredicatesFromSentenceList(language,sentenceList):
    print("extracting predicates")
    sentenceToPredicateMap={}
    if language=="de":
        modelfile ="germanModel.udpipe"
    elif language=="en":
        modelfile ="englishModel.udpipe"

    model = udp.UDPipeModel(modelfile)
    for x in sentenceList:
        sent = model.tokenize(x)
        for s in sent:
            model.tag(s)
            model.parse(s)
        conllu = model.write(sent, "conllu")
        outfile = "conllOut"+language+".txt"
        with codecs.open(outfile, 'a', 'utf-8') as o:
            o.write(conllu)
    print("wrote conllu file")

    sentenceToPredicateMap={}
    dtree = dependency_parse_to_graph("conllOut"+language+".txt")
    i=0
    for d in dtree:
        predicateList=treeToPredMap(d)
        sentenceToPredicateMap[i]=predicateList
        i+=1
    print("done extracting predicates") 
    return sentenceToPredicateMap


def testWithXNLI(testFile,listOfTuplesOfClusters,languagePair):
    mapOfJudgements={}
    #parse the tsv into a 2d array containing one entailment sentence pair per row. 
    inputArray=parseToArray(testFile)
    if [] in inputArray:
        inputArray.remove([])
    print("parsed text to array")   
    ##depending on the language pair zip the array to two lists
    if languagePair=="enDe":
        englishHalf, germanHalf= zip(*inputArray)
    elif languagePair=="deEn":
        germanHalf, englishHalf= zip(*inputArray)
    print("english")
    englishMapping=extractPredicatesFromSentenceList("en", englishHalf)
    print("german")
    germanMapping=extractPredicatesFromSentenceList("de", germanHalf)
    
    #if predicates in same cluster entail
    #if predicates not in same cluster contradict
    print(englishMapping)
    print(germanMapping)
    for el in listOfTuplesOfClusters:
        print(el[0].predicates,el[1].predicates, el[2])
    
    print("start looking in map")
    for i in englishMapping:
        englishPredicates=englishMapping[i]
        germanPredicates=germanMapping[i]
        for tup in listOfTuplesOfClusters:
            print(englishPredicates,germanPredicates,tup[0].predicates,tup[1].predicates)
            list1=tup[0].predicates
            list1.append(tup[1].predicates)
            #print(list1)
            if (englishPredicates in list1 and germanPredicates in list1):
                mapOfJudgements[i]=1
            else:
                mapOfJudgements[i]=0
    #add option for neutral based on other criteria as well? TODO
    
    return mapOfJudgements

def checkIfPredicatePairInCluster(typePair,pred1,pred2):
    clusterList=getRightClusterList(typePair)
    listOfFoundClusters=[]
    for cluster in clusterList:
        predicateSet,listOfFoundClusters=checkClusters(pred1,pred2,cluster,listOfFoundClusters)
    if listOfFoundClusters ==[]:
        print("NOPE")
    else:
        for cl in listOfFoundClusters:
            print("cluster: ",cl.predicates)
            print("length: ",len(cl.predicates))
    

def testWithLevy(inFile):
    mapOffalsePositives={}
    mapOffalseNegatives={}
    score=0
    
    counterMap={
    "hitcounter":0,
    "totalcounter":0,
    "truePositives":0,
    "trueNegatives":0,
    "falsePositives":0,
    "falseNegatives":0,
    "entCounter":0,
    "neuCounter":0}
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(inFile) as file:
        for line in tqdm(file,total=4894):
            line=line.rstrip()
            line=line.split(". ")
            print("line ",line)
            if len(line)<3:
                print("oopsie! ",line)
                continue
            
            listOfFoundClusters=[]
            typePairList=[]
            
            #each predicate has a list of type pairs
            firstPredicates=extractPredicateFromSentence(model,line[0])
            secondPredicates=extractPredicateFromSentence(model,line[1])
            totalPredicateSet=set()
            #for each combination of predictates from sentence one and two
            for pred1 in firstPredicates.keys():
                for pred2 in secondPredicates.keys():
                    #determine which cluster to pick dependent on predicate types
                    print(firstPredicates[pred1],secondPredicates[pred2])
                    overlapOfTypes = [value for value in firstPredicates[pred1] if value in secondPredicates[pred2]] 
                    #typePairList.append(firstPredicates[pred1])
                    #typePairList.append("|")
                    #typePairList.append(secondPredicates[pred2])
                    """
                    if len(overlapOfTypes)>0:
                        typePairList=overlapOfTypes
                    else:
                        typePairList = list(set(firstPredicates[pred1]) | set(secondPredicates[pred2])) 
                        
                    if len(typePairList)==0:
                        typePairList=[("MISC","MISC")]
                    """
                    typePairList=list(itertools.product(["PERSON","LOCATION","ORGANIZATION","EVENT","MISC"],repeat=2))
                    typePairList.remove(("EVENT","EVENT"))
                    
                    #retrieve right cluster list
                    for typePair in set(typePairList):
                        clusterList=getRightClusterList(typePair)
                        #print("got cluster list")
                        #print("length ",len(clusterList))
                        for cluster in clusterList:
                            if len(cluster.predicates)<21:
                                predicateSet,listOfFoundClusters=checkClusters(pred1,pred2,cluster,listOfFoundClusters)
                                if predicateSet != set():
                                    for p in predicateSet:
                                        totalPredicateSet.add(p)
                #print(" total predicates Set", totalPredicateSet)
                print(" list of found clusters ",listOfFoundClusters)
            counterMap, mapOffalsePositives, mapOffalseNegatives = controlForEntailmentInLevy(listOfFoundClusters,line,firstPredicates,secondPredicates,
                                                                                           mapOffalsePositives,mapOffalseNegatives,counterMap, typePairList,totalPredicateSet)
            
    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))

    return score,mapOffalsePositives, mapOffalseNegatives


def testWithLevyGermanetBaseline(inFile):
    gn = load_germanet()
    print("loaded")
    
    hitCounter=0
    failCounter=0
    
    yCount=0
    nCount=0
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(inFile) as file:
        for line in tqdm(file,total=506):
            line=line.rstrip()
            line=line.split(". ")
            print(line)
            if len(line)<3:
                print("oopsie! ",line)
                continue
            
            if line[2]=="y":
                yCount+=1
            else:
                nCount+=1
            
            #each predicate has a list of type pairs
            firstPredicates=extractPredicateFromSentence(model,line[0])
            secondPredicates=extractPredicateFromSentence(model,line[1])
            #for each combination of predictates from sentence one and two
            hit=False
            for pred1 in firstPredicates.keys():
                for pred2 in secondPredicates.keys():
                    print(pred1,pred2)
                    #check if pred1 is in hypernym path of pred2
                    #lemmatized= gn.lemmatise(pred2)[0]+'.v.1'
                    lemmatized= gn.lemmatise(pred2)[0]
                    print(lemmatized)
                    try:
                        synset=gn.synsets(lemmatized)
                        hypset=gn.synset(lemmatized+'.v.1').hypernym_paths
                        if pred1 in str(synset) or pred1 in str(hypset):
                            hit=True
                            #print(synset,pred1)
                    except:
                        print("woop")
            if hit and line[2]=="y":
                hitCounter+=1
            else: 
                failCounter+=1
            
    print("hits: ",hitCounter," fails: ",failCounter, " Score: ", (hitCounter/(hitCounter+failCounter)))
    print( " yes: ",yCount," no: ",nCount)
            
if __name__ == "__main__":
    #checkIfPredicatePairInCluster(('PERSON', 'MISC'), "sehen", "ansehen")
    print("Hello XNLITest!")
    print("begin: ",datetime.datetime.now())
    """
    gn = load_germanet()
    print("loaded")
    lemmatized= gn.lemmatise("erscheint")[0]+'.v.1'
    print(lemmatized)
    try:
        synset=gn.synset(lemmatized).hypernym_paths
        print(synset)
    except:
        print("woop")
    """
    score,mapOffalsePositives, mapOffalseNegatives=testGermanClusters("/disk/scratch_big/sweber/15Handcrafted.tsv")
    
    
    pp = pprint.PrettyPrinter(stream=open("xnliDetailedoutputFalsePos15Handcrafted.txt",'w'))
    pp.pprint(mapOffalsePositives)
    pp1 = pprint.PrettyPrinter(stream=open("xnliDetailedoutputFalseNeg15Handracted.txt",'w'))
    pp1.pprint(mapOffalseNegatives)
    

    
    
