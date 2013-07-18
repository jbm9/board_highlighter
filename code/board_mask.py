#!/usr/bin/env python

import scipy
import scipy.misc

from board_dump import BoardDump
from assembly_steps import AssemblySteps

import skimage
import skimage.color

import matplotlib.pyplot as plt

import re

import sys

class BoardMasker:
    def __init__(self, projectname, img_path, dmp_path, steps_path, html_path):
        self.projectname = projectname
        self.i = scipy.misc.imread(img_path)
        self.i = 255 - self.i
        self.x = self.i.shape[1]
        self.y = self.i.shape[0]

        self.board = BoardDump(dmp_path)
        self.steps = AssemblySteps(steps_path)

        self.htmlfile = file(html_path, "w")
        self.print_html_header()

    def print_html_header(self):
        f = file("steps.html.header")
        self.htmlfile.write(f.read())
        f.close()


    def print_html_footer(self):
        f = file("sidebar.html")
        self.htmlfile.write(f.read())
        f.close()

        f = file("steps.html.footer")
        self.htmlfile.write(f.read())
        f.close()



    def mask_component(self, designator):
        corners = self.board.corners_of(designator)

        x0 = corners[0]*(self.x-1)
        x1 = corners[2]*(self.x-1)

        y0 = corners[1]*(self.y-1)
        y1 = corners[3]*(self.y-1)

        return [x0, y0, x1, y1]

    def reverse_point(self, x, y):
        xp = float(x)/self.x
        yp = float(y)/self.y

        xpp = self.board.invert_x(xp)
        ypp = self.board.invert_y(yp)

        return [xpp, ypp, xp, yp, x, y, self.x, self.y]


    def run_calibration(self):
        _cal_x = 0
        _cal_y = 0

        def onclick(event):
            x = event.xdata
            y = event.ydata

            p = bm.reverse_point(x,y)

            bm.board.calibration_point(_cal_x, _cal_y, x, y)
            print "Point: %d,%d => %s" % (x,y,str(p))

            
        for pt in bm.board.get_cal_points():
            print "Please click on the corner of your board at %s" % pt
            fig = plt.figure()
            ax = fig.add_subplot(111)
            cid = fig.canvas.mpl_connect('button_press_event', onclick)

            _cal_x, _cal_y = pt
            plt.imshow(self.i)
            plt.show()

        self.board.calibrate()


    def highlight(self, i, component):
        extent = self.board.projection_of(component)
        (ex0, ey0) = map(int, extent[0])
        (ex1, ey1) = map(int, extent[1])

        # print "Extent: %s" % str(extent)

        if (ex1 < ex0):
            (ex0, ex1) = (ex1, ex0)

        if (ey1 < ey0):
            (ey0, ey1) = (ey1, ey0)

        print "Highlight %s: %d,%d ~ %d,%d" % (component, ex0, ey0, ex1, ey1)

        border = 0.05

        dx = ex1-ex0
        dy = ey1-ey0
        
        ex0 -= dx*border
        ex1 += dx*border
        ey0 -= dy*border
        ey1 += dy*border

        print "Highlight: dx %d dy %d" % (dx, dy)
        print "Highlight: shape: %s" % str(self.i.shape)
        print "Highlight: %d x %d" % (self.x, self.y)
        
        print "Highlight %s: %d,%d ~ %d,%d" % (component, ex0, ey0, ex1, ey1)
        if ex0 < 0:
            ex0 = 0
        if ey0 < 0:
            ey0 = 0
        if ex1 > self.x-1:
            ex1 = self.x-1
        if ey1 > self.y - 1:
            ey1 = self.y-1


        print "Highlight %s: %d,%d ~ %d,%d" % (component, ex0, ey0, ex1, ey1)
        j = skimage.color.rgb2hsv(i)
        k = j * [1.0, 0.25, 0.25]
        l = skimage.color.hsv2rgb(k)
        blk = self.i[ ey0:ey1,ex0:ex1 ].astype(float)/255.0
        l[ ey0:ey1, ex0:ex1 ] = blk

        return l


    def run(self):
        for i,step in enumerate(self.steps.steps):
            j = self.i.copy()
            for c in step["components"].split(","):
                j = self.highlight(j, c)


            bogons = re.compile("[^A-Za-z0-9._-]")
            
            filename = "%s__step_%d__%s.png" % (self.projectname, i+1, "_".join(step))

            step["img"] = filename
            step["dimx"] = self.x
            step["dimy"] = self.y

            filename = bogons.sub('_', filename)
            
            scipy.misc.imsave(filename, j)
            print "Saved step %d %s to %s" % (i, str(step), filename)
            print "Generating HTML"
            html = self.steps.gen_html(step)
            self.htmlfile.write(html)
            self.htmlfile.write("\n\n")

        self.print_html_footer()

if __name__ == "__main__":
    projectname = sys.argv[1]

    bm = BoardMasker(projectname, projectname+".png", projectname+".dmp", projectname+".json", projectname+"_steps_base.html")
    bm.run_calibration()

    bm.run()
