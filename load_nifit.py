import nibabel as nib
#import numpy as np
#import matplotlib.pyplot as plt
import vtk
import scipy
import os
import numpy as np
from nibabel.affines import apply_affine
import numpy.linalg as npl

from lib import config
from lib import transform


def load_nifti_PlaneWidget(self):
    #Path files
    T1_file = os.path.join(config.T1Path, 'T1W3DTFESENSE.nii.gz')
    fibers_file = os.path.join(config.fibersPath, 'CaminoTracts.vtk')
    orig_file = os.path.join(config.origPath, 'orig.nii.gz')

    #Fibers
    pd_reader = vtk.vtkPolyDataReader()
    pd_reader.SetFileName(fibers_file)
    pd_reader.Update()
    fibs = pd_reader.GetOutput()
    mapper2 = vtk.vtkPolyDataMapper()
    mapper2.SetInputData(fibs)

    #Sphere
    source = vtk.vtkSphereSource()
    source.SetCenter(0,0,0)
    source.SetRadius(100)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor2 =vtk.vtkActor()
    actor2.SetMapper(mapper2)

    #Load nifti images, T1 and orig
    img = nib.load(T1_file)
    img_orig = nib.load(orig_file)

    #Nifti header
    img_header = img.get_header()
    #print img_header

    #Get data images
    img_data = img.get_data()
    img_data_anat = img_orig.get_data()

    #Images shapes
    img_data_shape = img_data.shape
    img_data_anat_shape = img_data_anat.shape
    #print img_data_shape
    #print img_data_anat_shape

    #Get affine matrix
    affine_matrix = transform.getTransformMatrix(img)
    affine_matrix_anat = transform.getTransformMatrix(img_orig)
    print affine_matrix

    #Voxel center
    vox_center = (np.array(img_data.shape) - 1) / 2
    uno = np.array([0,0,0])
    dos = np.array([0,0,1])
    tres = np.array([0,0,2])
    ultimo = np.array([0,0,310])

    vox_center_anat = (np.array(img_data_anat.shape) - 1) / 2

    #Applying affine

    result_affine = apply_affine(affine_matrix, vox_center)
    result_affine2 = apply_affine(affine_matrix, uno)
    result_affine3 = apply_affine(affine_matrix, dos)
    result_affine4 = apply_affine(affine_matrix, tres)
    result_affine5 = apply_affine(affine_matrix, ultimo)
    print result_affine2
    print result_affine3
    print result_affine4
    print result_affine5

    #result_affine_anat = apply_affine(affine_matrix_anat, vox_center_anat)
    #img_vox2anat_vox = npl.inv(affine_matrix_anat).dot(affine_matrix)
    #corresponding_vox = apply_affine(img_vox2anat_vox, vox_center)

    #img_data = np.transpose(img_data, (2, 1, 0))

    array_type = img_data.dtype

    dataImporter = vtk.vtkImageImport()
    dataImporter.SetDataScalarTypeToShort()

    data_string = img_data.flatten(order='F').tostring()

    dataImporter.SetNumberOfScalarComponents(1)
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))
    dataImporter.SetDataExtent(0, img_data_shape[0] - 1, 0, img_data_shape[1] - 1, 0, img_data_shape[2] - 1)
    dataImporter.SetWholeExtent(0, img_data_shape[0] - 1, 0, img_data_shape[1] - 1, 0, img_data_shape[2] - 1)
    dataImporter.Update()
    temp_data = dataImporter.GetOutput()
    new_data2 = vtk.vtkImageData()
    new_data2.DeepCopy(temp_data)

    new_data = vtk.vtkImageData()
    new_data = transform.resliceImage(new_data2, affine_matrix)

    #outline
    outline=vtk.vtkOutlineFilter()
    outline.SetInputData(new_data)
    outlineMapper=vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outline.GetOutputPort())
    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)

    #Picker
    picker = vtk.vtkCellPicker()
    picker.SetTolerance(0.005)

    #PlaneWidget
    planeWidgetX = vtk.vtkImagePlaneWidget()
    planeWidgetX.DisplayTextOn()
    planeWidgetX.SetInputData(new_data)
    planeWidgetX.SetPlaneOrientationToXAxes()
    planeWidgetX.SetSliceIndex(100)
    planeWidgetX.SetPicker(picker)
    planeWidgetX.SetKeyPressActivationValue("x")
    prop1 = planeWidgetX.GetPlaneProperty()
    prop1.SetColor(1, 0, 0)

    planeWidgetY = vtk.vtkImagePlaneWidget()
    planeWidgetY.DisplayTextOn()
    planeWidgetY.SetInputData(new_data)
    planeWidgetY.SetPlaneOrientationToYAxes()
    planeWidgetY.SetSliceIndex(100)
    planeWidgetY.SetPicker(picker)
    planeWidgetY.SetKeyPressActivationValue("y")
    prop2 = planeWidgetY.GetPlaneProperty()
    prop2.SetColor(1, 1, 0)
    planeWidgetY.SetLookupTable(planeWidgetX.GetLookupTable())

    planeWidgetZ = vtk.vtkImagePlaneWidget()
    planeWidgetZ.DisplayTextOn()
    planeWidgetZ.SetInputData(new_data)
    planeWidgetZ.SetPlaneOrientationToZAxes()
    planeWidgetZ.SetSliceIndex(100)
    planeWidgetZ.SetPicker(picker)
    planeWidgetZ.SetKeyPressActivationValue("z")
    prop2 = planeWidgetY.GetPlaneProperty()
    prop2.SetColor(0, 0, 1)
    planeWidgetZ.SetLookupTable(planeWidgetX.GetLookupTable())

    #Renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0, 0, 1)

    #RenderWindow
    renwin = vtk.vtkRenderWindow()
    renwin.AddRenderer(renderer)

    #Add outlineactor
    renderer.AddActor(outlineActor)
    #renderer.AddActor(actor2)
    renwin.SetSize(1000,1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renwin)

    #Load widget interactors and enable
    planeWidgetX.SetInteractor(interactor)
    planeWidgetX.On()
    planeWidgetY.SetInteractor(interactor)
    planeWidgetY.On()
    planeWidgetZ.SetInteractor(interactor)
    planeWidgetZ.On()

    interactor.Initialize()
    renwin.Render()
    interactor.Start()