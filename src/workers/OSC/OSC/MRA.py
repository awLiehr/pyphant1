# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

import scipy.interpolate
from Scientific.Physics import PhysicalQuantities
import logging, copy, math

from scipy.special import ive
from scipy.signal import convolve

class MRA(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Multi Resolution Analyser"

    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = [("scale", u"Scale", "50 nm", None)]

    def convolve(self, field, sigma):
        if sigma==0:
            return field.data
        n = int(len(field.dimensions[-1].data)/2)
        kernel = ive(numpy.arange(-n, n), sigma)
        return convolve(field.data, kernel, mode='same')
        
    def findMinima(self, fieldData, lastExtrema=None):
        minima_c = numpy.logical_and(fieldData[:-2] > fieldData[1:-1],
                                   fieldData[2:]  > fieldData[1:-1])
        minima = minima_c.nonzero()[0]
        if lastExtrema==None or len(lastExtrema)==len(minima):
            return minima
        trackedMinima = []
        for lastMinimum in lastExtrema:
            distance = (minima-lastMinimum)**2
            trackedMinima.append(distance.argmin())
        return minima[trackedMinima]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def mra(self, field, subscriber=0):
        dim = field.dimensions[-1]
        try:
            scale = PhysicalQuantities.PhysicalQuantity(self.paramScale.value)
        except:
            scale = float(self.paramScale.value)
        d = scipy.diff(dim.data)
        assert numpy.allclose(d.min(), d.max())
        n = scale/(d[0]*dim.unit)
        mrr = [self.convolve(field, sigma) for sigma in
               numpy.linspace(1, n,10).tolist()]
        mrr.insert(0,field.data)
        firstMinima = lastMinima = self.findMinima(mrr[-1], None)
        for row in reversed(mrr[:-1]):
            lastMinima = self.findMinima(row, lastMinima)
        pos = dim.data[numpy.array(lastMinima)+1]
        error = numpy.abs(pos - dim.data[numpy.array(firstMinima)+1])
        roots = DataContainer.FieldContainer(pos,
                                             error = error,
                                             unit = dim.unit,
                                             longname="%s of the local %s of %s" % (dim.longname,"minima",field.longname),
                                             shortname="%s_0" % dim.shortname)
        roots.seal()
        return mrr, roots

def main():
    import pylab
    mra = MRA()
    N=200
    x = numpy.linspace(-2, 2, N)
    y = x**4-3*x**2+x
    z = y + scipy.random.randn(N)*0.5
    data = DataContainer.FieldContainer(z, dimensions=[DataContainer.FieldContainer(x, unit='1m')])
    mra.paramScale.value = "1.0m"
    mrr, roots = mra.mra(data)
    pylab.plot(x, mrr[-1])
    for c in mrr:
        pylab.plot(x, c)
        pylab.plot(x, y)
        pylab.plot(x, z)
    mrr.append(y)
    pylab.vlines(roots.data, -4, 4)
    pylab.vlines(roots.data+roots.error, -4, 4, linestyle='dashed')
    pylab.vlines(roots.data-roots.error, -4, 4, linestyle='dashed')
    pylab.show()

if __name__ == '__main__':
    main()
