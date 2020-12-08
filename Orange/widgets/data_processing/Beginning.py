import numpy

import Orange.data
from Orange.widgets.widget import OWWidget, Input, Output#, settings
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets import gui
from Orange.widgets.tods_base_widget import TODS_BaseWidget, PrimitiveInfo
from Orange.widgets.settings import Setting

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTextBrowser
from PyQt5 import QtCore

import os

# [start-snippet-1]
class Beginning(OWWidget):
    name = "Beginning"
    description = "The beginning of a constructed pipeline."
    icon = "icons/start.svg"
    category = "Reinforcement Module"


    # class Inputs:
    #     pipline_in = Input("Input a File", Orange.data.Table)

    class Outputs:
        pipline_out = Output("Primitive Information", list)

    want_main_area = False
    # print(os.path.join(os.getcwd(), 'datasets/yahoo_sub_5.csv'))
    # dataset_fullname = Setting(os.path.join(os.getcwd(), 'datasets/yahoo_sub_5.csv'))
    hyperparameter_list = ['dataset_folder']

    def __init__(self):
        super().__init__()

        # GUI
        box1 = gui.widgetBox(self.controlArea, "Dataset")
        box2 = gui.widgetBox(self.controlArea, "Dataset Folder")
        # self.infoa = gui.widgetLabel(
        #     box, "Dataset: None"
        # )

        self.python_path = 'HEAD'
        self.id = 0
        self.choose_dataset_button = gui.button(box1, self, "Choose a folder", callback=self.choose_dataset)

        # hyperparameters
        self.dataset_folder = None

        self.hyperparameter = {}
        for i in self.hyperparameter_list:
            hyper_tmp = getattr(self, i, None)
            self.hyperparameter[i] = hyper_tmp

        self.primitive_info = PrimitiveInfo(python_path=self.python_path,
                                            id=self.id,
                                            hyperparameter=self.hyperparameter,
                                            ancestors={},
                                            )

        self.textBrowser = QTextBrowser(box2)
        self.textBrowser.setGeometry(QtCore.QRect(0, 20, 1000, 500))
        # self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        # gui.lineEdit(box, self, 'dataset_fullname_tmp', label='Dataset File. (string)', callback=None)

        # start the pipeline
        self.Outputs.pipline_out.send([[self.primitive_info], self.id])


    def choose_dataset(self):

        # fileName, filetype = QFileDialog.getOpenFileName(self, "Choose a CSV file", "~/", "CSV Files (*.csv)")
        dataset_folder = QFileDialog.getExistingDirectory(self, "Choose dataset's folder.", "./")
        # 当窗口非继承QtWidgets.QDialog时，self可替换成 None
        self.dataset_folder = dataset_folder
        self.commit()

    def commit(self):
        for i in self.hyperparameter_list:
            hyper_tmp = getattr(self, i, None)
            self.hyperparameter[i] = hyper_tmp

        self.primitive_info.hyperparameter = self.hyperparameter
        self.Outputs.pipline_out.send([[self.primitive_info], self.id])

        self.textBrowser.append(self.dataset_folder)
        QtWidgets.QApplication.processEvents()

    # @Inputs.pipline_in
    # def set_pipline_in(self, pipline_in):
    #     if pipline_in is not None:
    #         self.infoa.setText("There is input, which is the beginning of th pipeline.")
    #
    #
    #         self.Outputs.pipline_out.send([[self.primitive_info], self.python_path])
    #         # output_class.display()
    #         # print([output_class], type([[output_class], self.python_path]))
    #
    #
    #     else:
    #         self.infoa.setText("No data on input yet, waiting to get something.")
    #         self.primitive_info.ancestors = {}
    #         # self.primitive_info.descendants = []
    #         self.Outputs.pipline_out.send(None)

    # @Outputs.pipline_out
    # def set_pipline_out(self):
    #     self.Outputs.pipline_out.send([[self.primitive_info], self.python_path])


if __name__ == "__main__":
    WidgetPreview(Beginning).run()
