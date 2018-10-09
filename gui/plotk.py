
#
# Copyright (c) 2011-2013, Bradley A. Minch
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
#     1. Redistributions of source code must retain the above copyright 
#        notice, this list of conditions and the following disclaimer. 
#     2. Redistributions in binary form must reproduce the above copyright 
#        notice, this list of conditions and the following disclaimer in the 
#        documentation and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#
import Tkinter as tk
import math, vector
import codecs

class plotk:

    class point:

        def __init__(self, x = None, y = None):
            self.x = x
            self.y = y

        def __str__(self):
            return '({x!s}, {y!s})'.format(x = self.x, y = self.y)

        def __repr__(self):
            return '({x!r}, {y!r})'.format(x = self.x, y = self.y)

    class curve:

        def __init__(self, **kwargs):
            self.data = kwargs.get('data', [])
            self.points = []
            self.name = kwargs.get('name', '')
            self.side = kwargs.get('side', 'left')
            self.marker_color = kwargs.get('marker_color', '')
            self.marker = kwargs.get('marker', '')
            self.curve_color = kwargs.get('curve_color', '')
            self.curve_style = kwargs.get('curve_style', '')

        def __str__(self):
            return str(self.data)

        def __repr__(self):
            return repr(self.data)

    def __init__(self, **kwargs):
        self.canvas_width = float(kwargs.get('width', 560.))
        self.canvas_height = float(kwargs.get('height', 420.))
        self.marker_radius = float(kwargs.get('marker_radius', 4.))
        self.marker_lineweight = float(kwargs.get('marker_lineweight', 0.5))
        self.curve_lineweight = float(kwargs.get('curve_lineweight', 1.))
        self.tick_length = float(kwargs.get('tick_length', 6.))
        self.tick_lineweight = float(kwargs.get('tick_lineweight', 0.5))
        self.canvas_background_color = kwargs.get('background', '#CDCDCD')
        self.axes_background_color = kwargs.get('axes_background', '#FFFFFF')
        self.axes_color = kwargs.get('axes_color', '#000000')
        self.axes_lineweight = kwargs.get('axes_lineweight', 1.)
        self.label_font_baseline = float(kwargs.get('baseline', 0.6))
        self.label_fontsize = int(kwargs.get('fontsize', 12))
        self.label_font = kwargs.get('font', 'Helvetica')

        self.init_markers(self.marker_radius)

        self.marker_names = [[' ',  'No marker'], ['.', 'Point'], ['o', 'Circle'], ['x', 'Ex'], 
                             ['+', 'Plus'], ['*', 'Star'], ['s', 'Square'], ['d', 'Diamond'],
                             ['v', 'Triangle (down)'], ['^', 'Triangle (up)'], ['<', 'Triangle (left)'], 
                             ['>', 'Triangle (right)'], ['p', 'Pentagram'], ['h', 'Hexagram']]

        self.colors = {'b': '#0000FF', 'g': '#00FF00', 'r': '#FF0000', 
                       'c': '#00FFFF', 'm': '#FF00FF', 'y': '#FFFF00',
                       'k': '#000000', 'w': '#FFFFFF'}

        self.color_names = [['b', 'Blue'], ['r', 'Red'], ['g', 'Green'], ['c', 'Cyan'], 
                            ['m', 'Magenta'], ['y', 'Yellow'], ['k', 'Black'], ['w', 'White']]

        self.linestyles = {'-': (), ':': (1, 4), '--': (10, 4), '-.': (10, 4, 1, 4), '-:': (10, 4, 1, 4, 1, 4)}

        self.linestyle_names = [[' ',   'No line'], ['-',  'Solid'], [':',  'Dotted'], 
                                ['-.', 'Dash-dot'], ['-:', 'Dash-dot-dot'], ['--', 'Dashed']]

        self.multipliers = (1., 1e-3, 1e-6, 1e-9, 1e-12, 1e-15, 1e-18, 1e-21, 1e-24, 
                            1e24, 1e21, 1e18, 1e15, 1e12, 1e9, 1e6, 1e3)

        self.prefixes = (u'', u'k', u'M', u'G', u'T', u'P', u'E', u'Z', u'Y', 
                         u'y', u'z', u'a', u'f', u'p', u'n', u'\xB5', u'm')

        self.default_color_order = ('b', 'g', 'r', 'c', 'm', 'y')
        self.default_color_index = 0
        self.default_marker = '.'
        self.default_curve_style = '-'

        self.curve_id = 0
        self.curves = []

        self.xaxis_mode = 'linear'
        self.xaxis_sign = 1.
        self.xlimits_mode = 'auto'
        self.xlim = [0., 1.]
        self.xmin = 0.
        self.xmax = 1.
        
        self.left_yaxis_mode = 'linear'
        self.left_yaxis_sign = 1.
        self.left_ylimits_mode = 'auto'
        self.left_ylim = [0., 1.]
        self.left_ymin = 0.
        self.left_ymax = 1.

        self.right_yaxis_mode = 'linear'
        self.right_yaxis_sign = 1.
        self.right_ylimits_mode = 'auto'
        self.right_ylim = [0., 1.]
        self.right_ymin = 0.
        self.right_ymax = 1.

        self.update_sizes()

        self.find_x_ticks()
        self.find_left_y_ticks()
        self.find_right_y_ticks()

        self.grid_state = 'off'

        self.xlabel_value = ''
        self.left_ylabel_value = ''
        self.right_ylabel_value = ''

        self.svg_output = False
        self.svg_file = None

        self.dw = 0.
        self.dh = 0.
        self.x0 = 0.
        self.y0 = 0.

        self.root = kwargs.get('parent')
        if self.root==None:
            self.root = tk.Tk()
            self.root.title('plotk')
        self.canvas = tk.Canvas(self.root, width = self.canvas_width, height = self.canvas_height, background = self.canvas_background_color, highlightbackground = self.canvas_background_color)
        self.draw_axes()
        self.draw_x_ticks()
        self.draw_y_ticks()
        self.draw_axis_labels()
        self.canvas.pack(fill = 'both', expand = 'yes')
        self.dw = 2.*float(self.canvas.cget('highlightthickness'))
        self.dh = self.dw
        self.canvas.bind('<Configure>', self.resize)

    def init_markers(self, r = 4.):
        r_over_sqrt2 = r/math.sqrt(2.)
        r_over_sqrt3 = r/math.sqrt(3.)
        pi_over_180 = math.pi/180.
        r2 = r*math.sin(pi_over_180*18.)/math.sin(pi_over_180*54.)

        self.marker_coords = {}
        self.marker_coords['.'] = ((-0.5*r, -0.5*r), (0.5*r, 0.5*r))
        self.marker_coords['o'] = ((-r, -r), (r, r))
        self.marker_coords['x'] = ((0., 0.), (r_over_sqrt2, -r_over_sqrt2), 
                                   (0., 0.), (r_over_sqrt2, r_over_sqrt2), 
                                   (0., 0.), (-r_over_sqrt2, r_over_sqrt2), 
                                   (0., 0.), (-r_over_sqrt2, -r_over_sqrt2), 
                                   (0., 0.))
        self.marker_coords['+'] = ((0., 0.), (0., -r), 
                                   (0., 0.), (r, 0.), 
                                   (0., 0.), (0., r), 
                                   (0., 0.), (-r, 0.), 
                                   (0., 0.))
        self.marker_coords['*'] = ((0., 0.), (0., -r), 
                                   (0., 0.), (r_over_sqrt2, -r_over_sqrt2), 
                                   (0., 0.), (r, 0.), 
                                   (0., 0.), (r_over_sqrt2, r_over_sqrt2), 
                                   (0., 0.), (0., r), 
                                   (0., 0.), (-r_over_sqrt2, r_over_sqrt2), 
                                   (0., 0.), (-r, 0.), 
                                   (0., 0.), (-r_over_sqrt2, -r_over_sqrt2), 
                                   (0., 0.))
        self.marker_coords['s'] = ((-r_over_sqrt2, -r_over_sqrt2), (r_over_sqrt2, -r_over_sqrt2), 
                                   (r_over_sqrt2, r_over_sqrt2), (-r_over_sqrt2, r_over_sqrt2), 
                                   (-r_over_sqrt2, -r_over_sqrt2))
        self.marker_coords['d'] = ((0., -1.25*r), (r, 0.), (0., 1.25*r), (-r, 0.), (0., -1.25*r))
        self.marker_coords['v'] = ((0., r), 
                                   (r*math.cos(pi_over_180*150.), -r*math.sin(pi_over_180*150.)), 
                                   (r*math.cos(pi_over_180*30.), -r*math.sin(pi_over_180*30.)), 
                                   (0., r))
        self.marker_coords['^'] = ((0., -r), 
                                   (r*math.cos(pi_over_180*330.), -r*math.sin(pi_over_180*330.)), 
                                   (r*math.cos(pi_over_180*210.), -r*math.sin(pi_over_180*210.)), 
                                   (0., -r))
        self.marker_coords['<'] = ((-r, 0.), 
                                   (r*math.cos(pi_over_180*60.), -r*math.sin(pi_over_180*60.)), 
                                   (r*math.cos(pi_over_180*300.), -r*math.sin(pi_over_180*300.)), 
                                   (-r, 0.))
        self.marker_coords['>'] = ((r, 0.), 
                                   (r*math.cos(pi_over_180*240.), -r*math.sin(pi_over_180*240.)), 
                                   (r*math.cos(pi_over_180*120.), -r*math.sin(pi_over_180*120.)), 
                                   (r, 0.))
        self.marker_coords['p'] = ((0., -r),
                                   (r2*math.cos(pi_over_180*54.), -r2*math.sin(pi_over_180*54.)), 
                                   (r*math.cos(pi_over_180*18.), -r*math.sin(pi_over_180*18.)), 
                                   (r2*math.cos(pi_over_180*342.), -r2*math.sin(pi_over_180*342.)), 
                                   (r*math.cos(pi_over_180*306.), -r*math.sin(pi_over_180*306.)), 
                                   (0., r2), 
                                   (r*math.cos(pi_over_180*234.), -r*math.sin(pi_over_180*234.)), 
                                   (r2*math.cos(pi_over_180*198.), -r2*math.sin(pi_over_180*198.)), 
                                   (r*math.cos(pi_over_180*162.), -r*math.sin(pi_over_180*162.)), 
                                   (r2*math.cos(pi_over_180*126.), -r2*math.sin(pi_over_180*126.)), 
                                   (0., -r))
        self.marker_coords['h'] = ((0., -r), 
                                   (r_over_sqrt3*math.cos(pi_over_180*60.), -r_over_sqrt3*math.sin(pi_over_180*60.)), 
                                   (r*math.cos(pi_over_180*30.), -r*math.sin(pi_over_180*30.)), 
                                   (r_over_sqrt3, 0.), 
                                   (r*math.cos(pi_over_180*330.), -r*math.sin(pi_over_180*330.)), 
                                   (r_over_sqrt3*math.cos(pi_over_180*300.), -r_over_sqrt3*math.sin(pi_over_180*300.)), 
                                   (0., r), 
                                   (r_over_sqrt3*math.cos(pi_over_180*240.), -r_over_sqrt3*math.sin(pi_over_180*240.)), 
                                   (r*math.cos(pi_over_180*210.), -r*math.sin(pi_over_180*210.)), 
                                   (-r_over_sqrt3, 0.), 
                                   (r*math.cos(pi_over_180*150.), -r*math.sin(pi_over_180*150.)), 
                                   (r_over_sqrt3*math.cos(pi_over_180*120.), -r_over_sqrt3*math.sin(pi_over_180*120.)), 
                                   (0., -r))

    def update_sizes(self):
        self.axes_left = 6.*self.label_fontsize
        self.axes_top = 3.*self.label_fontsize
        self.axes_right = self.canvas_width-6.*self.label_fontsize
        self.axes_bottom = self.canvas_height-4.*self.label_fontsize
        self.axes_width = self.axes_right-self.axes_left
        self.axes_height = self.axes_bottom-self.axes_top

        self.xrange = self.xlim[1]-self.xlim[0]
        self.left_yrange = self.left_ylim[1]-self.left_ylim[0]
        self.right_yrange = self.right_ylim[1]-self.right_ylim[0]

        self.x_pix_per_unit = self.axes_width/self.xrange
        self.left_y_pix_per_unit = self.axes_height/self.left_yrange
        self.right_y_pix_per_unit = self.axes_height/self.right_yrange

        self.x_epsilon = self.xrange/self.axes_width
        self.left_y_epsilon = self.left_yrange/self.axes_height
        self.right_y_epsilon = self.right_yrange/self.axes_height

    def resize(self, event):
#        if (self.dw==0.) and (self.dh==0.):
#            self.dw = event.width-self.canvas_width
#            self.dh = event.height-self.canvas_height
#            print 'dw = {0!r}, dh = {1!r}'.format(self.dw, self.dh)
#        else:
#            self.canvas_width = max(event.width-self.dw, 17.*self.label_fontsize)
#            self.canvas_height = max(event.height-self.dh, 12.*self.label_fontsize)
#            self.refresh()
        self.canvas_width = max(event.width-self.dw, 17.*self.label_fontsize)
        self.canvas_height = max(event.height-self.dh, 12.*self.label_fontsize)
        self.refresh()

    def configure(self, **kwargs):
        self.canvas_width = float(kwargs.get('width', self.canvas_width))
        self.canvas_height = float(kwargs.get('height', self.canvas_height))
        self.marker_radius = float(kwargs.get('marker_radius', self.marker_radius))
        self.marker_lineweight = float(kwargs.get('marker_lineweight', self.marker_lineweight))
        self.curve_lineweight = float(kwargs.get('curve_lineweight', self.curve_lineweight))
        self.tick_length = float(kwargs.get('tick_length', self.tick_length))
        self.tick_lineweight = float(kwargs.get('tick_lineweight', self.tick_lineweight))
        self.canvas_background_color = kwargs.get('background', self.canvas_background_color)
        self.axes_background_color = kwargs.get('axes_background', self.axes_background_color)
        self.axes_color = kwargs.get('axes_color', self.axes_color)
        self.axes_lineweight = kwargs.get('axes_lineweight', self.axes_lineweight)
        self.label_font_baseline = float(kwargs.get('baseline', self.label_font_baseline))
        self.label_fontsize = int(kwargs.get('fontsize', self.label_fontsize))
        self.label_font = kwargs.get('font', self.label_font)

        self.init_markers(self.marker_radius)
        self.canvas.configure(background = self.canvas_background_color, highlightbackground = self.canvas_background_color)
        self.refresh()

    def clear(self, **kwargs):
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        if side=='both':
            self.curves = []
        else:
            self.curves = [curve for curve in self.curves if curve.side!=side]
        self.refresh()

    def draw_now(self):
        self.root.update()

    def refresh(self):
        self.find_axes_limits()
        self.update_sizes()
        self.find_x_ticks()
        self.find_left_y_ticks()
        self.find_right_y_ticks()
        self.canvas.delete('all')
        self.draw_plot()

    def draw_plot(self):
        self.draw_axes()
        self.draw_grid()
        self.draw_x_ticks()
        self.draw_y_ticks()
        self.draw_axis_labels()
        self.draw_curves()

    def draw_axes(self):
        self.canvas.create_rectangle([self.axes_left, self.axes_top, self.axes_right, self.axes_bottom], outline = '', fill = self.axes_background_color)
        self.canvas.create_line(self.axes_left, self.axes_top, self.axes_right, self.axes_top, fill = self.axes_color, width = self.axes_lineweight)
        self.canvas.create_line(self.axes_right, self.axes_top, self.axes_right, self.axes_bottom, fill = self.axes_color, width = self.axes_lineweight)
        self.canvas.create_line(self.axes_left, self.axes_bottom, self.axes_right, self.axes_bottom, fill = self.axes_color, width = self.axes_lineweight)
        self.canvas.create_line(self.axes_left, self.axes_top, self.axes_left, self.axes_bottom, fill = self.axes_color, width = self.axes_lineweight)
        if self.svg_output:
            self.svg_file.write(u'        <g id="axes">\n')
            self.svg_file.write(u'            <rect x="{x!s}" y="{y!s}" width="{width!s}" height="{height!s}" stroke="none" fill="{color}"/>\n'.format(x = self.axes_left, y = self.axes_top, width = self.axes_width, height = self.axes_height, color = self.axes_background_color))
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_left, y1 = self.axes_top, x2 = self.axes_right, y2 = self.axes_top, color = self.axes_color, width = self.axes_lineweight))
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_right, y1 = self.axes_top, x2 = self.axes_right, y2 = self.axes_bottom, color = self.axes_color, width = self.axes_lineweight))
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_left, y1 = self.axes_bottom, x2 = self.axes_right, y2 = self.axes_bottom, color = self.axes_color, width = self.axes_lineweight))
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_left, y1 = self.axes_top, x2 = self.axes_left, y2 = self.axes_bottom, color = self.axes_color, width = self.axes_lineweight))
            self.svg_file.write(u'        </g>\n')

    def to_canvas_x(self, x):
        return self.axes_left+self.x_pix_per_unit*(x-self.xlim[0])

    def to_canvas_y(self, y, side = 'left'):
        if side=='left':
            return self.axes_top+self.left_y_pix_per_unit*(self.left_ylim[1]-y)
        else:
            return self.axes_top+self.right_y_pix_per_unit*(self.right_ylim[1]-y)

    def from_canvas_x(self, x):
        return self.xlim[0]+(x-self.axes_left)/self.x_pix_per_unit

    def from_canvas_y(self, y, side = 'left'):
        if side=='left':
            return self.left_ylim[1]-(y-self.axes_top)/self.left_y_pix_per_unit
        else:
            return self.right_ylim[1]-(y-self.axes_top)/self.right_y_pix_per_unit

    def to_canvas(self, x, y, side = 'left'):
        if side=='left':
            return [self.axes_left+self.x_pix_per_unit*(x-self.xlim[0]), self.axes_top+self.left_y_pix_per_unit*(self.left_ylim[1]-y)]
        else:
            return [self.axes_left+self.x_pix_per_unit*(x-self.xlim[0]), self.axes_top+self.right_y_pix_per_unit*(self.right_ylim[1]-y)]

    def from_canvas(self, x, y, side = 'left'):
        if side=='left':
            return [self.xlim[0]+(x-self.axes_left)/self.x_pix_per_unit, self.left_ylim[1]-(y-self.axes_top)/self.left_y_pix_per_unit]
        else:
            return [self.xlim[0]+(x-self.axes_left)/self.x_pix_per_unit, self.right_ylim[1]-(y-self.axes_top)/self.right_y_pix_per_unit]

    def draw_marker(self, x, y, marker, color, name = ''):
        coords = []
        for [dx, dy] in self.marker_coords[marker]:
            coords.append(x+dx)
            coords.append(y+dy)
        if marker=='.':
            item = self.canvas.create_oval(coords, fill = self.colors[color], outline = self.colors[color], width = self.marker_lineweight)
            if name!='':
                self.canvas.itemconfig(item, tags = name)
            if self.svg_output:
                self.svg_file.write(u'            <circle cx="{cx!s}" cy="{cy!s}" r="{r!s}" stroke="{color}" stroke-width="{width!s}px" fill="{color}"/>\n'.format(cx = x, cy = y, r = 0.5*self.marker_radius, color = self.colors[color], width = self.marker_lineweight))
        elif marker=='o':
            item = self.canvas.create_oval(coords, outline = self.colors[color], width = self.marker_lineweight)
            if name!='':
                self.canvas.itemconfig(item, tags = name)
            if self.svg_output:
                self.svg_file.write(u'            <circle cx="{cx!s}" cy="{cy!s}" r="{r!s}" stroke="{color}" stroke-width="{width!s}px" fill="none"/>\n'.format(cx = x, cy = y, r = self.marker_radius, color = self.colors[color], width = self.marker_lineweight))
        else:
            item = self.canvas.create_line(coords, fill = self.colors[color], width = self.marker_lineweight)
            if name!='':
                self.canvas.itemconfig(item, tags = name)
            if self.svg_output:
                self.svg_file.write(u'            <polyline points="{x1!s}'.format(x1 = coords[0]))
                for i in range(1, len(coords)):
                    if (i%2)==1:
                        self.svg_file.write(u',{y!s}'.format(y = coords[i]))
                    else:
                        self.svg_file.write(u' {x!s}'.format(x = coords[i]))
                self.svg_file.write(u'" stroke="{marker_color}" stroke-width="{width!s}px" fill="none"/>\n'.format(marker_color = self.colors[color], width = self.marker_lineweight))

    def draw_curve(self, curve):
        if len(curve.points)>1:
            if curve.side=='left':
                ylim = self.left_ylim
            else:
                ylim = self.right_ylim
            coords = []
            for i in range(len(curve.points)-1):
                if (curve.points[i].x>self.xlim[0]) and (curve.points[i].x<self.xlim[1]) and (curve.points[i].y>ylim[0]) and (curve.points[i].y<ylim[1]):
                    coords.append(self.to_canvas_x(curve.points[i].x))
                    coords.append(self.to_canvas_y(curve.points[i].y, curve.side))
                    if (curve.points[i+1].x<self.xlim[0]) or (curve.points[i+1].x>self.xlim[1]) or (curve.points[i+1].y<ylim[0]) or (curve.points[i+1].y>ylim[1]):
                        NW = (curve.points[i+1].y-ylim[1])*(curve.points[i].x-self.xlim[0])-(curve.points[i+1].x-self.xlim[0])*(curve.points[i].y-ylim[1])
                        NE = (curve.points[i+1].y-curve.points[i].y)*(self.xlim[1]-curve.points[i].x)-(curve.points[i+1].x-curve.points[i].x)*(ylim[1]-curve.points[i].y)
                        SE = (curve.points[i+1].y-curve.points[i].y)*(self.xlim[1]-curve.points[i].x)-(curve.points[i+1].x-curve.points[i].x)*(ylim[0]-curve.points[i].y)
                        SW = (curve.points[i+1].y-ylim[0])*(curve.points[i].x-self.xlim[0])-(curve.points[i+1].x-self.xlim[0])*(curve.points[i].y-ylim[0])
                        if (NW>0) and (NE>0):
                            coords.append(self.to_canvas_x(curve.points[i].x+(curve.points[i+1].x-curve.points[i].x)*(ylim[1]-curve.points[i].y)/(curve.points[i+1].y-curve.points[i].y)))
                            coords.append(self.axes_top)
                        elif (SE<=0) and (SW<=0):
                            coords.append(self.to_canvas_x(curve.points[i].x+(curve.points[i+1].x-curve.points[i].x)*(ylim[0]-curve.points[i].y)/(curve.points[i+1].y-curve.points[i].y)))
                            coords.append(self.axes_bottom)                   
                        elif (NW<=0) and (SW>0):
                            coords.append(self.axes_left)
                            coords.append(self.to_canvas_y(curve.points[i].y+(curve.points[i+1].y-curve.points[i].y)*(self.xlim[0]-curve.points[i].x)/(curve.points[i+1].x-curve.points[i].x), curve.side))
                        elif (NE<=0) and (SE>0):
                            coords.append(self.axes_right)
                            coords.append(self.to_canvas_y(curve.points[i].y+(curve.points[i+1].y-curve.points[i].y)*(self.xlim[1]-curve.points[i].x)/(curve.points[i+1].x-curve.points[i].x), curve.side))
                        item = self.canvas.create_line(coords, fill = self.colors[curve.curve_color], dash = self.linestyles[curve.curve_style], width = self.curve_lineweight)
                        if curve.name!='':
                            self.canvas.itemconfig(item, tags = curve.name)
                        if self.svg_output:
                            self.svg_file.write(u'            <polyline points="{x1!s}'.format(x1 = coords[0]))
                            for j in range(1, len(coords)):
                                if (j%2)==1:
                                    self.svg_file.write(u',{y!s}'.format(y = coords[j]))
                                else:
                                    self.svg_file.write(u' {x!s}'.format(x = coords[j]))
                            self.svg_file.write(u'" stroke="{curve_color}" stroke-width="{width!s}px" fill="none" dash-array="{dash}"/>\n'.format(curve_color = self.colors[curve.curve_color], width = self.curve_lineweight, dash = ','.join([str(n) for n in self.linestyles[curve.curve_style]])))
                        coords = []
                elif (curve.points[i].x<self.xlim[0]) or (curve.points[i].x>self.xlim[1]) or (curve.points[i].y<ylim[0]) or (curve.points[i].y>ylim[1]):
                    if (curve.points[i+1].x>self.xlim[0]) and (curve.points[i+1].x<self.xlim[1]) and (curve.points[i+1].y>ylim[0]) and (curve.points[i+1].y<ylim[1]):
                        NW = (curve.points[i].y-ylim[1])*(curve.points[i+1].x-self.xlim[0])-(curve.points[i].x-self.xlim[0])*(curve.points[i+1].y-ylim[1])
                        NE = (curve.points[i].y-curve.points[i+1].y)*(self.xlim[1]-curve.points[i+1].x)-(curve.points[i].x-curve.points[i+1].x)*(ylim[1]-curve.points[i+1].y)
                        SE = (curve.points[i].y-curve.points[i+1].y)*(self.xlim[1]-curve.points[i+1].x)-(curve.points[i].x-curve.points[i+1].x)*(ylim[0]-curve.points[i+1].y)
                        SW = (curve.points[i].y-ylim[0])*(curve.points[i+1].x-self.xlim[0])-(curve.points[i].x-self.xlim[0])*(curve.points[i+1].y-ylim[0])
                        if (NW>0) and (NE>0):
                            coords.append(self.to_canvas_x(curve.points[i+1].x+(curve.points[i].x-curve.points[i+1].x)*(ylim[1]-curve.points[i+1].y)/(curve.points[i].y-curve.points[i+1].y)))
                            coords.append(self.axes_top)
                        elif (SE<=0) and (SW<=0):
                            coords.append(self.to_canvas_x(curve.points[i+1].x+(curve.points[i].x-curve.points[i+1].x)*(ylim[0]-curve.points[i+1].y)/(curve.points[i].y-curve.points[i+1].y)))
                            coords.append(self.axes_bottom)                        
                        elif (NW<=0) and (SW>0):
                            coords.append(self.axes_left)
                            coords.append(self.to_canvas_y(curve.points[i+1].y+(curve.points[i].y-curve.points[i+1].y)*(self.xlim[0]-curve.points[i+1].x)/(curve.points[i].x-curve.points[i+1].x), curve.side))
                        elif (NE<=0) and (SE>0):
                            coords.append(self.axes_right)
                            coords.append(self.to_canvas_y(curve.points[i+1].y+(curve.points[i].y-curve.points[i+1].y)*(self.xlim[1]-curve.points[i+1].x)/(curve.points[i].x-curve.points[i+1].x), curve.side))
                    elif (curve.points[i+1].x<self.xlim[0]) or (curve.points[i+1].x>self.xlim[1]) or (curve.points[i+1].y<ylim[0]) or (curve.points[i+1].y>ylim[1]):
                        if not (((curve.points[i].x<self.xlim[0]) and (curve.points[i+1].x<self.xlim[0])) or ((curve.points[i].x>self.xlim[1]) and (curve.points[i+1].x>self.xlim[1])) or ((curve.points[i].y<ylim[0]) and (curve.points[i+1].y<ylim[0])) or ((curve.points[i].y>ylim[1]) and (curve.points[i+1].y>ylim[1]))):
                            if (curve.points[i].x==curve.points[i+1].x):
                                coords = [self.to_canvas_x(curve.points[i].x), self.axes_bottom, 
                                          self.to_canvas_x(curve.points[i].x), self.axes_top]
                            elif (curve.points[i].y==curve.points[i+1].y):
                                coords = [self.axes_left, self.to_canvas_y(curve.points[i].y, curve.side), 
                                          self.axes_right, self.to_canvas_y(curve.points[i].y, curve.side)]
                            else:
                                if curve.points[i].x<curve.points[i+1].x:
                                    x1, y1 = curve.points[i].x, curve.points[i].y
                                    x2, y2 = curve.points[i+1].x, curve.points[i+1].y
                                else:
                                    x1, y1 = curve.points[i+1].x, curve.points[i+1].y
                                    x2, y2 = curve.points[i].x, curve.points[i].y
                                NW = (ylim[1]-y1)*(x2-x1)-(self.xlim[0]-x1)*(y2-y1)
                                NE = (ylim[1]-y1)*(x2-x1)-(self.xlim[1]-x1)*(y2-y1)
                                SE = (ylim[0]-y1)*(x2-x1)-(self.xlim[1]-x1)*(y2-y1)
                                SW = (ylim[0]-y1)*(x2-x1)-(self.xlim[0]-x1)*(y2-y1)
                                if (NW>0) and (NE<=0) and (SW<=0):
                                    coords = [self.axes_left, self.to_canvas_y(y1+(y2-y1)*(self.xlim[0]-x1)/(x2-x1), curve.side),
                                              self.to_canvas_x(x1+(x2-x1)*(ylim[1]-y1)/(y2-y1)), self.axes_top]
                                elif (NE>0) and (NW<=0) and (SE<=0):
                                    coords = [self.to_canvas_x(x1+(x2-x1)*(ylim[1]-y1)/(y2-y1)), self.axes_top,
                                              self.axes_right, self.to_canvas_y(y1+(y2-y1)*(self.xlim[1]-x1)/(x2-x1), curve.side)]
                                elif (SW<=0) and (NW>0) and (SE>0):
                                    coords = [self.axes_left, self.to_canvas_y(y1+(y2-y1)*(self.xlim[0]-x1)/(x2-x1), curve.side),
                                              self.to_canvas_x(x1+(x2-x1)*(ylim[0]-y1)/(y2-y1)), self.axes_bottom]
                                elif (SE<=0) and (SW>0) and (NE>0):
                                    coords = [self.to_canvas_x(x1+(x2-x1)*(ylim[0]-y1)/(y2-y1)), self.axes_bottom,
                                              self.axes_right, self.to_canvas_y(y1+(y2-y1)*(self.xlim[1]-x1)/(x2-x1), curve.side)]
                                elif (NW>0) and (NE>0) and (SW<=0) and (SE<=0):
                                    coords = [self.axes_left, self.to_canvas_y(y1+(y2-y1)*(self.xlim[0]-x1)/(x2-x1), curve.side),
                                              self.axes_right, self.to_canvas_y(y1+(y2-y1)*(self.xlim[1]-x1)/(x2-x1), curve.side)]
                                elif (NW*NE<0) and (SW*SE<0):
                                    coords = [self.to_canvas_x(x1+(x2-x1)*(ylim[0]-y1)/(y2-y1)), self.axes_bottom,
                                              self.to_canvas_x(x1+(x2-x1)*(ylim[1]-y1)/(y2-y1)), self.axes_top]
                            if coords!=[]:
                                item = self.canvas.create_line(coords, fill = self.colors[curve.curve_color], dash = self.linestyles[curve.curve_style], width = self.curve_lineweight)
                                if curve.name!='':
                                    self.canvas.itemconfig(item, tags = curve.name)
                                if self.svg_output:
                                    self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{curve_color}" stroke-width="{width!s}px" fill="none" dash-array="{dash}"/>\n'.format(x1 = coords[0], y1 = coords[1], x2 = coords[2], y2 = coords[3], curve_color = self.colors[curve.curve_color], width = self.curve_lineweight, dash = ','.join([str(n) for n in self.linestyles[curve.curve_style]])))
                                coords = []
                else:
                    coords.append(self.to_canvas_x(curve.points[i].x))
                    coords.append(self.to_canvas_y(curve.points[i].y, curve.side))
                    if (curve.points[i+1].x<self.xlim[0]) or (curve.points[i+1].x>self.xlim[1]) or (curve.points[i+1].y<ylim[0]) or (curve.points[i+1].y>ylim[1]):
                        if len(coords)!=2:
                            item = self.canvas.create_line(coords, fill = self.colors[curve.curve_color], dash = self.linestyles[curve.curve_style], width = self.curve_lineweight)
                            if curve.name!='':
                                self.canvas.itemconfig(item, tags = curve.name)
                            if self.svg_output:
                                self.svg_file.write(u'            <polyline points="{x1!s}'.format(x1 = coords[0]))
                                for j in range(1, len(coords)):
                                    if (j%2)==1:
                                        self.svg_file.write(u',{y!s}'.format(y = coords[j]))
                                    else:
                                        self.svg_file.write(u' {x!s}'.format(x = coords[j]))
                                self.svg_file.write(u'" stroke="{curve_color}" stroke-width="{width!s}px" fill="none" dash-array="{dash}"/>\n'.format(curve_color = self.colors[curve.curve_color], width = self.curve_lineweight, dash = ','.join([str(n) for n in self.linestyles[curve.curve_style]])))
                        coords = []
            if (curve.points[-1].x>=self.xlim[0]) and (curve.points[-1].x<=self.xlim[1]) and (curve.points[-1].y>=ylim[0]) and (curve.points[-1].y<=ylim[1]):
                coords.append(self.to_canvas_x(curve.points[-1].x))
                coords.append(self.to_canvas_y(curve.points[-1].y, curve.side))
                if len(coords)!=2:
                    item = self.canvas.create_line(coords, fill = self.colors[curve.curve_color], dash = self.linestyles[curve.curve_style], width = self.curve_lineweight)
                    if curve.name!='':
                        self.canvas.itemconfig(item, tags = curve.name)
                    if self.svg_output:
                        self.svg_file.write(u'            <polyline points="{x1!s}'.format(x1 = coords[0]))
                        for j in range(1, len(coords)):
                            if (j%2)==1:
                                self.svg_file.write(u',{y!s}'.format(y = coords[j]))
                            else:
                                self.svg_file.write(u' {x!s}'.format(x = coords[j]))
                        self.svg_file.write(u'" stroke="{curve_color}" stroke-width="{width!s}px" fill="none" dash-array="{dash}"/>\n'.format(curve_color = self.colors[curve.curve_color], width = self.curve_lineweight, dash = ','.join([str(n) for n in self.linestyles[curve.curve_style]])))

    def draw_curves(self):
        for curve in self.curves:
            if self.svg_output:
                self.svg_file.write(u'        <g id="{0}">\n'.format(curve.name))
            if curve.curve_style!='':
                self.draw_curve(curve)
            if curve.marker!='':
                ylim = self.left_ylim if curve.side=='left' else self.right_ylim
                y_epsilon = self.left_y_epsilon if curve.side=='left' else self.right_y_epsilon
                for point in curve.points:
                    if (point.x>self.xlim[0]-self.x_epsilon) and (point.x<self.xlim[1]+self.x_epsilon) and (point.y>ylim[0]-y_epsilon) and (point.y<ylim[1]+y_epsilon):
                        self.draw_marker(self.to_canvas_x(point.x), self.to_canvas_y(point.y, curve.side), curve.marker, curve.marker_color, curve.name)
            if self.svg_output:
                self.svg_file.write(u'        </g>\n')

    def draw_v_grid_line(self, x):
        self.canvas.create_line(x, self.axes_top, x, self.axes_bottom, fill = self.axes_color, dash = (1, 4), width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px" stroke-dasharray="1,4"/>\n'.format(x1 = x, y1 = self.axes_top, x2 = x, y2 = self.axes_bottom, color = self.axes_color, width = self.tick_lineweight))

    def draw_h_grid_line(self, y):
        self.canvas.create_line(self.axes_left, y, self.axes_right, y, fill = self.axes_color, dash = (1, 4), width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px" stroke-dasharray="1,4"/>\n'.format(x1 = self.axes_left, y1 = y, x2 = self.axes_right, y2 = y, color = self.axes_color, width = self.tick_lineweight))

    def draw_grid(self):
        if self.grid_state=='on':
            if self.svg_output:
                self.svg_file.write(u'        <g id="grid">\n')
            for [x, label] in self.x_ticks:
                self.draw_v_grid_line(self.to_canvas_x(x))
            for [x, label] in self.x_minor_ticks:
                self.draw_v_grid_line(self.to_canvas_x(x))

            for [y, label] in self.left_y_ticks:
                self.draw_h_grid_line(self.to_canvas_y(y, 'left'))
            for [y, label] in self.left_y_minor_ticks:
                self.draw_h_grid_line(self.to_canvas_y(y, 'left'))

            for [y, label] in self.right_y_ticks:
                self.draw_h_grid_line(self.to_canvas_y(y, 'right'))
            for [y, label] in self.right_y_minor_ticks:
                self.draw_h_grid_line(self.to_canvas_y(y, 'right'))
            if self.svg_output:
                self.svg_file.write(u'        </g>\n')

    def draw_top_tick(self, x):
        self.canvas.create_line(x, self.axes_top, x, self.axes_top+self.tick_length, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = x, y1 = self.axes_top, x2 = x, y2 = self.axes_top+self.tick_length, color = self.axes_color, width = self.tick_lineweight))
    
    def draw_bottom_tick(self, x):
        self.canvas.create_line(x, self.axes_bottom, x, self.axes_bottom-self.tick_length, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = x, y1 = self.axes_bottom, x2 = x, y2 = self.axes_bottom-self.tick_length, color = self.axes_color, width = self.tick_lineweight))
    
    def draw_left_tick(self, y):
        self.canvas.create_line(self.axes_left, y, self.axes_left+self.tick_length, y, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_left, y1 = y, x2 = self.axes_left+self.tick_length, y2 = y, color = self.axes_color, width = self.tick_lineweight))
    
    def draw_right_tick(self, y):
        self.canvas.create_line(self.axes_right, y, self.axes_right-self.tick_length, y, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_right, y1 = y, x2 = self.axes_right-self.tick_length, y2 = y, color = self.axes_color, width = self.tick_lineweight))

    def draw_top_minor_tick(self, x):
        self.canvas.create_line(x, self.axes_top, x, self.axes_top+0.5*self.tick_length, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = x, y1 = self.axes_top, x2 = x, y2 = self.axes_top+0.5*self.tick_length, color = self.axes_color, width = self.tick_lineweight))
    
    def draw_bottom_minor_tick(self, x):
        self.canvas.create_line(x, self.axes_bottom, x, self.axes_bottom-0.5*self.tick_length, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = x, y1 = self.axes_bottom, x2 = x, y2 = self.axes_bottom-0.5*self.tick_length, color = self.axes_color, width = self.tick_lineweight))
    
    def draw_left_minor_tick(self, y):
        self.canvas.create_line(self.axes_left, y, self.axes_left+0.5*self.tick_length, y, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_left, y1 = y, x2 = self.axes_left+0.5*self.tick_length, y2 = y, color = self.axes_color, width = self.tick_lineweight))
    
    def draw_right_minor_tick(self, y):
        self.canvas.create_line(self.axes_right, y, self.axes_right-0.5*self.tick_length, y, fill = self.axes_color, width = self.tick_lineweight)
        if self.svg_output:
            self.svg_file.write(u'            <line x1="{x1!s}" y1="{y1!s}" x2="{x2!s}" y2="{y2!s}" stroke="{color}" stroke-width="{width!s}px"/>\n'.format(x1 = self.axes_right, y1 = y, x2 = self.axes_right-0.5*self.tick_length, y2 = y, color = self.axes_color, width = self.tick_lineweight))

    def draw_bottom_tick_label(self, x, label):
        self.canvas.create_text(x, self.axes_bottom+0.5*self.label_fontsize, text = label, font = (self.label_font, self.label_fontsize), fill = self.axes_color, anchor = 'n', justify = 'center')
        if self.svg_output:
            self.svg_file.write(u'            <text x="{x!s}" y="{y!s}" fill="{color}" text-anchor="middle" font-family="{font}" font-size="{fontsize!s}">{text}</text>\n'.format(x = x, y = self.axes_bottom+(0.5+self.label_font_baseline)*self.label_fontsize, color = self.axes_color, font = self.label_font, fontsize = self.label_fontsize, text = label))

    def draw_left_tick_label(self, y, label):
        self.canvas.create_text(self.axes_left-0.5*self.label_fontsize, y, text = label, font = (self.label_font, self.label_fontsize), fill = self.axes_color, anchor = 'e', justify = 'right')
        if self.svg_output:
            self.svg_file.write(u'            <text x="{x!s}" y="{y!s}" fill="{color}" text-anchor="end" font-family="{font}" font-size="{fontsize!s}">{text}</text>\n'.format(x = self.axes_left-0.5*self.label_fontsize, y = y+0.5*self.label_font_baseline*self.label_fontsize, color = self.axes_color, font = self.label_font, fontsize = self.label_fontsize, text = label))

    def draw_right_tick_label(self, y, label):
        self.canvas.create_text(self.axes_right+0.5*self.label_fontsize, y, text = label, font = (self.label_font, self.label_fontsize), fill = self.axes_color, anchor = 'w', justify = 'left')
        if self.svg_output:
            self.svg_file.write(u'            <text x="{x!s}" y="{y!s}" fill="{color}" text-anchor="start" font-family="{font}" font-size="{fontsize!s}">{text}</text>\n'.format(x = self.axes_right+0.5*self.label_fontsize, y = y+0.5*self.label_font_baseline*self.label_fontsize, color = self.axes_color, font = self.label_font, fontsize = self.label_fontsize, text = label))

    def draw_x_ticks(self):
        if (self.x_ticks!=[]) or (self.x_minor_ticks!=[]):
            if self.svg_output:
                self.svg_file.write(u'        <g id="x_ticks">\n')
            for [x, label] in self.x_ticks:
                self.draw_top_tick(self.to_canvas_x(x))
                self.draw_bottom_tick(self.to_canvas_x(x))
            for [x, label] in self.x_minor_ticks:
                self.draw_top_minor_tick(self.to_canvas_x(x))
                self.draw_bottom_minor_tick(self.to_canvas_x(x))
            if self.svg_output:
                self.svg_file.write(u'        </g>\n')
                self.svg_file.write(u'        <g id="x_ticklabels">\n')
            for [x, label] in self.x_ticks:
                if label!='':
                    self.draw_bottom_tick_label(self.to_canvas_x(x), label)
            for [x, label] in self.x_minor_ticks:
                if label!='':
                    self.draw_bottom_tick_label(self.to_canvas_x(x), label)
            if self.svg_output:
                self.svg_file.write(u'        </g>\n')        

    def draw_y_ticks(self):
        if (self.left_y_ticks!=[]) or (self.left_y_minor_ticks!=[]) or (self.right_y_ticks!=[]) or (self.right_y_minor_ticks!=[]):
            if self.svg_output:
                self.svg_file.write(u'        <g id="y_ticks">\n')
            for [y, label] in self.left_y_ticks:
                self.draw_left_tick(self.to_canvas_y(y, 'left'))
                if (self.right_y_ticks==[]) and (self.right_y_minor_ticks==[]):
                    self.draw_right_tick(self.to_canvas_y(y, 'left'))
            for [y, label] in self.left_y_minor_ticks:
                self.draw_left_minor_tick(self.to_canvas_y(y, 'left'))
                if (self.right_y_ticks==[]) and (self.right_y_minor_ticks==[]):
                    self.draw_right_minor_tick(self.to_canvas_y(y, 'left'))
            for [y, label] in self.right_y_ticks:
                self.draw_right_tick(self.to_canvas_y(y, 'right'))
                if (self.left_y_ticks==[]) and (self.left_y_minor_ticks==[]):
                    self.draw_left_tick(self.to_canvas_y(y, 'right'))
            for [y, label] in self.right_y_minor_ticks:
                self.draw_right_minor_tick(self.to_canvas_y(y, 'right'))
                if (self.left_y_ticks==[]) and (self.left_y_minor_ticks==[]):
                    self.draw_left_minor_tick(self.to_canvas_y(y, 'right'))
            if self.svg_output:
                self.svg_file.write(u'        </g>\n')
                self.svg_file.write(u'        <g id="y_ticklabels">\n')
            for [y, label] in self.left_y_ticks:
                if label!='':
                    self.draw_left_tick_label(self.to_canvas_y(y, 'left'), label)
            for [y, label] in self.left_y_minor_ticks:
                if label!='':
                    self.draw_left_tick_label(self.to_canvas_y(y, 'left'), label)
            for [y, label] in self.right_y_ticks:
                if label!='':
                    self.draw_right_tick_label(self.to_canvas_y(y, 'right'), label)
            for [y, label] in self.right_y_minor_ticks:
                if label!='':
                    self.draw_right_tick_label(self.to_canvas_y(y, 'right'), label)
            if self.svg_output:
                self.svg_file.write(u'        </g>\n')        

    def draw_axis_labels(self):
        if self.xlabel_value!='':
            self.canvas.create_text(0.5*(self.axes_left+self.axes_right), self.axes_bottom+2.5*self.label_fontsize, text = self.xlabel_value, font = (self.label_font, self.label_fontsize), fill = self.axes_color, anchor = 'n', justify = 'center')
            if self.svg_output:
                self.svg_file.write(u'        <text x="{x!s}" y="{y!s}" fill="{color}" text-anchor="middle" font-family="{font}" font-size="{fontsize!s}">{text}</text>\n'.format(x = 0.5*(self.axes_left+self.axes_right), y = self.axes_bottom+(2.5+self.label_font_baseline)*self.label_fontsize, color = self.axes_color, font = self.label_font, fontsize = self.label_fontsize, text = self.xlabel_value))
        if self.left_ylabel_value!='':
            self.canvas.create_text(self.axes_left, self.axes_top-0.5*self.label_fontsize, text = self.left_ylabel_value, font = (self.label_font, self.label_fontsize), fill = self.axes_color, anchor = 'sw', justify = 'left')
            if self.svg_output:
                self.svg_file.write(u'        <text x="{x!s}" y="{y!s}" fill="{color}" text-anchor="start" font-family="{font}" font-size="{fontsize!s}">{text}</text>\n'.format(x = self.axes_left, y = self.axes_top-(1.5-self.label_font_baseline)*self.label_fontsize, color = self.axes_color, font = self.label_font, fontsize = self.label_fontsize, text = self.left_ylabel_value))
        if self.right_ylabel_value!='':
            self.canvas.create_text(self.axes_right, self.axes_top-0.5*self.label_fontsize, text = self.right_ylabel_value, font = (self.label_font, self.label_fontsize), fill = self.axes_color, anchor = 'se', justify = 'right')
            if self.svg_output:
                self.svg_file.write(u'        <text x="{x!s}" y="{y!s}" fill="{color}" text-anchor="end" font-family="{font}" font-size="{fontsize!s}">{text}</text>\n'.format(x = self.axes_right, y = self.axes_top-(1.5-self.label_font_baseline)*self.label_fontsize, color = self.axes_color, font = self.label_font, fontsize = self.label_fontsize, text = self.right_ylabel_value))

    def find_x_ticks(self):
        self.x_ticks = []
        self.x_minor_ticks = []
        curves = [curve for curve in self.curves if curve.points!=[]]
        if curves!=[]:
            if self.xaxis_mode=='linear':
                self.x_ticks = self.find_linear_ticks(self.xlimits_mode, self.axes_width, self.xrange, self.xlim, self.x_epsilon, self.xmin, self.xmax)
                self.x_minor_ticks = []
            elif self.xaxis_mode=='log':
                self.x_ticks = self.find_log_ticks(self.xlimits_mode, self.axes_width, self.xrange, self.xlim, self.x_epsilon, self.xaxis_sign, self.xmin, self.xmax)
                self.x_minor_ticks = self.find_log_minor_ticks(self.axes_width, self.xrange, self.xlim, self.x_epsilon, self.xaxis_sign, self.xmin, self.xmax)

    def find_left_y_ticks(self):
        self.left_y_ticks =[]
        self.left_y_minor_ticks = []
        left_curves = [curve for curve in self.curves if (curve.side=='left') and (curve.points!=[])]
        if left_curves!=[]:
            if self.left_yaxis_mode=='linear':
                self.left_y_ticks = self.find_linear_ticks(self.left_ylimits_mode, self.axes_height, self.left_yrange, self.left_ylim, self.left_y_epsilon, self.left_ymin, self.left_ymax)
                self.left_y_minor_ticks = []
            elif self.left_yaxis_mode=='log':
                self.left_y_ticks = self.find_log_ticks(self.left_ylimits_mode, self.axes_height, self.left_yrange, self.left_ylim, self.left_y_epsilon, self.left_yaxis_sign, self.left_ymin, self.left_ymax)
                self.left_y_minor_ticks = self.find_log_minor_ticks(self.axes_height, self.left_yrange, self.left_ylim, self.left_y_epsilon, self.left_yaxis_sign, self.left_ymin, self.left_ymax)

    def find_right_y_ticks(self):
        self.right_y_ticks = []
        self.right_y_minor_ticks = []
        right_curves = [curve for curve in self.curves if (curve.side=='right') and (curve.points!=[])]
        if right_curves!=[]:
            if self.right_yaxis_mode=='linear':
                self.right_y_ticks = self.find_linear_ticks(self.right_ylimits_mode, self.axes_height, self.right_yrange, self.right_ylim, self.right_y_epsilon, self.right_ymin, self.right_ymax)
                self.right_y_minor_ticks = []
            elif self.right_yaxis_mode=='log':
                self.right_y_ticks = self.find_log_ticks(self.right_ylimits_mode, self.axes_height, self.right_yrange, self.right_ylim, self.right_y_epsilon, self.right_yaxis_sign, self.right_ymin, self.right_ymax)
                self.right_y_minor_ticks = self.find_log_minor_ticks(self.axes_height, self.right_yrange, self.right_ylim, self.right_y_epsilon, self.right_yaxis_sign, self.right_ymin, self.right_ymax)

    def find_linear_ticks(self, axis_limits_mode, axis_dimension, axis_range, axis_lim, epsilon, axis_min, axis_max):
        if axis_limits_mode=='auto':
            axis_range = axis_max-axis_min
        tick_interval = axis_range/min(10., axis_dimension/(2.5*self.label_fontsize))
        foo = math.log10(tick_interval)
        bar = math.floor(foo)
        foobar = foo-bar
        if foobar<0.001:
            tick_interval = math.pow(10., bar)
        elif foobar<math.log10(2.001):
            tick_interval = 2.*math.pow(10., bar)
        elif foobar<math.log10(5.001):
            tick_interval = 5.*math.pow(10., bar)
        else:
            tick_interval = 10.*math.pow(10., bar)
        if axis_limits_mode=='auto':
            axis_lim[0] = tick_interval*math.floor(axis_min/tick_interval)
            axis_lim[1] = tick_interval*math.ceil(axis_max/tick_interval)
            self.update_sizes()
        tick = tick_interval*round(axis_lim[0]/tick_interval)
        ticks = []
        for i in range(int(math.ceil((axis_lim[1]-axis_lim[0])/tick_interval))+1):
            if (tick>axis_lim[0]-epsilon) and (tick<axis_lim[1]+epsilon):
                ticks.append(tick_interval*round(tick/tick_interval))
            tick = tick+tick_interval

        if len(ticks)!=0:
            if (min(ticks)==0.) and (max(ticks)==0.):
                foo = 0
            else:
                foo = int(math.floor(math.log10(max(abs(min(ticks)), abs(max(ticks)), axis_range))/3.))
        axis_ticks = []
        for tick in ticks:
            if (foo>=-8) and (foo<=8):
                if tick==-0.:
                    tick = 0.
                tick_label = str(self.multipliers[foo]*tick)
                if tick_label[-2:]=='.0':
                    tick_label = tick_label.replace('.0', '')
                axis_ticks.append([tick, tick_label+self.prefixes[foo]])
            else:
                axis_ticks.append([tick, str(tick)])
        return axis_ticks

    def find_log_ticks(self, axis_limits_mode, axis_dimension, axis_range, axis_lim, epsilon, sign, axis_min, axis_max):
        if axis_limits_mode=='auto':
            axis_range = axis_max-axis_min
        tick_interval = math.ceil(axis_range/min(10., axis_dimension/(2.5*self.label_fontsize)))
        if axis_limits_mode=='auto':
            axis_lim[0] = tick_interval*math.floor(axis_min/tick_interval)
            axis_lim[1] = tick_interval*math.ceil(axis_max/tick_interval)
            self.update_sizes()
        tick = tick_interval*round(axis_lim[0]/tick_interval)
        ticks = []
        for i in range(int(math.ceil((axis_lim[1]-axis_lim[0])/tick_interval))+1):
            if (tick>axis_lim[0]-epsilon) and (tick<axis_lim[1]+epsilon):
                ticks.append(tick_interval*round(tick/tick_interval))
            tick = tick+tick_interval
        axis_ticks = []
        for tick in ticks:
            foo = int(math.floor(sign*tick/3.))
            if (foo>=-8) and (foo<=8):
                tick_label = str(sign*round(self.multipliers[foo]*math.pow(10., sign*tick)))
                if tick_label[-2:]=='.0':
                    tick_label = tick_label.replace('.0', '')
                axis_ticks.append([tick, tick_label+self.prefixes[foo]])
            else:
                axis_ticks.append([tick, str(sign*math.pow(10., sign*tick))])
        return axis_ticks

    def find_log_minor_ticks(self, axis_dimension, axis_range, axis_lim, epsilon, sign, axis_min, axis_max):
        minor_ticks = []
        tick_interval = axis_range/min(10., axis_dimension/(2.5*self.label_fontsize))
        minor_tick_interval = 10.*min(1.-math.pow(10., -tick_interval), math.pow(10., tick_interval)-1.)
        tick_interval = math.ceil(tick_interval)
        foo = math.log10(minor_tick_interval)
        bar = math.floor(foo)
        foobar = foo-bar
        if foobar<0.001:
            minor_tick_interval = math.pow(10., bar)
        elif foobar<math.log10(2.001):
            minor_tick_interval = 2.*math.pow(10., bar)
        elif foobar<math.log10(5.001):
            minor_tick_interval = 5.*math.pow(10., bar)
        else:
            minor_tick_interval = 10.*math.pow(10., bar)
        if (tick_interval==1.) and (axis_range<=1.):
            label_threshold = 2.5*self.label_fontsize*epsilon
            if minor_tick_interval<1.:
                ticks_to_label = []
                tick = 1.+minor_tick_interval
                while tick<10.-0.001*minor_tick_interval:
                    ticks_to_label.append(tick)
                    tick += minor_tick_interval
            elif math.log10(10./9.)>label_threshold:
                ticks_to_label = range(2, 10)
            elif math.log10(1.25)>label_threshold:
                ticks_to_label = range(2, 10, 2)
            elif math.log10(2)>label_threshold:
                ticks_to_label = [2, 5]
            elif math.log10(3)>label_threshold:
                ticks_to_label = [3]
            else:
                ticks_to_label = []
            for i in range(int(math.ceil(axis_range))+2):
                exponent = math.floor(axis_lim[0])+i
                for j in ticks_to_label:
                    minor_tick = exponent+sign*math.log10(float(j))
                    if (minor_tick>axis_lim[0]-epsilon) and (minor_tick<axis_lim[1]+epsilon):
                        foo = int(math.floor(sign*minor_tick/3.))
                        if (foo>=-8) and (foo<=8):
                            tick_label = str(sign*self.multipliers[foo]*math.pow(10., sign*minor_tick))
                            if tick_label[-2:]=='.0':
                                tick_label = tick_label.replace('.0', '')
                            minor_ticks.append([minor_tick, tick_label+self.prefixes[foo]])
                        else:
                            minor_ticks.append([minor_tick, str(sign*math.pow(10., sign*minor_tick))])
        elif (tick_interval==1.) and (math.log10(10./9.)>2.*epsilon):
            for i in range(int(math.ceil(axis_range))+2):
                exponent = math.floor(axis_lim[0])+i
                for j in range(2, 10):
                    minor_tick = exponent+sign*math.log10(float(j))
                    if (minor_tick>axis_lim[0]-epsilon) and (minor_tick<axis_lim[1]+epsilon):
                        minor_ticks.append([minor_tick, ''])
        elif (tick_interval>1.) and (epsilon<0.25):
            for i in range(int(math.ceil(axis_range))+2):
                minor_tick = math.floor(axis_lim[0])+i
                if (minor_tick>axis_lim[0]-epsilon) and (minor_tick<axis_lim[1]+epsilon) and (minor_tick!=tick_interval*round(minor_tick/tick_interval)):
                    minor_ticks.append([minor_tick, ''])
        return minor_ticks

    def find_axes_limits(self):
        if self.curves!=[]:
            if (self.xlimits_mode!='manual'):
                x_values = []
                for curve in self.curves:
                    ylimits_mode = self.left_ylimits_mode if curve.side=='left' else self.right_ylimits_mode
                    ylim = self.left_ylim if curve.side=='left' else self.right_ylim
                    y_epsilon = self.left_y_epsilon if curve.side=='left' else self.right_y_epsilon
                    if ylimits_mode=='manual':
                        x_values.extend([point.x for point in curve.points if (point.y>ylim[0]-y_epsilon) and (point.y<ylim[1]+y_epsilon)])
                    else:
                        x_values.extend([point.x for point in curve.points])
                if x_values!=[]:
                    self.xlim[0] = min(x_values)
                    self.xlim[1] = max(x_values)
                    if self.xlim[0]==self.xlim[1]:
                        if self.xlim[0]>0.:
                            self.xlim[0] = 0.95*self.xlim[0]
                            self.xlim[1] = 1.05*self.xlim[1]
                        elif self.xlim[0]<0.:
                            self.xlim[0] = 1.05*self.xlim[0]
                            self.xlim[1] = 0.95*self.xlim[1]
                        else:
                            self.xlim[0] = -0.05
                            self.xlim[1] = 0.05
                    self.xmin = self.xlim[0]
                    self.xmax = self.xlim[1]
        left_curves = [curve for curve in self.curves if curve.side=='left']
        if (left_curves!=[]):
            if (self.left_ylimits_mode!='manual'):
                y_values = []
                if self.xlimits_mode=='manual':
                    for curve in left_curves:
                        y_values.extend([point.y for point in curve.points if (point.x>self.xlim[0]-self.x_epsilon) and (point.x<self.xlim[1]+self.x_epsilon)])
                else:
                    for curve in left_curves:
                        y_values.extend([point.y for point in curve.points])
                if y_values!=[]:
                    self.left_ylim[0] = min(y_values)
                    self.left_ylim[1] = max(y_values)
                    if self.left_ylim[0]==self.left_ylim[1]:
                        if self.left_ylim[0]>0.:
                            self.left_ylim[0] = 0.95*self.left_ylim[0]
                            self.left_ylim[1] = 1.05*self.left_ylim[1]
                        elif self.left_ylim[0]<0.:
                            self.left_ylim[0] = 1.05*self.left_ylim[0]
                            self.left_ylim[1] = 0.95*self.left_ylim[1]
                        else:
                            self.left_ylim[0] = -0.05
                            self.left_ylim[1] = 0.05
                    self.left_ymin = self.left_ylim[0]
                    self.left_ymax = self.left_ylim[1]
        right_curves = [curve for curve in self.curves if curve.side=='right']
        if (right_curves!=[]):
            if (self.right_ylimits_mode!='manual'):
                y_values = []
                if self.xlimits_mode=='manual':
                    for curve in right_curves:
                        y_values.extend([point.y for point in curve.points if (point.x>self.xlim[0]-self.x_epsilon) and (point.x<self.xlim[1]+self.x_epsilon)])
                else:
                    for curve in right_curves:
                        y_values.extend([point.y for point in curve.points])
                if y_values!=[]:
                    self.right_ylim[0] = min(y_values)
                    self.right_ylim[1] = max(y_values)
                    if self.right_ylim[0]==self.right_ylim[1]:
                        if self.right_ylim[0]>0.:
                            self.right_ylim[0] = 0.95*self.right_ylim[0]
                            self.right_ylim[1] = 1.05*self.right_ylim[1]
                        elif self.right_ylim[0]<0.:
                            self.right_ylim[0] = 1.05*self.right_ylim[0]
                            self.right_ylim[1] = 0.95*self.right_ylim[1]
                        else:
                            self.right_ylim[0] = -0.05
                            self.right_ylim[1] = 0.05
                    self.right_ymin = self.right_ylim[0]
                    self.right_ymax = self.right_ylim[1]

    def parse_style(self, style):
        length = len(style)
        colors = self.colors.keys()
        markers = self.marker_coords.keys()
        linestyles = self.linestyles.keys()
        marker_color = ''
        marker = ''
        curve_color = ''
        curve_style = ''
        if (length>=1) and (style[0] in colors):
            if (length>=2) and (style[1] in markers):
                marker_color = style[0]
                marker = style[1]
                if (length>=3) and (style[2] in colors):
                    curve_color = style[2]
                    if (length>=5) and (style[3:5] in linestyles):
                        curve_style = style[3:5]
                    elif (length>=4) and (style[3] in linestyles):
                        curve_style = style[3]
                elif (length>=4) and (style[2:4] in linestyles):
                    curve_style = style[2:4]
                elif (length>=3) and (style[2] in linestyles):
                    curve_style = style[2]
            elif (length>=3) and (style[1:3] in linestyles):
                curve_color = style[0]
                curve_style = style[1:3]
            elif (length>=2) and (style[1] in linestyles):
                curve_color = style[0]
                curve_style = style[1]
        elif (length>=1) and (style[0] in markers):
            marker = style[0]
            if (length>=2) and (style[1] in colors):
                curve_color = style[1]
                if (length>=4) and (style[2:4] in linestyles):
                    curve_style = style[2:4]
                elif (length>=3) and (style[2] in linestyles):
                    curve_style = style[2]
            elif (length>=3) and (style[1:3] in linestyles):
                curve_style = style[1:3]
            elif (length>=2) and (style[1] in linestyles):
                curve_style = style[1]
        elif (length>=2) and (style[0:2] in linestyles):
            curve_style = style[0:2]
        elif (length>=1) and (style[0] in linestyles):
            curve_style = style[0]
        if (marker=='') and (curve_style==''):
            marker = self.default_marker
            curve_style = self.default_curve_style
        if ((marker!='') and (marker_color=='')) or ((curve_style!='') and (curve_color=='')):
            if (marker_color==''):
                marker_color = self.default_color_order[self.default_color_index]
            if (curve_color==''):
                curve_color = self.default_color_order[self.default_color_index]
            self.default_color_index = self.default_color_index+1
            if self.default_color_index>=len(self.default_color_order):
                self.default_color_index = 0
        if (marker_color!='') and (curve_color==''):
            curve_color = marker_color
        if (marker_color=='') and (curve_color!=''):
            marker_color = curve_color
        return [marker_color, marker, curve_color, curve_style]

    def new_data(self, x, y, style = '', side = 'left', hold = 'off'):
        if not ((isinstance(x, vector.vector) or (type(x) is list)) and (isinstance(y, vector.vector) or (type(y) is list))):
            raise TypeError('x and y supplied were not vectors or lists of vectors')
        elif isinstance(x, vector.vector) and isinstance(y, vector.vector):
            if len(x)==len(y):
                new_curves = [self.curve(side = side, data = [self.point(x[i], y[i]) for i in range(len(x))])]
                if type(style) is str:
                    [new_curves[0].marker_color, new_curves[0].marker, new_curves[0].curve_color, new_curves[0].curve_style] = self.parse_style(style)
                elif type(style) is list:
                    [new_curves[0].marker_color, new_curves[0].marker, new_curves[0].curve_color, new_curves[0].curve_style] = self.parse_style(style[0])
                else:
                    raise TypeError('style supplied was not a style string or a list of style strings')
                new_curves[0].name = 'curve{0:05d}'.format(self.curve_id)
                self.curve_id += 1
            else:
                raise IndexError('x and y vectors supplied did not have the same number of elements')
        elif vector.all([isinstance(x[i], vector.vector) for i in range(len(x))]) and vector.all([isinstance(y[i], vector.vector) for i in range(len(y))]):
            if len(x)==len(y):
                if vector.all([len(x[i])==len(y[i]) for i in range(len(x))]):
                    new_curves = [self.curve(side = side, data = [self.point(x[i][j], y[i][j]) for j in range(len(x[i]))]) for i in range(len(x))]
                    if type(style) is str:
                        for curve in new_curves:
                            [curve.marker_color, curve.marker, curve.curve_color, curve.curve_style] = self.parse_style(style)
                    elif type(style) is list:
                        if len(style)==len(x):
                            for i in range(len(x)):
                                [new_curves[i].marker_color, new_curves[i].marker, new_curves[i].curve_color, new_curves[i].curve_style] = self.parse_style(style[i])
                        else:
                            raise IndexError('number of style strings supplied was not equal to the number of curves')
                    else:
                        raise TypeError('style supplied was not a style string or a list of style strings')
                    for curve in new_curves:
                        curve.name = 'curve{0:05d}'.format(self.curve_id)
                        self.curve_id += 1
                else:
                    raise IndexError('the number of elements in at least one pair of x and y vectors supplied were mismatched')
            else:
                raise IndexError('mismatch in the number of x and y vectors supplied')
        elif isinstance(x, vector.vector) and vector.all([isinstance(y[i], vector.vector) for i in range(len(y))]):
            if vector.all([len(x)==len(y[i]) for i in range(len(y))]):
                new_curves = [self.curve(side = side, data = [self.point(x[j], y[i][j]) for j in range(len(x))]) for i in range(len(y))]
                if type(style) is str:
                    for curve in new_curves:
                        [curve.marker_color, curve.marker, curve.curve_color, curve.curve_style] = self.parse_style(style)
                elif type(style) is list:
                    if len(style)==len(y):
                        for i in range(len(y)):
                            [new_curves[i].marker_color, new_curves[i].marker, new_curves[i].curve_color, new_curves[i].curve_style] = self.parse_style(style[i])
                    else:
                        raise IndexError('number of style strings supplied was not equal to the number of curves')
                else:
                    raise TypeError('style supplied was not a style string or a list of style strings')
                for curve in new_curves:
                    curve.name = 'curve{0:05d}'.format(self.curve_id)
                    self.curve_id += 1
            else:
                raise IndexError('number of elements in at least one y vector supplied did not match the number of elements in x')
        else:
            raise TypeError('x and y supplied were not vectors or lists of vectors')
        if hold=='off':
            self.curves = [curve for curve in self.curves if curve.side!=side]
        self.curves.extend(new_curves)

    def plot(self, x, y, style = '', **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        hold = kwargs.get('hold', 'off')
        if hold not in ('on', 'off'):
            raise ValueError("if specified, hold must be 'on' or 'off'")
        if hold=='off':
            self.default_color_index = 0
        self.new_data(x, y, style, side, hold)
        self.xaxis_mode = 'linear'
        self.xlimits_mode = 'auto'
        if side=='left':
            self.left_yaxis_mode = 'linear'
            self.left_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='left':
                    curve.points = [self.point(p.x, p.y) for p in curve.data]
                else:
                    if self.right_yaxis_mode=='linear':
                        curve.points = [self.point(p.x, p.y) for p in curve.data]
                    elif self.right_yaxis_mode=='log':
                        curve.points = [self.point(p.x, self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if p.y*self.right_yaxis_sign>0.]
        else:
            self.right_yaxis_mode = 'linear'
            self.right_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='right':
                    curve.points = [self.point(p.x, p.y) for p in curve.data]
                else:
                    if self.left_yaxis_mode=='linear':
                        curve.points = [self.point(p.x, p.y) for p in curve.data]
                    elif self.left_yaxis_mode=='log':
                        curve.points = [self.point(p.x, self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if p.y*self.left_yaxis_sign>0.]
        self.refresh()

    def semilogx(self, x, y, style = '', **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        hold = kwargs.get('hold', 'off')
        if hold not in ('on', 'off'):
            raise ValueError("if specified, hold must be 'on' or 'off'")
        if hold=='off':
            self.default_color_index = 0
        self.new_data(x, y, style, side, hold)
        self.xaxis_mode = 'log'
        x_values = []
        for curve in self.curves:
            x_values.extend([point.x for point in curve.data])
        if [x>0. for x in x_values].count(True)>=len(x_values)/2:
            self.xaxis_sign = 1.
        else:
            self.xaxis_sign = -1.
        self.xlimits_mode = 'auto'
        if side=='left':
            self.left_yaxis_mode = 'linear'
            self.left_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='left':
                    curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                else:
                    if self.right_yaxis_mode=='linear':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                    elif self.right_yaxis_mode=='log':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
        else:
            self.right_yaxis_mode = 'linear'
            self.right_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='right':
                    curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                else:
                    if self.left_yaxis_mode=='linear':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                    elif self.left_yaxis_mode=='log':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
        self.refresh()

    def semilogy(self, x, y, style = '', **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        hold = kwargs.get('hold', 'off')
        if hold not in ('on', 'off'):
            raise ValueError("if specified, hold must be 'on' or 'off'")
        if hold=='off':
            self.default_color_index = 0
        self.new_data(x, y, style, side, hold)
        self.xaxis_mode = 'linear'
        self.xlimits_mode = 'auto'
        if side=='left':
            self.left_yaxis_mode = 'log'
            y_values = []
            for curve in self.curves:
                if curve.side=='left':
                    y_values.extend([point.y for point in curve.data])
            if [y>0. for y in y_values].count(True)>=len(y_values)/2:
                self.left_yaxis_sign = 1.
            else:
                self.left_yaxis_sign = -1.
            self.left_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='left':
                    curve.points = [self.point(p.x, self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if p.y*self.left_yaxis_sign>0.]
                else:
                    if self.right_yaxis_mode=='linear':
                        curve.points = [self.point(p.x, p.y) for p in curve.data]
                    elif self.right_yaxis_mode=='log':
                        curve.points = [self.point(p.x, self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if p.y*self.right_yaxis_sign>0.]
        else:
            self.right_yaxis_mode = 'log'
            y_values = []
            for curve in self.curves:
                if curve.side=='right':
                    y_values.extend([point.y for point in curve.data])
            if [y>0. for y in y_values].count(True)>=len(y_values)/2:
                self.right_yaxis_sign = 1.
            else:
                self.right_yaxis_sign = -1.
            self.right_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='right':
                    curve.points = [self.point(p.x, self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if p.y*self.right_yaxis_sign>0.]
                else:
                    if self.left_yaxis_mode=='linear':
                        curve.points = [self.point(p.x, p.y) for p in curve.data]
                    elif self.left_yaxis_mode=='log':
                        curve.points = [self.point(p.x, self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if p.y*self.left_yaxis_sign>0.]
        self.refresh()

    def loglog(self, x, y, style = '', **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        hold = kwargs.get('hold', 'off')
        if hold not in ('on', 'off'):
            raise ValueError("if specified, hold must be 'on' or 'off'")
        if hold=='off':
            self.default_color_index = 0
        self.new_data(x, y, style, side, hold)
        self.xaxis_mode = 'log'
        x_values = []
        for curve in self.curves:
            x_values.extend([point.x for point in curve.data])
        if [x>0. for x in x_values].count(True)>=len(x_values)/2:
            self.xaxis_sign = 1.
        else:
            self.xaxis_sign = -1.
        self.xlimits_mode = 'auto'
        if side=='left':
            self.left_yaxis_mode = 'log'
            y_values = []
            for curve in self.curves:
                if curve.side=='left':
                    y_values.extend([point.y for point in curve.data])
            if [y>0. for y in y_values].count(True)>=len(y_values)/2:
                self.left_yaxis_sign = 1.
            else:
                self.left_yaxis_sign = -1.
            self.left_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='left':
                    curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
                else:
                    if self.right_yaxis_mode=='linear':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                    elif self.right_yaxis_mode=='log':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
        else:
            self.right_yaxis_mode = 'log'
            y_values = []
            for curve in self.curves:
                if curve.side=='right':
                    y_values.extend([point.y for point in curve.data])
            if [y>0. for y in y_values].count(True)>=len(y_values)/2:
                self.right_yaxis_sign = 1.
            else:
                self.right_yaxis_sign = -1.
            self.right_ylimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='right':
                    curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
                else:
                    if self.left_yaxis_mode=='linear':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                    elif self.left_yaxis_mode=='log':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
        self.refresh()

    def grid(self, *args):
        if len(args)==0:
            return self.grid_state
        elif args[0] in ('on', 'off'):
            self.grid_state = args[0]
            self.canvas.delete('all')
            self.draw_plot()
        else:
            raise ValueError("invalid grid state specified; it must either be 'on' or 'off'")

    def xlabel(self, *args):
        if len(args)==0:
            return self.xlabel_value
        else:
            self.xlabel_value = args[0]
            self.canvas.delete('all')
            self.draw_plot()

    def ylabel(self, *args, **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        if len(args)==0:
            if side=='left':
                return self.left_ylabel_value
            else:
                return self.right_ylabel_value
        else:
            if side=='left':
                self.left_ylabel_value = str(args[0])
            else:
                self.right_ylabel_value = str(args[0])
        self.canvas.delete('all')
        self.draw_plot()

    def xaxis(self, *args):
        if len(args)==0:
            return self.xaxis_mode
        elif args[0]=='linear':
            self.xaxis_mode = 'linear'
            self.xlimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='left':
                    if self.left_yaxis_mode=='linear':
                        curve.points = [self.point(p.x, p.y) for p in curve.data]
                    elif self.left_yaxis_mode=='log':
                        curve.points = [self.point(p.x, self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if p.y*self.left_yaxis_sign>0.]
                else:
                    if self.right_yaxis_mode=='linear':
                        curve.points = [self.point(p.x, p.y) for p in curve.data]
                    elif self.right_yaxis_mode=='log':
                        curve.points = [self.point(p.x, self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if p.y*self.right_yaxis_sign>0.]
            self.refresh()
        elif args[0]=='log':
            self.xaxis_mode = 'log'
            x_values = []
            for curve in self.curves:
                x_values.extend([point.x for point in curve.data])
            if [x>0. for x in x_values].count(True)>=len(x_values)/2:
                self.xaxis_sign = 1.
            else:
                self.xaxis_sign = -1.
            self.xlimits_mode = 'auto'
            for curve in self.curves:
                if curve.side=='left':
                    if self.left_yaxis_mode=='linear':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                    elif self.left_yaxis_mode=='log':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
                else:
                    if self.right_yaxis_mode=='linear':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                    elif self.right_yaxis_mode=='log':
                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
            self.refresh()
        else:
            raise ValueError("invalid x-axis mode specified; it must either be 'linear' or 'log'")

    def yaxis(self, *args, **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        if len(args)==0:
            if side=='left':
                return self.left_yaxis_mode
            else:
                return self.right_yaxis_mode
        elif args[0] in ('linear', 'log'):
            if side=='left':
                if args[0]=='linear':
                    self.left_yaxis_mode = 'linear'
                    self.left_ylimits_mode = 'auto'
                    for curve in self.curves:
                        if curve.side=='left':
                            if self.xaxis_mode=='linear':
                                curve.points = [self.point(p.x, p.y) for p in curve.data]
                            elif self.xaxis_mode=='log':
                                curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                elif args[0]=='log':
                    self.left_yaxis_mode = 'log'
                    y_values = []
                    for curve in self.curves:
                        if curve.side=='left':
                            y_values.extend([point.y for point in curve.data])
                    if [y>0. for y in y_values].count(True)>=len(y_values)/2:
                        self.left_yaxis_sign = 1.
                    else:
                        self.left_yaxis_sign = -1.
                    self.left_ylimits_mode = 'auto'
                    for curve in self.curves:
                        if curve.side=='left':
                            if self.xaxis_mode=='linear':
                                curve.points = [self.point(p.x, self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if p.y*self.left_yaxis_sign>0.]
                            elif self.xaxis_mode=='log':
                                curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
            else:
                if args[0]=='linear':
                    self.right_yaxis_mode = 'linear'
                    self.right_ylimits_mode = 'auto'
                    for curve in self.curves:
                        if curve.side=='right':
                            if self.xaxis_mode=='linear':
                                curve.points = [self.point(p.x, p.y) for p in curve.data]
                            elif self.xaxis_mode=='log':
                                curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                elif args[0]=='log':
                    self.right_yaxis_mode = 'log'
                    y_values = []
                    for curve in self.curves:
                        if curve.side=='right':
                            y_values.extend([point.y for point in curve.data])
                    if [y>0. for y in y_values].count(True)>=len(y_values)/2:
                        self.right_yaxis_sign = 1.
                    else:
                        self.right_yaxis_sign = -1.
                    self.right_ylimits_mode = 'auto'
                    for curve in self.curves:
                        if curve.side=='right':
                            if self.xaxis_mode=='linear':
                                curve.points = [self.point(p.x, self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if p.y*self.right_yaxis_sign>0.]
                            elif self.xaxis_mode=='log':
                                curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
            self.refresh()
        else:
            raise ValueError("invalid y-axis mode specified; it must either be 'linear' or 'log'")

    def xlimits(self, *args):
        if len(args)==0:
            if self.xaxis_mode=='linear':
                return [self.xlim[0], self.xlim[1]]
            elif self.xaxis_mode=='log':
                return [self.xaxis_sign*math.pow(10., self.xaxis_sign*self.xlim[0]), self.xaxis_sign*math.pow(10., self.xaxis_sign*self.xlim[1])]
        elif args[0] in ('auto', 'tight'):
            self.xlimits_mode = args[0]
        elif type(args[0]) is list:
            if len(args[0])==2:
                args[0][0] = float(args[0][0])
                args[0][1] = float(args[0][1])
                if args[0][0]==args[0][1]:
                    raise ValueError('specified lower limit and upper limit were not distinct')
                else:
                    if self.xaxis_mode=='linear':
                        self.xlimits_mode = 'manual'
                        if args[0][0]<args[0][1]:
                            self.xlim[0] = args[0][0]
                            self.xlim[1] = args[0][1]
                        else:
                            self.xlim[0] = args[0][1]
                            self.xlim[1] = args[0][0]
                    elif self.xaxis_mode=='log':
                        if args[0][0]*args[0][1]<0.:
                            raise ValueError('for a logarithmic axis, both limits must have the same sign')
                        if (args[0][0]*args[0][1]==0.) or (args[0][0]*args[0][1]==-0.):
                            raise ValueError('for a logarithmic axis, neither limit can be zero')
                        self.xlimits_mode = 'manual'
                        if self.xaxis_sign*args[0][0]<0.:
                            self.xaxis_sign = -self.xaxis_sign
                            for curve in self.curves:
                                if curve.side=='left':
                                    if self.left_yaxis_mode=='linear':
                                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                                    elif self.left_yaxis_mode=='log':
                                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
                                else:
                                    if self.right_yaxis_mode=='linear':
                                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), p.y) for p in curve.data if p.x*self.xaxis_sign>0.]
                                    elif self.right_yaxis_mode=='log':
                                        curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
                        if args[0][0]<args[0][1]:
                            self.xlim[0] = self.xaxis_sign*math.log10(self.xaxis_sign*args[0][0])
                            self.xlim[1] = self.xaxis_sign*math.log10(self.xaxis_sign*args[0][1])
                        else:
                            self.xlim[0] = self.xaxis_sign*math.log10(self.xaxis_sign*args[0][1])
                            self.xlim[1] = self.xaxis_sign*math.log10(self.xaxis_sign*args[0][0])
            elif len(args[0])<2:
                raise IndexError('did not specify both a lower and an upper limit for the x-axis.')
            else:
                raise IndexError('more than two limits were specified for the x-axis')
        else:
            raise ValueError("invalid x-limits specification; it must be 'auto', 'tight', or a list of limits")
        self.refresh()

    def ylimits(self, *args, **kwargs):
        side = kwargs.get('side', 'left')
        if side not in ('left', 'right'):
            raise ValueError("if specified, side must be 'left' or 'right'")
        if len(args)==0:
            if side=='left':
                if self.left_yaxis_mode=='linear':
                    return [self.left_ylim[0], self.left_ylim[1]]
                elif self.left_yaxis_mode=='log':
                    return [self.left_yaxis_sign*math.pow(10., self.left_yaxis_sign*self.left_ylim[0]), self.left_yaxis_sign*math.pow(10., self.left_yaxis_sign*self.left_ylim[1])]
            else:
                if self.right_yaxis_mode=='linear':
                    return [self.right_ylim[0], self.right_ylim[1]]
                elif self.right_yaxis_mode=='log':
                    return [self.right_yaxis_sign*math.pow(10., self.right_yaxis_sign*self.right_ylim[0]), self.right_yaxis_sign*math.pow(10., self.right_yaxis_sign*self.right_ylim[1])]
        elif args[0] in ('auto', 'tight'):
            if side=='left':
                self.left_ylimits_mode = args[0]
            else:
                self.right_ylimits_mode = args[0]
        elif type(args[0]) is list:
            if side=='left':
                if len(args[0])==2:
                    args[0][0] = float(args[0][0])
                    args[0][1] = float(args[0][1])
                    if args[0][0]==args[0][1]:
                        raise ValueError('specified lower limit and upper limit were not distinct')
                    else:
                        if self.left_yaxis_mode=='linear':
                            self.left_ylimits_mode = 'manual'
                            if args[0][0]<args[0][1]:
                                self.left_ylim[0] = args[0][0]
                                self.left_ylim[1] = args[0][1]
                            else:
                                self.left_xlim[0] = args[0][1]
                                self.left_xlim[1] = args[0][0]
                        elif self.left_yaxis_mode=='log':
                            if args[0][0]*args[0][1]<0.:
                                raise ValueError('for a logarithmic axis, both limits must have the same sign')
                            if (args[0][0]*args[0][1]==0.) or (args[0][0]*args[0][1]==-0.):
                                raise ValueError('for a logarithmic axis, neither limit can be zero')
                            self.left_ylimits_mode = 'manual'
                            if self.left_yaxis_sign*args[0][0]<0.:
                                self.left_yaxis_sign = -self.left_yaxis_sign
                                for curve in self.curves:
                                    if curve.side=='left':
                                        if self.xaxis_mode=='linear':
                                            curve.points = [self.point(p.x, self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if p.y*self.left_yaxis_sign>0.]
                                        elif self.xaxis_mode=='log':
                                            curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.left_yaxis_sign*math.log10(self.left_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.left_yaxis_sign>0.)]
                            if args[0][0]<args[0][1]:
                                self.left_ylim[0] = self.left_yaxis_sign*math.log10(self.left_yaxis_sign*args[0][0])
                                self.left_ylim[1] = self.left_yaxis_sign*math.log10(self.left_yaxis_sign*args[0][1])
                            else:
                                self.left_ylim[0] = self.left_yaxis_sign*math.log10(self.left_yaxis_sign*args[0][1])
                                self.left_ylim[1] = self.left_yaxis_sign*math.log10(self.left_yaxis_sign*args[0][0])
                elif len(args[0])<2:
                    raise IndexError('did not specify both a lower and an upper limit for the left y-axis')
                else:
                    raise IndexError('more than two limits were specified for the left y-axis.')
            else:
                if len(args[0])==2:
                    args[0][0] = float(args[0][0])
                    args[0][1] = float(args[0][1])
                    if args[0][0]==args[0][1]:
                        raise ValueError('specified lower limit and upper limit were not distinct')
                    else:
                        if self.right_yaxis_mode=='linear':
                            self.right_ylimits_mode = 'manual'
                            if args[0][0]<args[0][1]:
                                self.right_ylim[0] = args[0][0]
                                self.right_ylim[1] = args[0][1]
                            else:
                                self.right_xlim[0] = args[0][1]
                                self.right_xlim[1] = args[0][0]
                        elif self.right_yaxis_mode=='log':
                            if args[0][0]*args[0][1]<0.:
                                raise ValueError('for a logarithmic axis, both limits must have the same sign')
                            if (args[0][0]*args[0][1]==0.) or (args[0][0]*args[0][1]==-0.):
                                raise ValueError('for a logarithmic axis, neither limit can be zero')
                            self.right_ylimits_mode = 'manual'
                            if self.right_yaxis_sign*args[0][0]<0.:
                                self.right_yaxis_sign = -self.right_yaxis_sign
                                for curve in self.curves:
                                    if curve.side=='right':
                                        if self.xaxis_mode=='linear':
                                            curve.points = [self.point(p.x, self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if p.y*self.right_yaxis_sign>0.]
                                        elif self.xaxis_mode=='log':
                                            curve.points = [self.point(self.xaxis_sign*math.log10(self.xaxis_sign*p.x), self.right_yaxis_sign*math.log10(self.right_yaxis_sign*p.y)) for p in curve.data if (p.x*self.xaxis_sign>0.) and  (p.y*self.right_yaxis_sign>0.)]
                            if args[0][0]<args[0][1]:
                                self.right_ylim[0] = self.right_yaxis_sign*math.log10(self.right_yaxis_sign*args[0][0])
                                self.right_ylim[1] = self.right_yaxis_sign*math.log10(self.right_yaxis_sign*args[0][1])
                            else:
                                self.right_ylim[0] = self.right_yaxis_sign*math.log10(self.right_yaxis_sign*args[0][1])
                                self.right_ylim[1] = self.right_yaxis_sign*math.log10(self.right_yaxis_sign*args[0][0])
                elif len(args[0])<2:
                    raise IndexError('did not specify both a lower and an upper limit for the right y-axis')
                else:
                    raise IndexError('more than two limits were specified for the right y-axis')
        else:
            raise ValueError("invalid y-limits specification; it must be 'auto', 'tight', or a list of limits")
        self.refresh()

    def svg(self, filename):
        self.svg_file = codecs.open(filename, encoding = 'utf-8', mode = 'w')
        self.svg_output = True
        self.svg_file.write(u'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width!s}px" height="{height!s}px" viewBox="0 0 {width!s} {height!s}">\n'.format(width = self.canvas_width, height = self.canvas_height))
        self.svg_file.write(u'    <g>\n')
        self.svg_file.write(u'        <rect x="0" y="0" width="{width!s}" height="{height!s}" stroke="none" fill="{color}"/>\n'.format(width = self.canvas_width, height = self.canvas_height, color = self.canvas_background_color))
        self.canvas.delete('all')
        self.draw_plot()
        self.svg_file.write(u'    </g>\n')
        self.svg_file.write(u'</svg>\n')
        self.svg_file.close()
        self.svg_file = None
        self.svg_output = False

    def zoom_to_fit(self, **kwargs):
        mode = kwargs.get('mode', 'auto')
        if mode not in ('auto', 'tight'):
            raise ValueError("if specified, mode must be 'auto' or 'tight'")
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        self.xlimits_mode = mode
        if (side=='left') or (side=='both'):
            self.left_ylimits_mode = mode
        if (side=='right') or (side=='both'):
            self.right_ylimits_mode = mode
        self.refresh()

    def zoom_in(self, **kwargs):
        factor = kwargs.get('factor', math.sqrt(2))
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        cx = kwargs.get('cx', 0.5*(self.axes_left+self.axes_right))
        cy = kwargs.get('cy', 0.5*(self.axes_top+self.axes_bottom))
        x = self.from_canvas_x(cx)
        self.xlimits_mode = 'manual'
        self.xlim[0] = x-0.5*self.xrange/factor
        self.xlim[1] = x+0.5*self.xrange/factor
        if (side=='left') or (side=='both'):
            y = self.from_canvas_y(cy, 'left')
            self.left_ylimits_mode = 'manual'
            self.left_ylim[0] = y-0.5*self.left_yrange/factor
            self.left_ylim[1] = y+0.5*self.left_yrange/factor
        if (side=='right') or (side=='both'):
            y = self.from_canvas_y(cy, 'right')
            self.right_ylimits_mode = 'manual'
            self.right_ylim[0] = y-0.5*self.right_yrange/factor
            self.right_ylim[1] = y+0.5*self.right_yrange/factor
        self.refresh()

    def zoom_in_x(self, **kwargs):
        factor = kwargs.get('factor', math.sqrt(2))
        cx = kwargs.get('cx', 0.5*(self.axes_left+self.axes_right))
        x = self.from_canvas_x(cx)
        self.xlimits_mode = 'manual'
        self.xlim[0] = x-0.5*self.xrange/factor
        self.xlim[1] = x+0.5*self.xrange/factor
        self.refresh()

    def zoom_in_y(self, **kwargs):
        factor = kwargs.get('factor', math.sqrt(2))
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        cy = kwargs.get('cy', 0.5*(self.axes_top+self.axes_bottom))
        if (side=='left') or (side=='both'):
            y = self.from_canvas_y(cy, 'left')
            self.left_ylimits_mode = 'manual'
            self.left_ylim[0] = y-0.5*self.left_yrange/factor
            self.left_ylim[1] = y+0.5*self.left_yrange/factor
        if (side=='right') or (side=='both'):
            y = self.from_canvas_y(cy, 'right')
            self.right_ylimits_mode = 'manual'
            self.right_ylim[0] = y-0.5*self.right_yrange/factor
            self.right_ylim[1] = y+0.5*self.right_yrange/factor
        self.refresh()

    def zoom_out(self, **kwargs):
        factor = kwargs.get('factor', math.sqrt(2))
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        cx = kwargs.get('cx', 0.5*(self.axes_left+self.axes_right))
        cy = kwargs.get('cy', 0.5*(self.axes_top+self.axes_bottom))
        x = self.from_canvas_x(cx)
        self.xlimits_mode = 'manual'
        self.xlim[0] = x-0.5*self.xrange*factor
        self.xlim[1] = x+0.5*self.xrange*factor
        if (side=='left') or (side=='both'):
            y = self.from_canvas_y(cy, 'left')
            self.left_ylimits_mode = 'manual'
            self.left_ylim[0] = y-0.5*self.left_yrange*factor
            self.left_ylim[1] = y+0.5*self.left_yrange*factor
        if (side=='right') or (side=='both'):
            y = self.from_canvas_y(cy, 'right')
            self.right_ylimits_mode = 'manual'
            self.right_ylim[0] = y-0.5*self.right_yrange*factor
            self.right_ylim[1] = y+0.5*self.right_yrange*factor
        self.refresh()

    def zoom_out_x(self, **kwargs):
        factor = kwargs.get('factor', math.sqrt(2))
        cx = kwargs.get('cx', 0.5*(self.axes_left+self.axes_right))
        x = self.from_canvas_x(cx)
        self.xlimits_mode = 'manual'
        self.xlim[0] = x-0.5*self.xrange*factor
        self.xlim[1] = x+0.5*self.xrange*factor
        self.refresh()

    def zoom_out_y(self, **kwargs):
        factor = kwargs.get('factor', math.sqrt(2))
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        cy = kwargs.get('cy', 0.5*(self.axes_top+self.axes_bottom))
        if (side=='left') or (side=='both'):
            y = self.from_canvas_y(cy, 'left')
            self.left_ylimits_mode = 'manual'
            self.left_ylim[0] = y-0.5*self.left_yrange*factor
            self.left_ylim[1] = y+0.5*self.left_yrange*factor
        if (side=='right') or (side=='both'):
            y = self.from_canvas_y(cy, 'right')
            self.right_ylimits_mode = 'manual'
            self.right_ylim[0] = y-0.5*self.right_yrange*factor
            self.right_ylim[1] = y+0.5*self.right_yrange*factor
        self.refresh()

    def zoom_rect(self, *args, **kwargs):
        left = kwargs.get('left', self.axes_left)
        right = kwargs.get('right', self.axes_right)
        top = kwargs.get('top', self.axes_top)
        bottom = kwargs.get('bottom', self.axes_bottom)
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        if len(args)==1:
            if (type(args[0]) is list) and (len(args[0])==4):
                left = float(args[0][0])
                right = float(args[0][2])
                top = float(args[0][1])
                bottom = float(args[0][3])
            else:
                raise ValueError('if specified, the optional argument must be a four-element list specifying the left, top, right, and bottom coordinates of the zoom rectangle')
        elif len(args)>1:
            raise IndexError('too many arguments supplied to zoom_rect')
        if (left<right) and (top<bottom):
            self.xlimits_mode = 'manual'
            self.xlim[0], self.xlim[1] = self.from_canvas_x(left), self.from_canvas_x(right)
            if (side=='left') or (side=='both'):
                self.left_ylimits_mode = 'manual'
                self.left_ylim[0], self.left_ylim[1] = self.from_canvas_y(bottom, 'left'), self.from_canvas_y(top, 'left')
            if (side=='right') or (side=='both'):
                self.right_ylimits_mode = 'manual'
                self.right_ylim[0], self.right_ylim[1] = self.from_canvas_y(bottom, 'right'), self.from_canvas_y(top, 'right')
            self.refresh()

    def pan_left(self, **kwargs):
        fraction = kwargs.get('fraction', 0.1)
        self.xlimits_mode = 'manual'
        self.xlim[0] -= fraction*self.xrange
        self.xlim[1] -= fraction*self.xrange
        self.refresh()

    def pan_right(self, **kwargs):
        fraction = kwargs.get('fraction', 0.1)
        self.xlimits_mode = 'manual'
        self.xlim[0] += fraction*self.xrange
        self.xlim[1] += fraction*self.xrange
        self.refresh()

    def pan_up(self, **kwargs):
        fraction = kwargs.get('fraction', 0.1)
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        if (side=='left') or (side=='both'):
            self.left_ylimits_mode = 'manual'
            self.left_ylim[0] += fraction*self.left_yrange
            self.left_ylim[1] += fraction*self.left_yrange
        if (side=='right') or (side=='both'):
            self.right_ylimits_mode = 'manual'
            self.right_ylim[0] += fraction*self.right_yrange
            self.right_ylim[1] += fraction*self.right_yrange
        self.refresh()

    def pan_down(self, **kwargs):
        fraction = kwargs.get('fraction', 0.1)
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        if (side=='left') or (side=='both'):
            self.left_ylimits_mode = 'manual'
            self.left_ylim[0] -= fraction*self.left_yrange
            self.left_ylim[1] -= fraction*self.left_yrange
        if (side=='right') or (side=='both'):
            self.right_ylimits_mode = 'manual'
            self.right_ylim[0] -= fraction*self.right_yrange
            self.right_ylim[1] -= fraction*self.right_yrange
        self.refresh()

    def pan(self, **kwargs):
        dx = kwargs.get('dx', 0.)
        dy = kwargs.get('dy', 0.)
        side = kwargs.get('side', 'both')
        if side not in ('left', 'right', 'both'):
            raise ValueError("if specified, side must be 'left', 'right', or 'both'")
        if (dx!=0.) or (dy!=0.):
            self.xlimits_mode = 'manual'
            self.xlim[0] -= dx*self.x_epsilon
            self.xlim[1] -= dx*self.x_epsilon
            if (side=='left') or (side=='both'):
                self.left_ylimits_mode = 'manual'
                self.left_ylim[0] += dy*self.left_y_epsilon
                self.left_ylim[1] += dy*self.left_y_epsilon
            if (side=='right') or (side=='both'):
                self.right_ylimits_mode = 'manual'
                self.right_ylim[0] += dy*self.right_y_epsilon
                self.right_ylim[1] += dy*self.right_y_epsilon
            self.refresh()

    def delete_curve(self, name):
        names = [curve.name for curve in self.curves]
        if name in names:
            i = names.index(name)
            del(self.curves[i])
        else:
            raise NameError('no curve exists with name = {0!r}'.format(name))
        self.refresh()

    def configure_curve(self, name, **kwargs):
        style = kwargs.get('style', '')
        names = [curve.name for curve in self.curves]
        if name in names:
            i = names.index(name)
            marker_color = kwargs.get('marker_color', self.curves[i].marker_color)
            marker = kwargs.get('marker', self.curves[i].marker)
            curve_color = kwargs.get('curve_color', self.curves[i].curve_color)
            curve_style = kwargs.get('curve_style', self.curves[i].curve_style)
            if style=='':
                self.curves[i].marker_color = marker_color
                self.curves[i].marker = marker
                self.curves[i].curve_color = curve_color
                self.curves[i].curve_style = curve_style
            else:
                [self.curves[i].marker_color, self.curves[i].marker, self.curves[i].curve_color, self.curves[i].curve_style] = self.parse_style(style)
        else:
            raise NameError('no curve exists with name = {0!r}'.format(name))
        self.refresh()

    def bindings(self):
        self.key_bindings()
        self.mouse_bindings()

    def key_bindings(self):
        self.canvas.bind('<Up>', lambda event: self.pan_up())
        self.canvas.bind('<Down>', lambda event: self.pan_down())
        self.canvas.bind('<Left>', lambda event: self.pan_left())
        self.canvas.bind('<Right>', lambda event: self.pan_right())
        self.canvas.bind('<Control-Up>', lambda event: self.pan_up(fraction = 0.5))
        self.canvas.bind('<Control-Down>', lambda event: self.pan_down(fraction = 0.5))
        self.canvas.bind('<Control-Left>', lambda event: self.pan_left(fraction = 0.5))
        self.canvas.bind('<Control-Right>', lambda event: self.pan_right(fraction = 0.5))
        self.canvas.bind('<Shift-Up>', lambda event: self.pan_up(fraction = 1./self.axes_height))
        self.canvas.bind('<Shift-Down>', lambda event: self.pan_down(fraction = 1./self.axes_height))
        self.canvas.bind('<Shift-Left>', lambda event: self.pan_left(fraction = 1./self.axes_width))
        self.canvas.bind('<Shift-Right>', lambda event: self.pan_right(fraction = 1./self.axes_width))
        self.canvas.bind('=', lambda event: self.zoom_in())
        self.canvas.bind('-', lambda event: self.zoom_out())
        self.canvas.bind('<Control-equal>', lambda event: self.zoom_in(factor = 2.))
        self.canvas.bind('<Control-minus>', lambda event: self.zoom_out(factor = 2.))
        self.canvas.bind('+', lambda event: self.zoom_in(factor = math.sqrt(math.sqrt(2.))))
        self.canvas.bind('_', lambda event: self.zoom_out(factor = math.sqrt(math.sqrt(2.))))
        self.canvas.bind('h', lambda event: self.zoom_to_fit())
        self.canvas.bind('<Home>', lambda event: self.zoom_to_fit())
        self.canvas.bind('g', lambda event: self.grid('off') if self.grid()=='on' else self.grid('on'))
        self.canvas.bind('x', lambda event: self.xaxis('log') if self.xaxis()=='linear' else self.xaxis('linear'))
        self.canvas.bind('y', lambda event: self.yaxis('log') if self.yaxis()=='linear' else self.yaxis('linear'))
        self.canvas.bind('l', lambda event: self.yaxis('log') if self.yaxis()=='linear' else self.yaxis('linear'))
        self.canvas.bind('r', lambda event: self.yaxis('log', side = 'right') if self.yaxis(side = 'right')=='linear' else self.yaxis('linear', side = 'right'))

    def mouse_bindings(self):
        self.marker_color = tk.StringVar()
        self.marker_color.set('b')
        self.marker = tk.StringVar()
        self.marker.set('')
        self.curve_color = tk.StringVar()
        self.curve_color.set('b')
        self.curve_style = tk.StringVar()
        self.marker.set('')
        self.curve_name = ''
        self.curve_menu = tk.Menu(self.canvas, tearoff = 0)
        marker_menu = tk.Menu(self.curve_menu, tearoff = 0)
        for [val, name] in self.marker_names:
            marker_menu.add_radiobutton(label = name, variable = self.marker, value = val, command = self.configure_curve_callback)
        self.curve_menu.add_cascade(label = 'Marker', menu = marker_menu)
        marker_color_menu = tk.Menu(self.curve_menu, tearoff = 0)
        for [val, name] in self.color_names:
            marker_color_menu.add_radiobutton(label = name, variable = self.marker_color, value = val, command = self.configure_curve_callback)
        self.curve_menu.add_cascade(label = 'Marker color', menu = marker_color_menu)
        curve_style_menu = tk.Menu(self.curve_menu, tearoff = 0)
        for [val, name] in self.linestyle_names:
            curve_style_menu.add_radiobutton(label = name, variable = self.curve_style, value = val, command = self.configure_curve_callback)
        self.curve_menu.add_cascade(label = 'Curve style', menu = curve_style_menu)
        curve_color_menu = tk.Menu(self.curve_menu, tearoff = 0)
        for [val, name] in self.color_names:
            curve_color_menu.add_radiobutton(label = name, variable = self.curve_color, value = val, command = self.configure_curve_callback)
        self.curve_menu.add_cascade(label = 'Curve color', menu = curve_color_menu)
        self.curve_menu.add_separator()
        self.curve_menu.add_command(label = 'Delete', command = lambda: self.delete_curve(self.curve_name))

        windowing_system = self.root.tk.call('tk', 'windowingsystem')
        self.arrow = 'arrow'
#        if windowing_system=='x11':
#            self.zoom = ('@cursors/zoom.xbm', 'cursors/zoom.xbm', 'black', 'white')
#            self.zoomin = ('@cursors/zoomin.xbm', 'cursors/zoommask.xbm', 'black', 'white')
#            self.zoomout = ('@cursors/zoomout.xbm', 'cursors/zoommask.xbm', 'black', 'white')
#            self.openhand = ('@cursors/openhand.xbm', 'cursors/openhandmask.xbm', 'black', 'white')
#            self.closedhand = ('@cursors/closedhand.xbm', 'cursors/closedhandmask.xbm', 'black', 'white')
#        elif windowing_system=='win32':
#            self.zoom = '@cursors/zoom.cur'
#            self.zoomin = '@cursors/zoomin.cur'
#            self.zoomout = '@cursors/zoomout.cur'
#            self.openhand = '@cursors/openhand.cur'
#            self.closedhand = '@cursors/closedhand.cur'
#        elif windowing_system=='aqua':
#            self.zoom = 'arrow'
#            self.zoomin = 'arrow'
#            self.zoomout = 'arrow'
#            self.openhand = 'openhand'
#            self.closedhand = 'closedhand'
#        else:
        self.zoom = 'arrow'
        self.zoomin = 'arrow'
        self.zoomout = 'arrow'
        self.openhand = 'arrow'
        self.closedhand = 'arrow'
        self.canvas.bind('<Control-Button-1>', self.curve_context_menu)
        self.canvas.bind('<Button-3>', self.curve_context_menu)
        self.canvas.bind('<Escape>', self.cancel_mouse_zoom_pan)
        self.canvas.bind('z', self.setup_mouse_zoom)
        self.canvas.bind('b', self.setup_mouse_box_zoom)
        self.canvas.bind('p', self.setup_mouse_pan)

    def curve_context_menu(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if (x>self.axes_left) and (x<self.axes_right) and (y>self.axes_top) and (y<self.axes_bottom):
            items = self.canvas.find_overlapping(x-2., y-2., x+2., y+2.)
            name = ''
            for item in items:
                tags = self.canvas.gettags(item)
                if (tags!=()) and (tags[0]!='current'):
                    name = tags[0]
            if name!='':
                names = [curve.name for curve in self.curves]
                if name in names:
                    i = names.index(name)
                    self.curve_name = name
                    self.marker_color.set(self.curves[i].marker_color)
                    self.marker.set(self.curves[i].marker)
                    self.curve_color.set(self.curves[i].curve_color)
                    self.curve_style.set(self.curves[i].curve_style)
                else:
                    raise NameError('no curve exists with name = {0!r}'.format(name))
                self.curve_menu.post(event.x_root, event.y_root)

    def configure_curve_callback(self):
        marker = self.marker.get()
        if marker==' ':
            marker = ''
        curve_style = self.curve_style.get()
        if curve_style==' ':
            curve_style = ''
        names = [curve.name for curve in self.curves]
        if self.curve_name in names:
            if (marker=='') and (curve_style==''):
                self.delete_curve(self.curve_name)
            else:
                i = names.index(self.curve_name)
                self.curves[i].marker_color = self.marker_color.get()
                self.curves[i].marker = marker
                self.curves[i].curve_color = self.curve_color.get()
                self.curves[i].curve_style = curve_style
        else:
            raise NameError('no curve exists with name = {0!r}'.format(name))
        self.refresh()

    def cancel_mouse_zoom_pan(self, event):
        self.canvas.bind('<Button-1>', lambda event: None)
        self.canvas.bind('<Shift-Button-1>', lambda event: None)
        self.canvas.bind('<Shift_L>', lambda event: None)
        self.canvas.bind('<KeyRelease-Shift_L>', lambda event: None)
        self.canvas.bind('<B1-Motion>', lambda event: None)
        self.canvas.bind('<ButtonRelease-1>', lambda event: None)
        self.canvas.configure(cursor = self.arrow)

    def setup_mouse_zoom(self, event):
        self.canvas.bind('<Button-1>', self.mouse_zoom_in)
        self.canvas.bind('<Shift-Button-1>', self.mouse_zoom_out)
        self.canvas.bind('<Shift_L>', lambda event: self.canvas.configure(cursor = self.zoomout))
        self.canvas.bind('<KeyRelease-Shift_L>', lambda event: self.canvas.configure(cursor = self.zoomin))
        self.canvas.bind('<B1-Motion>', lambda event: None)
        self.canvas.bind('<ButtonRelease-1>', lambda event: None)
        self.canvas.configure(cursor = self.zoomin)

    def mouse_zoom_in(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if (x>=self.axes_left) and (x<=self.axes_right) and (y>=self.axes_top) and (y<=self.axes_bottom):
            self.zoom_in(cx = x, cy = y)

    def mouse_zoom_out(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if (x>=self.axes_left) and (x<=self.axes_right) and (y>=self.axes_top) and (y<=self.axes_bottom):
            self.zoom_out(cx = x, cy = y)

    def setup_mouse_box_zoom(self, event):
        self.canvas.bind('<Button-1>', self.start_mouse_box_zoom)
        self.canvas.bind('<Shift-Button-1>', lambda event: None)
        self.canvas.bind('<Shift_L>', lambda event: None)
        self.canvas.bind('<KeyRelease-Shift_L>', lambda event: None)
        self.canvas.bind('<B1-Motion>', lambda event: None)
        self.canvas.bind('<ButtonRelease-1>', lambda event: None)
        self.canvas.configure(cursor = self.zoom)

    def start_mouse_box_zoom(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if (x>=self.axes_left) and (x<=self.axes_right) and (y>=self.axes_top) and (y<=self.axes_bottom):
            self.x0 = x
            self.y0 = y
            self.canvas.create_rectangle([self.x0, self.y0, self.x0, self.y0], outline = self.axes_color, fill = '', dash = (1, 4), tags = 'zoombox')
            self.canvas.bind('<B1-Motion>', self.continue_mouse_box_zoom)
            self.canvas.bind('<ButtonRelease-1>', self.finish_mouse_box_zoom)

    def continue_mouse_box_zoom(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if x<self.axes_left:
            x = self.axes_left
        if x>self.axes_right:
            x = self.axes_right
        if y<self.axes_top:
            y = self.axes_top
        if y>self.axes_bottom:
            y = self.axes_bottom
        self.canvas.coords('zoombox', self.x0, self.y0, x, y)

    def finish_mouse_box_zoom(self, event):
        self.canvas.delete('zoombox')
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if x<self.axes_left:
            x = self.axes_left
        if x>self.axes_right:
            x = self.axes_right
        if y<self.axes_top:
            y = self.axes_top
        if y>self.axes_bottom:
            y = self.axes_bottom
        if x<self.x0:
            self.x0, x = x, self.x0
        if y<self.y0:
            self.y0, y = y, self.y0
        self.zoom_rect([self.x0, self.y0, x, y])
        self.canvas.bind('<B1-Motion>', lambda event: None)
        self.canvas.bind('<ButtonRelease-1>', lambda event: None)

    def setup_mouse_pan(self, event):
        self.canvas.bind('<Button-1>', self.start_mouse_pan)
        self.canvas.bind('<Shift-Button-1>', lambda event: None)
        self.canvas.bind('<Shift_L>', lambda event: None)
        self.canvas.bind('<KeyRelease-Shift_L>', lambda event: None)
        self.canvas.bind('<B1-Motion>', lambda event: None)
        self.canvas.bind('<ButtonRelease-1>', lambda event: None)
        self.canvas.configure(cursor = self.openhand)

    def start_mouse_pan(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if (x>=self.axes_left) and (x<=self.axes_right) and (y>=self.axes_top) and (y<=self.axes_bottom):
            self.x0 = x
            self.y0 = y
            self.canvas.bind('<B1-Motion>', self.continue_mouse_pan)
            self.canvas.bind('<ButtonRelease-1>', self.finish_mouse_pan)
            self.canvas.configure(cursor = self.closedhand)

    def continue_mouse_pan(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.pan(dx = x-self.x0, dy = y-self.y0)
        self.x0 = x
        self.y0 = y

    def finish_mouse_pan(self, event):
        self.canvas.bind('<B1-Motion>', lambda event: None)
        self.canvas.bind('<ButtonRelease-1>', lambda event: None)
        self.canvas.configure(cursor = self.openhand)
