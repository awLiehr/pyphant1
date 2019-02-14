# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
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
"""

import numpy
from pyphant.core import (Worker, Connectors, DataContainer)
import pkg_resources


class EstimateParameter(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant.osc").version
    name = "Estimate Parameter"
    _sockets = [
        ("model", Connectors.TYPE_ARRAY),
        ("experimental", Connectors.TYPE_ARRAY)
        ]
    _params = [
        ("minima_model", "Minima in the model", ["Minima"], None),
        ("maxima_model", "Maxima in the model", ["Maxima"], None),
        (
            "minima_experimental",
            "Minima in the experiment",
            ["Minima"],
            None
            ),
        (
            "maxima_experimental",
            "Maxima in the experiment",
            ["Maxima"],
            None
            ),
        ("extentX", "Extension of x-axis [%%]", 10, None),
        ("extentY", "Extension of y-axis [%%]", 10, None)
        ]

    def refreshParams(self, subscriber=None):
        if self.socketModel.isFull():
            templ = self.socketModel.getResult(subscriber)
            self.paramMinima_model.possibleValues = list(templ.longnames.keys())
            self.paramMaxima_model.possibleValues = list(templ.longnames.keys())
        if self.socketExperimental.isFull():
            templ = self.socketExperimental.getResult(subscriber)
            self.paramMinima_experimental.possibleValues = (
                list(templ.longnames.keys())
                )
            self.paramMaxima_experimental.possibleValues = (
                list(templ.longnames.keys())
                )

    def calculateThickness(
        self, row_minima, row_maxima, minima_model, maxima_model,
        minima_error=None, maxima_error=None
        ):
        """
        Given a vector of minima (row) and a 2 dimensional model,
        this estimates the corresponding parameter.
        """
        if len(row_minima) + len(row_maxima) == 0:
            return numpy.nan

        def calc(row, model, col, error):
            if error:
                weight = 0
                for c, e in zip(row, error):
                    if e > 0:
                        weight += col[
                            numpy.argmin(
                                ((model.dimensions[0].data - c) / e) ** 2
                                )
                            ]
                    else:
                        weight += col[
                            numpy.argmin(
                                (model.dimensions[0].data - c) ** 2
                                )
                            ]
                return weight
            else:
                return sum(
                    [
                        col[numpy.argmin((model.dimensions[0].data - c) ** 2)]
                        for c in row
                        ]
                    )
        minima_data = minima_model.data.transpose()
        maxima_data = maxima_model.data.transpose()
        i = numpy.argmin(
            numpy.array(
                [calc(row_minima, minima_model, minima_col, minima_error) + \
                 calc(row_maxima, maxima_model, maxima_col, maxima_error) \
                     for minima_col, maxima_col in zip(
                                minima_data, maxima_data
                                )
                 ]
                )
            )
        assert minima_model.dimensions[1].data[i] == \
            maxima_model.dimensions[1].data[i]
        return minima_model.dimensions[1].data[i]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def compute(self, model, experimental, subscriber=1):
        minima_model = model[self.paramMinima_model.value]
        maxima_model = model[self.paramMaxima_model.value]
        minima_experimental = experimental[
            self.paramMinima_experimental.value
            ].inUnitsOf(
            minima_model.dimensions[0]
            )
        maxima_experimental = experimental[
            self.paramMaxima_experimental.value
            ].inUnitsOf(
            maxima_model.dimensions[0]
            )
        minima = minima_experimental.data.transpose()
        if minima_experimental.error != None:
            minima_error = iter(minima_experimental.error.transpose())
        else:
            minima_error = None
        maxima = maxima_experimental.data.transpose()
        if maxima_experimental.error != None:
            maxima_error = iter(maxima_experimental.error.transpose())
        else:
            maxima_error = None
        parameter = []
        inc = 100.0 / float(len(minima))
        acc = inc
        subscriber %= acc
        for row_minima, row_maxima in zip(minima, maxima):
            if minima_error:
                filtered_minima_error = [c for c in next(minima_error) if not numpy.isnan(c)]
            else:
                filtered_minima_error = None
            if maxima_error:
                filtered_maxima_error = [c for c in next(maxima_error) if not numpy.isnan(c)]
            else:
                filtered_maxima_error = None
            parameter.append(self.calculateThickness(
                    [c for c in row_minima if not numpy.isnan(c)],
                    [c for c in row_maxima if not numpy.isnan(c)],
                    minima_model,
                    maxima_model,
                    filtered_minima_error,
                    filtered_maxima_error
                    ))
            acc += inc
            subscriber %= acc
        result = DataContainer.FieldContainer(
            numpy.array(parameter),
            longname=minima_model.dimensions[-1].longname,
            shortname=minima_model.dimensions[-1].shortname,
            unit=minima_model.dimensions[-1].unit
            )
        result.seal()
        return result
