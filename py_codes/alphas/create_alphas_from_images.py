# Modified by Lanston Hau Man Chu on 2020.08.03
# this file is modified from testBatchModel.py

# this transform the images in image-list into an alphas array.
# this file should be run by the Docker's container
# this file should be placed in /app/demoCode/alphas
# To run:   > python create_alphas_from_images.py

import os
os.environ['GLOG_minloglevel'] = '2'
###################
import numpy as np
import cv2 # from OpenCV
import time
import ntpath
import os.path
import scipy.io
import shutil
import sys
sys.path.append("/app/demoCode") # so that we can also import modules from this folder
import utils # import utils from /app/demoCode
from skimage import io
import dlib
import torch
import imp
from torch.autograd import Variable

def create_alphas(ins, output_path, detector, predictor, net, mean):
    count = 0
    alphas = np.array([], dtype=np.int64).reshape(0,99)
    for image_path in ins:
        
        # Part I: crop images        
        image_path = image_path.strip() # string trimming
        
        print("> Prepare image "+image_path + ":")
        imname = ntpath.basename(image_path) # e.g. myXXX.jpg
        imname = imname.split(imname.split('.')[-1])[0][0:-1] # e.g. myXXX
        img = cv2.imread(image_path) # BGR; img is originally in the original size

        dlib_img = io.imread(image_path) # RGB; dlib_img is in original size, and approximately = img by re-ordering color channels
        img2 = cv2.copyMakeBorder(img,0,0,0,0,cv2.BORDER_REPLICATE)
        dets = detector(img, 1) # detas can be multiple faces
        print(">     Number of faces detected: {}".format(len(dets)))
        if len(dets) == 0: # dets have 0 faces
            raise Exception('> Could not detect the face, skipping the image...' + image_path)
        if len(dets) > 1: # dets have >=2 faces
            print("> Process only the first detected face!")
        detected_face = dets[0]
        
        ## If we are using landmarks to crop
        shape = predictor(dlib_img, detected_face) # to find landmarks' location
        nLM = shape.num_parts # number of landmarks, i.e. 68
        for i in range(0,nLM):
            cv2.circle(img2, (shape.part(i).x, shape.part(i).y), 5, (255,0,0)) # draw landmarks circles on imgs
        img, lms = utils.cropByLM(img, shape, img2) # img is cropped and resized to dim-(503, 503); lms are 68 2-D landmarks
        img = cv2.resize(img,(500, 500)) # DON't SKIP THIS STEP (to match the alphas by main code); resized to exactly dim-(500, 500)
        
        # Part II: create alphas
        im = cv2.resize(img, (224, 224)).astype(float).transpose((2,0,1)) # resized to dim-(224, 224)
        im = im - mean
        #im = im/255
        im = Variable(torch.from_numpy(im).unsqueeze(0).float().cpu())
        features = net(im).data.cpu().numpy() # dim(features) is 198; 0:98 refers to shape; 99:197 refers to texture
        alpha = features[0,0:99]    
        alphas = np.vstack([alphas, alpha])
        print(alphas.shape)

        count = count + 1    
    np.save(output_path, alphas)
    return

def call_models_to_create_alphas(ins, outs):
    # ins can be a io.TextIOWrapper, a list, or a list of lists.
    
    model_path  = '/app/CNN/shape_model.pth' # the PyTorch-model-file.
    mean_path = '/app/CNN/shape_mean.npz'
    predictor_path = "/app/dlib_model/shape_predictor_68_face_landmarks.dat"
    
    detector = dlib.get_frontal_face_detector() # to map an image to face(s)
    predictor = dlib.shape_predictor(predictor_path) # to map a face to landmarks' locations
    
    # load net
    MainModel = imp.load_source('MainModel', "/app/CNN/shape_model.py") # MainModel become a module
    net = torch.load(model_path) # net is the model from a .pth file
    net.eval() # model.eval() will notify all your layers that you are in eval mode; dropout/batchnorm layers will behave differently in training/eval mode
    
    mean0 = np.load(mean_path, encoding='latin1')
    mean = mean0['arr_0'] # mean is a numpy array with size 3*224*224
    net.cpu() # to move net to the memory accessible to the CPU
    
    # Case 1: TextIOWrapper is generated by opening a file
    # if isinstance(ins, io.TextIOWrapper)
    if isinstance(ins, file): 
        output_path = outs
        create_alphas(ins, output_path, detector, predictor, net, mean)
    
    # Case 2: ins is a list probablly because the function is called by another Python file
    elif isinstance(ins, list):          
        if isinstance(ins[0], str):
            output_path = outs
            create_alphas(ins, output_path, detector, predictor, net, mean)
        
    # Case 3: ins is a "list of lists"
        elif isinstance(ins[0], list):   
            if len(ins)!=len(outs):
                raise Exception("The length of input list and output list doesn't match.")
            
            if not(isinstance(ins[0][0], str) and isinstance(outs[0], str)):
                raise Exception("outs should be list of strings.")
            
            for i in range(len(ins)):
                inputList = ins[i]
                output_path = outs[i]
                create_alphas(inputList, output_path, detector, predictor, net, mean)
        else:
            raise Exception("ins should be either a io.TextIOWrapper, a list, or a list of lists.")
    else:
        print(type(ins))
        raise Exception("ins should be either a io.TextIOWrapper, a list, or a list of lists.")

    return

if __name__ == '__main__':
    fileList = "/app/demoCode/alphas/image_list.txt"
    output_path = "/shared/output/output_X/myAlphas.npy"
    
    with open(fileList, "r") as ins: # looping over input list "ins", which is a io.TextIOWrapper
        call_models_to_create_alphas(ins, output_path)