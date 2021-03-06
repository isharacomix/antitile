#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates SVG files for each subdivision square and triangle
"""

import csv
from math import gcd
import numpy as np
import antitile
from antitile import xmath

def lines(n, m, digits, poly, style='stroke="black"'):
    shape = poly['shape']
    frame_fun = poly['frame']
    statements = []
    lineitem = ('<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
                + style + '/>')
    frame = frame_fun(n, m)
    frame = frame.reshape((-1, 2, 2))
    if m > 0:#remove degenerate lines
        norm = np.linalg.norm(frame[:, 0]-frame[:, 1], axis=-1)
        bad = np.isclose(norm, 0)
    else: #remove lines that overlap the black triangle (and degenerates)
        norm = np.linalg.norm(frame[..., np.newaxis, :] - shape, axis=-1)
        bad = np.any(np.isclose(norm, 0), axis=(1, 2))
    frame = np.round(frame[~bad], digits)
    for line in frame:
        pt1 = line[0]
        pt2 = line[1]
        if np.all(np.isclose(pt1, pt2)):
            pass
        else:
            thisline = lineitem.format(x1=pt1[0], x2=pt2[0],
                                       y1=pt1[1], y2=pt2[1])
            statements.append(thisline)
    return statements

def svg_breakdowns(shapeinfo, n, m):
    g = gcd(n, m)
    digits = 1
    size = shapeinfo['size']
    shape = shapeinfo['shape']
    header1 = '<?xml version="1.0" encoding="utf-8" standalone="no"?>'
    header2 = ('<svg height="{h}" width="{w}" '.format(w=size[0], h=size[1]) +
               'xmlns="http://www.w3.org/2000/svg" ' +
               'xmlns:xlink="http://www.w3.org/1999/xlink">')
    footer1 = ('<polygon points="' +
               ' '.join([format(pt[0], 'g') + ',' + format(pt[1], 'g')
                         for pt in np.round(shape, digits)]) +
               '" fill="none" stroke=')
    if m > 0:
        footer1 += '"blue"/>'
    else:
        footer1 += '"black"/>'
    footer2 = '</svg>'
    statements = [header1, header2]
    if g > 1 and m > 0:
        style = 'stroke="red" stroke-dasharray="3"'
        statements += lines(g, 0, digits, shapeinfo, style)
    statements += lines(n, m, digits, shapeinfo)
    statements += [footer1, footer2]
    return '\n'.join(statements)

square = {'name': 'square',
          'shape': np.array([[1, 1],
                             [1, 181],
                             [181, 181],
                             [181, 1]]),
          'size': [182,]*2,
          'frame': lambda n, m: antitile.breakdown.frame_square(n, m)*180 + 1,
          'diagonal': 'Diagonal subdivision'}

tri_shape = np.array([[1, 157],
                      [181, 157],
                      [91, 1.1154273188010393]])
triangle = {'name': 'triangle',
            'shape': tri_shape,
            'size': [182, 158],
            'frame': lambda n, m: antitile.breakdown.frame_triangle(
                tri_shape, n, m, interp=xmath.lerp),
            'diagonal': 'Ortho subdivision'}

def factors(number):
    """Cheezy function to get the factors of a small number
    other than 1 and itself"""
    for i in range(2, number):
        if number % i == 0:
            yield i

def create_svgs(shapeinfo, end=16):
    """Produces a bunch of SVG files and a csv file for use with pattypan"""
    shapename = shapeinfo['name']
    desc_end = (". See [[:Category:Subdivision triangles; transparent]] for " +
                "details. Please do not edit this file without reading the " +
                "category page.")
    name_template = 'Subdivided ' + shapename + ' {:02d} {:02d}'
    wikifile = 'File:' + name_template + '.svg'

    with open(shapeinfo['name'] + '.csv', mode='w', newline='') as c:
        wr = csv.writer(c)
        wr.writerow(['path', 'name', 'description', 'other_versions',
                     'category'])
        for i in range(1, end+1):
            for j in range(end+1):
                g = gcd(i, j)
                svg = svg_breakdowns(shapeinfo, i, j)
                name = name_template.format(i, j)
                filename = name + '.svg'
                with open(filename, 'w') as f:
                    f.write(svg)
                gallery = ''
                if j == 0:
                    category = 'Parallel subdivision '+shapename+'s; transparent'
                elif j == i:
                    category = shapeinfo['diagonal']+' '+shapename+'s; transparent'
                else:
                    category = 'Skew subdivision '+shapename+'s; transparent'
                    gallery += (wikifile.format(j, i) + '|Mirror image ')
                if g > 1 and j > 0:
                    gallery += (wikifile.format(g, 0) +
                                '|Red lines indicate a composition of this...')
                    gallery += (wikifile.format(i//g, j//g) + '|...with this.')
                elif j == 0:
                    for n in factors(i):
                        gallery += (wikifile.format(n, 0) +
                                    '|Contained subdivision')
                if gallery:
                    other_versions = '<gallery>' + gallery + '</gallery>'
                else:
                    other_versions = ''
                desc = name + desc_end
                wr.writerow([filename, filename, desc,
                             other_versions, category])

def create_all(end=16):
    for shapeinfo in [triangle, square]:
        create_svgs(shapeinfo, end)

if __name__ == "__main__":
    create_all()
