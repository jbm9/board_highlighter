#!/usr/bin/env python

import sys


def gen_line(l):
    a = l.split(" ")
    if a[0] != "element":
        return None

    
    designator = a[1]
    return"""
    {
        "name": "Install %s",
        "components": "%s",
        "text": "Install %s"
    }""" % (designator, designator, designator)


f = file(sys.argv[1])

ds = filter(None, [ gen_line(l) for l in f ] )
print "[" + ",".join(ds) +"]"
f.close()
    
