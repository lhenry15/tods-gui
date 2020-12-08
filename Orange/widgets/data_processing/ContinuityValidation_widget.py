from functools import reduce
from types import SimpleNamespace

from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import QGridLayout
from AnyQt.QtWidgets import QFormLayout

import Orange.data
from Orange.util import Reprable
from Orange.statistics import distribution
from Orange.preprocess import Continuize
from Orange.preprocess.transformation import Identity, Indicator, Normalizer
from Orange.data.table import Table
from Orange.widgets import gui, widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.sql import check_sql_input
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.utils.state_summary import format_summary_details
from Orange.widgets.widget import Input, Output
from Orange.widgets.tods_base_widget import SingleInputWidget
from tods.data_processing.ContinuityValidation import *

class OWContinuityValidation(SingleInputWidget):
    name = "ContinuityValidation"
    description = ("Check whether the seires data is consitent in time interval and provide processing if not consistent.")
    icon = "icons/conval.svg"
    category = "Data Processing"
    keywords = []

    

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    test_treatment = Setting(0)
    autosend = Setting(True)
    interval = Setting(1.0)
    continuity_option = Setting('ablation')

    python_path = "d3m.primitives.tods.data_processing.continuity_validation"
    hyperparameter_list = ['interval', 'continuity_option']

    primitive = ContinuityValidationPrimitive



    


    def _use_columns_callback(self):
        self.use_columns = eval(''.join(self.use_columns_buf))
        # print(self.use_columns)
        self.settings_changed()

    def _exclude_columns_callback(self):
        self.exclude_columns = eval(''.join(self.exclude_columns_buf))
        # print(self.exclude_columns)
        self.settings_changed()

    def _init_ui(self):
        # implement your user interface here (for setting hyperparameters)
        # layout = QGridLayout()
        # gui.widgetBox(self.controlArea, orientation=layout)

        # ac = gui.auto_apply(None, self, "autosend", box=False)
        # layout.addWidget(ac, 1, 2)

        # # print_hyperparameter = gui.button(self.buttonsArea, self, "Print Hyperparameters",
        # #            callback=self._print_hyperparameter)

        # # layout.addWidget(print_hyperparameter, 1, 0)
        
        # layout.addWidget(gui.widgetLabel(None, "interval: "), 2, 0, Qt.AlignLeft)
        # sb = gui.hBox(None, margin=0)
        # layout.addWidget(sb, 2, 1)
        # gui.lineEdit(
        #     sb, self, "interval", controlWidth=60, valueType=int,
        #     callback=None)
        
        # layout.addWidget(gui.comboBox(
        #     None, self, "continuity_option", items=['ablation', 'imputation'],
        #     orientation=Qt.Horizontal, # callback=self._correlation_combo_changed
        # ), 3, 0)


        ######
        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Hyperparameter")
        # self.infoa = gui.widgetLabel(
        #     box, "Choose ablation or imputation the original data"
        # )

        gui.separator(self.controlArea)

        gui.lineEdit(
            box, self, "interval", label='interval', valueType=float,
            callback=None)

        gui.comboBox(
            box, self, "continuity_option", label='continuity_option', items=['ablation', 'imputation'],
            orientation=Qt.Horizontal, # callback=self._correlation_combo_changed
        )

        gui.auto_apply(box, self, "autosend", box=False)





        ######
        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)

    

    


from Orange.widgets.utils.widgetpreview import WidgetPreview
if __name__ == "__main__":
    WidgetPreview(OWContinuityValidation).run(Orange.data.Table("iris"))
