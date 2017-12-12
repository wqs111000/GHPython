import math
import rhinoscriptsyntax as rs 
import ghpythonlib.components as ghc
import Rhino.Geometry as rg
icurvesn=[]
icurvesm=[]
ipointssnm=[]
ipointssmn=[]
curve01=curves[0]
curve12=curves[1]
curve23=curves[2]
curve30=curves[3]
points01 = rs.DivideCurveLength(curve01,length)
points12 = rs.DivideCurveLength(curve12,length)
points23 = rs.DivideCurveLength(curve23,length)
points30 = rs.DivideCurveLength(curve30,length)
m=(len(points12)+len(points30))/2
n=(len(points01)+len(points23))/2


points01 = rs.DivideCurve(curve01,n+1)
points12 = rs.DivideCurve(curve12,m+1)
points23 = rs.DivideCurve(curve23,n+1)
points30 = rs.DivideCurve(curve30,m+1)
m=int(m)
n=int(n)
bpoints=points01+points12+points23+points30
for i in range(n): 
    icurve=rs.ShortPath(surface, points01[i+1], points23[-(i+2)])
    icurvesn.append(icurve)
count=0
while (count<loop):
    icurvesm=[]
    ipointssnm=[]
    for icurve in icurvesn: 
        ipoints = rs.DivideCurve(icurve,m+1)
        ipointssnm.append(ipoints)
#    global surfObj 
    surfObj= rs.coercerhinoobject(surface).Geometry
    print surfObj
    for i in range(m):
        ps=[]
        puvs=[]
        p=points30[-(i+1)-1]
        puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
        puvs.append(puv)
        for j in range(n):
            #转换数据类型
            p=ipointssnm[j][i+1]
            puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
            ps.append(p)
            puvs.append(puv)
        p=points12[i+1]
        puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
        puvs.append(puv)
        print (count)
        print (puvs[2])
        crv=ghc.CurveOnSurface(surfObj,puvs,False)[0]
        icurvesm.append(crv)
        #print (crv)
    #print surfObj
    count=count+1
    if(count>=loop):
        print ('aaaaaaaaaaaaaaaaaaaaaaaaaaa')
        break
    icurvesn=[]
    ipointssmn=[]
    for icurve in icurvesm: 
        ipoints = rs.DivideCurve(icurve,n+1)
        ipointssmn.append(ipoints)
    global surfObj 
    surfObj= rs.coercerhinoobject(surface).Geometry
    print surfObj
    for i in range(n):
        ps=[]
        puvs=[]
        p=points01[(i+1)]
        puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
        puvs.append(puv)
        for j in range(m):
            #转换数据类型
            p=ipointssmn[j][i+1]
            puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
            ps.append(p)
            puvs.append(puv)
        p=points23[-(i+1)-1]
        puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
        puvs.append(puv)
        crv=ghc.CurveOnSurface(surfObj,puvs,False)[0]
        icurvesn.append(crv)
    count=count+1
    if(count>=50):
        break
        

ipointss0=[]
ipointss1=[]
for icurve in icurvesn: 
    ipoints = rs.DivideCurve(icurve,m+1)
    ipointss0=ipointss0+ipoints
ipointss0=ipointss0+points12+points30
for icurve in icurvesm: 
    ipoints = rs.DivideCurve(icurve,n+1)
    ipointss1=ipointss1+ipoints
ipointss1=ipointss1+points01+points23



#以下代码无用
#icurvesn=tweenCurveOnsurface(n,m,icurvesm,points01,points23)
def tweenCurveOnsurface(m,n,icurves,points0,points1):
    print {'def'}
    print {m}
    for icurve in icurves:
        ipoints = rs.DivideCurve(icurve,m+1)
        ipointssnm.append(ipoints)
    for i in range(m):
        icurvesNew=[]
        ps=[]
        puvs=[]
        p=points1[(i+1)]
        puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
        puvs.append(puv)
        for j in range(n):
            #转换数据类型
            p=ipointssnm[j][i+1]
            puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
            ps.append(p)
            puvs.append(puv)
        p=points0[i+1]
        puv=ghc.SurfaceClosestPoint(p,surfObj)[1]
        puvs.append(puv)
        crv=ghc.CurveOnSurface(surfObj,puvs,False)[0]
        icurvesNew.append(crv)
        print (crv)
    return icurvesNew
