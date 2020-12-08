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
from tods.feature_analysis.TRMF import *

class OWTRMF(SingleInputWidget):
    name = "TRMF"
    description = ("Temporal Regularized Matrix Factorization.")
    icon = "icons/trmf.svg"
    category = "Feature Analysis"
    keywords = []


    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    test_treatment = Setting(0)
    autosend = Setting(True)
    
    lags_buf = Setting(())
    lags = ()
    K = Setting(2)
    lambda_f = Setting(1.0)
    lambda_x = Setting(1.0)
    lambda_w = Setting(1.0)
    alpha = Setting(1000.0)
    eta = Setting(1.0)
    max_iter = Setting(1000)
    F_step = Setting(default=0.0001)
    X_step = Setting(default=0.0001)
    W_step = Setting(default=0.0001)

    use_columns_buf = Setting(())
    use_columns = ()
    exclude_columns_buf = Setting(())
    exclude_columns = ()
    return_result = Setting('new')
    use_semantic_types = Setting(False)
    add_index_columns = Setting(False)
    error_on_no_input = Setting(True)
    return_semantic_type = Setting('https://metadata.datadrivendiscovery.org/types/Attribute')

    primitive = TRMFPrimitive


    

    


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
        box1 = gui.widgetBox(self.controlArea, "Hyperparameter:Algorithm")
        box2 = gui.widgetBox(self.controlArea, "Hyperparameter:Columns")

        line1 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line2 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line3 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line4 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line5 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line6 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)


        gui.lineEdit(line1, self, "lags_buf", label='lags_buf',  callback=self._lags_callback)
        gui.lineEdit(line2, self, "K", label='K', valueType=int, callback=None)
        gui.lineEdit(line2, self, "lambda_f", label='lambda_f', valueType=float, callback=None)
        gui.lineEdit(line3, self, "lambda_x", label='lambda_x', valueType=float, callback=None)
        gui.lineEdit(line3, self, "lambda_w", label='lambda_w', valueType=float, callback=None)
        gui.lineEdit(line4, self, "alpha", label='alpha', valueType=float, callback=None)
        gui.lineEdit(line4, self, "eta", label='eta', valueType=float, callback=None)
        gui.lineEdit(line5, self, "max_iter", label='max_iter', valueType=int, callback=None)
        gui.lineEdit(line5, self, "F_step", label='F_step', valueType=float, callback=None)
        gui.lineEdit(line6, self, "X_step", label='X_step', valueType=float, callback=None)
        gui.lineEdit(line6, self, "W_step", label='W_step', valueType=float, callback=None)

        gui.checkBox(box2, self, "use_semantic_types", label='Mannally select columns if active.',  callback=None)

        gui.lineEdit(box2, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        gui.lineEdit(box2, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

        gui.comboBox(box2, self, "return_result", label='Output results.', items=['new', 'append', 'replace'], )

        gui.checkBox(box2, self, "add_index_columns", label='Keep index in the outputs.',  callback=None)

        gui.checkBox(box2, self, "error_on_no_input", label='Error on no input.',  callback=None)

        gui.comboBox(box2, self, "return_semantic_type", label='Semantic type attach with results.', items=['https://metadata.datadrivendiscovery.org/types/Attribute',
                                                                                                            'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'], )
         

        gui.auto_apply(box2, self, "autosend", box=False)

        gui.button(box2, self, "Print Hyperparameters", callback=self._print_hyperparameter)

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)


    def _print_hyperparameter(self):
        print(type(self.lags), self.lags)
        self.commit()
    

    


from Orange.widgets.utils.widgetpreview import WidgetPreview
if __name__ == "__main__":
    WidgetPreview(OWTRMF).run(Orange.data.Table("iris"))