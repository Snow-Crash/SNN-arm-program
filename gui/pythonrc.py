
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
import plotk, pickle, codecs
from vector import *

__root__ = tk.Tk()
__root__.withdraw()
__fig__ = 0
__figs__ = {}
__plot__ = None

class fig:
    
    def __init__(self, title, **kwargs):
        global __root__
        global __plot__
        self.width = float(kwargs.get('width', 560.))
        self.height = float(kwargs.get('height', 420.))
        self.rows = kwargs.get('rows', 1)
        self.cols = kwargs.get('cols', 1)
        self.row = kwargs.get('row', 0)
        self.col = kwargs.get('col', 0)
        self.top = tk.Toplevel(__root__)
        self.top.title(title)
        self.top.protocol('WM_DELETE_WINDOW', self.close)
        subplot_width = round(self.width/self.cols)
        subplot_height = round(self.height/self.rows)
        self.plots = []
        for row in range(self.rows):
            row_frame = tk.Frame(self.top)
            plot_row = []
            for col in range(self.cols):
                plot_frame = tk.Frame(row_frame)
                plot = plotk.plotk(parent = plot_frame, width = subplot_width, height = subplot_height)
                plot.bindings()
                plot_row.append(plot)
                plot_frame.pack(side = tk.LEFT, fill = 'both', expand = 'yes')
            self.plots.append(plot_row)
            row_frame.pack(side = tk.TOP, fill = 'both', expand = 'yes')
        self.top.lift()
        __plot__ = self.plots[self.row][self.col]

    def close(self):
        global __plot__
        title = self.top.title()
        for row in range(self.rows):
            for col in range(self.cols):
                if __plot__==self.plots[row][col]:
                    __plot__ = None
        self.top.destroy()
        del(__figs__[title])

def figure(*args, **kwargs):
    '''
    figure([<fig>], [width = <width>], [height = <height>], 
               [rows = <rows>], [cols = <cols>], 
               [row = <row>], [col = <col>])
    
    Create a new figure window or select an existing figure window, raising 
    it to the top of the stacking order.  If <fig> is specified, it can either 
    be an integer or a string.  If the figure window specified by <fig> exists, 
    it is raised to the top of the stacking order and the subplot specified by 
    <row> and <col> is selected.  If the figure window specified by <fig> does 
    not exist, a new figure window is created with a <rows> x <cols> matrix of 
    subplots.  The subplot specified by <row> and <col> is selected.  The 
    optional parameters are given below (default values are provided in square 
    brackets):
    
         width [540.]: Width in pixels to be distributed evenly among the 
                           number of subplot columns specified by <cols>.
        height [420.]: Height in pixels to be distributed evenly among the 
                           number of subplot rows specidied by <rows>.
             rows [1]: Number of subplot rows in the figure window.
             cols [1]: Number of subplot columns in the figure window.
              row [0]: Row index of the selected subplot (the first row 
                           is numbered starting at zero).
              col [0]: Column index of the selected subplot (the first 
                           column is numbered starting at zero).
    '''
    global __figs__
    global __plot__
    global __fig__
    rows = kwargs.get('rows')
    cols = kwargs.get('cols')
    row = kwargs.get('row')
    col = kwargs.get('col')
    if len(args)==0:
        __fig__ = __fig__+1
        title = 'Figure {0!s}'.format(__fig__)
    elif type(args[0]) is int:
        title = 'Figure {0!s}'.format(args[0])
    elif type(args[0]) is str:
        title = args[0]
    else:
        raise TypeError('if specified, figure identifier must be an integer or a string')
    if title in __figs__.keys():
        __figs__[title].top.lift()
        if (rows!=None) or (cols!=None):
            raise ValueError('the number of subplot rows and columns cannot be changed for an existing figure')
        if row!=None:
            if (row>=0) and (row<__figs__[title].rows):
                __figs__[title].row = row
            else:
                raise IndexError('the specified subplot row is out of range for the selected figure')
        if col!=None:
            if (col>=0) and (col<__figs__[title].cols):
                __figs__[title].col = col
            else:
                raise IndexError('the specified subplot column is out of range for the selected figure')
        __plot__ = __figs__[title].plots[__figs__[title].row][__figs__[title].col]
    else:
        if rows==None:
            rows = 1
        if rows<1:
            raise ValueError('if specified, the number of subplot rows must be one or greater')
        if row!=None:
            if (row<0) or (row>=rows):
                raise IndexError('the specified subplot row is out of range')
        if cols==None:
            cols = 1
        if cols<1:
            raise ValueError('if specified, the number of subplot columns must be one or greater')
        if col!=None:
            if (col<0) or (col>=cols):
                raise IndexError('the specified subplot column is out of range')
        __figs__[title] = fig(title, **kwargs)

def select_plot():
    global __root__
    global __figs__
    global __plot__
    if len(__figs__.keys())==0:
        figure()
    else:
        stackingorder = __root__.tk.eval('wm stackorder '+str(__root__))
        figs = stackingorder.split(' ')
        for title in __figs__.keys():
            if str(__figs__[title].top)==figs[-1]:
                __figs__[title].top.lift()
                __plot__ = __figs__[title].plots[__figs__[title].row][__figs__[title].col]

def configure(**kwargs):
    '''
    configure([<parameter1> = <value1>, <parameter2> = <value2>, ...])

    Configure all of the plots in the currently selected figure.  The 
    parameters can be any of the following (default values are shown in 
    square brackets):

               marker_radius [4.0]: Radius in pixels of the pointmarkers.
           marker_lineweight [0.5]: Line weight in pixels of the 
                                        pointmarkers.
            curve_lineweight [1.0]: Line weight in pixels of curves.
                 tick_length [6.0]: Length in pixels of major ticks (minor 
                                        ticks are half the length of 
                                        major ticks).
             tick_lineweight [0.5]: Line weight in pixels of ticks and grid 
                                        lines.
            background ['#CDCDCD']: Background color of the plot.
       axes_background ['#FFFFFF']: Background color of the axes.
            axes_color ['#000000']: Color of the axes frame, ticks, tick 
                                        labels, axes labels, and grid lines.
             axes_lineweight [1.0]: Line weight in pixels of the axes frame.
                    baseline [0.6]: Relative position of the text baseline 
                                        from the top of the bounding box
                                        for SVG output. 
                     fontsize [12]: Font size for tick labels and axes 
                                        labels (must be an integer).
                font ['Helvetica']: Font for tick labels and axes labels.
    '''
    global __figs__
    global __plot__
    if __plot__==None:
        select_plot()
    title = __plot__.root.winfo_toplevel().title()
    fig = __figs__[title]
    for row in range(fig.rows):
        for col in range(fig.cols):
            fig.plots[row][col].configure(**kwargs)

def config_plot(**kwargs):
    '''
    configure([<parameter1> = <value1>, <parameter2> = <value2>, ...])

    Configure the currently selected plot.  The parameters can be any of the 
    following (default values are shown in square brackets):

               marker_radius [4.0]: Radius in pixels of the pointmarkers.
           marker_lineweight [0.5]: Line weight in pixels of the 
                                        pointmarkers.
            curve_lineweight [1.0]: Line weight in pixels of curves.
                 tick_length [6.0]: Length in pixels of major ticks (minor 
                                        ticks are half the length of 
                                        major ticks).
             tick_lineweight [0.5]: Line weight in pixels of ticks and grid 
                                        lines.
            background ['#CDCDCD']: Background color of the plot.
       axes_background ['#FFFFFF']: Background color of the axes.
            axes_color ['#000000']: Color of the axes frame, ticks, tick 
                                        labels, axes labels, and grid lines.
             axes_lineweight [1.0]: Line weight in pixels of the axes frame.
                    baseline [0.6]: Relative position of the text baseline 
                                        from the top of the bounding box
                                        for SVG output. 
                     fontsize [12]: Font size for tick labels and axes 
                                        labels (must be an integer).
                font ['Helvetica']: Font for tick labels and axes labels.
    '''
    global __plot__
    if __plot__==None:
        select_plot()
    __plot__.configure(**kwargs)

def clear(**kwargs):
    '''
    clear([side = 'left'|'right'|'both'])
    
    Clear the curves associated with the specified y axis or axes of the 
    currently selected plot.  If no side is specified, the curves associated 
    with both y axes are cleared.
    '''
    if __plot__==None:
        select_plot()
    __plot__.clear(**kwargs)

def draw_now():
    '''
    Force the currently selected plot to update.
    '''
    if __plot__==None:
        select_plot()
    __plot__.draw_now()

def plot(*args, **kwargs):
    '''
    plot(x, y, [style], [side = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on linear axes 
    associated with the specified y axis.  If no side is specified, the curves 
    are plotted on the left y axis.  If the hold argument is specified as 'on', 
    any previously plotted curves are retained.  By default old curves are not 
    retained.
    
    The x and y arguments must either be vectors or lists of vectors.  If x is 
    a vector and y is a list of vectors, then each of the y vectors is plotted 
    against the one x vector.  If x and y are both lists of vectors, then each 
    y vector is plotted against the corresponding x vector.  If x is given as 
    a list of vectors, then y must also be a list of vectors.
    
    The optional style argument can be a string or a list of strings that 
    specify the style of the curves to be plotted.  If a single string is 
    supplied, then it is applied to all curves.  If a list of strings is 
    supplied, then there must be one for each curve.  A style string generally 
    specifies a point marker color, a point marker, a line color, and a line 
    style (in that order) using characters from the following three lists:
    
         b     blue            .     point                  -     solid
         g     green           o     circle                 :     dotted
         r     red             x     ex                     -.    dashdot
         c     cyan            +     plus                   -:    dashdotdot
         m     magenta         *     star                   --    dashed
         y     yellow          s     square               (none)  no line
         k     black           d     diamond
         w     white           v     triangle (down)
                               ^     triangle (up)
                               <     triangle (left)
                               >     triangle (right)
                               p     pentagram
                               h     hexagram
                             (none)  no point marker
    
    If a color is not specified for a point marker or for a curve, then a 
    default color is assigned by cycling through the first six colors in the 
    list in the order shown.  If no point marker is specified and no line 
    style is specified, then by default the corresponding curve is plotted 
    with points and solid lines.
    '''
    if __plot__==None:
        select_plot()
    __plot__.plot(*args, **kwargs)

def semilogx(*args, **kwargs):
    '''
    semilogx(x, y, [style], [side = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on semilogartihmic 
    axes (x-axis logarithmic) associated with the specified y axis.  If no 
    side is specified, the curves are plotted on the left y axis.  If the hold 
    argument is specified as 'on', any previously plotted curves are retained.  
    By default old curves are not retained.  For further details, see help for 
    the plot function.
    '''
    if __plot__==None:
        select_plot()
    __plot__.semilogx(*args, **kwargs)

def semilogy(*args, **kwargs):
    '''
    semilogy(x, y, [style], [side = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on semilogartihmic 
    axes (y-axis logarithmic) associated with the specified y axis.  If no 
    side is specified, the curves are plotted on the left y axis.  If the hold 
    argument is specified as 'on', any previously plotted curves are retained.  
    By default old curves are not retained.  For further details, see help for 
    the plot function.
    '''
    if __plot__==None:
        select_plot()
    __plot__.semilogy(*args, **kwargs)

def loglog(*args, **kwargs):
    '''
    loglog(x, y, [style], [side = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on logartihmic axes 
    associated with the specified y axis.  If no side is specified, the curves 
    are plotted on the left y axis.  If the hold argument is specified as 
    'on', any previously plotted curves are retained.  By default old curves 
    are not retained.  For further details, see help for the plot function.
    '''
    if __plot__==None:
        select_plot()
    __plot__.loglog(*args, **kwargs)

def grid(*args):
    '''
    grid(['on'|'off'])
    
    Set or get the state of the grid on the currently selected plot.  If no 
    state is specified, the current state of the grid of the selected plot is 
    returned.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.grid(*args)

def xlabel(*args):
    '''
    xlabel([label])
    
    Set or get the x-axis label of the currently selected plot.  If specified, 
    label becomes the x-axis label of the selected plot.  If no label is 
    specified, the current x-axis label is returned.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.xlabel(*args)

def ylabel(*args, **kwargs):
    '''
    ylabel([label], [side = 'left'|'right'])
    
    Set or get a y-axis label of the currently selected plot.  If specified, 
    label becomes the label of the specified y axis of the selected plot.  If 
    no label is specified, the current label of the specified y axis is 
    returned.  If no side is specified, the left side is assumed.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.ylabel(*args, **kwargs)

def xaxis(*args):
    '''
    xaxis(['linear'|'log'])
    
    Set or get the x-axis mode of the currently selected plot.  If no mode is 
    specified, the current x-axis mode is returned.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.xaxis(*args)

def yaxis(*args, **kwargs):
    '''
    yaxis(['linear'|'log'], [side = 'left'|'right'])

    Set or get the mode of the specified y axis of the currently selected 
    plot.  If no mode is specified, the current mode of the specified y 
    axis is returned.  If no side is specified, the left side is assumed.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.yaxis(*args, **kwargs)

def xlimits(*args):
    '''
    xlimits(['auto'|'tight'|xlimits])
    
    Set or get the x-axis limits of the currently selected plot.  If fixed 
    limits are specified, they must be supplied in a two-element list.  If 
    no limits are specified, the current lower and upper x-axis limits are 
    returned in a list.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.xlimits(*args)

def ylimits(*args, **kwargs):
    '''
    ylimits(['auto'|'tight'|ylimits], [side = 'left'|'right'])

    Set or get the limits of the specified y axis of the currently selected 
    plot.  If fixed limits are specified, they must be supplied in a two-
    element list.  If no limits are specified, the current lower and upper 
    limit of the specified y axis are returned in a list.  If no side is 
    specified, the left side is assumed.
    '''
    if __plot__==None:
        select_plot()
    return __plot__.ylimits(*args, **kwargs)

def svg(filename):
    '''
    Export the currently selected figure as a scalable vector graphics (.svg) 
    file whose name is specified by the argument.
    '''
    global __figs__
    global __plot__
    if __plot__==None:
        select_plot()
    title = __plot__.root.winfo_toplevel().title()
    fig = __figs__[title]
    svg_file = codecs.open(filename, encoding = 'utf-8', mode = 'w')
    width = 0.
    for col in range(fig.cols):
        width += fig.plots[0][col].canvas_width
    height = 0.
    for row in range(fig.rows):
        height += fig.plots[row][0].canvas_height
    svg_file.write(u'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width!s}px" height="{height!s}px" viewBox="0 0 {width!s} {height!s}">\n'.format(width = width, height = height))
    svg_file.write(u'<defs>\n')
    for row in range(fig.rows):
        for col in range(fig.cols):
            plot = fig.plots[row][col]
            plot.svg_file = svg_file
            plot.svg_output = True
            svg_file.write(u'    <g id="subplot_{0!s}_{1!s}">\n'.format(row, col))
            svg_file.write(u'        <rect x="0" y="0" width="{width!s}" height="{height!s}" stroke="none" fill="{color}"/>\n'.format(width = plot.canvas_width, height = plot.canvas_height, color = plot.canvas_background_color))
            plot.canvas.delete('all')
            plot.draw_plot()
            svg_file.write(u'    </g>\n')
            plot.svg_output = False
            plot.svg_file = None
    svg_file.write(u'</defs>\n')
    svg_file.write(u'<g>\n')
    y = 0.
    for row in range(fig.rows):
        x = 0.
        for col in range(fig.cols):
            svg_file.write(u'    <use x="{0!s}" y="{1!s}" xlink:href="#subplot_{2!s}_{3!s}"/>\n'.format(x, y, row, col))
            x += fig.plots[row][col].canvas_width
        y += fig.plots[row][col].canvas_height
    svg_file.write(u'</g>\n')
    svg_file.write(u'</svg>\n')
    svg_file.close()

def workspace():
    variables = []
    for variable in globals().keys():
        if (variable[0:2]!='__' or variable[-2:]!='__'):
            if (type (globals()[variable]) is dict) or (type (globals()[variable]) is tuple) or (type (globals()[variable]) is list) or (type (globals()[variable]) is str) or (type (globals()[variable]) is float) or (type (globals()[variable]) is int) or (type (globals()[variable]) is long) or isinstance((globals()[variable]), vector):
                variables.append(variable)
    return variables

def save(filename):
    '''
    Save the variables in the current workspace using the pickle module 
    to a file whose name is specified by the argument provided. 
    '''
    file = open(filename, 'w')
    variables = workspace()
    pickle.dump(variables, file)
    for variable in variables:
        pickle.dump((globals()[variable]), file)
    file.close()

def load(filename):
    '''
    Load variables into the workspace from a file that was created previously 
    using the save function.
    '''
    file = open(filename, 'r')
    variables = pickle.load(file)
    for variable in variables:
        globals()[variable] = pickle.load(file)
    file.close()

def who():
    '''
    Display a list of the names of the variables in the current workspace.
    '''
    print '    '.join(sorted(workspace()))

def whos():
    '''
    Display a detailed list of the names, types, and contents of the variables 
    in the current workspace.
    '''
    print '  Name              Type      Length    Value'
    for variable in sorted(workspace()):
        line = '  {0:<16}  '.format(variable)
        if type (globals()[variable]) is dict:
            line = line + 'dict      {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value)<=40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        elif type (globals()[variable]) is tuple:
            line = line + 'tuple     {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value)<=40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        elif type (globals()[variable]) is list:
            line = line + 'list      {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value)<=40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        elif type (globals()[variable]) is str:
            line = line + "str       {0!s:>6}    '".format(len((globals()[variable])))
            value = (globals()[variable])
            if len(value)<=38:
                line = line + value + "'"
            else:
                line = line + value[0:20] + '...' + value[-15:] + "'"
        elif type (globals()[variable]) is float:
            line = line + 'float               {0!s}'.format((globals()[variable]))
        elif type (globals()[variable]) is int:
            line = line + 'int                 {0!s}'.format((globals()[variable]))
        elif type (globals()[variable]) is long:
            line = line + 'long                {0!s}'.format((globals()[variable]))
        elif isinstance((globals()[variable]), vector):
            line = line + 'vector    {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value)<=40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        print line

