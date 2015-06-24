from __future__ import division

import os
import read_and_transform
import tms_geom
import vtk
import numpy as np
from itertools import izip

def __add_sphere_to_ren(ctr, radius, ren):
    import vtk

    p = ctr
    r = radius
    source = vtk.vtkSphereSource()
    source.SetCenter(*p)
    source.SetRadius(r)
    source.SetPhiResolution(20)
    source.SetThetaResolution(20)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    ac = vtk.vtkActor()
    ac.SetMapper(mapper)
    ren.AddActor(ac)
    return ac

def __add_line_to_ren(origin, dest, ren):
    import vtk

    p1 = origin
    p2 = dest
    source = vtk.vtkLineSource()
    source.SetPoint1(p1)
    source.SetPoint2(p2)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    ac = vtk.vtkActor()
    ac.SetMapper(mapper)
    ren.AddActor(ac)
    return ac

def main():
    os.chdir(os.path.dirname(__file__))
    os.chdir("../data")


    test_file = "TMS-597.csv"
    test_file = "TMS-640.csv"
    points = read_and_transform.read_csv_file(test_file)
    points = read_and_transform.normalize_to_ref(points,points[0])
    calib = read_and_transform.extract_calibration_samples(points)

    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    iren.SetRenderWindow(ren_win)
    ren = vtk.vtkRenderer()
    ren_win.AddRenderer(ren)

    colors = [(1,0,0),(0,1,0),(0,1,1),(1,0,1)]
    ot_points = [p.point_pos for p in calib.itervalues()]
    d = calib[1].date
    point_f = read_and_transform.get_pointer_transform_function(d)
    calib_ps = [point_f(p) for p in calib.itervalues()]

    for p1,p2,c in izip(ot_points,calib_ps,colors):
        ac = __add_sphere_to_ren(p1,0.01,ren)
        ac.GetProperty().SetColor(c)
        ac.GetProperty().SetOpacity(0.2)
        ac = __add_sphere_to_ren(p2,0.01,ren)
        ac.GetProperty().SetColor(c)
        ac = __add_line_to_ren(p1,p2,ren)
        ac.GetProperty().SetColor(c)
        #ac.GetProperty().SetRepresentationToWireframe()

    calib_ps2 = [calib_ps[i] for i in [0,2,3]]
    r,ctr = tms_geom.adjust_sphere(calib_ps2)
    print r
    print ctr
    __add_sphere_to_ren(ctr,r,ren)

    coil_fun = read_and_transform.get_coil_transform_function(d)
    coils = read_and_transform.extract_coil_samples(points)
    oops = 0
    for p in coils:
        c,t = coil_fun(p)
        __add_sphere_to_ren(c,0.01,ren)
        l=__add_line_to_ren(c,t,ren)
        l.GetProperty().SetLineWidth(2)
        x = tms_geom.intersect_point_with_sphere(c,t-c,r,ctr)
        if x is None:
            x = tms_geom.intersect_point_with_sphere(c,c-t,r,ctr)
            oops += 1
        if x is not None:
            l2 = __add_line_to_ren(c,x,ren)


    print oops
    iren.Initialize()
    iren.Start()





    iren.Initialize()
    iren.Start()

if __name__ == "__main__":
    main()