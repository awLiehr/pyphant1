#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2014, Rectorate of the University of Freiburg
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


"""script for running all unit tests from pyphant and the toolboxes"""

from pyphant.mplbackend import ensure_mpl_backend
ensure_mpl_backend('agg')
import os
import os.path
import sys
import unittest

suites = []
for root, dirs, files in os.walk("."):
    for ignore in ('.git', 'dist', 'build', '__pycache__'):
        if ignore in dirs:
            dirs.remove(ignore)

    files = filter(lambda f: f.startswith('Test') and f.endswith('.py'), files)

    if len(files) > 0:
        sys.path.append(root)
        for f in files:
            mod = f[:-3]
            exec 'import ' + mod
            mod = sys.modules[mod]
            suites.append(unittest.TestLoader().loadTestsFromModule(mod))


suite = unittest.TestSuite(suites)

unittest.TextTestRunner().run(suite)
