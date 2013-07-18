import math
import numpy as np

class BoardDump:
    def __init__(self, path):
        self.path = path
        self.elements = {} # name => { "x0": ... }
        self.wires = []


        self.calpts = []

        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0


        self.x_m = 0
        self.x_c = 0
        self.y_m = 0
        self.y_c = 0

        f = file(path)
        for l in f:
            l = l.strip()
            a = l.split()

            k = a[0]

            if "board" == k:
                (self.x0, self.y0, self.x1, self.y1) = map(int, a[1:])

            if "element" == k:
                a = l.split(" ", 6)
                name = a[1]
                (x0,y0,x1,y1) = map(int, a[2:6])

                if len(a) > 6:
                    value = a[6]
                else:
                    value = None

                self.elements[name] = {
                    "x0": x0,
                    "x1": x1,
                    "y0": y0,
                    "y1": y1,
                    "value": value,
                    }

            if "wire" == k:
                (level, x0, y0, x1, y1) = map(int, a[1:])
                if level == 20:
                    self.wires.append( [x0, y0, x1, y1] )

        f.close()

    def scale_x(self, x):
        return (float(x) - self.x0)/(self.x1 - self.x0)

    def scale_y(self, y):
        return 1.0 - (float(y) - self.y0)/(self.y1 - self.y0)

    def invert_x(self, xp):
        return self.x0 + (self.x1-self.x0)*xp

    def invert_y(self, yp):
        return self.y0 + (self.y1-self.y0)*(1.0-yp)


    def corners_of(self, name):
        e = self.elements[name]

        return (self.scale_x(e["x0"]), self.scale_y(e["y0"]),
                self.scale_x(e["x1"]), self.scale_y(e["y1"]) )


    def get_cal_points(self):
        zero_pt = [9999,0,0] # d, x, y
        maxpt = [0,0,0]

        def chkpt(x,y, zero_pt, maxpt):
            retval = 0
            d = math.sqrt(x*x+y*y)
            if d < zero_pt[0]:
                retval += 1
            if d > maxpt[0]:
                retval += 2
            return retval
        
        for (x0,y0,x1,y1) in self.wires:
            d = math.sqrt(x0*x0+y0*y0)
            c =  chkpt(x0,y0, zero_pt, maxpt)
            if 0 != c:
                if c & 1:
                    zero_pt = [ d, x0, y0 ]
                if c & 2:
                    maxpt = [d, x0,y0]

            c = chkpt(x1,y1, zero_pt, maxpt)
            if 0 != c:
                if c & 1:
                    zero_pt = [ d, x1, y1 ]
                if c & 2:
                    maxpt = [d, x1,y1]
                    
        return [ [ zero_pt[1],zero_pt[2]],
                 [ maxpt[1],maxpt[2]]      ]

    def calibration_point(self, bx, by, sx,sy):
        self.calpts.append( [bx,by, sx,sy] )

    def projection_of(self, name):
        e = self.elements[name]
        return [ self.project(e["x0"], e["y0"]),
                 self.project(e["x1"], e["y1"]) ]

    def project(self, x, y):
        return [self.x_c + self.x_m * x, self.y_c + self.y_m*y ]
    

    def calibrate(self):

        def fitof(a,b):
            x = np.array([ p[a] for p in self.calpts ])
            y = np.array([ p[b] for p in self.calpts ])

            A = np.vstack([x, np.ones(len(x))]).T
            m,c = np.linalg.lstsq(A, y)[0]

            return m,c

        self.x_m, self.x_c = fitof(0,2)
        self.y_m, self.y_c = fitof(1,3)

        
        
