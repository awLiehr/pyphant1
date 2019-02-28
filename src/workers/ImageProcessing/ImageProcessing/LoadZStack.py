# -*- coding: utf-8 -*-

# Copyright (c) 2006-2011, Rectorate of the University of Freiburg
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

"""
The Load ZStack worker is a class of Pyphant's Image Processing
Toolbox. It simply loads a set of images from the location given in the
worker's configuration as a 3d image.
"""

from pyphant.core.Connectors import (SUBTYPE_FILE, TYPE_IMAGE)
from pyphant.core import Worker
from pyphant.core.Helpers import parseFCUnit
import pkg_resources


class LoadZStack(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Load ZStack"
    _params = [
        ("path", "Path (select any file)", "", SUBTYPE_FILE),
        ("regex", "File Filter Regex", r'(?i)^.+\.tif$', None),
        ("fieldUnit", "Unit of the field", "1", None),
        ("dz", "z increment", '1 mum', None),
        ("dy", "y increment", '1 mum', None),
        ("dx", "x increment", '1 mum', None),
        ("startz", "z start", '0 mum', None),
        ("starty", "y start", '0 mum', None),
        ("startx", "x start", '0 mum', None),
        ("zClip", "Clipping of z-axis (pixels)", ':', None),
        ("yClip", "Clipping of y-axis (pixels)", ':', None),
        ("xClip", "Clipping of x-axis (pixels)", ':', None),
        ("dtype", "data type", 'uint8', None),
        ("longname", "Longname", 'ZStack', None),
        ("shortname", "Shortname", 'I', None)
        ]

    @Worker.plug(TYPE_IMAGE)
    def loadImageAsGreyScale(self, subscriber=0):
        import os
        import re
        from scipy.misc import imread
        import numpy
        from pyphant.core.DataContainer import FieldContainer
        path = os.path.realpath(self.paramPath.value)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        pattern = re.compile(self.paramRegex.value)
        filenames = [x for x in os.listdir(path) if pattern.match(x) is not None]
        filenames.sort()
        filenames = [os.path.join(path, fname) for fname in filenames]
        print(path)
        zClip = self.getClip(self.paramZClip.value)
        filenames = filenames[zClip[0]:zClip[1]]
        assert len(filenames) >= 1
        yClip = self.getClip(self.paramYClip.value)
        xClip = self.getClip(self.paramXClip.value)
        dtype = self.paramDtype.value
        data = []
        for i, fn in enumerate(filenames):
            subscriber %= 1 + 99 * i / len(filenames)
            data.append(imread(fn, True)[yClip[0]:yClip[1], xClip[0]:xClip[1]])
        data = numpy.array(data, dtype=dtype)
        axes = ['z', 'y', 'x']
        dimensions = [
            self.getDimension(a, data.shape[i]) for i, a in enumerate(axes)
            ]
        unit = parseFCUnit(self.paramFieldUnit.value)
        longname = self.paramLongname.value
        shortname = self.paramShortname.value
        image = FieldContainer(
            data=data, dimensions=dimensions, unit=unit,
            longname=longname, shortname=shortname,
            attributes={'yFactor': parseFCUnit(self.paramDy.value),
                        'xFactor': parseFCUnit(self.paramDx.value)}
            )
        image.seal()
        subscriber %= 100
        return image

    def getClip(self, clipStr):
        split = clipStr.split(':')
        assert len(split) == 2
        return [int(x) if len(x) else None for x in split]

    def getDimension(self, axis, length):
        from pyphant.quantities import Quantity
        from pyphant.core.DataContainer import FieldContainer
        import numpy
        delta = parseFCUnit(self.getParam('d' + axis).value)
        start = parseFCUnit(self.getParam('start' + axis).value)

        if isinstance(delta, Quantity):
            unit = Quantity(1.0, delta.unit)
            start = start.inUnitsOf(delta.unit).value
            delta = delta.value
        else:
            unit = 1
        data = start + numpy.arange(0, length, dtype=float) * delta
        dim = FieldContainer(
            data, unit=unit,
            shortname=axis,
            longname='%s-Axis' % (axis.upper(), )
            )
        return dim
