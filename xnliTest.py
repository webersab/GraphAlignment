#standard
import codecs
import csv
import sys
from nltk.parse import DependencyGraph
from theano.gof.lazylinker_c import actual_version
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
    for predicate in cluster.predicates:
        if ("("+pred1+".1" in str(predicate)):
            pred1C+=1 
            predicateSet.add(str(predicate))
        if ("("+pred2+".1" in str(predicate)):
            pred2C+=1
            predicateSet.add(str(predicate))
    if (pred1C>0)and(pred2C>0):
        listOfFoundClusters.append(cluster)
        print(pred1,pred2,"in",cluster.typePair)
        print(str(predicateSet))
        return listOfFoundClusters
    else:
        return listOfFoundClusters
    
def controlForEntailment(listOfFoundClusters,row,firstPredicates,secondPredicates,mapOffalsePositives,mapOffalseNegatives,counterMap,typePairList):
    
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
            innerMap["predicates per cluster"]=numberOfPredicates/numberOfClusters
            innerMap["sentences"]=sentences
            innerMap["predicates"]=predicates
            innerMap["number of clusters"]=len(listOfFoundClusters)
            innerMap["Type Pair List"]=set(typePairList)
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
            
            innerMap2["Type Pair list"]= set(typePairList)
            innerMap2["sentences"]=sentences
            innerMap2["predicates"]=predicates
            #innerMap2["parse"]=showDependencyParse(model, [row[1],row[2]])

            mapOffalseNegatives[counterMap["falseNegatives"]]=innerMap2

    return counterMap, mapOffalsePositives, mapOffalseNegatives
 
def getRightClusterList(typePair):
    clusterList=[]
    
    if socket.gethostname()=="pataphysique.inf.ed.ac.uk":
        outputFolder="/disk/scratch_big/sweber/outputPickles/"
    elif socket.gethostname()=="ebirah.inf.ed.ac.uk":
        outputFolder="/group/project/s1782911/outputPickles/"
    elif socket.gethostname()=="darkstar.inf.ed.ac.uk":
        outputFolder="/disk/data/darkstar2/s1782911/outputPickles/"
       
    if typePair[0] == "NoSubj":
        type1="MISC"
    else:
        type1=typePair[0]
    if typePair[1]=="NoObj":
        type2="MISC"
    else:
        type2=typePair[1]
    
    pickleAddress=outputFolder+"german#"+type1+"#"+type2+"Clustered.dat" 
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
    
    with open(xnliSlice) as fd:
        rd = csv.reader(fd, delimiter="\t")
        for row in tqdm(rd,total=1660):
            listOfFoundClusters=[]
            typePairList=[]
            #each predicate has a list of type pairs
            firstPredicates=extractPredicateFromSentence(model,row[1])
            secondPredicates=extractPredicateFromSentence(model,row[2])

            #for each combination of predictates from sentence one and two
            for pred1 in firstPredicates.keys():
                for pred2 in secondPredicates.keys():
                    #determine which cluster to pick dependent on predicate types
                    overlapOfTypes = [value for value in firstPredicates[pred1] if value in secondPredicates[pred2]] 
                    typePairList=overlapOfTypes
                    if len(overlapOfTypes)>0:
                        #retrieve right cluster list
                        for typePair in set(overlapOfTypes):
                            clusterList=getRightClusterList(typePair)
                            for cluster in clusterList:
                                listOfFoundClusters=checkClusters(pred1,pred2,cluster,listOfFoundClusters)

            counterMap, mapOffalsePositives, mapOffalseNegatives = controlForEntailment(listOfFoundClusters,row,firstPredicates,secondPredicates,
                                                                                           mapOffalsePositives,mapOffalseNegatives,counterMap, typePairList)
            
    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))
        #print("true positives "+str(truePositives)+" of "+str(entCounter)+", "+(str(float(truePositives)/float(entCounter))))
        #print("false positives "+str(falsePositives)+" of "+str(entCounter)+", "+(str(float(falsePositives)/float(entCounter))))
        #print("true negatives "+str(trueNegatives)+" of "+str(neuCounter)+", "+(str(float(trueNegatives)/float(neuCounter))))
        #print("false negatives "+str(falseNegatives)+" of "+str(neuCounter)+", "+(str(float(falseNegatives)/float(neuCounter))))
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
        if d.nodes[i]['ctag']=='VERB':
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
    outfile = "conllOut.txt"
    with codecs.open(outfile, 'w', 'utf-8') as o:
        o.write(conllu)
    #print("wrote conllu file")
    
    #predicateList=[]
    predicateMap={}
    dtree = dependency_parse_to_graph("conllOut.txt")
    i=0
    for d in dtree:
        predicateMap=treeToPredMapSimple(d)
    #print("done extracting predicates") 
    
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

def compareJudgements(goldJudgements,myJudgements):
    #make a list from the gold judgement input file
    #totalJudgements=len(goldList)
    #if golList[i]==myList[i] counter+=1
    #finalPercentage=counter/totalJudgements
    return None

if __name__ == "__main__":
    print("Hello XNLITest!")
    print("begin: ",datetime.datetime.now())
    
    score, mapOfHits, mapOfFails=testGermanClusters("deXNLINoContra.tsv")
    
    pp = pprint.PrettyPrinter(stream=open("xnliDetailedoutputFalsePosEnt.txt",'w'))
    pp.pprint(mapOfHits)
    pp1 = pprint.PrettyPrinter(stream=open("xnliDetailedoutputFalsePosNeu.txt",'w'))
    pp1.pprint(mapOfFails)
    
    #pp.pprint(mapOfHits)
    print("The score is: "+str(score))
    #pp.pprint(mapOfFails)
    
    
    
    """
    print("hup hup")
    with open("alignedList.dat", "rb") as f:
        clusterTupleList=pickle.load(f)
    print("got the pickle")
    mapOfJudegements=testWithXNLI("enDeXnli.txt", clusterTupleList, "enDe")
    print(mapOfJudegements)
    """
