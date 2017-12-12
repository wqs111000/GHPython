import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import Rhino.Geometry as rg
torrent=0.001
newCurves=[]
newCurves.append(curves[0])
crvs=curves[:]
del crvs[0]
startP0=rs.CurveStartPoint(newCurves[-1])
for i in range(len(curves)-1):
    endP0=rs.CurveEndPoint(newCurves[-1])
    if (rs.Distance(startP0,endP0)<torrent):
        break
    flag=False
    print len(crvs)
    for crv in crvs:
        sp=rs.CurveStartPoint(crv)
        ep=rs.CurveEndPoint(crv)
        if (rs.Distance(sp,endP0)<torrent):
            flag=True
            print (crv)
            crvs.remove(crv)
            break
        if (rs.Distance(ep,endP0)<torrent):
            crvObj= rs.coercerhinoobject(crv).Geometry
            crvs.remove(crv)
            crv=gh.FlipCurve(crvObj)[0]
            print ('fanle')
            flag=True
            break
    if not flag:
        print ('wrong')
        break
    newCurves.append(crv)
    print crv
print (len(newCurves))