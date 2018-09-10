import pickle

class Linker:
    
    def createEntityDictionary(self,filePathGerman,filePathTranslation):
        entDict={}
        with open(filePathGerman) as textfile1, open(filePathTranslation) as textfile2: 
            for x, y in zip(textfile1, textfile2):
                x = x.strip()
                y = y.strip()
                entDict[x]=y.lower()
        with open("entityDictionary.dat", "wb") as f:
            pickle.dump(entDict, f)
        return entDict
    
    def cheapLink(self, a, entDict):
        if a in entDict:
            return entDict[a]
        else:
            return a
            