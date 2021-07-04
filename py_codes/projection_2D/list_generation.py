import numpy as np

# Created by Lanston Chu on 2021.06.14

# to generate list to control colored_2D.py
# this file is to be run by host

# this function is to write 6 lines for 1 group
def write_1_group(myDir, initialDir, person_i, nx_str, nx_num, pb, pivot, vVecStr, outs, skipPrePB_flag):
    
    if (pb == 0 and pivot !=0) or (pb != 0 and pivot ==0):
        raise Exception("pb and pivot should be 0 together.")

    # Line 1: final frontal (i.e. input)
    if pb == 0 and skipPrePB_flag == 1:
        return
    
    # Line 0: initial (i.e. input)
    line0 = initialDir + "/" + str(person_i + 1) + "-" + nx_num + ".ply"

    line1 = myDir + "/" + str(person_i + 1) + "-" + nx_num + "_final_frontal.ply"        
    
    # Line 2: rotation (i.e. input)
    line2 = vVecStr[1:-1]
    
    # line 3: final frontal colored (i.e. output)
    line3 = myDir + "/" + str(person_i + 1) + "-" + nx_num + "_final_frontal_colored.ply"
    
    # line 4: rotated/resized (i.e. output)
    line4 = myDir + "/" + str(person_i + 1) + "-" + nx_num + "_rotated_resized.ply"
    
    # line 5: 2D imgage (i.e. output)
    line5 = myDir + "/" + str(person_i + 1) + "-" + nx_num + "_2D_proj.png"
      
    # write lines
    outs.write(line0 + "\n")
    outs.write(line1 + "\n")
    outs.write(line2 + "\n")
    outs.write(line3 + "\n")
    outs.write(line4 + "\n")
    outs.write(line5 + "\n")
    outs.write("\n")    
    return

num_person = 200 # total number of person in the database
pb_List = [2, 10] # number of neighbors selected from pivots
pivot_List = [20, 100] # number of pivots being used
normal_smile_str_List = ["normal", "smile"]
normal_smile_num_List = [11, 12]

runFrom = 1
runTo = 200
skipPrePB_flag = 0 # whether to skip the prePB .ply files

mainDir = "C:/your_path/output" # main directory to store the .ply output of the C++ codes in host machine

rotation_path = "./rotation.npy" # where you place the rotation input
txtOutputPath = "./inputList_180_normal_smile.txt"

rVecs = np.load(rotation_path)

with open(txtOutputPath,"w") as outs: # input list and output list
    
    count = 0
    for person_i in range(num_person):
        dir_index = 1 + int(np.floor(person_i/(num_person/4))) # the first 1/4 persons are in "dir 1", second 1/4 in "dir 2" etc.
        vVecStr = str(rVecs[count,:])
        
        if person_i % 10 == 0:
            continue    

        if not(runFrom <= (person_i + 1) and (person_i + 1) <= runTo): # for partial list generation
            count += 1
            continue  

        for ns_i in range(2):
            
            nx_str = normal_smile_str_List[ns_i]
            nx_num = str(normal_smile_num_List[ns_i])
            
            initialDir = mainDir + "/output_180_" + nx_str + "_initial" # directory of the initial .ply (i.e. no-expression, no-wrinkles, non-perturbed)
            plyInOutputDir_prePB = mainDir + "/output_180_" + nx_str  + "_prePB" # directory of the non-perturbed face .ply
            write_1_group(plyInOutputDir_prePB, initialDir, person_i, nx_str, nx_num, 0, 0, vVecStr, outs, skipPrePB_flag) # no pb and no pivot

            for pivot in pivot_List:
                for pb in pb_List:    
                    plyInOutputDir_PB = mainDir + "/output_180_" + nx_str + "_PB" + \
                                        "/pb" + str(pb) + "_pivot" + str(pivot) # where you place the perturbed faces .ply
                
                    write_1_group(plyInOutputDir_PB, initialDir, person_i, nx_str, nx_num, pb, pivot, vVecStr, outs, skipPrePB_flag)
        count += 1