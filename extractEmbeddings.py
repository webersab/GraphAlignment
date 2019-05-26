import numpy as np
import pickle
from numpy import vstack,array,savetxt
from scipy.cluster.vq import kmeans,vq
import collections


if __name__ == "__main__":
    ent_embeddings = np.load('/disk/scratch_big/sweber/ent_embeddings.npy')
    print(ent_embeddings.shape)
    entities_dict = pickle.load( open( "/disk/scratch_big/sweber/entities_dict.p", "rb" ) )
    print("Length : %d" % len(entities_dict))
    #print(entities_dict)"\t"
    
    np.savetxt("ent_embeddings.tsv",ent_embeddings,delimiter="\t")
    od = collections.OrderedDict(sorted(entities_dict.items()))
    f=open("entities_dict.tsv", "a")
    for k, v in od.items():
        f.write(v+"\n")
    
    
    #centroids,_ = kmeans(ent_embeddings,50000)
    #idx,_ = vq(data,centroids)
    
    #print(idx)
    
    