#!/usr/bin/env python

import scipy
import scipy.misc

from board_dump import BoardDump
from assembly_steps import AssemblySteps


class BoardMasker:
    def __init__(self, img_path, dmp_path, steps_path):
        self.i = scipy.misc.imread(img_path)
        self.x = self.i.shape[1]
        self.y = self.i.shape[0]

        self.board = BoardDump(dmp_path)
        self.steps = AssemblySteps(steps_path)


    def mask_component(self, designator):
        corners = self.board.corners_of(designator)

        x0 = corners[0]*(self.x-1)
        x1 = corners[2]*(self.x-1)

        y0 = corners[1]*(self.y-1)
        y1 = corners[3]*(self.y-1)


        if (x1 < x0):
            (x0,x1) = (x1,x0)

        if (y1 < y0):
            (y0,y1) = (y1,y0)

        return [x0, y0, x1, y1]


    def reverse_point(self, x, y):
        xp = float(x)/self.x
        yp = float(y)/self.y

        xpp = self.board.invert_x(xp)
        ypp = self.board.invert_y(yp)

        return [xpp, ypp, xp, yp, x, y, self.x, self.y]

bm = BoardMasker("foo.png", "fiducial.dmp", "steps.txt")

import skimage
import skimage.color

import matplotlib.pyplot as plt


def p(i):
    plt.imshow(i)
    plt.show()

i = bm.i

def highlight(i, component):
    j = i
    extent = [ int(round(y)) for y in  bm.mask_component(component) ]
    (ex0, ey0, ex1, ey1) = extent

    if (ex1 < ex0):
        (ex0, ex1) = (ex1, ex0)

    if (ey1 < ey0):
        (ey0, ey1) = (ey1, ey0)

    
    j[ ey0:ey1, ex0:ex1 ] += 80
    return j


fig = plt.figure()
ax = fig.add_subplot(111)

j = highlight(i, "B")
for r in range(0, 6):
    j = highlight(j, "R%d" % r)

def onclick(event):
    x = event.xdata
    y = event.ydata

    p = bm.reverse_point(x,y)

    print "Point: %d,%d => %s" % (x,y,str(p))

cid = fig.canvas.mpl_connect('button_press_event', onclick)


p(j)
