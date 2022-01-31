import numpy as np
import math


def rot_mat_to_euler(M):
    """
    The angles returned are defined as "xyz" in terms of
      `scipy.spatial.transform.Rotation.as_euler`,
      i.e. x-y-z in the extrinsic coordinate frame.
    This is the same notation as the one used in GI4E HPDB.
    Based on glm::extractEulerAngleXYZ.

    :param M: 3x3 or 4x4 (homogenous) rotation matrix
              (left-multiplication, i.e. for column-vectors)
    :return: (pitch, yaw, roll)
    """
    t1 = math.atan2(M[2, 1], M[2, 2])
    C2 = math.sqrt(M[0, 0] * M[0, 0] + M[1, 0] * M[1, 0])
    t2 = math.atan2(-M[2, 0], C2)
    S1 = math.sin(t1)
    C1 = math.cos(t1)
    t3 = math.atan2(S1 * M[0, 2] - C1 * M[0, 1], C1 * M[1, 1] - S1 * M[1, 2])
    
    return t1, t2, t3


def euler_to_rot_mat(pitch, yaw, roll):
    """
    The inverse of `rot_mat_to_euler()`.

    :return: 3x3 rotation matrix (left-multiplication,
             i.e. for column-vectors).
    """
    x_angle = pitch
    y_angle = yaw
    z_angle = roll
    zs = math.sin(z_angle)
    zc = math.cos(z_angle)
    ys = math.sin(y_angle)
    yc = math.cos(y_angle)
    xs = math.sin(x_angle)
    xc = math.cos(x_angle)
    return np.array([
        [yc*zc,  xs*ys*zc-xc*zs,  xc*ys*zc+xs*zs],
        [yc*zs,  xs*ys*zs+xc*zc,  xc*ys*zs-xs*zc],
        [  -ys,           xs*yc,           xc*yc]])