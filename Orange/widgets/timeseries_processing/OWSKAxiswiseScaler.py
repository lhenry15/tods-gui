from functools import reduce
from types import SimpleNamespace

from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import QGridLayout
from AnyQt.QtWidgets import QFormLayout
from AnyQt.QtGui import QIntValidator

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
from tods.timeseries_processing.SKAxiswiseScaler import *

class OWSKAxiswiseScaler(SingleInputWidget):
    name = "AxiswiseScaler"
    description = ("Axis-wise Scaling.")
    icon = "icons/scaler.svg"
    category = "Time Series Processing"
    keywords = []

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    autosend = Setting(True)

    axis = Setting(0)
    with_mean = Setting(True)
    with_std = Setting(True)

    use_columns_buf = Setting(())
    use_columns = ()
    exclude_columns_buf = Setting(())
    exclude_columns = ()
    return_result = Setting('new')
    use_semantic_types = Setting(False)
    add_index_columns = Setting(False)
    error_on_no_input = Setting(True)
    return_semantic_type = Setting('https://metadata.datadrivendiscovery.org/types/Attribute')

    primitive = SKAxiswiseScalerPrimitive



    


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
        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Hyperparameter")
        gui.separator(self.controlArea)

        gui.comboBox(box, self, "axis", sendSelectedValue=True, label='Scaling axis.', items=[0, 1], )
        gui.checkBox(box, self, "with_mean", label='Center the data before scaling.',  callback=None)
        gui.checkBox(box, self, "with_std", label='Scale the data to unit variance.',  callback=None)

        # use_semantic_types = Setting(False)
        gui.checkBox(box, self, "use_semantic_types", label='Mannally select columns if active.',  callback=None)

        # use_columns = Setting(())
        gui.lineEdit(box, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        # exclude_columns = Setting(())
        gui.lineEdit(box, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

        # return_result = Setting(['append', 'replace', 'new'])
        gui.comboBox(box, self, "return_result", sendSelectedValue=True, label='Output results.', items=['new', 'append', 'replace'], )

        # add_index_columns = Setting(False)
        gui.checkBox(box, self, "add_index_columns", label='Keep index in the outputs.',  callback=None)

        # error_on_no_input = Setting(True)
        gui.checkBox(box, self, "error_on_no_input", label='Error on no input.',  callback=None)

        # return_semantic_type = Setting(['https://metadata.datadrivendiscovery.org/types/Attribute',
        #                                 'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'])
        gui.comboBox(box, self, "return_semantic_type", sendSelectedValue=True, label='Semantic type attach with results.', items=['https://metadata.datadrivendiscovery.org/types/Attribute',
                                                                                        'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'], )
        # Only for test
        gui.button(box, self, "Print Hyperparameters", callback=self._print_hyperparameter)

        gui.auto_apply(box, self, "autosend", box=False)

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)

    def _print_hyperparameter(self):
        print(self.IntVariable, type(self.IntVariable))
        print(self.FloatVariable, type(self.FloatVariable))
        print(self.BoolVariable, type(self.BoolVariable))
        print(self.TupleVariable, type(self.TupleVariable))
        print(self.ListVariable, type(self.ListVariable))
        print(self.EnumVariable, type(self.EnumVariable))
        print(self.BoundedInt, type(self.BoundedInt))
        print(self.BoundedFloat, type(self.BoundedFloat))
        print(self.contamination, type(self.contamination))
        print(self.return_subseq_inds, type(self.return_subseq_inds))
        print(self.use_columns, type(self.use_columns))
        print(self.exclude_columns, type(self.exclude_columns))
        print(self.return_result, type(self.return_result))
        print(self.use_semantic_types, type(self.use_semantic_types))
        print(self.add_index_columns, type(self.add_index_columns))
        print(self.error_on_no_input, type(self.error_on_no_input))
        print(self.return_semantic_type, type(self.return_semantic_type))


        self.commit()

    

    

    

    

if __name__ == "__main__":
    WidgetPreview(OWSKAxiswiseScaler).run([[],[]])