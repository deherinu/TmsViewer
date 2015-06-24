from PyQt4 import QtGui, QtCore
import numpy as np

from tms import tms_data_structures


__author__ = 'Diego'


class ComboTypeDelegate(QtGui.QItemDelegate):
    BLOCK_TYPES = tms_data_structures.TmsBlock.BLOCK_TYPES

    def __init__(self, parent=None):
        super(ComboTypeDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        editor = QtGui.QComboBox(QWidget)
        for t in self.BLOCK_TYPES:
            editor.addItem(t.title())
        return editor

    def setEditorData(self, QWidget, QModelIndex):
        model = QModelIndex.model()
        text = model.data(QModelIndex, QtCore.Qt.DisplayRole)
        ix = QWidget.findText(text)
        if ix >= 0:
            QWidget.setCurrentIndex(ix)

    def setModelData(self, QWidget, QAbstractItemModel, QModelIndex):
        text = QWidget.currentText()
        QAbstractItemModel.setData(QModelIndex, text, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, QWidget, QStyleOptionViewItem, QModelIndex):
        QWidget.setGeometry(QStyleOptionViewItem.rect)


class BlockModel(QtCore.QAbstractTableModel):
    __headers = ["#", "Hemi", "Start", "Duration", "Samples", "P.Error", "T.Error", "Classify"]
    __tooltips = {"#": "Block number", "Hemi": "Hemisphere", "Start": "Start time",
                  "Duration": "Block duration in seconds",
                  "Samples": "Number of valid samples", "P.Error": "Position error",
                  "T.Error": "Timing error in seconds",
                  "Classify": "Ignore:Valid trial but problem with spatial data\nAccept: Valid trial\nReject: Prueba, hotspot search..."}
    selection_changed = QtCore.pyqtSignal(name="selection_changed")

    def __init__(self):
        super(BlockModel, self).__init__()
        self.blocks = []
        self.__data_functions = {"#": self.get_block_number,
                                 "Hemi": self.get_hemi,
                                 "Start": self.get_start_time,
                                 "Duration": self.get_duration,
                                 "Samples": self.get_samples,
                                 "P.Error": self.get_pos_error,
                                 "T.Error": self.get_time_error,
                                 "Classify": self.get_type}
        self.active_blocks = []


    def set_blocks(self, blocks):
        self.blocks = blocks
        self.active_blocks = [True, ] * len(blocks)
        self.modelReset.emit()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.blocks)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.__headers)

    def headerData(self, p_int, Qt_Orientation, int_role=None):
        try:
            if int_role == QtCore.Qt.DisplayRole:
                return self.__headers[p_int]
            elif int_role == QtCore.Qt.ToolTipRole:
                return self.__tooltips[self.__headers[p_int]]
            elif int_role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignHCenter
        except Exception:
            pass
        return QtCore.QVariant()

    def flags(self, QModelIndex):
        if not QModelIndex.isValid():
            return QtCore.Qt.NoItemFlags
        col = QModelIndex.column()
        row = QModelIndex.row()
        flag = QtCore.Qt.ItemIsSelectable
        b_type = self.blocks[row].block_type
        if b_type != "IGNORED":
            flag |= QtCore.Qt.ItemIsEnabled
        if col == 0:
            flag |= QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        elif col == 7:
            flag |= QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        return flag

    def setData(self, QModelIndex, QVariant, int_role=None):
        if not QModelIndex.isValid():
            return False
        row = QModelIndex.row()
        col = QModelIndex.column()

        if col == 0 and int_role == QtCore.Qt.CheckStateRole:
            value = QVariant == QtCore.Qt.Checked
            self.active_blocks[row] = value

            self.dataChanged.emit(QModelIndex, QModelIndex)
            self.selection_changed.emit()
            return True
        if col == 7 and int_role == QtCore.Qt.EditRole:
            text2 = str(QVariant).upper()
            block = self.blocks[row]
            block.block_type = text2
            index2 = QModelIndex.model().index(row, self.columnCount() - 1)
            self.dataChanged.emit(QModelIndex, index2)
            self.modelReset.emit()
            return True
        return False

    def data(self, QModelIndex, int_role=None):
        if not QModelIndex.isValid():
            return QtCore.QVariant()
        try:
            row = QModelIndex.row()
            col = QModelIndex.column()
            if int_role == QtCore.Qt.DisplayRole:
                return self.get_data(row, self.__headers[col])
            elif int_role == QtCore.Qt.CheckStateRole and col == 0:
                return QtCore.Qt.Checked if self.active_blocks[row] else QtCore.Qt.Unchecked
            elif int_role == QtCore.Qt.TextAlignmentRole:
                if col in {3, 4, 5, 6}:
                    return QtCore.Qt.AlignRight
                else:
                    return QtCore.Qt.AlignLeft
        except Exception:
            pass
        return QtCore.QVariant()

    def get_block_number(self, index):
        block = self.blocks[index]
        if block.block_type == "REJECTED":
            return ""
        nn = [1 for i in xrange(index) if self.blocks[i].block_type != "REJECTED"]
        return len(nn) + 1

    def get_start_time(self, index):
        block = self.blocks[index]
        time = block.start
        return time.strftime("%H:%M:%S")

    def get_duration(self, index):
        block = self.blocks[index]
        dur = block.end - block.start
        return "%d s." % dur.seconds

    def get_samples(self, index):
        block = self.blocks[index]
        return str(sum((not s.ignored for s in block.samples)))

    def get_pos_error(self, index):
        block = self.blocks[index]
        return "{:0> 6.3f}".format(block.position_error * 1000) if not np.isnan(block.position_error) else "nan"

    def get_time_error(self, index):
        block = self.blocks[index]
        return str(block.max_timing_error)

    def get_type(self, index):
        block = self.blocks[index]
        type = block.block_type
        return type.title()

    def get_hemi(self, index):
        block = self.blocks[index]
        return block.hemisphere.upper()

    def get_data(self, row, column_name):
        fun = self.__data_functions[column_name]
        return fun(row)


class DetailsModel(QtCore.QAbstractTableModel):
    __headers = ["#", "Time", "T.Error"]
    __tooltips = {"#": "Sample number", "Time": "Capture time",
                  "T.Error": "Timing error in seconds", }
    selection_changed = QtCore.pyqtSignal(name="selection_changed")

    def __init__(self):
        super(DetailsModel, self).__init__()
        self.block = None

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        if self.block is None:
            return 0
        return len(self.block.samples)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.__headers)

    def headerData(self, p_int, Qt_Orientation, int_role=None):
        try:
            if int_role == QtCore.Qt.DisplayRole:
                return self.__headers[p_int]
            elif int_role == QtCore.Qt.ToolTipRole:
                return self.__tooltips[self.__headers[p_int]]
            elif int_role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignHCenter
        except Exception:
            pass
        return QtCore.QVariant()

    def flags(self, QModelIndex):
        if not QModelIndex.isValid():
            return QtCore.Qt.NoItemFlags
        col = QModelIndex.column()
        row = QModelIndex.row()
        flag = QtCore.Qt.ItemIsSelectable
        ignored = self.block.samples[row].ignored
        if not ignored:
            flag |= QtCore.Qt.ItemIsEnabled
        if col == 0:
            flag |= QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        return flag

    def data(self, QModelIndex, int_role=None):
        if not QModelIndex.isValid():
            return QtCore.QVariant()
        try:
            row = QModelIndex.row()
            col = QModelIndex.column()
            if int_role == QtCore.Qt.DisplayRole:
                if col == 0:
                    return str(row)
                elif col == 1:
                    return str(self.block.samples[row].date)
                elif col == 2:
                    return "%d s." % self.block.samples[row].timing_error
            elif int_role == QtCore.Qt.CheckStateRole and col == 0:
                return QtCore.Qt.Checked if not self.block.samples[row].ignored else QtCore.Qt.Unchecked
            elif int_role == QtCore.Qt.TextAlignmentRole:
                if col == 2:
                    return QtCore.Qt.AlignRight
                else:
                    return QtCore.Qt.AlignLeft
        except Exception:
            pass
        return QtCore.QVariant()

    def set_block(self, block):
        self.block = block
        self.modelReset.emit()

    def setData(self, QModelIndex, QVariant, int_role=None):
        if not QModelIndex.isValid():
            return False
        row = QModelIndex.row()
        col = QModelIndex.column()

        if col == 0 and int_role == QtCore.Qt.CheckStateRole:
            value = QVariant == QtCore.Qt.Checked
            self.block.samples[row].ignored = not value
            index2 = QModelIndex.model().index(row, self.columnCount() - 1)
            self.dataChanged.emit(QModelIndex, index2)
            self.modelReset.emit()
            self.selection_changed.emit()
            return True
        return False
