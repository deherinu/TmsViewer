import os
from functools import partial, wraps
import gzip
import cPickle
import csv

from PyQt4 import QtGui, QtCore

from tms.tms_viewer_gui import Ui_MainWindow
from tms import read_and_transform
from tms import vtk_tms_widget
from tms import qt_tms_models
from tms import tms_data_structures

def shows_error(fun):
    @wraps(fun)
    def wrapped(*args, **kwargs):
        self = args[0]
        try:
            return fun(*args, **kwargs)
        except Exception as e:

            QtGui.QMessageBox.warning(self, "Error running %s" % fun.__name__, str(e.message))
            raise

    return wrapped


class TmsView(QtGui.QMainWindow):
    def __init__(self):
        super(TmsView, self).__init__()

        config = self.get_vtk_config()
        self.__input_dir = config.get("Directories","Default_input_directory")
        self.__output_dir = config.get("Directories","Default_output_directory")

        self.viewer_widget = vtk_tms_widget.QTmsViwerWidget(self, config)
        self.viewer = self.viewer_widget.viewer
        self.experiment = tms_data_structures.TmsExperiment()
        self.blocks_model = qt_tms_models.BlockModel()
        self.details_model = qt_tms_models.DetailsModel()
        self.__last_highlighted = None
        self.__details_block = None


        self.load_ui()
        QtCore.QTimer.singleShot(0, self.viewer_widget.initialize_widget)


    @shows_error
    def get_vtk_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.txt")
        if os.path.isfile(config_path):
            try:
                config = vtk_tms_widget.TmsViewer.read_config(config_path)
                return config
            except Exception as e:
                err = QtGui.QMessageBox.warning(self, "Couldn't read configuration file", e.message)
                return vtk_tms_widget.TmsViewer.get_default_config()
        else:
            vtk_tms_widget.TmsViewer.write_default_config(config_path)
            return vtk_tms_widget.TmsViewer.get_default_config()


    def load_ui(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionNew_Session.triggered.connect(self.open_file)
        self.ui.vtk_layout.insertWidget(0, self.viewer_widget)
        self.ui.blocks_table.setModel(self.blocks_model)
        combo_type_delegate = qt_tms_models.ComboTypeDelegate()
        self.ui.blocks_table.setItemDelegateForColumn(7, combo_type_delegate)
        self.ui.cyls_rep.clicked.connect(self.draw_blocks)
        self.ui.cones_rep.clicked.connect(self.draw_blocks)
        self.ui.lines_rep.clicked.connect(self.draw_blocks)
        self.blocks_model.selection_changed.connect(self.draw_blocks)
        # self.ui.blocks_table.clicked.connect(self.delayed_highlight_block)
        self.ui.blocks_table.activated.connect(self.delayed_highlight_block)
        self.ui.blocks_table.clicked.connect(self.show_details)
        self.ui.blocks_table.activated.connect(self.show_details)
        self.ui.details_table.setModel(self.details_model)
        #self.ui.details_table.clicked.connect(self.highlight_sample)
        self.ui.details_table.activated.connect(self.highlight_sample)
        self.details_model.selection_changed.connect(self.update_block)

        self.ui.actionQuit.triggered.connect(self.quit)
        self.ui.actionSave_Session.triggered.connect(self.save_session_action)
        self.ui.actionOpen_Session.triggered.connect(self.load_session)

        self.ui.select_all.clicked.connect(self.select_all_blocks)
        self.ui.un_select_all.clicked.connect(self.unselect_all_blocks)
        self.ui.export_table.clicked.connect(self.export_table)



    def save_session_action(self, checked=False):
        if self.experiment.raw_points is None:
            err = QtGui.QMessageBox.warning(self, "Nothing to save", "Create a session first")
            return
        file_name = str(QtGui.QFileDialog.getSaveFileName(self, "Save session", self.__output_dir, "TMS-view (*.tmv)"))
        self.save_session(file_name)

    def save_session(self, file_name):
        if len(file_name) == 0:
            return
        self.__output_dir = os.path.dirname(file_name)
        session = {"experiment": self.experiment, "file_name": str(self.ui.file_label.text()),
                   "selected_blocks": self.blocks_model.active_blocks, "details_index": self.__details_block,
                   "cyl": self.ui.cyls_rep.isChecked(), "cones": self.ui.cones_rep.isChecked(),
                   "camera": self.viewer.get_camera()}

        try:
            with gzip.open(file_name, "wb", 9) as f:
                cPickle.dump(session, f, -1)
        except Exception as e:
            err = QtGui.QMessageBox.warning(self, "Couldn't save session", e.message)
        else:
            self.statusBar().showMessage("saved session to %s" % file_name, 5000)

    @shows_error
    def load_session(self, checked=False):
        file_name = str(QtGui.QFileDialog.getOpenFileName(self, "Load session", self.__output_dir, "TMS-view (*.tmv)"))
        if len(file_name) == 0:
            return
        self.__output_dir = os.path.dirname(file_name)
        try:
            with gzip.open(file_name, "rb") as f:
                session = cPickle.load(f)
        except Exception as e:
            err = QtGui.QMessageBox.warning(self, "Couldn't read session", e.message)
            return
        self.ui.cones_rep.setChecked(session["cones"])
        self.ui.cyls_rep.setChecked(session["cyl"])
        self.ui.lines_rep.setChecked(not (session["cones"] or session["cyl"]))
        self.experiment = session["experiment"]
        self.ui.file_label.setText(session["file_name"])
        self.ui.date_label.setText(self.experiment.mid_date.strftime("%a %d %b %Y"))
        self.ui.duration_label.setText("Duration: " + str(self.experiment.total_duration))
        self.blocks_model.set_blocks(self.experiment.blocks)
        self.details_model.set_block(None)
        self.viewer.draw_experiment_reference(self.experiment)
        self.blocks_model.active_blocks = session["selected_blocks"]
        self.blocks_model.modelReset.emit()
        details_index = session["details_index"]
        if details_index is not None:
            index = self.blocks_model.index(details_index, 0)
            self.show_details(index)
        self.viewer.set_camera(*session["camera"])
        self.draw_blocks()

    @shows_error
    def open_file(self, checked=False):
        global nombre_archivo
        fileDialog = QtGui.QFileDialog(self, )
        file_name = str(fileDialog.getOpenFileName(self, "Select csv file", self.__input_dir, "csv (*.csv)"))
        nombre_archivo = file_name
        if len(file_name) == 0: return
        self.__input_dir = os.path.dirname(file_name)
        #Points is the initial dataset
        points = read_and_transform.read_csv_file(file_name)
        hacks = {
            #"skip_calib":("nasion",),
            #"Not_Normalize" : True,
            }
        self.experiment.set_points(points,file_name, hacks=hacks)
        self.experiment.file_name = file_name
        self.ui.file_label.setText(os.path.basename(file_name))
        self.ui.date_label.setText(self.experiment.mid_date.strftime("%a %d %b %Y"))
        self.ui.duration_label.setText("Duration: " + str(self.experiment.total_duration))
        self.blocks_model.set_blocks(self.experiment.blocks)
        self.details_model.set_block(None)
        self.viewer.draw_experiment_reference(self.experiment)
        self.draw_blocks()

    @shows_error
    def draw_blocks(self, dummy=None):
        print "redrawing"
        if self.experiment is None:
            return
        self.viewer.clear_coil()
        self.__last_highlighted = None
        if self.ui.cones_rep.isChecked():
            fun = lambda b: self.viewer.draw_block(b)
        elif self.ui.cyls_rep.isChecked():
            fun = lambda b: self.viewer.draw_samples(b.samples, cylinder=True)
        else:
            fun = lambda b: self.viewer.draw_samples(b.samples, cylinder=False)
        for i, b in enumerate(self.experiment.blocks):
            if self.blocks_model.active_blocks[i]:
                fun(b)
        self.viewer.ren_win.Render()

    @shows_error
    def select_all_blocks(self, dummy=None):
        for i in xrange(len(self.blocks_model.active_blocks)):
            self.blocks_model.active_blocks[i] = True
        self.blocks_model.modelReset.emit()
        self.draw_blocks()

    @shows_error
    def unselect_all_blocks(self, dummy=None):
        for i in xrange(len(self.blocks_model.active_blocks)):
            self.blocks_model.active_blocks[i] = False
        self.blocks_model.modelReset.emit()
        self.draw_blocks()

    @shows_error
    def export_table(self, dummy=None):
        file_name = str(QtGui.QFileDialog.getSaveFileName(self, "Save table", self.__output_dir,
                                                          "Comma separated (*.csv)"))
        if len(file_name) < 1:
            return
        self.__output_dir = os.path.dirname(file_name)
        self.write_table(file_name)
        session_file_name = file_name[:-3] + ".tmv"
        exists = os.path.isfile(session_file_name)
        if exists:
            q = "A file called %s exists\n would you like to overwrite with the current section?" % session_file_name
            question = QtGui.QMessageBox(self)
            question.setText(q)
            question.setWindowTitle("Save session")
            question.setIcon(question.Question)
            over_button = question.addButton("Overwrite", question.DestructiveRole)
            new_name = question.addButton("New name", question.AcceptRole)
            question.addButton(question.Cancel)

            def overwrite():
                self.save_session(session_file_name)

            over_button.clicked.connect(overwrite)
            new_name.clicked.connect(self.save_session_action)
            question.exec_()

        else:
            q = "Save the current session with name %s" % session_file_name
            question = QtGui.QMessageBox.question(self, "Save session", q,
                                                  QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            if question == QtGui.QMessageBox.Ok:
                self.save_session(session_file_name)

    def write_table(self, file_name):
        with open(file_name, "wb") as csv_file:
            import numpy as np
            writer = csv.writer(csv_file)
            valid_blocks = (b for b in self.blocks_model.blocks if b.block_type != "REJECTED")
            numbered_blocks = dict(( (i+1,b) for i,b in  enumerate(valid_blocks)))
            print numbered_blocks
            for i in xrange(len(numbered_blocks)):
                line_number = i+1
                block = numbered_blocks[line_number]
                if block.block_type != "IGNORED":
                    l = [line_number, block.position_error * 1000]
                else:
                    l = [line_number, float("nan")]
                writer.writerow(l)
            left = ["Left", self.get_side_total("l") * 1000]
            writer.writerow(left)
            right = ["Right", self.get_side_total("r") * 1000]
            writer.writerow(right)
            try:
                dif1 = np.linalg.norm(numbered_blocks[1].mean_intersection - numbered_blocks[3].mean_intersection)*1000
            except KeyError:
                dif1 = np.nan
            diff1 = ["Difference 1-3", dif1]
            writer.writerow(diff1)
            try:
                dif2 = np.linalg.norm(numbered_blocks[5].mean_intersection - numbered_blocks[7].mean_intersection)*1000
            except KeyError:
                dif2 = np.nan
            diff2 = ["Difference 5-7", dif2]
            writer.writerow(diff2)

            dist_l_intra = self.get_points_distance_to_center([numbered_blocks.get(i) for i in (1,2,3,4)])
            dist_r_intra = self.get_points_distance_to_center([numbered_blocks.get(i) for i in (5,6,7,8)])

            dist_l_inter = self.get_points_distance_to_center([numbered_blocks.get(9)])
            dist_r_inter = self.get_points_distance_to_center([numbered_blocks.get(10)])

            l = ["Left distance INTRA",dist_l_intra*1000]
            writer.writerow(l)
            l = ["Right distance INTRA",dist_r_intra*1000]
            writer.writerow(l)

            l = ["Left distance INTER",dist_l_inter*1000]
            writer.writerow(l)
            l = ["Right distance INTER",dist_r_inter*1000]
            writer.writerow(l)

    @shows_error
    def get_side_total(self, hemi):
        from itertools import chain
        from tms import tms_geom

        blocks = [b for b in self.blocks_model.blocks
                  if b.block_type in {"ACCEPTED", "UNKNOWN"} and b.hemisphere == hemi]

        intercepts = [s.sphere_intersection for s in chain(*(b.samples for b in blocks))
                      if s.sphere_intersection is not None and not s.ignored]

        vec, circle_radius = tms_geom.circle_from_points_in_sphere(intercepts,
                                                                   self.experiment.sphere_radius,
                                                                   self.experiment.sphere_center)

        return circle_radius

    @shows_error
    def get_points_distance_to_center(self,blocks):
        from tms import tms_geom
        from itertools import ifilter
        import numpy as np
        points = []
        for b in ifilter(lambda x: x is not None, blocks):
            points.extend([s.sphere_intersection for s in b.samples if not s.ignored])
        if len(points) == 0:
            return np.nan
        m_point = np.mean(points,axis=0)
        plane_point = self.experiment.calibration_points["vertex"]
        p_2,p_o = self.experiment.calibration_points["nasion"],self.experiment.sphere_center
        normal = np.cross(plane_point-p_o,p_2-p_o)
        d = tms_geom.distance_to_plane(m_point,plane_point,normal)
        return d

    def delayed_highlight_block(self, index):
        QtCore.QTimer.singleShot(0, partial(self.highlight_block, index))

    @shows_error
    def highlight_block(self, index):
        print "highlight"
        self.viewer.clear_highlight()
        row = index.row()
        block = self.blocks_model.blocks[row]
        if block == self.__last_highlighted:
            return
        if self.ui.cones_rep.isChecked():
            self.viewer.highlight_block(block)
        elif self.ui.cyls_rep.isChecked():
            for s in block.samples:
                self.viewer.highlight_sample(s, cylinder=True)
        else:
            for s in block.samples:
                self.viewer.highlight_sample(s, cylinder=False)

        self.viewer.draw_block_error(block)
        self.viewer.ren_win.Render()
        self.__last_highlighted = block

    @shows_error
    def show_details(self, index):
        row = index.row()
        block = self.blocks_model.blocks[row]
        self.details_model.set_block(block)
        self.__details_block = row

    @shows_error
    def highlight_sample(self, index):
        sample = self.details_model.block.samples[index.row()]
        if self.__last_highlighted == sample:
            return
        self.viewer.clear_highlight()
        if self.ui.cones_rep.isChecked():
            self.viewer.draw_temporal_highlighted_sample(sample, cylinder=True)
        elif self.ui.cyls_rep.isChecked():
            self.viewer.highlight_sample(sample, cylinder=True)
        else:
            self.viewer.highlight_sample(sample, cylinder=False)
        self.viewer.draw_block_error(self.details_model.block)
        self.__last_highlighted = sample
        self.viewer.ren_win.Render()

    @shows_error
    def update_block(self):
        self.experiment.update_block(self.details_model.block)
        self.blocks_model.modelReset.emit()
        self.draw_blocks()

    def quit(self):
        self.close()


if __name__ == "__main__":
    import locale
    locale.setlocale(locale.LC_TIME,"C")
    app = QtGui.QApplication([])
    tms_view = TmsView()
    tms_view.show()
    app.exec_()