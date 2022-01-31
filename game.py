import pygame as pg
import random as rand

import numpy as np
import math

from settings import *

from projection import *
from rotation import *

d2r = math.pi / 180
r2d = 180 / math.pi

pitch = yaw = roll = 0.0

simpleRotMat = np.array([[1.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0],
                         [0.0, 0.0, 1.0]])

tvec = np.array((0.0, 0.0, 1.0)).reshape(3,1)

calib_coefs = (SCR_WIDTH/2, SCR_HEIGHT/2, 150.0, 150.0)

sub_faces_steps = [0.2, 0.4, 0.6, 0.8]

cc = CommonColors()
face_colors = (cc.White, cc.Silver, cc.Gray, cc.Red, cc.Maroon, cc.Yellow, cc.Olive, cc.Lime, cc.Green, cc.Aqua, cc.Teal, cc.Blue)
rect_colors = (cc.Silver, cc.Red, cc.Yellow, cc.Blue, cc.Green, cc.Maroon)
light_colors = (cc.Yellow, cc.Yellow, cc.Yellow, cc.Yellow, cc.Yellow, cc.Yellow)

def get_meshes():
    v0 = np.array((0,0,0), 'float64')
    v1 = np.array((0,0,1), 'float64')
    v2 = np.array((0,1,0), 'float64')
    v3 = np.array((0,1,1), 'float64')
    v4 = np.array((1,0,0), 'float64')
    v5 = np.array((1,0,1), 'float64')
    v6 = np.array((1,1,0), 'float64')
    v7 = np.array((1,1,1), 'float64')

    verts = np.array([v0,v1,v2,v3,v4,v5,v6,v7])

    faces = [1,3,2 , 1,2,0 , 5,7,3 , 5,3,1 , 1,4,5 , 1,0,4 , 5,6,7 , 5,4,6 , 0,2,6 , 0,6,4 , 3,7,2 , 2,7,6]
    faces_size = int(len(faces)/3)
    faces = np.array(faces).reshape(faces_size, 3)

    meshes = {'verts': verts, 'faces': faces}
    return meshes

class Game:
    is_running = True
    dir = DIR_RIGHT
    
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.display = pg.display.set_mode(SCR_SIZE)
        self.bg_color = BLACK

        # pg.draw.rect(self.display , RED, (10,10, 100, 100))
        
        self.mesh = get_meshes()

        scale = 1
        self.mesh['verts'] *= scale


        self.display.fill(BLACK)
        self.update_pos(simpleRotMat, tvec)

        # self.pos = Position(*START_POS)
        # self.snake = Snake(self.pos, GREEN)
        # self.snake.move(*self.dir)

        # self.meal = self.draw_meal()

    def update_pos(self, rot_mat, tvec):
        verts = self.mesh['verts']

        verts_in_cam = model_to_camera(verts, rot_mat, tvec)

        ### Perspective projection
        img_xy = np.array(camera_to_image(*verts_in_cam, calib_coefs)).T 

        ### New verision of back edges cutting
        verts_in_cam = verts_in_cam.T
        self.draw_faces(verts_in_cam, img_xy, 'rect')

    def draw_faces(self, verts_in_cam, img_xy, face=None):
        i = 0
        j = 0
        k = 1
        for i1, i2, i3 in self.mesh['faces']:
              
            p1 = verts_in_cam[i1]
            p2 = verts_in_cam[i2]
            p3 = verts_in_cam[i3]
            intensvs = is_face_vis(p1,p2,p3)
            if intensvs > 0:
                p1_2d = img_xy[i1,:]
                p2_2d = img_xy[i2,:]
                p3_2d = img_xy[i3,:]

                if  face == 'rect':
                    r = light_colors[j][0] * intensvs
                    g = light_colors[j][1] * intensvs
                    b = light_colors[j][2] * intensvs

                    pg.draw.polygon(self.display, (r,g,b), [p1_2d,p2_2d,p3_2d])
                    # self.draw_triangle(p1_2d, p2_2d, p3_2d)
                elif face == 'triang':
                    pg.draw.polygon(self.display, face_colors[i], [p1_2d,p2_2d,p3_2d])
                else:
                    self.draw_triangle(p1_2d, p2_2d, p3_2d)
                    # faces = btp2d(p1_2d, p2_2d, p3_2d, 1)
                    # for face in faces:
                    #     self.draw_triangle(face[0], face[1], face[2])

            i += 1
            if i % 2 == 0: j += 1
    
    def get_sub_faces(self, i1, i2, i3):
        v1,v2,v3 = self.mesh['verts'][[i1, i2, i3]]
        axis = self.get_axis(v2, v3)
        sub_faces = []
        for i in sub_faces_steps:
            sub_faces.append(tuple())


    def get_axis(self, p2, p3):
        if np.absolute(p2[0] - p3[0]) > 0.1: return 0 # x
        if np.absolute(p2[1] - p3[1]) > 0.1: return 1 # y
        if np.absolute(p2[2] - p3[2]) > 0.1: return 2 # z

    
    def draw_triangle(self, p1, p2, p3):
        pg.draw.line(self.display, cc.Purple, p1, p2, 2)
        pg.draw.line(self.display, cc.Purple, p2, p3, 2)
        pg.draw.line(self.display, cc.Purple, p3, p1, 2)
    
    def render(self):
        pg.display.update()

    def update(self):
        self.clock.tick(FPS)

    def event_handler(self):
        global simpleRotMat
        global tvec

        global pitch, yaw, roll

        step = 0.05

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.is_running = False

        key_pressed = pg.key.get_pressed()
                
        if key_pressed[pg.K_d]:
            yaw += step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_a]:
            yaw -= step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_w]:
            pitch += step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_s]:
            pitch -= step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_q]:
            roll += step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_c]:
            roll -= step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_UP]:
            tvec[2,0] += step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_DOWN]:
            tvec[2,0] -= step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_LEFT]:
            tvec[0,0] -= step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)
        elif key_pressed[pg.K_RIGHT]:
            tvec[0,0] += step
            simpleRotMat = euler_to_rot_mat(pitch, yaw, roll)
            self.display.fill(BLACK)
            self.update_pos(simpleRotMat, tvec)

    def quit(self):
        pg.quit()

