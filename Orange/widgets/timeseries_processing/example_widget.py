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

class OWContinuize(SingleInputWidget):
    name = "Example"
    description = ("Example widget")
    icon = "icons/Continuize.svg"
    category = "Time Series Processing"
    keywords = []

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    test_treatment = Setting(0)
    autosend = Setting(True)

    example_btn_choices = ["Test1", "Test2", "Test3"]

    


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
        layout = QGridLayout()
        gui.widgetBox(self.controlArea, orientation=layout)
        box = gui.radioButtonsInBox(
                None, self, "test_treatment", box="TTTTTest",
                btnLabels=self.example_btn_choices,
                callback=self.settings_changed)
        gui.rubber(box)
        layout.addWidget(box, 0, 0, 2, 1)
        form = QFormLayout

        ac = gui.auto_apply(None, self, "autosend", box=False)
        layout.addWidget(ac, 1, 2)

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)

    
