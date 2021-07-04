# author: Lanston Hau Man Chu
# 2021.06.12

import numpy as np
from create_alphas_from_images import call_models_to_create_alphas

input_path = "/shared/input/FEI_Face_Database"

output_path_0 = "/app/demoCode/alphas/FEI/alphas_180_normal.npy"
output_path_1 = "/app/demoCode/alphas/FEI/alphas_180_smile.npy"
output_path_2 = "/app/demoCode/alphas/FEI/alphas_20_half.npy"

# =============================================================================
# output_path_0 = "/app/demoCode/alphas/FEI/alphas_100_normal.npy"
# output_path_1 = "/app/demoCode/alphas/FEI/alphas_100_smile.npy"
# output_path_2 = "/app/demoCode/alphas/FEI/alphas_100_half.npy"
# =============================================================================

outputList = [output_path_0, output_path_1, output_path_2]

num_person = 200 # total number of person in the database

inputListList = [[], [], []]
for person_i in range(num_person):
    dir_index = 1 + int(np.floor(person_i/(num_person/4))) # the first 1/4 persons are in "dir 1", second 1/4 in "dir 2" etc.
    person_dir = input_path + "/originalimages_part" + str(dir_index)

    if person_i % 10 != 0: # 9 persons: 1 person for "train/eval":pivot
# =============================================================================
#     if person_i % 2 != 0: # 1 persons: 1 person for "train/eval":pivot, i.e.for "alphas_100_half.npy"
# =============================================================================
        train_eval_flag = 1
        images_capture_indices = [[11, 0], [12, 1]] # to embed "normal image no. 11" and "normal image no. 12" into alphas

    else: # pivot-person for no. 0, 10, 20, ..., 190
        train_eval_flag = 0
        if person_i/2 % 2 == 0:
            images_capture_indices = [[11, 2]]
        else:
            images_capture_indices = [[12, 2]]

    # create lists
    for pair_j in images_capture_indices:
        image_j = pair_j[0]
        list_index_j = pair_j[1]
        person_i_plusOne = person_i + 1 # image's indices is from 1 to 200 instead of 0 to 199
        image_path = person_dir + "/" + str(person_i_plusOne) + "-" + "{:02d}".format(image_j) + ".jpg"
        # print(image_path)
        inputListList[list_index_j].extend([image_path])

call_models_to_create_alphas(inputListList, outputList)
