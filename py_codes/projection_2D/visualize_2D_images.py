# Created by Lanston on 2021.06.16

# to visualize 2D images of selected individuals
# this file is to be run by host

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

def show_1_img(imgPath, person_i, nx_num, count, order_list, zoom_ratio, pb_pivot_str):
   
    # print(imgPath)
    try:
        img = mpimg.imread(imgPath)
        h, w, _ = np.shape(img)
        
        if zoom_ratio > 1:
            raise Exception("zoom_ratio shouldn't exceed 1.")
            
        h_small = round(h*zoom_ratio)
        w_small = round(w*zoom_ratio)
        h_margin = round((h - h_small)/2)
        w_margin = round((w - w_small)/2)
        
        img_zoomed = img[h_margin:(h_margin + h_small), w_margin:(w_margin + w_small)]
        
        # plot image
        order = order_list[count]
        mySubplot = plt.subplot(4, 3, order)
        mySubplot.title.set_text(pb_pivot_str)
        # plt.axis('off')
        
        plt.imshow(img_zoomed)
    
    except FileNotFoundError:
        2+2

    count += 1   
    return count

def show_1_person(person_i_plusOne, zoom_ratio, num_person, mainDir, datasetDir):
    
    fig = plt.figure(figsize=(12, 8*2), dpi=80) # change output size
    
    # mainInOutputDir = mainDir + "/output_180_3"
    mainInOutputDir = mainDir
    
    fig.suptitle('Person ' + str(person_i_plusOne), fontsize=16)
    
    person_i = person_i_plusOne - 1
    dir_index = 1 + int(np.floor(person_i/(num_person/4))) # the first 1/4 persons are in "dir 1", second 1/4 in "dir 2" etc.
    
    imgDir = datasetDir + "/originalimages_part" + str(dir_index)
    
    count = 0
    for ns_i in range(2):    
        nx_txt = normal_smile_txt_List[ns_i]
        nx_num = str(normal_smile_num_List[ns_i])
    
        pb_pivot_str = "(0, 0)"
        myDir = mainDir + "/output_180_" + nx_txt  + "_prePB"
        imgPath_prePB = myDir + "/" + str(person_i + 1) + "-" + nx_num + "_2D_proj.png"
        count = show_1_img(imgPath_prePB, person_i, nx_num, count, order_list, zoom_ratio, pb_pivot_str)
        
        pb_pivot_str = "Image " + nx_txt + " \"" + nx_num + "\""
        imgPath_Ori = imgDir + "/" +  str(person_i + 1) + "-" + nx_num + ".jpg"
        count = show_1_img(imgPath_Ori, person_i, nx_num, count, order_list, zoom_ratio, pb_pivot_str)
        
        for pivot in pivot_List:
            for pb in pb_List:                
                myDir = mainInOutputDir + \
                    "/output_180_" + nx_txt + "_PB" + \
                    "/pb" + str(pb) + "_pivot" + str(pivot)
                pb_pivot_str = "(" + str(pb) + ", " + str(pivot) + ")"
                imgPath = myDir + "/" + str(person_i + 1) + "-" + nx_num + "_2D_proj.png"
                count = show_1_img(imgPath, person_i, nx_num, count, order_list, zoom_ratio, pb_pivot_str)
                    
    plt.show()    
    return

pb_List = [2, 10] # number of neighbors selected from pivots
pivot_List = [20, 100] # number of pivots being used
normal_smile_txt_List = ["normal", "smile"]
normal_smile_num_List = [11, 12]
order_list = [1, 4, 2, 3, 5, 6, 7, 10, 8, 9, 11, 12]

mainDir = "C:/your_path/output" # main directory to store the .ply output of the C++ codes in host machine
datasetDir = "C:/your_path/input/FEI_Face_Database" # directory in host machine to store the FEI_Face_Database

zoom_ratio = 0.7
num_person = 200

# person_i_plusOne_list = range(1,201) # list of individuals to be visualized
person_i_plusOne_list = [3] # list of individuals to be visualized
# person_i_plusOne_list = [3, 14, 18, 22, 30, 77, 79, 84, 143, 157, 179, 200] # list of individuals to be visualized

for person_i_plusOne in person_i_plusOne_list:
    show_1_person(person_i_plusOne, zoom_ratio, num_person, mainDir, datasetDir)