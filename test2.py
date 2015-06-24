import vtk

def slice(ImageSet,Orientation,slice,window,grayscale):
    # reader is the input VTK volume
    # Calculate the center of the volume
    #ImageSet.UpdateInformation()
    (xMin, xMax, yMin, yMax, zMin, zMax) = ImageSet.GetWholeExtent()
    (xSpacing, ySpacing, zSpacing) = ImageSet.GetSpacing()
    (x0, y0, z0) = ImageSet.GetOrigin()

    center = [x0 + xSpacing * 0.5 * (xMin + xMax),
                      y0 + ySpacing * 0.5 * (yMin + yMax),
                      z0 + zSpacing * 0.5 * (zMin + zMax)]

    # Matrices for axial, coronal, sagittal, oblique view orientations
    axial = vtk.vtkMatrix4x4()
    axial.DeepCopy((1, 0, 0,center[0] ,
                    0, 1, 0,center[1] ,
                    0, 0, 1, slice,
                    0, 0, 0, 1))

    sagittal = vtk.vtkMatrix4x4()
    sagittal.DeepCopy((0, 0,-1, slice,
                       1, 0, 0, center[1],
                       0,-1, 0,center[2] ,
                       0, 0, 0, 1))


    coronal = vtk.vtkMatrix4x4()
    coronal.DeepCopy((1, 0, 0, center[0],
                      0, 0, 1, slice,
                      0,-1, 0, center[2],
                      0, 0, 0, 1))






    oblique = vtk.vtkMatrix4x4()
    oblique.DeepCopy((1, 0, 0, center[0],
                      0, 0.866025, -0.5, center[1],
                      0, 0.5, 0.866025, center[2],
                      0, 0, 0, 1))


    # Extract a slice in the desired orientation
    reslice = vtk.vtkImageReslice()
    reslice.SetInput(ImageSet)
    reslice.SetOutputDimensionality(2)
    reslice.SetResliceAxesOrigin(10,20,20)
    if Orientation=='axial':
        reslice.SetResliceAxes(axial)
    elif Orientation=='sagittal':
        reslice.SetResliceAxes(sagittal)
    elif Orientation=='coronal':
        reslice.SetResliceAxes(coronal)


    reslice.SetInterpolationModeToCubic()

    # Create a greyscale lookup table
    table = vtk.vtkLookupTable()
    table.SetRange(grayscale) # image intensity range
    table.SetValueRange(0, 1.0) # from black to white
    table.SetSaturationRange(0.0, 0.0) # no color saturation
    table.SetRampToSCurve()
    table.SetNumberOfTableValues(402)
    table.Build()

    # Map the image through the lookup table
    color = vtk.vtkImageMapToColors()
    color.SetLookupTable(table)
    color.SetInputConnection(reslice.GetOutputPort())

    # Display the image
    actor = vtk.vtkImageActor()
    actor.SetInput(color.GetOutput())

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)

    ctv=vtk.vtkSphereSource()
    ctv.SetRadius(100)
    ctv.SetThetaResolution(100)
    ctv.SetPhiResolution(100)
    sphereMapper=vtk.vtkPolyDataMapper()
    sphereMapper.SetInputConnection(ctv.GetOutputPort())
    sp=vtk.vtkPlane()
    sp.SetOrigin(0,0,10)
    sp.SetNormal(0,0,1)
    cutter=vtk.vtkCutter()
    cutter.SetCutFunction(sp)
    cutter.SetInput(sphereMapper.GetInput())
    cutter.Update()
    cmapper=vtk.vtkPolyDataMapper()
    cmapper.SetInputConnection( cutter.GetOutputPort())
    cmapper.ScalarVisibilityOff()
    sphereActor=vtk.vtkActor()
    sphereActor.GetProperty().SetColor(1.0,1,0)
    sphereActor.GetProperty().SetLineWidth(3)
    sphereActor.GetProperty().SetEdgeColor(1,1,0.5)
    sphereActor.GetProperty().SetAmbient(1)
    sphereActor.GetProperty().SetDiffuse(0)
    sphereActor.GetProperty().SetSpecular(0)
    sphereActor.SetMapper(cmapper)
    renderer.AddActor(sphereActor)
    #renderer.SetColorWindow (900)
    #renderer.SetColorLevel (-100)

    #window = vtk.vtkRenderWindow()
    #renderer.GetActiveCamera().Zoom(1.1)
    window.GetRenderWindow().AddRenderer(renderer)
    renwin=window.GetRenderWindow()

    # Set up the interaction
    interactorStyle = vtk.vtkInteractorStyleImage()
    interactor = vtk.vtkRenderWindowInteractor()
##    interactor.SetInteractorStyle(interactorStyle)
    renwin.GetRenderWindow().SetInteractor(QVW.QVTKRenderWindowInteractor)
    renwin.Render()