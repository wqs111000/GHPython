# 用拟合分段的方法生成点阵或者网格等
"""Create grid points.
  Inputs:
    surface: 曲面，单重曲面或者网格面. (surface or mesh)
    curves：边界线。通常是4条曲线，
                特殊地，环形曲面可以是2条，会自动以测地线生成另两条()
    bSortCurves:是否对输入的4条边界线进行自动排序、翻转,
                    一当存在闭合边界线，不要自动排序，输入的边界线应排好序的边界。(bool)
    bLength: 是否以给定的长度和网格样式自动确定m和n. (bool)
    desired length:期望的杆长.(float)
    m:主方向插值曲线数(int)
    n:次方向插值曲线数，也是环形曲面的径向曲线数(int)
    sm:主方向加密倍数，一般就取1吧(int)
    sn:次方向加密倍数，一般就取1吧(int)
    bRatio:是否按相对边界的长度按比例调控内部插值曲线间距(bool)
    bAdaptive:是否开启网格的全局自适应(bool)
    loop:循环次数，(int)
    bFlip:是否翻转第3条边界线，仅针对环形曲面时考虑(bool)
    bSquare:网格样式，True为方形，False为三角形，
            实质是控制主次方向的间距比为1，还是根号3
    bRun:是否运行主程序。(bool)
  Outputs:
    surface:
    curve01:
    curve12:
    curve23:
    curve30:
    icurvesm：主方向插值曲线
    icurvesn：次方向插值曲线
    pointss：点阵[m+2][n+2]
    pointss2：点阵[m+2][n+3],环形曲面，有一列重合[m+2][1]=[m+2][n+3] [list of Point]
    row：即点阵的行数，即m+2
    bRingRow：是否环形曲面
    m：主方向插值曲线数(int)
    n: 次方向插值曲线数(int)
"""
import math
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Rhino.Geometry as rg


# import sys
# file='H:/4rd year/mesh generation based on rhino and grasshopper/python/py'
# sys.path.append(file)
# import GeodesicCurve
# icurve=GeodesicCurve_new.GeodesicCurve(surface,[points01[i+1], points23[-(i+2)]])

def surfaceToMesh(surfaces):
    meshes = []
    for s in surfaces:
        print s
        surfObj = rs.coercerhinoobject(s).Geometry
        m = ghc.MeshBrep(surfObj)
        meshes.append(m)
    mesh = ghc.MeshJoin(meshes)
    return mesh


def CurveLengthPoint(curve, length, torrent=0.01):
    L = rs.CurveLength(curve)
    curveStartPoint = rs.CurveStartPoint(curve)
    curveEndPoint = rs.CurveEndPoint(curve)
    domain = rs.CurveDomain(curve)
    uS = domain[0]
    # print "domain",domain
    u0, u1 = domain[0], domain[1]
    for i in range(1000):
        u = u0 + (u1 - u0) * length / L
        p = rs.EvaluateCurve(curve, u)
        length1 = rs.CurveLength(curve, -1, [uS, u])
        # print "(length1-length)",(length1-length)
        if abs(length1 - length) < torrent:
            break
        elif length1 - length < 0:
            u0 = u
        elif length1 - length > 0:
            u1 = u
    else:
        print "超出循环次数"
        # print u0,u1,u
    p = rs.EvaluateCurve(curve, u)
    return p


def DivideCurveByLengths(curve, lengths):
    # 根据各分段点到起点的长度，含起始点，确定分段点
    points = []
    # print lengths
    for leng in lengths:
        p = CurveLengthPoint(curve, leng)
        points.append(p)
    if rs.IsCurveClosed(curve):
        points = points[:-1]
    return points


def DivideCurveByNumberAndRatio(curve, n, ratio):
    # 根据分段数和比例分段，弧长，含端点
    if ratio == 1:
        return rs.DivideCurve(curve, n)
    n = int(n)
    points = []
    L = rs.CurveLength(curve)
    curveStartPoint = rs.CurveStartPoint(curve)
    curveEndPoint = rs.CurveEndPoint(curve)
    lengths = []
    length0 = L * (1 - ratio) / (1 - ratio ** n)
    # print "length0,ratio",length0,ratio
    lengths = list((length0 * (1 - ratio ** (i)) / (1 - ratio)) for i in range(n + 1))
    return DivideCurveByLengths(curve, lengths)


def DivideCurveByRelativeLengths(curve, relativeLengths, torrent=0.01):
    # 根据点阵的长度相对位置划分曲线,就先以弧长为长度准则，含端点
    L = rs.CurveLength(curve)
    lengths = []
    length = 0
    lengths.append(length)
    for r in relativeLengths:
        length += L * r
        lengths.append(length)
    # print lengths
    if (abs(length - L) > torrent):
        print "erro:根据点阵的长度相对位置划分曲线"
    return DivideCurveByLengths(curve, lengths)


def SortCurves(curves, torrent=0.001):
    """将多条曲线组成的闭合环线,按照首尾相连的顺序重新排列

    """
    newCurves = []
    newCurves.append(curves[0])
    crvs = curves[:]
    del crvs[0]
    startP0 = rs.CurveStartPoint(newCurves[-1])
    for i in range(len(curves) - 1):
        endP0 = rs.CurveEndPoint(newCurves[-1])
        # if (rs.Distance(startP0,endP0)<torrent):
        #    break
        flag = False
        for crv in crvs:
            sp = rs.CurveStartPoint(crv)
            ep = rs.CurveEndPoint(crv)
            if (rs.Distance(sp, endP0) < torrent):
                flag = True
                crvs.remove(crv)
                break
            if (rs.Distance(ep, endP0) < torrent):
                crvObj = rs.coercerhinoobject(crv).Geometry
                crvs.remove(crv)
                crv = ghc.FlipCurve(crvObj)[0]
                print ('flip')
                flag = True
                break
        if not flag:
            print ('erro:出现孤立的线')
            return None
        newCurves.append(crv)
    return newCurves


def InterporateCurves(surface, curves, m, n, loop, bAdaptive, bRatio, bRing=False):
    """在两个方向上分别生成m,n条生成插值曲线"""
    bEdgeBePoint = False
    m = int(m)
    n = int(n)
    icurvesn = []
    icurvesm = []
    ipointssnm = []
    ipointssmn = []
    if len(curves) == 4:
        curve01 = curves[0]
        curve12 = curves[1]
        curve23 = curves[2]
        curve30 = curves[3]
    if len(curves) == 3:
        curve01 = curves[0]
        curve12 = curves[1]
        curve23 = rs.CurveEndPoint(curves[1])
        curve30 = curves[2]
    rm = 1
    rn = 1
    # print len(curves)
    if bRatio:
        rm = (rs.CurveLength(curve23) / rs.CurveLength(curve01)) ** (1 / (m))
        # rn=1
        rn = (rs.CurveLength(curve30) / rs.CurveLength(curve12)) ** (1 / (n))
    points01 = DivideCurveByNumberAndRatio(curve01, n + 1, 1 / rn)
    points12 = DivideCurveByNumberAndRatio(curve12, m + 1, rm)
    if len(curves) == 4:
        points23 = DivideCurveByNumberAndRatio(curve23, n + 1, rn)
        global points000
        points000 = points23[:]
    if len(curves) == 3:
        points23 = [curve23] * (n + 2)
    points30 = DivideCurveByNumberAndRatio(curve30, m + 1, 1 / rm)

    # print "points01",points01
    # print "points23",points23


    # if bRing:
    #   points23=ghc.ShiftList(points23,1,True)


    #   if rs.IsCurveClosed(curve23)and rs.IsCurveClosed(curve30):
    #       points30=ghc.ShiftList(points30,1,True)
    bpoints = points01 + points12 + points23 + points30

    if bRing:
        points23 = ghc.ShiftList(points23, 1, True)
    for i in range(n):
        if (rs.IsSurface(surface)):
            icurve = rs.ShortPath(surface, points01[i + 1], points23[::-1][i + 1])
        else:
            icurve = rs.AddLine(points01[i + 1], points23[::-1][i + 1])
        icurvesn.append(icurve)
    count = 0
    ipointss = []
    while (count < loop):  # 完整的一次循环，count=+2
        ipointssnm = []
        ipointssnm = []
        relativeLengths = []
        if (bAdaptive and count != 0):
            curvesm = icurvesm[:]
            curvesm.insert(0, curve01)
            curvesm.append(curve23)
            sumMidLength = 0
            midLengths = []
            for ii in range(m + 1):
                midLength = (rs.CurveLength(curvesm[ii]) + rs.CurveLength(curvesm[ii + 1])) * 0.5
                midLengths.append(midLength)
                sumMidLength += midLength
            relativeLengths = [midLength / sumMidLength for midLength in midLengths]
            points12 = DivideCurveByRelativeLengths(curve12, relativeLengths)
            points30 = DivideCurveByRelativeLengths(curve30, list(reversed(relativeLengths)))
        for icurve in icurvesn:
            if (bAdaptive and count != 0):
                # print "relativeLengths1",relativeLengths
                ipoints = DivideCurveByRelativeLengths(icurve, relativeLengths)

            else:
                ipoints = DivideCurveByNumberAndRatio(icurve, m + 1, rm)
            ipointssnm.append(ipoints)
            #    global surfObj
        surfObj = rs.coercerhinoobject(surface).Geometry
        # print surfObj
        icurvesm = []
        for i in range(m):
            if (rs.IsSurface(surface)):
                puvs = []
                p = points30[-(i + 1) - 1]
                puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                puvs.append(puv)
                for j in range(n):
                    # 转换数据类型
                    p = ipointssnm[j][i + 1]
                    puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                    puvs.append(puv)
                if not bRing:
                    p = points12[i + 1]
                    puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                    puvs.append(puv)
                # print (count)
                # print (puvs[2])
                crv = ghc.CurveOnSurface(surfObj, puvs, bRing)[0]
                icurvesm.append(crv)
            else:
                ps = []
                p = points30[-(i + 1) - 1]
                ps.append(p)
                for j in range(n):
                    # 转换数据类型
                    p = ipointssnm[j][i + 1]
                    pm = rs.MeshClosestPoint(surface, p)[0]
                    ps.append(pm)
                # points12和points03的节点位置可能不完全重合，曲线的朝向影响了分段结果
                if not bRing:
                    p = points12[i + 1]
                else:
                    p = points30[-(i + 1) - 1]
                ps.append(p)
                crv = rs.AddPolyline(ps)
                # print rs.IsCurveClosed(crv)
                icurvesm.append(crv)
        count = count + 1
        points03 = list(reversed(points30))
        ipointss = ipointssnm
        ipointss.insert(0, points03)
        if not bRing:
            ipointss.append(points12)
        if (count >= loop):
            print ('循环正常结束')
            break
        ipointssmn = []
        relativeLengths = []
        if (bAdaptive and count != 0):
            curvesn = icurvesn[:]
            curvesn.insert(0, curve30)
            curvesn.append(curve12)
            sumMidLength = 0
            midLengths = []
            for ii in range(n + 1):
                midLength = (rs.CurveLength(curvesn[ii]) + rs.CurveLength(curvesn[ii + 1])) * 0.5
                midLengths.append(midLength)
                sumMidLength += midLength
            # print "midLengths",midLengths
            relativeLengths = [midLength / sumMidLength for midLength in midLengths]
            points01 = DivideCurveByRelativeLengths(curve01, relativeLengths)
            points23 = DivideCurveByRelativeLengths(curve23, list(reversed(relativeLengths)))
            if rs.IsCurveClosed(curve23):
                points23 = ghc.ShiftList(points23, 1, True)
        for icurve in icurvesm:
            if (bAdaptive and count != 0):
                # print "relativeLengths2",relativeLengths
                ipoints = DivideCurveByRelativeLengths(icurve, relativeLengths)
            else:
                ipoints = DivideCurveByNumberAndRatio(icurve, n + 1, 1 / rn)
                # print n+1,1/rn,rs.IsCurveClosed(icurve)
                # print "ipoints",len(ipoints)
            ipointssmn.append(ipoints)
        icurvesn = []
        # global surfObj
        surfObj = rs.coercerhinoobject(surface).Geometry
        # print surfObj
        for i in range(n):
            if (rs.IsSurface(surface)):
                ps = []
                puvs = []
                p = points01[(i + 1)]
                ps.append(p)
                puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                puvs.append(puv)
                for j in range(m):
                    # 转换数据类型
                    p = ipointssmn[j][i + 1]
                    puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                    puvs.append(puv)
                p = points23[-(i + 1) - 1]
                ps.append(p)
                puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                puvs.append(puv)
                crv = ghc.CurveOnSurface(surfObj, puvs, False)[0]
                crvm = rs.AddPolyline(ps)
                icurvesn.append(crv)
            else:
                ps = []
                p = points01[(i + 1)]
                ps.append(p)
                for j in range(m):
                    # 转换数据类型
                    p = ipointssmn[j][i + 1]
                    pm = rs.MeshClosestPoint(surface, p)[0]
                    ps.append(pm)
                p = points23[-(i + 1) - 1]
                ps.append(p)
                crv = rs.AddPolyline(ps)
                icurvesn.append(crv)
        count = count + 1
        ipointss = ipointssmn
        points32 = list(reversed(points23))
        ipointss.insert(0, points01)
        ipointss.append(points32)
        # print count,len(ipointss[0]),len(ipointss[1]),len(ipointss[2]),len(ipointss[3])
        if (count >= 100):
            break
    # print "ipointss",ipointss
    return icurvesm, icurvesn, ipointss


def ConnectPointss(surface, pointss, diagonalDirection, bRing, step):
    # print "bRing",bRing
    # 01
    if (rs.IsSurface(surface)):
        curves = []
        polylines = []
        step = int(step)
        # 11
        if not bRing:
            if diagonalDirection == 1:
                for i in range(len(pointss) - 1):
                    i = len(pointss) - i - 2
                    puvs = []
                    pls = []
                    surfObj = rs.coercerhinoobject(surface).Geometry
                    for j in range(len(pointss[0])):
                        if i + j >= len(pointss):
                            break
                        p = pointss[(i + j)][j]
                        pls.append(p)
                        puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                        puvs.append(puv)
                    crv = ghc.CurveOnSurface(surfObj, puvs, False)[0]
                    curves.append(crv)
                    polyline = rs.AddPolyline(pls)
                    polylines.append(polyline)
                for i in range(len(pointss[0]) - 1):
                    i = i + 1
                    puvs = []
                    pls = []
                    surfObj = rs.coercerhinoobject(surface).Geometry
                    for j in range(len(pointss)):
                        if i + j >= len(pointss[0]):
                            break
                        p = pointss[j][(i + j)]
                        pls.append(p)
                        puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                        puvs.append(puv)
                    crv = ghc.CurveOnSurface(surfObj, puvs, False)[0]
                    curves.append(crv)
                    polyline = rs.AddPolyline(pls)
                    polylines.append(polyline)
            if diagonalDirection == -1:
                for i in range(len(pointss) - 1):
                    i = len(pointss) - i - 2
                    puvs = []
                    pls = []
                    surfObj = rs.coercerhinoobject(surface).Geometry
                    for j in range(len(pointss[0])):
                        if i + j >= len(pointss):
                            break
                        p = pointss[(i + j)][len(pointss[0]) - j - 1]
                        pls.append(p)
                        puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                        puvs.append(puv)
                    crv = ghc.CurveOnSurface(surfObj, puvs, False)[0]
                    curves.append(crv)
                    polyline = rs.AddPolyline(pls)
                    polylines.append(polyline)
                for i in range(len(pointss[0]) - 1):
                    i = i + 1
                    puvs = []
                    pls = []
                    surfObj = rs.coercerhinoobject(surface).Geometry
                    for j in range(len(pointss)):
                        if i + j >= len(pointss[0]):
                            break
                        p = pointss[j][len(pointss[0]) - (i + j) - 1]
                        pls.append(p)
                        puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                        puvs.append(puv)
                    crv = ghc.CurveOnSurface(surfObj, puvs, False)[0]
                    curves.append(crv)
                    polyline = rs.AddPolyline(pls)
                    polylines.append(polyline)
            if diagonalDirection == 0:
                polylines = [rs.AddPolyline(pls) for pls in pointss]
        # 11 成环
        else:
            # print len(pointss)
            for i in range(int(len(pointss) / step)):
                puvs = []
                surfObj = rs.coercerhinoobject(surface).Geometry
                pls = []
                for j in range(len(pointss[0])):
                    # print  (i*step+j*diagonalDirection)%len(pointss)
                    p = pointss[(i * step + j * diagonalDirection) % len(pointss)][j]
                    puv = ghc.SurfaceClosestPoint(p, surfObj)[1]
                    puvs.append(puv)
                    pls.append(p)
                crv = ghc.CurveOnSurface(surfObj, puvs, False)[0]
                curves.append(crv)
                polyline = rs.AddPolyline(pls)
                polylines.append(polyline)
    return curves


# 主函数开始
if bRun:
    """
    if len(surface)!=1:
        surface=surfaceToMesh(surface)
        print surface,type(surface)
    """
    sortedCurves = []
    bRing = False
    if bSquare:
        length01 = length
        length12 = length
    else:
        length01 = length / 2
        length12 = length * 3 ** 0.5 / 2
    if len(curves) == 2:  # 仅适用于单重曲面
        addedCurves = []
        if bFlip:
            rs.ReverseCurve(curves[1])
        curve12 = rs.ShortPath(surface, rs.CurveEndPoint(curves[0]), rs.CurveStartPoint(curves[1]))
        curve30 = rs.ShortPath(surface, rs.CurveEndPoint(curves[1]), rs.CurveStartPoint(curves[0]))
        sortedCurves = [curves[0], curve12, curves[1], curve30]
    if len(curves) == 4 or len(curves) == 3:
        if bSortCurves:
            sortedCurves = SortCurves(curves)
        else:
            sortedCurves = curves
    if bLength and length:
        m = round((rs.CurveLength(sortedCurves[1]) + rs.CurveLength(sortedCurves[3])) / length12 / 2) - 1
        n = round((rs.CurveLength(sortedCurves[0]) + rs.CurveLength(sortedCurves[2])) / length01 / 2) - 1
    nn = n
    if rs.IsCurveClosed(curves[0]) and rs.IsCurveClosed(curves[2]):
        bRing = True
        nn = n - 1
    # print "m,n",m,nn
    icurvesm0, icurvesn0, ipointsssmsn = InterporateCurves(surface, sortedCurves, sm * m + sm - 1, sn * nn + sn - 1,
                                                           loop, bAdaptive, bRatio, bRing)
    icurvesm = [c for i, c in enumerate(icurvesm0) if i % sm == sm - 1]
    icurvesn = [c for i, c in enumerate(icurvesn0) if i % sn == sn - 1]
    # print len(ipointsssmsn),len(ipointsssmsn[6])
    if loop % 2 == 1:
        ipointsssmsn = map(list, zip(*ipointsssmsn))  # len(ipointsssmsn) = m+2
    ipointssmn = [[p for i, p in enumerate(ps) if i % sm == 0] for j, ps in enumerate(ipointsssmsn) if j % sn == 0]
    row = len(ipointssmn)
    bRingRow = bRing
    pointss = []
    for ps in ipointssmn:
        pointss += ps
    if len(curves) == 4:
        curve01 = sortedCurves[0]
        curve12 = sortedCurves[1]
        curve23 = sortedCurves[2]
        curve30 = sortedCurves[3]
    if len(curves) == 3:
        curve01 = sortedCurves[0]
        curve12 = sortedCurves[1]
        curve23 = rs.CurveEndPoint(curves[1])
        curve30 = sortedCurves[2]
    if (rs.IsSurface(surface)):
        if bRing:
            icurvesn.append(curve12)
        icurves45 = ConnectPointss(surface, map(list, zip(*ipointssmn)), 1, bRing, step)
        icurves135 = ConnectPointss(surface, map(list, zip(*ipointssmn)), -1, bRing, step)

    if bRing:
        ipointssnm2 = map(list, zip(*ipointssmn))
        ipointssnm2.append(ipointssnm2[0])
        ipointssmn2 = map(list, zip(*ipointssnm2))
        pointss2 = []
        for ps in ipointssmn2:
            pointss2 += ps
