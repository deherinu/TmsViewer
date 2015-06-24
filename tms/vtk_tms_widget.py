from __future__ import division
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QFrame, QHBoxLayout
from PyQt4.QtCore import pyqtSignal
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import numpy as np
import ConfigParser
import nibabel as nib

__author__ = 'Diego'


class TmsViewer(object):
    BACKGROUND1 = (0.2, 0.2, 0.2)
    BACKGROUND2 = (0.5, 0.5, 0.5)
    SKULL_COLOR = (0.5, 0.5, 0.5)
    CALIB_COLOR = (0.7804, 0.5216, 0.6824)

    SAMPLE_LINE_COLOR = (0.2588, 0.0000, 0.1647)
    SAMPLE_LINE_WARNING_COLOR = (1.0000, 0.3373, 0.0000)
    SAMPLE_LINE_HIGHLIGHT_COLOR = (0.0000, 1, 1)

    SAMPLE_CYLINDER_COLOR = (0.5216, 0.1725, 0.3922)
    SAMPLE_CYLINDER_WARNING_COLOR = (1.0000, 0.3373, 0.0000)
    SAMPLE_CYLINDER_HIGHLIGHT_COLOR = (0, 1, 1)
    SAMPLE_RADIUS = 0.0005

    ERROR_COLOR = (0.5020, 0.8039,	0.7569)

    BLOCK_COLOR = (0.7804, 0.5216, 0.6824)
    BLOCK_HIGHLIGHT_COLOR = (0, 1, 1)

    COIL_HEIGHT = 0.07
    SHADOWS = False
    def __init__(self, render_window_interactor, widget,config=None):

        # render_window_interactor.Initialize()
        # render_window_interactor.Start()
        self.configure(config)
        self.iren = render_window_interactor
        self.ren_win = render_window_interactor.GetRenderWindow()
        self.ren = vtk.vtkRenderer()
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground2(self.BACKGROUND2)
        self.ren.SetBackground(self.BACKGROUND1)
        self.ren.SetUseDepthPeeling(1)
        self.ren_win.SetMultiSamples(0)
        self.ren_win.AlphaBitPlanesOn()
        self.ren.SetOcclusionRatio(0.1)
        self.ren_win.AddRenderer(self.ren)

        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        self.light = vtk.vtkLight()
        self.ren.AddLight(self.light)
        self.light.SetLightTypeToSceneLight()
        self.light.SetPositional(0)


        self.light2 = vtk.vtkLight()
        self.ren.AddLight(self.light2)
        self.light2.SetLightTypeToSceneLight()
        self.light2.SetPositional(0)

        self.light3 = vtk.vtkLight()
        self.ren.AddLight(self.light3)
        self.light3.SetLightTypeToSceneLight()
        self.light3.SetPositional(0)

        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.0005)
        self.iren.SetPicker(self.picker)

        self.experiment = None
        self.__cylinder_actors = {}
        self.__line_actors = {}
        self.__cone_actors = {}
        self.__cone_sources = {}
        self.__error_triple = None
        self.__temp_sample = None
        self.__highlighted_actors = []

        #orientation axes
        axes_actor = vtk.vtkAnnotatedCubeActor()
        axes_actor.SetXPlusFaceText("R")
        axes_actor.SetXMinusFaceText("L")
        axes_actor.SetYPlusFaceText("P")
        axes_actor.SetYMinusFaceText("I ")
        axes_actor.SetZPlusFaceText("B")
        axes_actor.SetZMinusFaceText("F")

        axes_actor.GetTextEdgesProperty().SetColor(1, 1, 1)
        axes_actor.GetTextEdgesProperty().SetLineWidth(2)
        axes_actor.GetCubeProperty().SetColor(0.3, 0.3, 0.3)
        axes_actor.SetTextEdgesVisibility(1)
        axes_actor.SetFaceTextVisibility(0)

        axes_actor.SetZFaceTextRotation(90)
        axes_actor.SetXFaceTextRotation(-90)

        axes = vtk.vtkOrientationMarkerWidget()
        axes.SetOrientationMarker(axes_actor)
        axes.SetViewport(0.01, 0.01, 0.2, 0.2)

        self.axes = axes
        self.axes_actor = axes_actor


        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()

        self.__widget = widget

        if self.SHADOWS:
            opaque_sequence = vtk.vtkSequencePass()
            passes2 = vtk.vtkRenderPassCollection()
            opaque = vtk.vtkOpaquePass()
            lights = vtk.vtkLightsPass()
            peeling = vtk.vtkDepthPeelingPass()
            translucent = vtk.vtkTranslucentPass()
            peeling.SetTranslucentPass(translucent)
            passes2.AddItem(lights)
            passes2.AddItem(opaque)
            opaque_sequence.SetPasses(passes2)

            opaque_camera_pass = vtk.vtkCameraPass()
            opaque_camera_pass.SetDelegatePass(opaque_sequence)

            shadow_baker = vtk.vtkShadowMapBakerPass()
            shadow_baker.SetOpaquePass(opaque_camera_pass)

            shadow_baker.SetResolution(2**12)
            shadow_baker.SetPolygonOffsetFactor(3.1)
            shadow_baker.SetPolygonOffsetUnits(10.0)

            shadows = vtk.vtkShadowMapPass()
            shadows.SetShadowMapBakerPass(shadow_baker)

            shadows.SetOpaquePass(opaque_sequence)

            seq = vtk.vtkSequencePass()
            passes = vtk.vtkRenderPassCollection()
            seq.SetPasses(passes)
            passes.AddItem(shadow_baker)
            passes.AddItem(shadows)

            passes.AddItem(lights)
            passes.AddItem(peeling)
            passes.AddItem(vtk.vtkVolumetricPass())

            cameraP = vtk.vtkCameraPass()
            cameraP.SetDelegatePass(seq)
            self.ren.SetPass(cameraP)

    def configure(self,config):
        if config is None:
            return
        def get_tuple(section,key):
            s = config.get(section,key)
            return tuple((float(v) for v in s.split()))

        self.SAMPLE_RADIUS=config.getfloat("Samples","Cylinder_radius")
        self.SAMPLE_CYLINDER_COLOR = get_tuple("Samples","Cylinder_color")
        self.SAMPLE_CYLINDER_HIGHLIGHT_COLOR = get_tuple("Samples","Cylinder_highlight")
        self.SAMPLE_CYLINDER_WARNING_COLOR = get_tuple("Samples","Cylinder_warning")
        self.SAMPLE_LINE_COLOR = get_tuple("Samples","Line_color")
        self.SAMPLE_LINE_HIGHLIGHT_COLOR = get_tuple("Samples","Line_highlight")
        self.SAMPLE_LINE_WARNING_COLOR = get_tuple("Samples","Line_warning")

        self.BLOCK_COLOR = get_tuple("Blocks","Cone_color")
        self.BLOCK_HIGHLIGHT_COLOR = get_tuple("Blocks","Highlight_color")

        self.COIL_HEIGHT = config.getfloat("Coil","Height")
        self.ERROR_COLOR = get_tuple("Coil","Error_circle_color")

        self.SKULL_COLOR = get_tuple("Calibration","Skull_color")
        self.CALIB_COLOR = get_tuple("Calibration","Points_color")

        self.BACKGROUND1 = get_tuple("Background","color1")
        self.BACKGROUND2 = get_tuple("Background","color2")

        self.SHADOWS = config.getboolean("Rendering","shadows")



    @classmethod
    def get_default_config(cls):
        from os import path
        def set_tuple(t):
            return " ".join(("%f"%v for v in t))

        config = ConfigParser.SafeConfigParser()

        config.add_section("Directories")
        config.set("Directories","Default_input_directory",
                   path.normpath(path.join(path.dirname(__file__),"..","data")))
        config.set("Directories","Default_output_directory",
                   path.normpath(path.join(path.dirname(__file__),"..","output")))

        config.add_section("Rendering")
        config.set("Rendering","shadows",str(cls.SHADOWS))

        config.add_section("Background")
        config.set("Background","color1",set_tuple(cls.BACKGROUND1))
        config.set("Background","color2",set_tuple(cls.BACKGROUND2))

        config.add_section("Calibration")
        config.set("Calibration","Skull_color",set_tuple(cls.SKULL_COLOR))
        config.set("Calibration","Points_color",set_tuple(cls.CALIB_COLOR))

        config.add_section("Coil")
        config.set("Coil","Height",str(cls.COIL_HEIGHT))
        config.set("Coil","Error_circle_color",set_tuple(cls.ERROR_COLOR))

        config.add_section("Blocks")
        config.set("Blocks","Cone_color",set_tuple(cls.BLOCK_COLOR))
        config.set("Blocks","Highlight_color",set_tuple(cls.BLOCK_HIGHLIGHT_COLOR))

        config.add_section("Samples")
        config.set("Samples","Cylinder_radius",str(cls.SAMPLE_RADIUS))
        config.set("Samples","Cylinder_color",set_tuple(cls.SAMPLE_CYLINDER_COLOR))
        config.set("Samples","Cylinder_highlight",set_tuple(cls.SAMPLE_CYLINDER_HIGHLIGHT_COLOR))
        config.set("Samples","Cylinder_warning",set_tuple(cls.SAMPLE_CYLINDER_WARNING_COLOR))
        config.set("Samples","Line_color",set_tuple(cls.SAMPLE_LINE_COLOR))
        config.set("Samples","Line_highlight",set_tuple(cls.SAMPLE_LINE_HIGHLIGHT_COLOR))
        config.set("Samples","Line_warning",set_tuple(cls.SAMPLE_LINE_WARNING_COLOR))

        return config
    @classmethod
    def read_config(cls,file_path):
        config = cls.get_default_config()
        config.read(file_path)
        return config

    @classmethod
    def write_default_config(cls,file_path):
        config = cls.get_default_config()
        with open(file_path,"wb") as config_file:
            config_file.write("#TMS OPTITRACK DATA VIEWER CONFIGURATION\n\n")
            config_file.write("")
            config.write(config_file)

    def draw_block(self,block,color=None):
        a = self.__cone_actors.get(block)
        if a is not None:
            a.SetVisibility(1)
            source = self.__cone_sources[block]
        else:
            source = vtk.vtkConeSource()

        ctr = block.mean_coil_center
        tip = block.mean_intersection
        r = block.circle_radius

        source.SetCenter(tip-((tip-ctr)/np.linalg.norm(tip-ctr))*0.5*self.COIL_HEIGHT)
        source.SetHeight(self.COIL_HEIGHT*100)
        source.SetRadius(r)
        source.SetDirection(tip-ctr)
        source.SetResolution(20)

        if a is not None:
            return

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(source.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.__cone_actors[block]=actor
        self.__cone_sources[block] = source
        self.ren.AddActor(actor)

        prop = actor.GetProperty()
        if color is None:
            color = self.BLOCK_COLOR
        prop.SetColor(color)
        info = vtk.vtkInformation()
        info.Set(vtk.vtkShadowMapBakerPass.RECEIVER(),0)
        info.Set(vtk.vtkShadowMapBakerPass.OCCLUDER(),0)
        actor.SetPropertyKeys(info)




    def draw_samples(self,samples,color=None,warning_color=None,cylinder=True):
        for s in samples:
            if not s.ignored and (s.sphere_intersection is not None):
                if cylinder:
                    self.__draw_sample_as_cylinder(s,color,warning_color)
                else:
                    self.__draw_sample_as_line(s,color,warning_color)

    def __draw_sample_as_line(self,sample,color,warning_color):
        a = self.__line_actors.get(sample)
        if a is not None:
            a.SetVisibility(1)
            return
        p1 = sample.coil_center
        p2 = sample.sphere_intersection
        p1 = (p2+(p1-p2)/np.linalg.norm(p1-p2)*self.COIL_HEIGHT)
        p3 = p1+(p2-p1)*1.2  # an extra 20% to guarantee it goes into the sphere

        source = vtk.vtkLineSource()
        source.SetPoint1(p1)
        source.SetPoint2(p3)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)
        self.__line_actors[sample]=actor

        prop = actor.GetProperty()
        if sample.timing_error > 1:
            if warning_color is None:
                warning_color = self.SAMPLE_LINE_WARNING_COLOR
            prop.SetColor(warning_color)
        else:
            if color is None:
                color = self.SAMPLE_LINE_COLOR
            prop.SetColor(color)
        prop.SetAmbient(1.0)



    def __draw_sample_as_cylinder(self,sample,color,warning_color):
        a = self.__cylinder_actors.get(sample)
        if a is not None:
            a.SetVisibility(1)
            return
        p1 = sample.coil_center
        p2 = sample.sphere_intersection
        p3 = p1+(p2-p1)*1.2  # an extra 20% to guarantee it goes into the sphere
        height = self.COIL_HEIGHT*1.2
        source = vtk.vtkCylinderSource()
        source.SetCenter(0,0,0)
        source.SetRadius(self.SAMPLE_RADIUS)
        source.SetHeight(height)
        source.SetResolution(8)

        trans = vtk.vtkTransform()
        trans.Identity()

        v1 = p1-p2
        v1 /= np.linalg.norm(v1)

        v2 = (0,1,0)
        vp = np.cross(v2,v1)
        angle = np.arcsin(np.linalg.norm(vp))
        angle_deg = 180*angle/np.pi

        trans.Translate(p3)
        trans.RotateWXYZ(angle_deg,vp)
        trans.Translate((0,height/2,0))

        trans_filter = vtk.vtkTransformPolyDataFilter()
        trans_filter.SetInputConnection(source.GetOutputPort())
        trans_filter.SetTransform(trans)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(trans_filter.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)
        self.__cylinder_actors[sample]=actor

        prop = actor.GetProperty()
        if sample.timing_error > 1:
            if warning_color is None:
                warning_color = self.SAMPLE_CYLINDER_WARNING_COLOR
            prop.SetColor(warning_color)
        else:
            if color is None:
                color = self.SAMPLE_CYLINDER_COLOR
            prop.SetColor(color)
        info = vtk.vtkInformation()
        info.Set(vtk.vtkShadowMapBakerPass.RECEIVER(),0)
        info.Set(vtk.vtkShadowMapBakerPass.OCCLUDER(),0)
        #prop.SetAmbient(0.8)
        actor.SetPropertyKeys(info)


    def clear_highlight(self):
        for a,c in self.__highlighted_actors:
            a.GetProperty().SetColor(c)
        self.__highlighted_actors = []

        if self.__error_triple is not None:
            self.__error_triple[2].SetVisibility(0)
        if self.__temp_sample is not None:
            a = self.__cylinder_actors.get(self.__temp_sample)
            if a is not None: a.SetVisibility(0)
            a = self.__line_actors.get(self.__temp_sample)
            if a is not None: a.SetVisibility(0)
            self.__temp_sample = None

    def clear_coil(self):
        self.clear_highlight()
        for a in self.__cone_actors.itervalues():
            a.SetVisibility(0)
        for s,a in self.__cylinder_actors.iteritems():
            a.SetVisibility(0)
        for s,a in self.__line_actors.iteritems():
            a.SetVisibility(0)
        if self.__error_triple is not None:
            self.__error_triple[2].SetVisibility(0)


    def deep_clear_coil(self):
        for a in self.__cone_actors.itervalues():
            self.ren.RemoveViewProp(a)
        for a in self.__cylinder_actors.itervalues():
            self.ren.RemoveViewProp(a)
        for a in self.__line_actors.itervalues():
            self.ren.RemoveViewProp(a)
        if self.__error_triple is not None:
            self.ren.RemoveViewProp(self.__error_triple[2])
            self.__error_triple = None
        self.__line_actors.clear()
        self.__cylinder_actors.clear()
        self.__cone_actors.clear()

    def __draw_sphere(self,radius,center,color,resolution=20):
        source = vtk.vtkSphereSource()
        source.SetCenter(*center)
        source.SetRadius(radius)
        source.SetPhiResolution(resolution)
        source.SetThetaResolution(resolution)

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(source.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(color)
        #prop.SetInterpolationToPhong()
        brightness = np.max(color)
        specular_color = np.array(color)/brightness
        prop.SetSpecularColor(specular_color)
        prop.SetSpecular(0.1)
        prop.SetDiffuse(1)
        prop.SetAmbient(0)

        info = vtk.vtkInformation()
        info.Set(vtk.vtkShadowMapBakerPass.RECEIVER(),0)
        info.Set(vtk.vtkShadowMapBakerPass.OCCLUDER(),0)
        actor.SetPropertyKeys(info)

        self.ren.AddActor(actor)


    def draw_block_error(self,block):
        #universal
        if self.__error_triple is None:
            big_r = self.experiment.sphere_radius
            height = big_r*0.05
            source = vtk.vtkCylinderSource()
            source.SetCenter(0,0,0)
            source.SetResolution(20)
            source.CappingOff()
            source.SetHeight(height)
            trans = vtk.vtkTransform()
            trans_filter = vtk.vtkTransformPolyDataFilter()
            trans_filter.SetInputConnection(source.GetOutputPort())
            trans_filter.SetTransform(trans)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(trans_filter.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            self.ren.AddActor(actor)
            self.__error_actor = actor

            prop = actor.GetProperty()
            prop.SetColor(self.ERROR_COLOR)
            prop.SetOpacity(0.8)
            self.__error_triple = (source,trans,actor)
        else:
            source,trans,actor = self.__error_triple
            actor.SetVisibility(1)
        #specific
        big_r = self.experiment.sphere_radius
        height = big_r*0.05
        radius = block.circle_radius
        rel_center = block.circle_relative_center

        sphere_center = self.experiment.sphere_center
        circle_center = sphere_center+rel_center

        source.SetRadius(radius)

        trans.Identity()

        v1 = rel_center / np.linalg.norm(rel_center)
        v2 = (0,1,0)
        vp = np.cross(v2,v1)
        angle = np.arcsin(np.linalg.norm(vp))
        angle_deg = 180*angle/np.pi

        trans.Translate(circle_center)
        trans.RotateWXYZ(angle_deg,vp)
        trans.Translate((0,height/2,0))


    def __draw_nose(self,calib_points,center):
        source = vtk.vtkCubeSource()

        width = np.linalg.norm(calib_points["left"]-calib_points["right"])/5
        source.SetXLength(width)
        height = np.linalg.norm(calib_points["nasion"]-calib_points["vertex"])/3
        source.SetYLength(height)
        source.SetZLength(height)

        #make it straight (y facing vertex)
        v3 = calib_points["vertex"]-center
        v3 /= np.linalg.norm(v3)
        v4 = np.array((0,1,0))
        perp2 = np.cross(v3,v4)
        angle2 = np.arcsin(np.linalg.norm(perp2))
        angle_deg2 = angle2*180/np.pi

        #make it straight (z facing front)
        front = calib_points["nasion"]-center
        front2 = front - np.dot(front,v3)*v3
        front2/= np.linalg.norm(front2)
        front_o = np.array((0,0,1))
        front_o2 = front_o-np.dot(front_o,v3)*v3
        front_o2/= np.linalg.norm(front_o2)
        angle3 = np.arcsin(np.linalg.norm(np.cross(front2,front_o2)))
        angle_deg3 = angle3*180/np.pi

        transform = vtk.vtkTransform()
        transform.Translate(-1*front2*height/2)
        transform.Translate(calib_points["nasion"])
        transform.RotateWXYZ(angle_deg3,v3)
        transform.RotateWXYZ(-1*angle_deg2,perp2)

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(source.GetOutputPort())
        transform_filter.SetTransform(transform)

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(transform_filter.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)

        color = self.SKULL_COLOR
        prop = actor.GetProperty()
        prop.SetColor(color)
        prop.SetDiffuseColor(color)
        brightness = np.max(color)
        specular_color = np.array(color)/brightness
        prop.SetSpecularColor(specular_color)
        prop.SetInterpolationToFlat()
        prop.SetSpecular(0.0)
        prop.SetDiffuse(0.8)
        info = vtk.vtkInformation()
        info.Set(vtk.vtkShadowMapBakerPass.RECEIVER(),0)
        info.Set(vtk.vtkShadowMapBakerPass.OCCLUDER(),0)
        actor.SetPropertyKeys(info)

    def draw_experiment_reference(self,experiment):
        self.deep_clear_coil()
        self.ren.RemoveAllViewProps()
        self.experiment = experiment
        #self.__draw_sphere(experiment.sphere_radius-100,experiment.sphere_center,self.SKULL_COLOR,resolution=50)
        for p in experiment.calibration_points.itervalues():
            self.__draw_sphere(10,p,self.CALIB_COLOR)
        #self.__draw_nose(experiment.calibration_points,experiment.sphere_center)
        self.image_plane_widget()
        self.ren.Render()
        self.reset_camera()
        self.ren_win.Render()

    def reset_camera(self):
        self.ren.ResetCamera()
        self.ren.ResetCameraClippingRange()

        if self.experiment is not None:
            calib = self.experiment.calibration_points
            focal_point = self.experiment.sphere_center
            view_up = calib["vertex"]-focal_point
            mid_point = (calib["nasion"]*0.7+calib["vertex"]*0.3)
            pos_vec = mid_point - focal_point
            pos = focal_point+pos_vec*15

            cam = self.ren.GetActiveCamera()
            cam.SetFocalPoint(focal_point)
            cam.SetPosition(pos)
            cam.SetViewUp(view_up)
            self.light.SetFocalPoint(focal_point)
            self.light2.SetFocalPoint(focal_point)
            self.light3.SetFocalPoint(focal_point)

            left_mid_point= (calib["vertex"]+calib["left"])/2
            right_mid_point= (calib["vertex"]+calib["right"])/2

            #top_left_pos = focal_point + (left_mid_point-focal_point)*5
            #top_right_pos = focal_point + (right_mid_point-focal_point)*5
            right_pos = focal_point + (calib["right"]-focal_point)*15

            top_pos = focal_point+(calib["vertex"]-focal_point)*15
            top_front_pos = focal_point+((calib["nasion"]+calib["vertex"])/2-focal_point)*15

            #self.light.SetPosition(top_left_pos)
            #self.light2.SetPosition(top_right_pos)

            trans = vtk.vtkTransform()
            view_up_uni = view_up/np.linalg.norm(view_up)

            n1 = calib["nasion"]-focal_point
            n1 = n1 - (np.dot(n1, view_up_uni) * view_up_uni)
            n1 /= np.linalg.norm(n1)
            n2 = np.array((0,0,1))
            n2 = n2 - (np.dot(n2, view_up_uni) * view_up_uni)
            n2 /= np.linalg.norm(n2)
            v2 = np.cross(n2,n1)
            angle2 = np.arcsin(np.linalg.norm(v2))
            angle2_deg = 180*angle2/np.pi

            v1 = np.cross((0,1,0),view_up_uni)
            angle1 = np.arcsin(np.linalg.norm(v1))
            angle1_deg = 180*angle1/np.pi

            trans.RotateWXYZ(angle2_deg,view_up_uni)
            trans.RotateWXYZ(angle1_deg,*v1)

            acs = vtk.vtkPropCollection()
            self.axes_actor.GetActors(acs)
            for i in xrange(acs.GetNumberOfItems()):
                ac = acs.GetItemAsObject(i)
                mapper = ac.GetMapper()
                source_con = mapper.GetInputConnection(0,0)
                source = source_con.GetProducer()
                if not isinstance(source,vtk.vtkTransformFilter):
                    trans_filter = vtk.vtkTransformFilter()
                    trans_filter.SetInputConnection(source.GetOutputPort())
                    trans_filter.SetTransform(trans)
                    mapper.SetInputConnection(trans_filter.GetOutputPort())
                else:
                    source.SetTransform(trans)

            #self.axes_actor.RotateY(180)

            self.light.SetPosition(top_pos)
            self.light2.SetPosition(top_front_pos)
            self.light3.SetPosition(right_pos)
            self.light3.SetIntensity(0.5)
            self.ren.ResetCameraClippingRange()



    def draw_sample_cone(self):
        "For testing"
        cone = vtk.vtkConeSource()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cone.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        self.ren_win.Render()

    def highlight_block(self,block):
        a = self.__cone_actors.get(block)
        if a is not None:
            self.__highlighted_actors.append((a,a.GetProperty().GetColor()))
            a.GetProperty().SetColor(self.BLOCK_HIGHLIGHT_COLOR)


    def highlight_sample(self,sample,cylinder=True):
        if cylinder:
            a = self.__cylinder_actors.get(sample)
            if a is not None:
                self.__highlighted_actors.append((a,a.GetProperty().GetColor()))
                a.GetProperty().SetColor(self.SAMPLE_CYLINDER_HIGHLIGHT_COLOR)
        else:
            a = self.__line_actors.get(sample)
            if a is not None:
                self.__highlighted_actors.append((a,a.GetProperty().GetColor()))
                a.GetProperty().SetColor(self.SAMPLE_LINE_HIGHLIGHT_COLOR)

    def draw_temporal_highlighted_sample(self,sample,cylinder=True):
        if cylinder:
            self.__draw_sample_as_cylinder(sample,self.SAMPLE_CYLINDER_HIGHLIGHT_COLOR,
                                           self.SAMPLE_CYLINDER_HIGHLIGHT_COLOR)
            a = self.__cylinder_actors[sample]
            self.__highlighted_actors.append((a,a.GetProperty().GetColor()))
            a.GetProperty().SetColor(self.SAMPLE_CYLINDER_HIGHLIGHT_COLOR)
        else:
            self.__draw_sample_as_line(sample,self.SAMPLE_LINE_HIGHLIGHT_COLOR,
                                       self.SAMPLE_LINE_HIGHLIGHT_COLOR)
            a = self.__line_actors[sample]
            self.__highlighted_actors.append((a,a.GetProperty().GetColor()))
            a.GetProperty().SetColor(self.SAMPLE_LINE_HIGHLIGHT_COLOR)
        self.__temp_sample = sample

    def get_camera(self):
        camera = self.ren.GetActiveCamera()
        pos = camera.GetPosition()
        foc = camera.GetFocalPoint()
        vu = camera.GetViewUp()
        return pos,foc,vu

    def set_camera(self,pos,foc,vu):
        camera = self.ren.GetActiveCamera()
        camera.SetPosition(pos)
        camera.SetFocalPoint(foc)
        camera.SetViewUp(vu)
        self.ren.ResetCameraClippingRange()


    def image_plane_widget(self):

        img = nib.load('C:/Users/deyberth/Desktop/429.nii.gz')
        img_data = img.get_data()
        img_data = np.transpose(img_data, (2, 1, 0))
        img_data_shape = img_data.shape

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

        #Add outlineactor
        self.ren.AddActor(outlineActor)

        #Load widget interactors and enable
        planeWidgetX.SetInteractor(self.iren)
        planeWidgetX.On()
        planeWidgetY.SetInteractor(self.iren)
        planeWidgetY.On()
        planeWidgetZ.SetInteractor(self.iren)
        planeWidgetZ.On()


class QTmsViwerWidget(QFrame):
    def __init__(self, parent,configure=None):
        QFrame.__init__(self, parent)
        self.__qwindow_interactor = QVTKRenderWindowInteractor(self)
        self.__layout = QHBoxLayout()
        self.__layout.addWidget(self.__qwindow_interactor)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__vtk_viewer = TmsViewer(self.__qwindow_interactor,self,configure)
        self.setLayout(self.__layout)

    def initialize_widget(self):
        """call after showing the interface"""
        self.__qwindow_interactor.Initialize()
        self.__qwindow_interactor.Start()
        #self.__vtk_viewer.draw_sample_cone()
        self.__vtk_viewer.ren.ResetCamera()

    @property
    def viewer(self):
        return self.__vtk_viewer