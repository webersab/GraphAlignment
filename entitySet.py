class EntitySet:

    def __init__(self):
        self.list = []
        
    def __iter__(self):
        return iter(self.list)
    
    def getIndex(self, entity):
        if entity in self.list:
            #print("in set already",entity)
            return self.list.index(entity)
        else:
            #print("new ",entity)
            self.list.append(entity)
            return len(self.list)
    
    def printEntitySet(self):
        for s in self.list:
            print(str(s))

    def printEntitySetToFile(self):
        text_file = open("entitySet.txt", "w")
        for s in self.list:
            text_file.write(str(s))
            text_file.write("\n")
        text_file.close()
    
    def length(self):
        return len(self.list)