import numpy as np
from cv2 import Rodrigues

def model_to_camera(points_3d, rot_mat, tvec):
    # single_dim = points_3d.ndim == 1
    # if single_dim:
    #     points_3d = points_3d.reshape((1, 3))
    # if rot_vec_or_mat.shape == (3, 3):
    #     rot_mat = rot_vec_or_mat
    # else:
    #     rot_mat, _ = Rodrigues(rot_vec_or_mat)

    cam_points = rot_mat @ points_3d.T + tvec


    
    # if single_dim:
    #     cam_points = cam_points.reshape((3,))
    return cam_points


def model_to_normal_coords(points_3d, rot_vec_or_mat, tvec):
    return camera_to_normal_coords(*model_to_camera(points_3d, rot_vec_or_mat, tvec))


def model_to_normal_coords_array(points_3d, rot_vec_or_mat, tvec):
    '''
    :return: np.ndarray, shape: Nx2.
        Note: may not be contiguous in memory, use np.ascontiguousarray() if needed.
    '''
    xy_tuple = model_to_normal_coords(points_3d, rot_vec_or_mat, tvec)
    return np.array(xy_tuple, 'float32').T


def camera_to_image(X, Y, Z, calib_coefs):
    return normal_coords_to_image(*camera_to_normal_coords(X, Y, Z), calib_coefs)

def ort_projection(X, Y, Z):
    return X, Y


def camera_to_normal_coords(X, Y, Z):

    if 0:
        inv_z = 1 / Z
        x = X * inv_z
        y = Y * inv_z
    else:
        x = (Z * 1 * X) / Z
        y = (Z * 1 * Y) / Z
    
    
    return x, y


def normal_coords_to_image(x, y, calib_coefs):
    # w, h, k1, k2, p1, p2, cx, cy, fx, fy = calib_coefs
    # x2 = np.square(x)
    # y2 = np.square(y)
    # r2 = x2 + y2
    # r4 = np.square(r2)
    # xy = x * y
    # radial_coef = 1 + k1 * r2 + k2 * r4
    # x_dist = x * radial_coef + p1 * (r2 + 2 * x2) + 2 * p2 * xy
    # y_dist = y * radial_coef + p2 * (r2 + 2 * y2) + 2 * p1 * xy
    # u = cx + x_dist * fx
    # v = cy + y_dist * fy

    '''
    Great revelation!

    fx, fy is a ZOOM
    cx, cy is a CENTER of screen

    '''

    cx, cy, fx, fy = calib_coefs
    u = cx + x * fx
    v = cy + y * fy
    
    return u, v

def are_vertices_ccw_in_screen_space(p0, p1, p2):
    dx01 = p1[0] - p0[0]
    dy01 = p1[1] - p0[1]
    dx02 = p2[0] - p0[0]
    dy02 = p2[1] - p0[1]
    return (dx01 * dy02 - dy01 * dx02) < 0

def get_vis_and_luma(p1, p2, p3, light_src=None):
    p12 = p2-p1
    p13 = p3-p1

    face_normal = np.cross(p12,p13)
    face_normal_unit = face_normal / np.linalg.norm(face_normal)

    if light_src is None:
        vis_unit = np.array([0,0,-1])
        vis = np.dot(face_normal_unit, vis_unit)
        return vis, vis
    else:
        vis_unit = np.array([0,0,-1])
        vis = np.dot(face_normal_unit, vis_unit)
        l_unit = light_src / np.linalg.norm(light_src)
        luma = np.dot(face_normal_unit, l_unit)
        return vis, luma


def btp2d(p1,p2,p3,depth):
    '''
    binary triangle partition
    '''
    intensvs = [] # intensivities
    faces    = []

    leafs = get_sub_faces(p1,p2,p3)
    faces.append(leafs['right'])

    for i in range(depth):
        leafs = get_sub_faces(*leafs['left'])
        faces.append(leafs['right'])
    
    faces.append(leafs['left'])
    
    return faces

def btp3d(p1,p2,p3,depth): # points 3d
    faces    = []

    leafs = get_sub_faces(p1,p2,p3)
    faces.append(leafs['right'])

    for i in range(depth):
        leafs = get_sub_faces(*leafs['left'])
        faces.append(leafs['right'])

    faces.append(leafs['left'])
    
    return faces # 3d

def get_sub_faces_with_coefs_2d(p1, p2, p3, coefs):
    pnts_on_line = []
    for coef in coefs:
        pass

def get_sub_faces(p1, p2, p3):
    p =  (np.absolute(p1-p2) // 2) + p1
    return {'left': (p1, p, p3), 'right': (p, p2, p3)}

    