# this file is to match the OpenCV's Rodrigues result with the theorectical values

# Matlab equivalent 1: transpose(rotationVectorToMatrix([0.1, 0.2, 0.3]))
# Matlab equivalent 2: rotationMatrixToVector(transpose([0.9357548,  -0.28316496, 0.21019171;
# 0.30293271,  0.95058062, -0.06803132; -0.18054008, 0.12733457,  0.97529031]))

import cv2 as cv2
import numpy as np

def rVec_to_R(r_ori):
    # theorectical values
    # r_ori is 3x1 and is before normalization

    th = np.linalg.norm(r_ori)
    r = r_ori/th # normalization
    rt = np.transpose(r)

    rx = float(r[[0]])
    ry = float(r[[1]])
    rz = float(r[[2]])

    I = np.identity(3)
    K = np.array([[0, -rz, ry], [rz, 0, -rx], [-ry, rx, 0]]) # K: cross product matrix
    rrt = np.matmul(r, rt) # also I + K^2

    R = np.cos(th)*I + (1-np.cos(th))*rrt + np.sin(th)*K

    return R

def R_to_rVec(R):
    
    K_sin_th = (R - np.transpose(R))/2 # i.e. K*sin(th)

    r_norm_sin_th = np.array([[-K_sin_th[1,2]], [K_sin_th[0,2]], [-K_sin_th[0,1]]]) # i.e. normalized(r)*sin(th)
    sin_th = np.linalg.norm(r_norm_sin_th) # sin(th)
    th0 = np.arcsin(sin_th)
    th1 = np.pi - th0 # another solution of sin(th) = y
    rVec0 = th0*r_norm_sin_th/sin_th
    rVec1 = th1*r_norm_sin_th/sin_th
    
    # determine whether rVec0 or rVec1 is the initial solution
    if np.all(np.round(R - rVec_to_R(rVec0), 4)==np.zeros([3, 3]))==True:
        rVec = rVec0
    elif np.all(np.round(R - rVec_to_R(rVec1), 4)==np.zeros([3, 3]))==True:
        rVec = rVec1
    else:
        raise Exception("Either rVec0 or rVec1 should match R.")
                
    return rVec

if __name__ == '__main__':
    
    r_ori = np.transpose(np.array([[0.1, 0.2, 0.3]]))
    
    R1 = rVec_to_R(r_ori)
    print(R1)
    
    R2, _ = cv2.Rodrigues(r_ori)
    print(R2)
    
    # =============================================================================
    # R = np.array([[ 0.9357548,  -0.28316496,  0.21019171],
    #  [0.30293271,  0.95058062, -0.06803132],
    #  [-0.18054008, 0.12733457,  0.97529031]])
    # =============================================================================
    
    s = np.sqrt(2)/2    
    R = np.array([[ 0,  -s,  s],
     [1,  0, 0],
     [0, s, s]])    
    
    if np.all(np.round(np.matmul(R,np.transpose(R)), 4)==np.identity(3))==False:
        raise Exception("'R*(R^T) = I' doesn't hold.")
        
    r1, _ = cv2.Rodrigues(R)
    print(r1)
    
    r2 = R_to_rVec(R)
    print(r2)
