import nibabel as nib
import vtk
import os
import numpy as np
from nibabel.affines import apply_affine
from lib_tms import config
from lib_tms import transform
from lib_tms.braviz.readAndFilter import transforms as braviztransforms


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

#Actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor2 =vtk.vtkActor()
actor2.SetMapper(mapper2)

#Load nifti images, T1 and orig
img = nib.load(T1_file)
img_orig = nib.load(orig_file)

#Nifti header
img_header = img.get_header()

#Get data images
img_data = img.get_data()

#Images shapes
img_data_shape = img_data.shape

#Get affine matrix
affine_matrix = transform.getTransformMatrix(img)

#Voxel center
vox_center = (np.array(img_data.shape) - 1) / 2
uno = np.array([0,0,0])
dos = np.array([0,0,1])
tres = np.array([0,0,2])
ultimo = np.array([0,0,310])

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

#Transpose matrix
#img_data = np.transpose(img_data, (2, 1, 0))

#Array type img_data
array_type = img_data.dtype

#Data Importer
dataImporter = vtk.vtkImageImport()
dataImporter.SetDataScalarTypeToShort()
data_string = img_data.flatten(order='F').tostring()
dataImporter.SetNumberOfScalarComponents(1)
dataImporter.CopyImportVoidPointer(data_string, len(data_string))
dataImporter.SetDataExtent(0, img_data_shape[0] - 1, 0, img_data_shape[1] - 1, 0, img_data_shape[2] - 1)
dataImporter.SetWholeExtent(0, img_data_shape[0] - 1, 0, img_data_shape[1] - 1, 0, img_data_shape[2] - 1)
dataImporter.Update()
temp_data = dataImporter.GetOutput()

#Create and copy new vtkImageData Object
new_data2 = vtk.vtkImageData()
new_data2.DeepCopy(temp_data)

#Reslice new vtkImageData Object with voxel size using affine_matrix from header
new_data = vtk.vtkImageData()
new_data = braviztransforms.applyTransform(new_data2, affine_matrix)

#Start ImagePlaneWidget

#Outline
outline=vtk.vtkOutlineFilter()
outline.SetInputData(new_data)
outlineMapper=vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())
outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)

#Picker
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.005)

#PlaneWidget X
planeWidgetX = vtk.vtkImagePlaneWidget()
planeWidgetX.DisplayTextOn()
planeWidgetX.SetInputData(new_data)
planeWidgetX.SetPlaneOrientationToXAxes()
planeWidgetX.SetSliceIndex(100)
planeWidgetX.SetPicker(picker)
planeWidgetX.SetKeyPressActivationValue("x")
prop1 = planeWidgetX.GetPlaneProperty()
prop1.SetColor(1, 0, 0)

#PlaneWidget Y
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

#PlaneWidget Z
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

#Start drawing
#Renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(0, 0, 1)

#RenderWindow
renwin = vtk.vtkRenderWindow()
renwin.AddRenderer(renderer)
renwin.SetSize(1000,1000)

#Add outlineactor
renderer.AddActor(outlineActor)
renderer.AddActor(actor2)

#Create Window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renwin)

#Load widget interactors and enable
planeWidgetX.SetInteractor(interactor)
planeWidgetX.On()
planeWidgetY.SetInteractor(interactor)
planeWidgetY.On()
planeWidgetZ.SetInteractor(interactor)
planeWidgetZ.On()

#Start renderer
interactor.Initialize()
renwin.Render()
interactor.Start()