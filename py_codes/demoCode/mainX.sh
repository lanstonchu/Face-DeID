# This file is created by Lanston
# this file is to run the python code for all 8 main set of data
# this file should be run in Docker's container with Cuda
# > sh mainX.sh

python testBatchModel.py testImages_180_normal.txt /shared/output/output_180_normal_prePB
python testBatchModel.py testImages_180_normal.txt /shared/output/output_180_normal_PB/pb2_pivot20
python testBatchModel.py testImages_180_normal.txt /shared/output/output_180_normal_PB/pb10_pivot20
python testBatchModel.py testImages_180_normal.txt /shared/output/output_180_normal_PB/pb2_pivot100
python testBatchModel.py testImages_180_normal.txt /shared/output/output_180_normal_PB/pb10_pivot100

python testBatchModel.py testImages_180_normal.txt /shared/output/output_180_smile_prePB
python testBatchModel.py testImages_180_smile.txt /shared/output/output_180_smile_PB/pb2_pivot20
python testBatchModel.py testImages_180_smile.txt /shared/output/output_180_smile_PB/pb10_pivot20
python testBatchModel.py testImages_180_smile.txt /shared/output/output_180_smile_PB/pb2_pivot100
python testBatchModel.py testImages_180_smile.txt /shared/output/output_180_smile_PB/pb10_pivot100

# python testBatchModel.py testImages_5_old_people.txt /shared/output/output_180_normal_PB/pb2_pivot20
# python testBatchModel.py testImages_5_old_people.txt /shared/output/output_180_normal_PB/pb10_pivot20
# python testBatchModel.py testImages_5_old_people.txt /shared/output/output_180_normal_PB/pb2_pivot100
# python testBatchModel.py testImages_5_old_people.txt /shared/output/output_180_normal_PB/pb10_pivot100
