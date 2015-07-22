__author__ = 'deyberth'

import os
import numpy as np
import nibabel as nib
import vtk
import logging


def getTransformMatrix (file_name):
    transMat = file_name.get_affine()
    return transMat


def applyAffine(matriz, lastrow, i,j,k):
    return matriz.dot([i, j, k]) + lastrow

def numpy2vtkMatrix(M):
    """
    Transform a 4x4 numpy array into vtk4x4 matrix

    Args:
        M (numpy.ndarray) : Numpy 4x4 array

    Returns
        vtk4x4Matrix
    """
    vtk_matrix = vtk.vtkMatrix4x4()
    for i in range(0, 4):
        for j in range(0, 4):
            vtk_matrix.SetElement(i, j, M[i, j])
    return vtk_matrix

def resliceImage(img, transform, origin2=None, dimension2=None, spacing2=None, interpolate=True):
    if isinstance(transform, (np.matrix, np.ndarray)):
        transform = numpy2vtkMatrix(transform)
        print 'bu'
    if isinstance(transform, vtk.vtkMatrix4x4):
        vtkTrans = vtk.vtkMatrixToHomogeneousTransform()
        vtkTrans.SetInput(transform)
        if spacing2 is None or origin2 is None:
            transform_i = transform.NewInstance()
            transform_i.DeepCopy(transform)
            transform_i.Invert()
            if spacing2 is None:
                org = np.array(transform_i.MultiplyDoublePoint((0,0,0,1)))
                next_pt = np.array(transform_i.MultiplyDoublePoint((1,1,1,1)))
                delta = (org[0:3]/org[3]) - (next_pt[0:3]/next_pt[3])
                spacing2 = delta
                #spacing2 = [transform_i.GetElement(0, 0), transform_i.GetElement(1, 1), transform_i.GetElement(2, 2)]
            if origin2 is None or spacing2 is None:

                if origin2 is None:
                    # TODO: Use a better strategy to find the new origin; this doesn't
                    # work with large rotations or reflections
                    x_min, x_max, y_min, y_max, z_min, z_max = img.GetBounds()
                    corners = [(x_min, y_min, z_min), (x_min, y_min, z_max), (x_min, y_max, z_min),
                               (x_min, y_max, z_max),
                               (x_max, y_min, z_min), (x_max, y_min, z_max), (x_max, y_max, z_min),
                               (x_max, y_max, z_max)]

                    corners2 = []
                    for c in corners:
                        ch = c + (1,)
                        corners2.append(transform_i.MultiplyDoublePoint(ch))
                    x2_min, y2_min, z2_min, _ = np.min(corners2, axis=0)
                    x2_max, y2_max, z2_max, _ = np.max(corners2, axis=0)
                    origin2 = [0, 0, 0]
                    origin2[0] = x2_min if spacing2[0] >= 0 else x2_max
                    origin2[1] = y2_min if spacing2[1] >= 0 else y2_max
                    origin2[2] = z2_min if spacing2[2] >= 0 else z2_max

                    if dimension2 is None:
                        dimension2 = [0, 0, 0]
                        dimension2[0] = int(np.ceil(np.abs((x2_min - x2_max) / spacing2[0])))
                        dimension2[1] = int(np.ceil(np.abs((y2_min - y2_max) / spacing2[1])))
                        dimension2[2] = int(np.ceil(np.abs((z2_min - z2_max) / spacing2[2])))


    elif isinstance(transform, vtk.vtkAbstractTransform):
        vtkTrans = transform
        if None == spacing2 or None == origin2:
            log = logging.getLogger(__name__)
            log.error(
                "spacing2 and origin2 are required when using a general transform")
            raise Exception(
                "spacing2 and origin2 are required when using a general transform")
    else:
        log = logging.getLogger(__name__)
        log.error("Method not implemented for %s transform" % type(transform))
        raise Exception(
            "Method not implemented for %s transform" % type(transform))
    if None == dimension2:
        dimension2 = img.GetDimensions()
        #=============================Finished parsing arguments===============

    reslicer = vtk.vtkImageReslice()
    reslicer.SetResliceTransform(vtkTrans)
    reslicer.SetInputData(img)
    outData = vtk.vtkImageData()
    outData.SetOrigin(origin2)
    outData.SetDimensions(dimension2)
    outData.SetSpacing(spacing2)
    reslicer.SetInformationInput(outData)
    if interpolate is False:
        reslicer.SetInterpolationModeToNearestNeighbor()
    else:
        reslicer.SetInterpolationModeToCubic()
    reslicer.Update()
    outImg = reslicer.GetOutput()
    # print dimension2
    return outImg


def reslice(img, transform, data):
    reslicer=vtk.vtkImageReslice()

    reslicer.SetInputData(img)

    transform = numpy2vtkMatrix(transform)
    vtkTrans = vtk.vtkMatrixToHomogeneousTransform()
    vtkTrans.SetInput(transform)

    reslicer.SetResliceTransform(vtkTrans)
    reslicer.SetOutputOrigin(data.GetOrigin())
    reslicer.SetOutputSpacing(data.GetSpacing())
    reslicer.SetOutputExtent(data.GetExtent())