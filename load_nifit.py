import nibabel as nib
#import numpy as np
#import matplotlib.pyplot as plt
import vtk
import scipy
import numpy as np
#import
#from vtk.util import numpy_support
#import Tkinter
#from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

#VTK_data = numpy_support.numpy_to_vtk(num_array=img_data.ravel(), deep=True, array_type=vtk.VTK_DATA_OBJECT)
#new_data = numpy_support.vtk_to_numpy(VTK_data)
#new_data = img_data.reshape(img_data_shape)
#
# def show_slices(slices):
#     fig,axes = plt.subplots(1, len(slices))
#     for i, slice in enumerate(slices):
#         axes[i].imshow(slice.T, cmap="gray", origin="lower")
#
# slice_0=new_data[100, :, :]
# slice_1=new_data[:, 100, :]
# slice_2=new_data[:, :, 100]
# show_slices([slice_0, slice_1, slice_2])
# plt.suptitle("Image")
#plt.show()

#Sphere
source = vtk.vtkSphereSource()
source.SetCenter(0,0,0)
source.SetRadius(100)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(source.GetOutputPort())
# actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

img = nib.load('C:/Users/deyberth/Desktop/t1.nii.gz')
img_data = img.get_data()

img_data = np.transpose(img_data, (2, 1, 0))
#print tt.shape

img_data_shape = img_data.shape
print img_data_shape

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
new_data = vtk.vtkImageData()
new_data.DeepCopy(temp_data)

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
#renderer.AddActor(actor)
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