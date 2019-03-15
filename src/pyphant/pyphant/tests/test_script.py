# # 2.7
#
# import os
# # print(os.getcwd())
# os.chdir("/Volumes/Imogen's Brain/Pyphant/")
# # print(os.getcwd())

#
# from pyphant.core.LoadFMF import *
#
# # ddd = readDataFile("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/quantities/Solar.fmf")
# ddd = readDataFile("/Volumes/Imogen's Brain/SRS2/data/interim/Auswertung-Exp-Drift copy.fmf")
#
# print('hi')



# 3.7
import numpy
# import pyphant.core.LoadFMF as ff
# import pyphant.core.LoadFMF as ff
import json
import pyphant.Read_FMF.Read_fmf as ff
import pint

single = 1

if single:

    ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/Read_FMF/Solar.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/dep.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/onecolumn.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/onerow.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/onerow_dep.fmf", 1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/onevalue.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/SRS2/data/interim/Auswertung-Exp-Drift.fmf", 1)

    print(json.dumps(eee, indent=1))
    print(ddd)
    print(ddd.dtypes)
else:

    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/Read_FMF/Faraday.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/hash_test.fmf",1)
    # ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/multitable.fmf",1)
    ddd, eee = ff.readFMF("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/tests/resources/fmf/semi_test.fmf", 1)

    # print(ddd.dtypes)
    print(json.dumps(eee, indent = 1))
    for d in ddd:
        print(d)
        print(d.dtypes)
        print('\n\n')


# pint test

print(ddd['voltage']/ddd['current'])