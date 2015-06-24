"""
Contains commands useful for the calibration process
"""
from __future__ import division
from tms import quat

__author__ = 'Diego'

if __name__ == "__main__":
    import sys

    print "This script is not mean't to be run, it should be used interactively"
    sys.exit(0)

from tms.calibration_data import CALIB_SAMPLES, CALIB_RESULTS
import vtk
import numpy as np
from collections import namedtuple
import tms_utils

def read_csv_file(file_path):
    """
    Reads a csv file
    :param file_path: path to the csv file
    :return: A list of points with ref
    """
    with open(file_path) as input_file:
        points = [tms_utils.PointWithRef(l.split(";")) for l in input_file]
    return points


#0) Go to the directory containing the calibration samples
# os.chdir(SAMPLES DIR)

#1)  Load the samples
def load_pointer_samples(date):
    """get the list of pointer samples for an specific date"""
    #get sample indexes
    samples = CALIB_SAMPLES[date].Pointer
    return samples


def load_coil_samples(date):
    """get the list of pointer samples for an specific date"""
    #get sample indexes
    samples = CALIB_SAMPLES[date].Coil
    return samples




def get_pointer_point_function(date):
    """Get the appropriate pointer function for the given date"""
    v = CALIB_RESULTS[date].Pointer_v
    f = get_point_function(v)
    return f

PointerSample = namedtuple("PointerSample", ["pos", "orn"])


def transform_sample_no_ref(point):
    assert isinstance(point, tms_utils.PointWithRef)
    o = point.point_or
    x, y, z = point.point_pos
    p2 = np.array((x, y, z))
    return PointerSample(p2, quat.Quaternion(o))


def get_sphere_actor(x, y, z):
    source = vtk.vtkSphereSource()
    source.SetCenter(x, y, z)
    source.SetRadius(0.01)
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    mapper.SetInputConnection(source.GetOutputPort())
    return actor

def get_line_actor(p0,p1):
    source = vtk.vtkLineSource()
    source.SetPoint1(p0)
    source.SetPoint2(p1)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


class VtkViewer():
    def __init__(self):
        self.renwin = vtk.vtkRenderWindow()
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.renwin.SetInteractor(self.iren)
        self.ren = vtk.vtkRenderer()
        self.renwin.AddRenderer(self.ren)
        self.iren.Initialize()

    def start(self):
        self.iren.Start()

    def add_actor(self, actor):
        self.ren.AddActor(actor)
        self.renwin.Render()


def get_point_function(v):
    v2 = np.zeros(4)
    v2[1:4] = v
    quat_v = quat.Quaternion(v2)
    def point_f(pos, orn):
        vrotq = orn * quat_v * orn.conj()
        v3 = vrotq.x[1:]
        return pos + v3
    return point_f

def find_inverse_vec(target,pair):
    pos,orn = pair
    v = target-pos
    v_q = quat.Quaternion([0,v[0],v[1],v[2]])
    oi = orn.inv()
    v2_q = oi*v_q*oi.conj()
    v2 = v2_q.x[1:]
    return v2

def load_data(sample_name):
    file_name = "TMS-%s.csv" % sample_name
    return read_csv_file(file_name)