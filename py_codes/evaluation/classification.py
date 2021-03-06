# created by Lanston in 2021.06

# this file will run the identity classification statistics based on the embeddings generated by embed_2d.py
# this file is to be run by host

import numpy as np
from numpy import load
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import time

def accuracy_score_in_set(y0_trans, y0hat_set):
    # y0_trans is a size-n vector
    # y0hat_set is a n x m matrix
    # if y0_trans is in y0hat_set, will be counted as one "hit"
    
    rank_y0_trans = len(np.shape(y0_trans))
    rank_y0hat_set = len(np.shape(y0hat_set))
    
    if rank_y0_trans != 1:
        raise Exception("Rank of y0_trans should be 1.")

    if rank_y0hat_set != 2:
        raise Exception("Rank of y0hat_set should be 2.")
        
    if np.shape(y0_trans)[0] != np.shape(y0hat_set)[0]:
        raise Exception("Number of data of y0_trans and y0hat_set doesn't match.")

    n = np.shape(y0_trans)[0]
    
    hit = 0
    for i in range(n):
        y0_i = y0_trans[i]
        y0hats_i = y0hat_set[i,:]
        if y0_i in y0hats_i:
            hit += 1
    score = hit / n       
    
    return score

def accuracy_of_1_set(path, filterList, out_encoder, model, num_candidates_allowed, fitFlag):
    # "num_candidates_allowed = n" determines the criteria for us to treat a guess as a "hit", i.e. true answer in best n guesses
    # fitFlag determines whether we should re-train the SVM model again
    
    data = load(path)
    
    X, y = data['arr_0'], data['arr_1']
    y0 = y[:,0] # only the first column, i.e. person_i, is needed
    
    # normalize input vectors
    in_encoder = Normalizer(norm='l2')
    X = in_encoder.transform(X)
    
    # filter X and y0 by selected list
    indices = [i for i, val in enumerate(y0) if val in filterList] 
    X = X[indices]
    y0 = y0[indices]
    
    # label encode targets
    if out_encoder == "":
        out_encoder = LabelEncoder()
        out_encoder.fit(y0)
    y0_trans = out_encoder.transform(y0)
        
    if fitFlag == 1:
        model.fit(X, y0_trans) # original images as training data for SVM
    
    # predict
    y0hat = model.predict(X)
    probas = model.predict_proba(X)
    
    sorted_indices = np.flip(probas.argsort(axis=1), axis = 1)
    y0hat_set = sorted_indices[:,:num_candidates_allowed]
        
    # compute score
    # score = accuracy_score(y0_trans, y0hat)
    score = accuracy_score_in_set(y0_trans, y0hat_set)

    return score, out_encoder, model

# generate the list of person that should be used to train SVM, i.e. exclude pivots and error faces
def generate_person_train_list(ns_str, pivot):
    
    num_person = 200
    
    if ns_str == "normal": 
        errList = [122, 123] # 2D prePB images of person 122 and 123 are not available for "normal"
    elif ns_str == "smile":
        errList = [] # 2D prePB iamges of all 180 person are available
    else:
        raise Exception("ns_str should be either normal or smile.")
    
    filterList = []
    for person_i in range(200):
        
        if (person_i + 1) in errList: # skip person if the 2D image is not available
            continue
        
        if person_i % (num_person/pivot) != 0:
            filterList.append(str(person_i + 1))
        
    return filterList

tic = time.perf_counter() # count the running time

myDir = "./embeddings_FaceNet" # folder to store the .npz embeddings in the host machine

cropStr = ""
# cropStr = "_NoCrop" # FaceNet embeddings without using MTCHH face detector in the pre-processing; worse result

ns_str = "normal"
path_ori = myDir + '/embeddings_Ys_original_angle_02to09.npz'
path_prePB = myDir + '/embeddings_Ys_' + ns_str + '_pb0_pivot0' + cropStr + '.npz'
path_PB_2_20 = myDir + '/embeddings_Ys_' + ns_str + '_pb2_pivot20' + cropStr + '.npz'
path_PB_10_20 = myDir + '/embeddings_Ys_' + ns_str + '_pb10_pivot20' + cropStr + '.npz'
path_PB_2_100 = myDir + '/embeddings_Ys_' + ns_str + '_pb2_pivot100' + cropStr + '.npz'
path_PB_10_100 = myDir + '/embeddings_Ys_' + ns_str + '_pb10_pivot100' + cropStr + '.npz'

filterList_20 = generate_person_train_list(ns_str, 20)
filterList_100 = generate_person_train_list(ns_str, 100)

C = 1 # larger C for more regularization
model0 = SVC(kernel='linear', C=C, probability=True, \
                                   random_state=0)        
model1 = LogisticRegression(C=C, penalty='l2', \
                                 solver='saga', \
                                 multi_class='ovr', \
                                 max_iter=10000)
model2 = LogisticRegression(C=C, penalty='l2', \
                                 solver='saga', \
                                 multi_class='multinomial', \
                                 max_iter=10000)
model3 = LogisticRegression(C=C, penalty='l1', \
                                 solver='saga', \
                                 multi_class='multinomial', \
                                 max_iter=10000)

models = [model0, model1, model2, model3]
# models = [model0, model1, model2]
# models = [model0, model1]

for model in models:
    
    model_20 = model
    num_candidates_allowed = 5
    score_ori_20, out_encoder_20, model_20 = accuracy_of_1_set(path_ori, filterList_20, "", model_20, num_candidates_allowed, 1) # train SVM model and obtain accuracy
    score_prePB_20, _, _ = accuracy_of_1_set(path_prePB, filterList_20, out_encoder_20, model_20, num_candidates_allowed, 0)
    score_PB_2_20,  _, _ = accuracy_of_1_set(path_PB_2_20, filterList_20, out_encoder_20, model_20, num_candidates_allowed, 0)
    score_PB_10_20, _, _ = accuracy_of_1_set(path_PB_10_20, filterList_20, out_encoder_20, model_20, num_candidates_allowed, 0)
    
    model_100 = model
    num_candidates_allowed = 10
    score_ori_100, out_encoder_100, model_100 = accuracy_of_1_set(path_ori, filterList_100, "", model_100, num_candidates_allowed, 1) # train SVM model and obtain accuracy
    score_prePB_100,       _, _ = accuracy_of_1_set(path_prePB, filterList_100, out_encoder_100, model_100, num_candidates_allowed, 0)
    score_PB_2_20_on_100,  _, _ = accuracy_of_1_set(path_PB_2_20, filterList_100, out_encoder_100, model_100, num_candidates_allowed, 0) # re-run _20 on the smaller list
    score_PB_10_20_on_100, _, _ = accuracy_of_1_set(path_PB_10_20, filterList_100, out_encoder_100, model_100, num_candidates_allowed, 0)
    score_PB_2_100,        _, _ = accuracy_of_1_set(path_PB_2_100, filterList_100, out_encoder_100, model_100, num_candidates_allowed, 0)
    score_PB_10_100,       _, _ = accuracy_of_1_set(path_PB_10_100, filterList_100, out_encoder_100, model_100, num_candidates_allowed, 0)
    
    # summarize
    print('Accuracy_20: ori=%.3f, prePB=%.3f, PB_2_20=%.3f, PB_10_20=%.3f' \
          % (score_ori_20*100, score_prePB_20*100, score_PB_2_20*100, score_PB_10_20*100))
    print('Accuracy_100: ori=%.3f, prePB=%.3f, PB_2_20=%.3f, PB_10_20=%.3f, PB_2_100=%.3f, PB_10_100=%.3f' \
          % (score_ori_100*100, score_prePB_100*100, score_PB_2_20_on_100*100, score_PB_10_20_on_100*100, score_PB_2_100*100, score_PB_10_100*100))
    
    # for generate LaTex table code
    code = ('%.1f' % (score_prePB_20*100)) + "\% & " + \
           ('%.1f' % (score_PB_2_20*100)) + "\% & " + \
           ('%.1f' % (score_PB_10_20*100)) + "\% & " + \
           ('%.1f' % (score_PB_2_20_on_100*100)) + "\% & " + \
           ('%.1f' % (score_PB_10_20_on_100*100)) + "\% & " + \
           "\multicolumn{2}{| c |}{" + \
           ('%.1f' % (score_prePB_100*100)) + "\% } & " + \
           ('%.1f' % (score_PB_2_100*100)) + "\% & " + \
           ('%.1f' % (score_PB_10_100*100)) + "\% \\\\"    
    print("code = " + code)
    
    toc = time.perf_counter() # running time counted
    print(f"time: {toc - tic:0.1f} seconds")
