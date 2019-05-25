import numpy as np
import pickle

if __name__ == "__main__":
    ent_embeddings = np.load('/disk/scratch_big/sweber/ent_embeddings.npy')
    print(ent_embeddings.shape)
    entities_dict = pickle.load( open( "/disk/scratch_big/sweber/entities_dict.p", "rb" ) )
    print("Length : %d" % len(entities_dict))
    print(entities_dict)
    