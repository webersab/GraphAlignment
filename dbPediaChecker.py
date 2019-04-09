# coding=utf-8

import requests
import pickle
import os
import pprint
import time
import string
from tqdm import tqdm

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
def getAttributesFomInternet(entity,lang):
    if lang=="de":
        url = 'http://de.dbpedia.org/resource/'
        propUrl='http://de.dbpedia.org/property/'
    else:
        url = 'http://dbpedia.org/resource/'
        propUrl='http://dbpedia.org/property/'
        
    r = requests.get(url+entity)
    
    foundList=[]
    for line in r.text.split(sep="\n"):
        if lang=="de":
            found=find_between(line, "<li><span class=\"literal\"><a class=\"uri\" rev=\"prop-de:", "\"")
            found=propUrl+found
            
            if (found!=propUrl) and (found not in foundList):
                foundList.append(found)
        else:
            found=find_between(line, "</ul></td></tr><tr class=\"even\"><td class=\"property\"><a class=\"uri\" href=\"", "\"")
            if (found!="") and ("ontology" not in found) and found not in foundList:
                foundList.append(found)
    return foundList
    
def getAttributesFromFile(entity):
    foundList=[]
    filePath="/group/project/s1782911/infobox_properties_de.ttl"
    propUrl='http://de.dbpedia.org/property/'
    toFind='<http://de.dbpedia.org/resource/'+entity+">"
    
    with open(filePath, 'r') as inF:
        for line in inF:
            if toFind in line:
                #print(line)
                found=find_between(line, propUrl, ">")
                found=propUrl+found
                #print(found)
                if (found!=propUrl) and (found not in foundList):
                    foundList.append(found)
                
    print(foundList)
    
def getGermanLink(entity):
    firstLetter=entity[0].lower()
    if firstLetter in list(string.ascii_lowercase):
        filePath="/disk/scratch_big/sweber/alphabetBatches/InterLanguage_"+firstLetter
        with open(filePath, 'r') as inF:
            for line in inF:
                if "http://dbpedia.org/resource/"+entity in line and "http://de.dbpedia.org/resource/" in line:
                    link=find_between(line, "http://de.dbpedia.org/resource/", "> .")
                    link="http://de.dbpedia.org/resource/"+link
                    print(link)
                    return link
    return ""
    
def constructEnglishEntityDict():
    englishEntDict={}
    identifier=0
    for filename in os.listdir("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f"):
        with open("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f/"+filename, 'r') as inF:
            for line in inF:
                if "inv idx of" in line:
                    start = time.time()
                    doubleEnt=find_between(line, "inv idx of", " :")
                    enti=doubleEnt.split(sep="#")
                    for ent in enti:
                        ent=ent.lstrip()
                        ent=ent.title()
                        ent=ent.replace(" ", "_")
                        if ent not in englishEntDict.keys():
                            print(ent)
                            newDict={}
                            newDict["identifier"]=identifier
                            identifier+=1
                            newDict["URI"]='http://dbpedia.org/resource/'+ent
                            newDict["attributes"]=getAttributesFomInternet(ent,"en")
                            newDict["germanLink"]=getGermanLink(ent)
                            englishEntDict[ent]=newDict
                    end = time.time()
                    print("one loop took", end - start)
    with open("/disk/scratch/sweber/englishEntDict.dat", "wb") as f:
            pickle.dump(englishEntDict, f)
    return englishEntDict

def createAlphabetBatchesForInterlanguage():
    openFilesMap={}
    for x in list(string.ascii_lowercase):
        f = open("/disk/scratch_big/sweber/alphabetBatches/InterLanguage_"+str(x), 'a')
        f.write("")
        openFilesMap[str(x)]=f
        
    filePath="/disk/scratch_big/sweber/interlanguage_links_en.ttl"
    with open(filePath, 'r') as inF:
        for line in tqdm(inF, total=44122707, unit="lines"):
            if "http://de.dbpedia.org/resource/" in line:
                entity=find_between(line, "<http://dbpedia.org/resource/", ">")
                firstLetter=entity[0].lower()
                if firstLetter!="/" and firstLetter in openFilesMap.keys():
                    f = openFilesMap[firstLetter]
                    f.write(line)

                
                #print(line)

def createAlphabetBatchesForAttributes():
    print("HupHUP")
    openFilesMap={}
    for x in list(string.ascii_lowercase):
        f = open("/disk/scratch_big/sweber/alphabetBatches/Attribute_"+str(x), 'a')
        f.write("")
        openFilesMap[str(x)]=f
        print("done files")
        
    filePath="/disk/scratch_big/sweber/infobox_properties_de.ttl"
    with open(filePath, 'r') as inF:
        for line in tqdm(inF, total=14048417, unit="lines"):
            if "<http://de.dbpedia.org/resource/" in line:
                entity=find_between(line, "<http://de.dbpedia.org/resource/", ">")
                firstLetter=entity[0].lower()
                if firstLetter!="/" and firstLetter in openFilesMap.keys():
                    f = openFilesMap[firstLetter]
                    f.write(line)
    for f in openFilesMap.values():
        f.close
    
    
if __name__ == "__main__":
    #constructEnglishEntityDict()
    #createAlphabetBatchesForAttributes()
    constructEnglishEntityDict()

    """
    for entity in ["Wheat","Spelt","Rye","Corn","Yo_Mamma"]:
        
        getAttributesFomInternet(entity, "en")
    print("-------------------------------")
    for entity in ["Weizen","Angela_Merkel","Barack_Obama","Obama"]:
        getAttributesFromFile(entity)
    """
    