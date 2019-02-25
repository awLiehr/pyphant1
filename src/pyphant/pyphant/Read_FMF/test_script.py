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
import src.pyphant.pyphant.core.LoadFMF as ff
# import pyphant.core.LoadFMF as ff

ddd = ff.readDataFile("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/quantities/Solar.fmf")
ddd = ff.readDataFile("/Volumes/Imogen's Brain/Pyphant/src/pyphant/pyphant/quantities/Faraday.fmf")
ddd = ff.readDataFile("/Volumes/Imogen's Brain/SRS2/data/interim/Auswertung-Exp-Drift.fmf")
print (ddd)