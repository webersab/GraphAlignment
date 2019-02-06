#standard
import codecs
import csv
import sys
from nltk.parse import DependencyGraph
sys.path.append("/disk/scratch_big/sweber/udpipe-1.1.0-bin")
#sys.path.append("/afs/inf.ed.ac.uk/user/s17/s1782911")
import pickle
#custom
import udpipe_model as udp
import datetime
from tqdm import tqdm
import pprint

def testGermanClusters(clusterListPickle,xnliSlice):

    mapOfFalsePositivesEntailment={}
    mapOfFalsePositivesNeutral={}
    score=0

    #unpickle cluster list
    with open(clusterListPickle, "rb") as f:
        clusterList=pickle.load(f)
    print("unpickled")
    hitcounter=0
    totalcounter=0
    
    truePositivesEnt=0
    truePositivesNeu=0
    falsePositivesEnt=0
    falsePositivesNeu=0
    
    entCounter=0
    neuCounter=0
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(xnliSlice) as fd:
        rd = csv.reader(fd, delimiter="\t")
        for row in tqdm(rd,total=1660):
            listOfFoundClusters=[]
            firstPredicates=extractPredicateFromSentence(model,row[1])
            secondPredicates=extractPredicateFromSentence(model,row[2])
            #print("predicates: ", str(firstPredicates), str(secondPredicates))
        #for each combination of predictates from sentence one and two
            #localHitCounter=0
            for pred1 in firstPredicates:
                for pred2 in secondPredicates:
                    for cluster in clusterList:
                        pred1C=0
                        pred2C=0
                        for predicate in cluster.predicates:
                            #print("p in cluster: ", str(predicate))
                            if (pred1 in str(predicate)):
                                pred1C+=1 
                            if (pred2 in str(predicate)):
                                pred2C+=1
                        if (pred1C>0)and(pred2C>0):
                            #localHitCounter+=1
                            #print("local hit")
                            listOfFoundClusters.append(cluster)
            #print("Local hits in this row ",localHitCounter)
            #print("row 0 ",row[0])
            if len(listOfFoundClusters)>0:
                if row[0]=="entailment":   
                    truePositivesEnt+=1
                    entCounter+=1
                    hitcounter+=1
                    totalcounter+=1
                else:
                    falsePositivesEnt+=1
                    #print("fals pos ent",falsePositivesEnt)
                    hitcounter+=1
                    entCounter+=1
                    
                    innerMap={}
                    sentences=row[1]+row[2]
                    firstPredicates.extend(secondPredicates)
                    predicates=(",".join(firstPredicates))
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
                    #innerMap["clusters"]=s
                    innerMap["number of clusters"]=len(listOfFoundClusters)
                    mapOfFalsePositivesEntailment[falsePositivesEnt]=innerMap
            else:
                if row[0]=="neutral":
                    truePositivesNeu+=1
                    #print("true pos neu",truePositivesNeu)
                    neuCounter+=1
                else:
                    falsePositivesNeu+=1
                    neuCounter+=1
                    #print("false pos neu",falsePositivesNeu)
                    innerMap2={}
                    sentences=row[1]+row[2]
                    firstPredicates.extend(secondPredicates)
                    predicates=(",".join(firstPredicates))
                    #parse=
                    
                    innerMap2["sentences"]=sentences
                    innerMap2["predicates"]=predicates
                    innerMap2["parse"]=showDependencyParse(model, [row[1],row[2]])

                    mapOfFalsePositivesNeutral[falsePositivesNeu]=innerMap2
                #print(firstPredicates,secondPredicates)
    if totalcounter>0:
        score=hitcounter/totalcounter
        print("ent true positives "+str(truePositivesEnt)+" of "+str(entCounter)+", "+(str(float(truePositivesEnt)/float(entCounter))))
        print("ent false positives "+str(falsePositivesEnt)+" of "+str(entCounter)+", "+(str(float(falsePositivesEnt)/float(entCounter))))
        print("neu true positives "+str(truePositivesNeu)+" of "+str(neuCounter)+", "+(str(float(truePositivesNeu)/float(neuCounter))))
        print("neu false positives "+str(falsePositivesNeu)+" of "+str(neuCounter)+", "+(str(float(falsePositivesNeu)/float(neuCounter))))
    return score,mapOfFalsePositivesEntailment, mapOfFalsePositivesNeutral

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

def treeToPredList(d):   
    #in the simplest case root is predicate
    listOfPredicates=[]
    root=d.nodes[0]['deps']['ROOT'][0]
    predicate=d.nodes[root]['lemma']
    listOfPredicates.append(predicate)
    #other cases
    #if d.nodes[root]['ctag'] != 'VERB':
    for n in d.nodes:
        #adj or noun plus 'be'
        if d.nodes[n]['ctag']=='VERB' and (d.nodes[n]['lemma']=='sein' or d.nodes[n]['lemma']=='be'):
            predicate=d.nodes[root]['word']
            predicate=predicate+'.sein'
            listOfPredicates.append(predicate)
        elif d.nodes[n]['ctag']=='VERB' and (d.nodes[n]['lemma']!='sein'or d.nodes[n]['lemma']=='be'):
            listOfPredicates.append(d.nodes[n]['lemma'])
        #print(predicate)
        #print(listOfPredicates)
    #else:
        #listOfPredicates.append(predicate)
        
    return listOfPredicates

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
    
    predicateList=[]
    dtree = dependency_parse_to_graph("conllOut.txt")
    i=0
    for d in dtree:
        predicateList=treeToPredList(d)
    #print("done extracting predicates") 
    return predicateList

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
        predicateList=treeToPredList(d)
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
    
    score, mapOfHits, mapOfFails=testGermanClusters("clusteredGerman.dat","deXNLINoContra.tsv")
    
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
