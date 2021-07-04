# Author: Lanston Hau Man Chu
# 2020.08.02

# perturbation_1_alpha() is to reflect/perturbate the original alpha to a new alpha
# an alpha file would be used as input (i.e. the selected neighbors)

# this file should be placed in /alphas
# this file can be run by either host or VM

import sys
import numpy as np
from scipy import spatial
from scipy.spatial import Delaunay
import time

def check_in_hull(p, hull):
    # hull should be a scipy.spatial.Delaunay object
    # i.e. do "nbHull = Delaunay(neighbors)" before calling this method

    # check if points in `p` are in `hull`
    # return True if p is in hull, otherwise return False
    # `p` is a `NxK` matrix, i.e. `N` points in `K` dimensions

    return hull.find_simplex(p)>=0
    # return hull.find_simplex(p)

def reflection_from_neighbors(alpha, neighbors, num_pivot, near_far_flag):
    # alpha is the point that we would like to perturbed
    # neighbors: #(neighbors) x 99 matrix; the K-nearest neighbors of alphas
    # num_pivot is the number of neighbors we would use in the reflection
    # near_far_flag = 0: near reflection; = 1: far reflection

    if (near_far_flag==0):
        neighbors_for_reflection = neighbors[0:num_pivot,:] # take the first n neighbors for near reflection
    elif (near_far_flag==1):
        neighbors_for_reflection = neighbors[-num_pivot:0,:] # take the last n neighbors for far reflection
    else:
        raise Exception("near_far_flag should be either 0 or 1")

    mid_point = neighbors_for_reflection.sum(0)/num_pivot # mid_point is the centroid of the neighbors

    alpha_new = 2 * mid_point - alpha # reflection: use the mid-point as the point of lever

    return alpha_new

def interpolation(alpha_Initial, alpha_new):
    # save the alpha of interpolation
    alpha_diff = alpha_new - alpha_Initial

    num_step = 10
    alphas_interpolate = np.array([], dtype=np.int64).reshape(0,99)
    for j in range(num_step + 1):

        alpha_j = alpha_Initial + j*alpha_diff/num_step
        alphas_interpolate = np.vstack([alphas_interpolate, alpha_j])

    # np.save("./alphas/alphas_10_interpolate.npy", alphas_interpolate)

    # np.savetxt("/shared/perturbed.alpha", alpha_new) # for VM
    # np.savetxt("./perturbed.alpha", alpha_new) # for debugging    
    return alphas_interpolate

def perturbation_1_alpha(alpha_Initial, alphas_pivot, num_pivot, near_far_flag, alphas_output_dir, img_idx, normal_smile_suffix):

    # alpha_Initial is in the size of (1, 99)
    # e.g. alphas_pivot = alphas-array from "./alphas/alphas_DF_29.npy" or "./alphas/alphas_DF_1000.npy" etc.
    # num_pivot is the number of pivots we would use in the reflection
    # near_far_flag = 0: near reflection; = 1: far reflection

    num_total_pivots, dim = np.shape(alphas_pivot) # dimension of the space
    
    if len(np.shape(alpha_Initial))!=1:
        raise Exception("alpha_Initial should have rank 1.")
    
    if len(alpha_Initial)!=99:
        raise Exception("The dimensions of alpha_initial should be 99.")
        
    K = min(dim + 1, num_pivot) # number of neighbors

    myTree = spatial.cKDTree(alphas_pivot) # create k-d tree for neaerest neighbors searching
    distances, indexes = myTree.query(alpha_Initial, K) # find K neaerest neighbors of alpha_Initial
    neighbors = alphas_pivot[indexes, :] #(neighbors) x 99 matrix;

    alpha_new = reflection_from_neighbors(alpha_Initial, neighbors, num_pivot, near_far_flag)

    # alphas_interpolate = interpolation(alpha_Initial, alpha_new)
    
    output_path = alphas_output_dir + "/person" + str(img_idx) + "_pb" + str(num_pivot) + "_pivot" + str(num_total_pivots) + normal_smile_suffix + ".alpha"
    np.savetxt(output_path, alpha_new) # save .alpha files for C++ to call

    return alpha_new

def perturbation_all_alphas(alphas_to_jump, alphas_pivot, num_pivot, near_far_flag, alphas_output_dir, normal_smile_suffix, img_idx_list):
    
    num_alphas_to_jump, dim_alphas_to_jump = np.shape(alphas_to_jump)
    num_alphas_pivot, dim_alphas_pivot = np.shape(alphas_pivot)

    if dim_alphas_to_jump != 99 or dim_alphas_pivot!=99:
        raise Exception("The dimensions of alpha/alphas should be 99.")
        
    if num_pivot > num_alphas_pivot:
        raise Exception("No. of requested neighbors shouldn't exceed the no. of the pivot alphas.")
        
    alphas_pb = np.array([], dtype=np.int64).reshape(0,99) # perturbed alphas
    
    for i in range(num_alphas_to_jump):
        alpha = alphas_to_jump[i, :]
        img_idx = img_idx_list[i]
        alpha_new = perturbation_1_alpha(alpha, alphas_pivot, num_pivot, near_far_flag, alphas_output_dir, img_idx, normal_smile_suffix)
        alphas_pb = np.vstack([alphas_pb, alpha_new])
    
    return alphas_pb

def create_image_indices_list():
    myList = []
    for i in range(200):
        if i % 10 == 0:
            continue
        myList.append(i + 1)
    
    return myList

if __name__ == '__main__':
    
    tic = time.perf_counter() # count the running time
    
    input_prefix = "alphas_180"
    # normal_smile_suffix = "_normal"                 # for normal
    normal_smile_suffix = "_smile"           # for smile
    alphas_to_jump_path = "./FEI/"+ input_prefix + normal_smile_suffix + ".npy"
    # alphas_pivot_path = "./FEI/alphas_20_half.npy"
    alphas_pivot_path = "./FEI/alphas_100_half.npy"
    alphas_output_dir = "./FEI"
    # num_pivot = 2
    num_pivot = 10
    near_far_flag = 0 # 0: near reflection; = 1: far reflection
    
    alphas_to_jump = np.load(alphas_to_jump_path)
    alphas_pivot = np.load(alphas_pivot_path)
    num_total_pivot, _ = np.shape(alphas_pivot)
    
    img_idx_list = create_image_indices_list()
    alphas_pb = perturbation_all_alphas(alphas_to_jump, alphas_pivot, num_pivot, near_far_flag, alphas_output_dir, normal_smile_suffix, img_idx_list) # alpha' saved to "/shared/perturbed.alpha"
    
    output_path = alphas_output_dir + input_prefix + "_pb" + str(num_pivot) + "_pivot" + str(num_total_pivot) + normal_smile_suffix + ".npy"
    np.save(output_path, alphas_pb)
    
    toc = time.perf_counter() # running time counted
    print(f"time: {toc - tic:0.1f} seconds")