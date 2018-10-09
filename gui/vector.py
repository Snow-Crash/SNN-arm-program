
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
import math, random, sys
from math import pi, e

def any(x):
    return x.count(True)>0

def all(x):
    return x.count(True)==len(x)

def num2str(x, n = 0):
    if not ((type(x) is float) or (type(x) is int) or (type(x) is long)):
        raise TypeError('x must be a numeric data type')
    x = float(x)
    multipliers = (1., 1e-3, 1e-6, 1e-9, 1e-12, 1e-15, 1e-18, 1e-21, 1e-24, 
                   1e24, 1e21, 1e18, 1e15, 1e12, 1e9, 1e6, 1e3)
    prefixes = ('', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 
                'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm')
    if abs(x)==0.:
        index = 0
    else:
        index = int(math.floor(math.log10(abs(x))/3.))
    if (index>=-8) and (index<=8):
        return str(multipliers[index]*x if n==0 else round(multipliers[index]*x, n))+prefixes[index]
    else:
        return str(x if n==0 else round(x, n))

def str2num(s):
    if not (type(s) is str):
        raise TypeError('s must be a string')
    multipliers = {'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15, 'E': 1e18, 'Z': 1e21, 'Y': 1e24, 
                   'y': 1e-24, 'z': 1e-21, 'a': 1e-18, 'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3}
    if s[-1] in multipliers.keys():
        return float(s[0:-1])*multipliers[s[-1]]
    else:
        return float(s)

def zeros(n):
    return vector([0. for i in range(n)])

def ones(n):
    return vector([1. for i in range(n)])

def rand(n):
    return vector([random.random() for i in range(n)])

def linspace(initial, final, n = 100):
    if n>=2:
        increment = (float(final)-float(initial))/(n-1)
        return vector([float(initial)+i*increment for i in range(n)])
    else:
        return vector()

def logspace(initial, final, n = 100):
    if n>=2:
        increment = (float(final)-float(initial))/(n-1)
        logvals = [float(initial)+i*increment for i in range(n)]
        return vector([math.pow(10., value) for value in logvals])
    else:
        return vector()

def spline(x, y, xx):
    if not isinstance(xx, vector) and type(xx) is not float:
        raise TypeError('xx must be either a vector or a float')
    if not isinstance(x, vector) or not isinstance(y, vector):
        raise TypeError('x and y must both be vectors')
    if len(x)!=len(y):
        raise IndexError('x and y must be of the same length')
    coeffs = [0.]
    factors = [0.]
    for i in range(1, len(x)-1):
        delta = (x[i]-x[i-1])/(x[i+1]-x[i-1])
        temp = delta*coeffs[i-1]+2.
        coeffs.append((delta-1)/len(x))
        factors.append((y[i+1]-y[i])/(x[i+1]-x[i])-(y[i]-y[i-1])/(x[i]-x[i-1]))
        factors[i] = (6.*factors[i]/(x[i+1]-x[i-1])-delta*factors[i-1])/temp
    coeffs.append(0)
    for i in range(len(x)-2, -1, -1):
        coeffs[i] = coeffs[i]*coeffs[i+1]+factors[i]
    if isinstance(xx, vector):
        yy = zeros(len(xx))
        for k in range(len(xx)):
            i = 0
            for j in range(len(x)-2, 0, -1):
                if xx[k]>x[j]:
                    i = j
                    break
            delta = x[i+1]-x[i]
            mult = 0.5*coeffs[i]+(xx[k]-x[i])*(coeffs[i+1]-coeffs[i])/(6.*delta)
            mult *= xx[k]-x[i]
            mult += (y[i+1]-y[i])/delta
            mult -= (coeffs[i+1]+2.*coeffs[i])*delta/6.
            yy[k] = y[i]+mult*(xx[k]-x[i])
        return yy
    else:
        i = 0
        for j in range(len(x)-2, 0, -1):
            if xx>x[j]:
                i = j
                break
        delta = x[i+1]-x[i]
        mult = 0.5*coeffs[i]+(xx-x[i])*(coeffs[i+1]-coeffs[i])/(6.*delta)
        mult *= xx-x[i]
        mult += (y[i+1]-y[i])/delta
        mult -= (coeffs[i+1]+2.*coeffs[i])*delta/6.
        return y[i]+mult*(xx-x[i])

def linefit(x, y, epsilon = 0.001):
    '''
    Attempts to fit a straight line to an appropriate part of the curve 
    specified by x and y.  It steps through the curve specified by 
    vectors x and y searching for a consecutive run of at least 10 
    coordinate pairs to which a straight line can be fit using linear 
    regression with an R^2 (i.e., goodness of fit) value of greater 
    than 1-epsilon.  If there is more than one such run of points, 
    the one with the steepest slope is selected.  A typical value 
    for epsilon is in the range of 5e-4 to 5e-3.  The return values 
    are [first, last, mmax, bmax, Nmax], where

        first is the index of the first point used in the fit,
        last is the index of the last point used in the fit,
        mmax is the slope of the best fit line,
        bmax is the y-axis intercept of the best-fit line, and
        Nmax is the number of points used in the fit.
    '''
    if isinstance(x, vector) and isinstance(y, vector):
        if len(x)==len(y):
            first = 0
            last = 0
            mmax = 0
            bmax = 0
            Nmax = 0
            i = 0
            while i<len(x)-1:
                R2 = 1
                N = 1
                sumX = x[i]
                sumX2 = x[i]*x[i]
                sumY = y[i]
                sumY2 = y[i]*y[i]
                sumXY= x[i]*y[i]
                j = i
                while (j<len(x)-1) and (R2>1-epsilon):
                    j = j+1
                    N = N+1
                    sumX = sumX+x[j]
                    sumX2 = sumX2+x[j]*x[j]
                    sumY = sumY+y[j]
                    sumY2 = sumY2+y[j]*y[j]
                    sumXY = sumXY+x[j]*y[j]
                    SXX = sumX2 - sumX*sumX/N
                    SYY = sumY2 - sumY*sumY/N
                    SXY = sumXY - sumX*sumY/N
                    m = SXY/SXX
                    b = (sumY-m*sumX)/N
                    R2 = SXY*SXY/(SXX*SYY)
                if (N>10) and (abs(m)>abs(mmax)):
                    first = i
                    last = j
                    mmax = m
                    bmax = b
                    Nmax = N
                i = j
            return [first, last, mmax, bmax, Nmax]
        else:
            raise IndexError('vectors supplied to linefit must be of the same length')
    else:
        raise ValueError('x and y arguments supplied to linefit must be vectors')

def diff(x):
    if isinstance(x, vector):
        if len(x)>=2:
            return vector([x[i]-x[i-1] for i in range(1, len(x))])
        else:
            raise IndexError('vector supplied to diff must have at least two elements')
    else:
        raise ValueError('argument supplied to diff must be a vector')

def mean(x):
    if isinstance(x, vector):
        if len(x)>=1:
            return fsum(x)/float(len(x))
        else:
            raise IndexError('vector supplied to mean must have at least one element')
    else:
        raise ValueError('argument supplied to mean must be a vector')

def std(x):
    if isinstance(x, vector):
        if len(x)>=2:
            return sqrt(fsum((x-mean(x))**2)/(float(len(x))-1.))
        else:
            raise IndexError('vector supplied to std must have at least two elements')
    else:
        raise ValueError('argument supplied to std must be a vector')

def ceil(x):
    if isinstance(x, vector):
        return vector([math.ceil(element) for element in x])
    else:
        return math.ceil(float(x))

def fabs(x):
    if isinstance(x, vector):
        return vector([math.fabs(element) for element in x])
    else:
        return math.fabs(float(x))

def floor(x):
    if isinstance(x, vector):
        return vector([math.floor(element) for element in x])
    else:
        return math.floor(float(x))

if sys.version_info>(2, 6):
    def fsum(x):
        if isinstance(x, vector):
            return math.fsum(x.elements)
        else:
            return math.fsum(x)

    def isinf(x):
        if isinstance(x, vector):
            return [math.isinf(element) for element in x]
        else:
            return math.isinf(float(x))

    def isnan(x):
        if isinstance(x, vector):
            return [math.isnan(element) for element in x]
        else:
            return math.isnan(float(x))

def modf(x):
    if isinstance(x, vector):
        values = [math.modf(element) for element in x]
        return [vector([f for (f, i) in values]), vector([i for (f, i) in values])]
    else:
        return math.modf(float(x))

if sys.version_info>(2, 6):
    def trunc(x):
        if isinstance(x, vector):
            return vector([math.trunc(element) for element in x])
        else:
            return math.trunc(float(x))

def exp(x):
    if isinstance(x, vector):
        return vector([math.exp(element) for element in x])
    else:
        return math.exp(float(x))

if sys.version_info>(2, 7):
    def expm1(x):
        if isinstance(x, vector):
            return vector([math.expm1(element) for element in x])
        else:
            return math.expm1(float(x))

def log(x, base = math.e):
    if isinstance(x, vector):
        return vector([math.log(element, base) for element in x])
    else:
        return math.log(float(x), base)

if sys.version_info>(2, 6):
    def log1p(x):
        if isinstance(x, vector):
            return vector([math.log1p(element) for element in x])
        else:
            return math.log1p(float(x))

def log10(x):
    if isinstance(x, vector):
        return vector([math.log10(element) for element in x])
    else:
        return math.log10(float(x))

def sqrt(x):
    if isinstance(x, vector):
        return vector([math.sqrt(element) for element in x])
    else:
        return math.sqrt(float(x))

def acos(x):
    if isinstance(x, vector):
        return vector([math.acos(element) for element in x])
    else:
        return math.acos(float(x))

def asin(x):
    if isinstance(x, vector):
        return vector([math.asin(element) for element in x])
    else:
        return math.asin(float(x))

def atan(x):
    if isinstance(x, vector):
        return vector([math.atan(element) for element in x])
    else:
        return math.atan(float(x))

def atan2(y, x):
    if isinstance(y, vector) and isinstance(x, vector):
        if len(y)==len(x):
            return vector([math.atan2(y.elements[i], x.elements[i]) for i in range(len(y))])
        else:
            raise IndexError('vectors supplied to atan2 must be of the same length')
    elif isinstance(y, vector) and ((type(x) is float) or (type(x) is int) or (type(x) is long) or (type(x) is str)):
        return vector([math.atan2(element, float(x)) for element in y])
    elif isinstance(x, vector) and ((type(y) is float) or (type(y) is int) or (type(y) is long) or (type(y) is str)):
        return vector([math.atan2(float(y), element) for element in x])
    else:
        return math.atan2(float(y), float(x))

def cos(x):
    if isinstance(x, vector):
        return vector([math.cos(element) for element in x])
    else:
        return math.cos(float(x))

def hypot(x, y):
    if isinstance(x, vector) and isinstance(y, vector):
        if len(x)==len(y):
            return vector([math.hypot(x.elements[i], y.elements[i]) for i in range(len(x))])
        else:
            raise IndexError('vectors supplied to hypot must be of the same length')
    elif isinstance(x, vector) and ((type(y) is float) or (type(y) is int) or (type(y) is long) or (type(y) is str)):
        return vector([math.hypot(element, float(y)) for element in x])
    elif isinstance(y, vector) and ((type(x) is float) or (type(x) is int) or (type(x) is long) or (type(x) is str)):
        return vector([math.hypot(float(x), element) for element in y])
    else:
        return math.hypot(float(x), float(y))

def sin(x):
    if isinstance(x, vector):
        return vector([math.sin(element) for element in x])
    else:
        return math.sin(float(x))

def tan(x):
    if isinstance(x, vector):
        return vector([math.tan(element) for element in x])
    else:
        return math.tan(float(x))

def degrees(x):
    if isinstance(x, vector):
        return vector([math.degrees(element) for element in x])
    else:
        return math.degrees(float(x))

def radians(x):
    if isinstance(x, vector):
        return vector([math.radians(element) for element in x])
    else:
        return math.radians(float(x))

if sys.version_info>(2, 6):
    def acosh(x):
        if isinstance(x, vector):
            return vector([math.acosh(element) for element in x])
        else:
            return math.acosh(float(x))

    def asinh(x):
        if isinstance(x, vector):
            return vector([math.asinh(element) for element in x])
        else:
            return math.asinh(float(x))

    def atanh(x):
        if isinstance(x, vector):
            return vector([math.atanh(element) for element in x])
        else:
            return math.atanh(float(x))

def cosh(x):
    if isinstance(x, vector):
        return vector([math.cosh(element) for element in x])
    else:
        return math.cosh(float(x))

def sinh(x):
    if isinstance(x, vector):
        return vector([math.sinh(element) for element in x])
    else:
        return math.sinh(float(x))

def tanh(x):
    if isinstance(x, vector):
        return vector([math.tanh(element) for element in x])
    else:
        return math.tanh(float(x))

if sys.version_info>(2, 7):
    def erf(x):
        if isinstance(x, vector):
            return vector([math.erf(element) for element in x])
        else:
            return math.erf(float(x))

    def erfc(x):
        if isinstance(x, vector):
            return vector([math.erfc(element) for element in x])
        else:
            return math.erfc(float(x))

    def gamma(x):
        if isinstance(x, vector):
            return vector([math.gamma(element) for element in x])
        else:
            return math.gamma(float(x))

    def lgamma(x):
        if isinstance(x, vector):
            return vector([math.lgamma(element) for element in x])
        else:
            return math.lgamma(float(x))

class vector:

    def __init__(self, *args):
        self.multipliers = {'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15, 'E': 1e18, 'Z': 1e21, 'Y': 1e24, 
                            'y': 1e-24, 'z': 1e-21, 'a': 1e-18, 'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3}
        self.elements = []
        for arg in args:
            if (type(arg) is float) or (type(arg) is int) or (type(arg) is long):
                self.elements.append(float(arg))
            elif type(arg) is str:
                if arg[-1] in self.multipliers.keys():
                    self.elements.append(float(arg[0:-1])*self.multipliers[arg[-1]])
                else:
                    self.elements.append(float(arg))
            elif (type(arg) is list) or isinstance(arg, vector):
                for element in arg:
                    if (type(element) is float) or (type(element) is int) or (type(arg) is long):
                        self.elements.append(float(element))
                    elif type(element) is str:
                        if element[-1] in self.multipliers.keys():
                            self.elements.append(float(element[0:-1])*self.multipliers[element[-1]])
                        else:
                            self.elements.append(float(element))

    def __repr__(self):
        return repr(self.elements)

    def __str__(self):
        multipliers = (1., 1e-3, 1e-6, 1e-9, 1e-12, 1e-15, 1e-18, 1e-21, 1e-24, 
                       1e24, 1e21, 1e18, 1e15, 1e12, 1e9, 1e6, 1e3)
        prefixes = ('', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 
                    'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm')
        strings = []
        for element in self.elements:
            if element==0.:
                index = 0
            else:
                index = int(math.floor(math.log10(abs(element))/3.))
            if (index>=-8) and (index<=8):
                strings.append(str(multipliers[index]*element)+prefixes[index])
            else:
                strings.append(str(element))
        return '['+', '.join(strings)+']'

    def __nonzero__(self):
        return [element==0. for element in self.elements].count(False)==0

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, index):
        return self.elements[index]

    def __setitem__(self, index, element):
        if (type(element) is float) or (type(element) is int) or (type(element) is long):
            self.elements[index] = float(element)
        elif type(element) is str:
            if element[-1] in self.multipliers.keys():
                self.elements[index] = float(element[0:-1])*self.multipliers[element[-1]]
            else:
                self.elements[index] = float(element)

    def __delitem__(self, index):
        del(self.elements[index])

    def __contains__(self, element):
        if type(element) is str:
            if element[-1] in self.multipliers.keys():
                return float(element[0:-1])*self.multipliers[element[-1]] in self.elements
        return float(element) in self.elements

    def append(self, element):
        if (type(element) is float) or (type(element) is int) or (type(element) is long):
            self.elements.append(float(element))
        elif type(element) is str:
            if element[-1] in self.multipliers.keys():
                self.elements.append(float(element[0:-1])*self.multipliers[element[-1]])
            else:
                self.elements.append(float(element))

    def extend(self, elements):
        for element in elements:
            if (type(element) is float) or (type(element) is int) or (type(element) is long):
                self.elements.append(float(element))
            elif type(element) is str:
                if element[-1] in self.multipliers.keys():
                    self.elements.append(float(element[0:-1])*self.multipliers[element[-1]])
                else:
                    self.elements.append(float(element))

    def insert(self, index, element):
        if (type(element) is float) or (type(element) is int) or (type(element) is long):
            self.elements.insert(index, float(element))
        elif type(element) is str:
            if element[-1] in self.multipliers.keys():
                self.elements.insert(index, float(element[0:-1])*self.multipliers[element[-1]])
            else:
                self.elements.insert(index, float(element))

    def remove(self, element):
        if (type(element) is float) or (type(element) is int) or (type(element) is long):
            self.elements.remove(float(element))
        elif type(element) is str:
            if element[-1] in self.multipliers.keys():
                self.elements.remove(float(element[0:-1])*self.multipliers[element[-1]])
            else:
                self.elements.remove(float(element))

    def pop(self, index = -1):
        return self.elements.pop(index)

    def index(self, element):
        if type(element) is str:
            if element[-1] in self.multipliers.keys():
                return self.elements.index(float(element[0:-1])*self.multipliers[element[-1]])
        return self.elements.index(float(element))

    def count(self, element):
        if type(element) is str:
            if element[-1] in self.multipliers.keys():
                return self.elements.count(float(element[0:-1])*self.multipliers[element[-1]])
        return self.elements.count(float(element))

    def sort(self):
        self.elements.sort()

    def reverse(self):
        self.elements.reverse()

    def __lt__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return [self.elements[i]<other[i] for i in range(len(self))]
            else:
                raise IndexError('vectors being compared must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return [element<float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements]
        return [element<float(other) for element in self.elements]

    def __le__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return [self.elements[i]<=other[i] for i in range(len(self))]
            else:
                raise IndexError('vectors being compared must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return [element<=float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements]
        return [element<=float(other) for element in self.elements]

    def __eq__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return [self.elements[i]==other[i] for i in range(len(self))]
            else:
                raise IndexError('vectors being compared must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return [element==float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements]
        return [element==float(other) for element in self.elements]

    def __ne__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return [self.elements[i]!=other[i] for i in range(len(self))]
            else:
                raise IndexError('vectors being compared must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return [element!=float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements]
        return [element!=float(other) for element in self.elements]

    def __gt__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return [self.elements[i]>other[i] for i in range(len(self))]
            else:
                raise IndexError('vectors being compared must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return [element>float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements]
        return [element>float(other) for element in self.elements]

    def __ge__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return [self.elements[i]>=other[i] for i in range(len(self))]
            else:
                raise IndexError('vectors being compared must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return [element>=float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements]
        return [element>=float(other) for element in self.elements]

    def __neg__(self):
        return vector([-element for element in self.elements])

    def __pos__(self):
        return vector([+element for element in self.elements])

    def __abs__(self):
        return vector([abs(element) for element in self.elements])

    def __add__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]+other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being added must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element+float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements])
        return vector([element+float(other) for element in self.elements])

    def __sub__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]-other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being subtracted must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element-float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements])
        return vector([element-float(other) for element in self.elements])

    def __mul__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]*other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being multiplied must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element*float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements])
        return vector([element*float(other) for element in self.elements])

    def __div__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]/other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being divided must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element/(float(other[0:-1])*self.multipliers[other[-1]]) for element in self.elements])
        return vector([element/float(other) for element in self.elements])

    def __truediv__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]/other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being divided must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element/(float(other[0:-1])*self.multipliers[other[-1]]) for element in self.elements])
        return vector([element/float(other) for element in self.elements])

    def __floordiv__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]//other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being divided must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element//(float(other[0:-1])*self.multipliers[other[-1]]) for element in self.elements])
        return vector([element//float(other) for element in self.elements])

    def __mod__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]%other[i] for i in range(len(self))])
            else:
                raise IndexError('vectors being modded must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element%(float(other[0:-1])*self.multipliers[other[-1]]) for element in self.elements])
        return vector([element%float(other) for element in self.elements])

    def __pow__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                return vector([self.elements[i]**other[i] for i in range(len(self))])
            else:
                raise IndexError('when one vector is being raised to the powers contained in another, they must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element**(float(other[0:-1])*self.multipliers[other[-1]]) for element in self.elements])
        return vector([element**float(other) for element in self.elements])

    def __radd__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element+float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements])
        return vector([element+float(other) for element in self.elements])

    def __rsub__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([float(other[0:-1])*self.multipliers[other[-1]]-element for element in self.elements])
        return vector([float(other)-element for element in self.elements])

    def __rmul__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([element*float(other[0:-1])*self.multipliers[other[-1]] for element in self.elements])
        return vector([element*float(other) for element in self.elements])

    def __rdiv__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([float(other[0:-1])*self.multipliers[other[-1]]/element for element in self.elements])
        return vector([float(other)/element for element in self.elements])

    def __rtruediv__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([float(other[0:-1])*self.multipliers[other[-1]]/element for element in self.elements])
        return vector([float(other)/element for element in self.elements])

    def __rfloordiv__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([(float(other[0:-1])*self.multipliers[other[-1]])//element for element in self.elements])
        return vector([float(other)//element for element in self.elements])

    def __rmod__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([(float(other[0:-1])*self.multipliers[other[-1]])%element for element in self.elements])
        return vector([float(other)%element for element in self.elements])

    def __rpow__(self, other):
        if type(other) is str:
            if other[-1] in self.multipliers.keys():
                return vector([(float(other[0:-1])*self.multipliers[other[-1]])**element for element in self.elements])
        return vector([float(other)**element for element in self.elements])

    def __iadd__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] += other[i]
                return self
            else:
                raise IndexError('vectors being added must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] += float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] += float(other)
        return self

    def __isub__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] -= other[i]
                return self
            else:
                raise IndexError('vectors being subtracted must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] -= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] -= float(other)
        return self

    def __imul__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] *= other[i]
                return self
            else:
                raise IndexError('vectors being multiplied must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] *= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] *= float(other)
        return self

    def __idiv__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] /= other[i]
                return self
            else:
                raise IndexError('vectors being divided must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] /= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] /= float(other)
        return self

    def __itruediv__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] /= other[i]
                return self
            else:
                raise IndexError('vectors being divided must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] /= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] /= float(other)
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] //= other[i]
                return self
            else:
                raise IndexError('vectors being divided must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] //= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] //= float(other)
        return self

    def __imod__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] %= other[i]
                return self
            else:
                raise IndexError('vectors being modded must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] %= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] %= float(other)
        return self

    def __ipow__(self, other):
        if isinstance(other, vector):
            if len(self)==len(other):
                for i in range(len(self.elements)):
                    self.elements[i] **= other[i]
                return self
            else:
                raise IndexError('when one vector is being raised to the powers contained in another, they must be of the same length')
        elif type(other) is str:
            if other[-1] in self.multipliers.keys():
                for i in range(len(self.elements)):
                    self.elements[i] **= float(other[0:-1])*self.multipliers[other[-1]]
                return self
        for i in range(len(self.elements)):
            self.elements[i] **= float(other)
        return self
