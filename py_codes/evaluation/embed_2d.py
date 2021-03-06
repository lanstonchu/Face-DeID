# created by Lanston in 2021.06

# this file will embed images generated by colored_2D.py into FaceNet embeddings
# this file will save 1 embeddings.npz file for each directory concerned, depending on the directory type
# this file is to be run by host

import os
from PIL import Image
from matplotlib import pyplot
import matplotlib.image as mpimg
import numpy as np
from mtcnn.mtcnn import MTCNN
from keras.models import load_model
import time

# extract a single face from a given photograph
# modified from https://machinelearningmastery.com/how-to-develop-a-face-recognition-system-using-facenet-in-keras-and-an-svm-classifier/
def crop_1_face(filename, cropFace_flag, required_size=(160, 160)):
    
    # load image from file
    image = Image.open(filename)
    
    # convert B&W to RGB and convert 1-scale to 255-scale if necessary
    image = image.convert('RGB')
    
    # convert to array
    pixels = np.asarray(image)
 
    if cropFace_flag == 1:
        
        # create the detector, using default weights
        detector = MTCNN()
        
        # detect faces in the image
        results = detector.detect_faces(pixels)
        
        if len(results) == 0: # detected no face
            return ""
        # extract the bounding box from the first face
        x1, y1, width, height = results[0]['box']
        
        # bug fix
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        
        # extract the face
        face = pixels[y1:y2, x1:x2]
        
    elif cropFace_flag == 0:
        face = pixels
        
    else:
        raise Exception("cropFace_flag should be either 0 or 1.")
   
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = np.asarray(image)
    # pyplot.imshow(face_array)
    
    return face_array

# load images and crop faces for all/selected images in a directory
def dir_to_XY(directory, dirType, allowed_ori_indices, skip_existing_flag, cropFace_flag):
    # dirType: determine the type of the directory
    # each label would be [person_i_str, pb_str, pivot_str, angle_str]

    if directory[-1] == "/":
        raise Exception("The last character of directory shouldn't be '/'.")

    if skip_existing_flag== 1: # will skip directory if .npz file already exists
        if os.path.exists(directory + '/embeddings_Ys.npz'):
            return
          
    posi_last = directory.rfind("/")
    dir_last_part = directory[posi_last + 1:]

    X = []
    Y = []
    for filename in os.listdir(directory):       
        
        if filename[0]==".": # avoid Colab's cookies
            continue
        elif filename[-4:] not in allowed_extension:
            continue

        print(directory + "/" + filename)
        posi = filename.find("-")
        person_i_str = filename[:posi] # i.e. label
        
        if dirType == 0: # original dir
            angle_str = filename[(posi + 1):-4]
            if angle_str not in allowed_ori_indices:  # only ready some partial images for the original dataset
                continue
            pb = 0
            pivot = 0
            
        elif dirType == 1: # prePB dir
            pb = 0
            pivot = 0
            
            ns_num = int(filename[-14:-12]) # normal or smile, i.e. 11 or 12            
            if not(ns_num == 11 or ns_num == 12):
                raise Exception("ns_num should be either 11 or 12.")
            angle_str = str(ns_num)
                
        elif dirType == 2: # PB dir
            ns_num = int(filename[-14:-12]) # normal or smile, i.e. 11 or 12
            if not(ns_num == 11 or ns_num == 12):
                raise Exception("ns_num should be either 11 or 12.")
            angle_str = str(ns_num)
            
            posi_underscore = dir_last_part.find("_")
            pb = int(dir_last_part[2:posi_underscore])
            pivot = int(dir_last_part[posi_underscore + 6:])
                                    
        # get 1 face for 1 image
        path = directory + "/" + filename
        face = crop_1_face(path, cropFace_flag)
        if face == "": # detected no face
            continue
        label = [person_i_str, str(pb), str(pivot), angle_str]
        
        X.append(face)
        Y.append(label)
        
    X_array = np.asarray(X)
    Y_array = np.asarray(Y)
    
    # np.savez_compressed(directory + '/cropped_faces.npz', X_array, Y_array)
    embeddings = get_embedding_faces(model, X_array)            
    np.savez_compressed(directory + '/embeddings_Ys.npz', embeddings, Y_array)
        
    return

def dir_dir_to_embeddings(model, directory, dirType, allowed_ori_indices, skip_existing_flag, cropFace_flag):
    
    if dirType == 0 or dirType == 2:        
        for subdir in os.listdir(directory):

            subdir_full = directory + "/" + subdir
            
            if not os.path.isdir(subdir_full):
                continue
                
            dir_to_XY(subdir_full, dirType, allowed_ori_indices, skip_existing_flag, cropFace_flag)

    elif dirType == 1:
        dir_to_XY(directory, dirType, allowed_ori_indices, skip_existing_flag, cropFace_flag)
        
    else:
        raise Exception("dirType should be 0, 1 or 2.")
            
    return

# get the face embedding for one face
def get_embedding_1_face(model, face_pixels):

    # scale pixel values
    face_pixels = face_pixels.astype('float32')

    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std

    # transform face into one sample
    samples = np.expand_dims(face_pixels, axis=0)

    # make prediction to get embedding
    yhat = model.predict(samples)
    return yhat[0]

def get_embedding_faces(model, X_array):
    
    embeddings = []    
    for face_pixels in X_array:
        embedding = get_embedding_1_face(model, face_pixels)
        embeddings.append(embedding)
    embeddings = np.asarray(embeddings)    
    return embeddings

if __name__ == '__main__':
    modelDir = "C:/your_path/facenet" # directory to store the FaceNet model
    
    # load the facenet model
    model = load_model(modelDir + '/facenet_keras.h5')
    model.load_weights(modelDir + '/facenet_keras_weights.h5')
    print('Loaded Model')
    
    tic = time.perf_counter() # count the running time
    
    allowed_extension = ['.jpg', '.png']
    allowed_ori_indices = ['02', '03', '04', '05', '06', '07', '08', '09']
   
    mainDir = "C:/your_path/output" # main directory to store the .png 2D images output of colored_2D.py
    datasetDir = "C:/your_path/input/FEI_Face_Database" # directory in host machine to store the FEI_Face_Database
    
    dir_prePB_normal = mainDir + "/output_180_normal_prePB"
    dir_prePB_smile  = mainDir + "/output_180_smile_prePB"
    dir_PB_normal = mainDir + "/output_180_normal_PB"
    dir_PB_smile = mainDir + "/output_180_smile_PB"
    
    skip_existing_flag = 1 # will skip directory if the .npz already exists
    cropFace_flag = 1 # whether to use the MTCNN face detector to crop face; Much longer run time if yes.

    dirType = 2 # PB
    dir_dir_to_embeddings(model, dir_PB_normal, dirType, "", skip_existing_flag, cropFace_flag)
    dir_dir_to_embeddings(model, dir_PB_smile, dirType, "", skip_existing_flag, cropFace_flag)
    
    dirType = 1 # prePB
    dir_dir_to_embeddings(model, dir_prePB_normal, dirType, "", skip_existing_flag, cropFace_flag)
    dir_dir_to_embeddings(model, dir_prePB_smile, dirType, "", skip_existing_flag, cropFace_flag)
    
    dirType = 0 # original
    dir_dir_to_embeddings(model, datasetDir, dirType, allowed_ori_indices, skip_existing_flag, cropFace_flag)
       
    toc = time.perf_counter() # running time counted
    print(f"time: {toc - tic:0.1f} seconds")
