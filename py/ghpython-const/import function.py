import math
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Rhino.Geometry as rg
import sys
file='H:/3rd year/mesh generation based on rhino and grasshopper/python/py'
#在file目录下有一个名为Hello.py的文件
sys.path.append(file)
import Hello2 as hi
hi.Hello()
reload(hi) #重新导入
hi.Hello()