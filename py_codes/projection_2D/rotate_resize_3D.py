# this file is to rotate and resize a 3D shape
# resize of 3D shape: of resize the coordinates to the scale of around 1.0, so as to fit the 2D renderer's spotlight

import trimesh
import pyrender
from PIL import Image
import numpy as np
from plyfile import PlyData, PlyElement
from Rodrigues import rVec_to_R
import os
import time

# generate a random rotation vector with small magnitude
def random_rot_vector():
   
    # sample direction of vector on a unit sphere
    z = np.random.rand(1)
    r = np.sqrt(1-z**2) # radius of circle on the xy-cross-section-plane
    th = np.random.rand(1)*2*np.pi
    x = r*np.cos(th)
    y = r*np.sin(th)
    
    # sample magnitude of vector
    radius_vector = np.random.rand(1)*np.pi/8 # max. rotation allowed for 1 direction = 22.5 degree = pi/8
    rVec = radius_vector*np.array([x, y, z])
        
    return rVec


# rotate and resize 1 .ply file
def rotate_resize_1_plydata(plydata, rotated_resized_path, image_2D_path, image_size, rVec, remove_PLY_flag):
    
    vertices = plydata.elements[0] # 0 for vertices; 1 for faces    
    vertices_values = np.array([list(vertix_values) for vertix_values in vertices.data]) # re-format vertices' coordinates/color as array
    R = rVec_to_R(rVec) # convert vector into rotation matrix
    Rt = np.transpose(R)
    # Rt = np.identity(3)
    
    # use x-axis to do the resize (because more symmetric)
    resize_ratio = 1/(np.max(vertices_values[:,0]) - np.min(vertices_values[:,0])) # resize coordinates of the existing .ply such that face's width is around 1.0
    # resize_ratio = 1
    shape = np.matmul(vertices_values[:,0:3], Rt)*resize_ratio # rotation and resize
    myColor = vertices_values[:,3:6]
    
    myList = [(np.round(v[0],4), np.round(v[1],4), np.round(v[2],4), rgb[0], rgb[1], rgb[2]) for v, rgb in zip(shape, myColor)]
    vertices_xyzrgb = np.array(myList, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4'), ('red','u1'), ('green','u1'), ('blue','u1')])
    
    element_vertices = PlyElement.describe(vertices_xyzrgb, 'vertex')
    element_faces = plydata.elements[1]
    
    plydata_colored = PlyData([element_vertices, element_faces], text=True)
    plydata_colored.write(rotated_resized_path) # save the .ply file
    
    fuze_trimesh = trimesh.load(rotated_resized_path)
    mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
    scene = pyrender.Scene(ambient_light=[0.3, 0.3, 0.3]) # with background light apart from spotlight
    scene.add(mesh)
    
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
    
    camera_pose = np.array([
        [1.0,  0.0, 0.0, 0],
        [0.0,  1.0, 0.0, 0],
        [0.0,  0.0, 1.0, 1.8],
        [0.0,  0.0, 0.0, 1.0],
    ])
    
    scene.add(camera, pose=camera_pose)
    light = pyrender.SpotLight(color=np.ones(3), intensity=5.5,
                               innerConeAngle=np.pi/2,
                               outerConeAngle=np.pi/2) # max. spotlight angle is pi/2
    scene.add(light, pose=camera_pose)
    r = pyrender.OffscreenRenderer(*image_size)
    color, depth = r.render(scene)
    
    im = Image.fromarray(color)
    # im.show()
    im.save(image_2D_path)
    
    if remove_PLY_flag == 1:
        os.remove(rotated_resized_path) # remove the unused .ply file
    
    return rVec

if __name__ == '__main__':
    input_path = "./Desktop/rotate_resize_3D/yourPrefix_colored.ply"
    rotated_resized_path = "./Desktop/rotate_resize_3D/yourPrefix_rotated_resized.ply" # 3D output to be generated
    image_2D_path = "./Desktop/rotate_resize_3D/yourPrefix_project_2D.png" # 2D output to be generated
    image_size = [450, 450] # width and height
    remove_PLY_flag = 1
    
    plydata = PlyData.read(input_path)
    rVec = random_rot_vector()
    rotate_resize_1_plydata(plydata, rotated_resized_path, image_2D_path, image_size, rVec, remove_PLY_flag)
