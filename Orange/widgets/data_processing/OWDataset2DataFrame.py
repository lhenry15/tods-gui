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
from tods.data_processing.DatasetToDataframe import *

class OWDataset2DataFrame(SingleInputWidget):
    name = "Dataset2DataFrame"
    description = ("Convert Dataset to DataFrame.")
    icon = "icons/table-grid.svg"
    category = "Time Series Processing"
    keywords = []

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False

    # python_path = 'd3m.primitives.tods.data_processing.dataset_to_dataframe'
    # hyperparameter_list = []

    primitive = DatasetToDataFramePrimitive

    def _init_ui(self):
        self.infoa = gui.widgetLabel(
            self.controlArea, "Convert Dataset to DataFrame."
        )


if __name__ == "__main__":
    WidgetPreview(OWDataset2DataFrame).run(Orange.data.Table("iris"))
