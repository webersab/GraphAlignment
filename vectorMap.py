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