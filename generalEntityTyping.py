from pygermanet import load_germanet
import sys
import datetime
from nltk.corpus.reader.wordnet import Lemma
import re
import os

class GeneralEntityTyping():
    
    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
        
    def typeEntity(self,entity):  
        lemmatized= gn.lemmatise(entity)[0]+'.n.1'
        try:
            synset=gn.synset(lemmatized).hypernym_paths
        except:
            return "MISC"
        
        if "Mensch" in str(synset):
            return "PERSON"
        elif ("Ereignis"in str(synset)) or ("Geschehnis"in str(synset)) or ("Vorfall" in str(synset)):
            return "EVENT"
        elif ("Organisation"in str(synset)) or ("Gruppe"in str(synset)) or ("Institution" in str(synset)):
            return "ORGANIZATION"
        elif ("Gegend"in str(synset)) or ("Ortschaft"in str(synset)) or ("Siedlung"in str(synset)) or ("Stelle" in str(synset)):
            return "LOCATION"
        else:
            return "MISC"
    
    def swapTypesInFile(self,inFile,outFile):
        inFile = open(inFile,'r')
        orig_stdout = sys.stdout
        f = open(outFile, 'w')
        sys.stdout = f
        for line in inFile:
            if ("(" and "#" and "::" in line):
                types=self.find_between(line,")#","::") 
                if "NOUN" in types:
                    a,b=types.split("#")
                    if a == "NOUN" and b== "NOUN":
                        word1=self.find_between(line,"::","::")
                        word2=self.find_between(line,"::","|||")
                        newType1=self.typeEntity(word1)
                        newType2=self.typeEntity(word2)
                        print(line.replace("NOUN#NOUN",newType1+"#"+newType2),end='')
                    elif a == "NOUN" and b != "NOUN":
                        word=self.find_between(line,"::","::")
                        newType=self.typeEntity(word)
                        print(line.replace("NOUN",newType),end='')
                    else:
                        shortenedLine=re.sub(r'.*::', '::', line)
                        word=self.find_between(shortenedLine,"::","|||")
                        newType=self.typeEntity(word)
                        print(line.replace("NOUN",newType),end='')
                else:
                    print(line,end='')
            else:
                #write line to new file without change
                print(line,end='')
        
        sys.stdout = orig_stdout
        f.close()   
                 
if __name__ == "__main__":
    print("Hello entity typing!")
    gn = load_germanet()
    g=GeneralEntityTyping()
    #print(g.typeEntity("Schauspielerin"))
    
    print("begin: ",datetime.datetime.now())
    
    for filename in os.listdir("/disk/scratch_big/sweber/pipelineOutput"):
        g.swapTypesInFile("/disk/scratch_big/sweber/pipelineOutput/"+filename, "/disk/scratch_big/sweber/pipelineOutput/"+filename[-6:])
        print("typed "+filename)
    print("end : ",datetime.datetime.now())
    

