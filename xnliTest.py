#standard
import codecs
import csv
import sys
from nltk.parse import DependencyGraph
sys.path.append("/afs/inf.ed.ac.uk/user/s17/s1782911/udpipe-1.1.0-bin")
import pickle
#custom
import udpipe_model as udp

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
    #other cases
    if d.nodes[root]['ctag'] != 'VERB':
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
    else:
        listOfPredicates.append(predicate)
    return listOfPredicates

def extractPredicates(language,sentenceList):
    """print("extracting predicates")
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
    print("wrote conllu file")"""

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
    englishMapping=extractPredicates("en", englishHalf)
    print("german")
    germanMapping=extractPredicates("de", germanHalf)
    
    #if predicates in same cluster entail
    #if predicates not in same cluster contradict
    print(englishMapping)
    print(germanMapping)
    for el in listOfTuplesOfClusters:
        print(el[0].predicates,el[1].predicates, el[2])
    
    """print("start looking in map")
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
                mapOfJudgements[i]=0"""
    #add option for neutral based on other criteria as well? TODO
    
    return mapOfJudgements

def compareJudgements(goldJudgements,myJudgements):
    #make a list from the gold judgement input file
    #totalJudgements=len(goldList)
    #if golList[i]==myList[i] counter+=1
    #finalPercentage=counter/totalJudgements
    return None

if __name__ == "__main__":
    print("hup hup")
    with open("alignedList.dat", "rb") as f:
        clusterTupleList=pickle.load(f)
    print("got the pickle")
    mapOfJudegements=testWithXNLI("enDeXnli.txt", clusterTupleList, "enDe")
    print(mapOfJudegements)
