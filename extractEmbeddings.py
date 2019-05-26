import numpy as np
import pickle
from numpy import vstack,array
from scipy.cluster.vq import kmeans,vq


if __name__ == "__main__":
    ent_embeddings = np.load('/disk/scratch_big/sweber/ent_embeddings.npy')
    print(ent_embeddings.shape)
    entities_dict = pickle.load( open( "/disk/scratch_big/sweber/entities_dict.p", "rb" ) )
    print("Length : %d" % len(entities_dict))
    #print(entities_dict)
    
    centroids,_ = kmeans(ent_embeddings,50000)
    idx,_ = vq(data,centroids)
    
    print(idx)
    
    