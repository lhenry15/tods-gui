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

from tods.detection_algorithm.PyodAE import *

class OWPyodAE(SingleInputWidget):
    name = "OWPyodAE"
    description = ('Unsupervised Outlier Detection using autoencoder')
    icon = "icons/autoReg.svg"
    category = "Detection Algorithm"
    keywords = []

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    autosend = Setting(True)

    train_contamination = Setting(0.0)
    hidden_neurons_buf = Setting([4,2,4])
    hidden_neurons = Setting([4,2,4])
    validation_size = Setting(0.5)
    loss_func = Setting('mean_squared_error')
    optimizer = Setting('adam')
    epochs = Setting(10)
    batch_size = Setting(32)
    dropout_rate = Setting(0.1)
    feature_dim = Setting(1)
    hidden_dim = Setting(16)
   # decoder_neurons = Setting(0)
    activation = Setting('relu')
    diff_group_method = Setting('average')

    contamination = Setting(0.1)
    return_subseq_inds = Setting(False)
    use_columns_buf = Setting(())
    use_columns = ()
    exclude_columns_buf = Setting(())
    exclude_columns = ()
    return_result = Setting('new')
    use_semantic_types = Setting(False)
    add_index_columns = Setting(False)
    error_on_no_input = Setting(True)
    return_semantic_type = Setting('https://metadata.datadrivendiscovery.org/types/Attribute')
    
    primitive = AutoEncoderPrimitive



    


    def _use_columns_callback(self):
        self.use_columns = eval(''.join(self.use_columns_buf))
        # print(self.use_columns)
        self.settings_changed()

    def _exclude_columns_callback(self):
        self.exclude_columns = eval(''.join(self.exclude_columns_buf))
        # print(self.exclude_columns)
        self.settings_changed()

    def _hidden_neurons_callback(self):
        self.hidden_neurons = eval(''.join(self.hidden_neurons_buf))
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
        line7 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        

        gui.doubleSpin(line1, self, "train_contamination", minv=0., maxv=0.5, step=0.0001, label="contamination",)
        gui.lineEdit(line2, self, 'hidden_neurons_buf', label='hidden_neurons. List, e.g. [4,2,4]', validator=None, callback=self._hidden_neurons_callback)
        gui.doubleSpin(line1, self, "validation_size", minv=0., maxv=1., step=0.0001, label="validation_size",)
        gui.comboBox(line3, self, "loss_func", label='loss_func', items=['mean_squared_error'])
        gui.comboBox(line3, self, "optimizer", label='optimizer', items=['adam', 'sgd', 'rmsprop', 'nadam', 'adamax', 'adadelta', 'adagrad'])
        gui.lineEdit(line2, self, 'epochs', label='epochs')

        gui.lineEdit(line4, self, 'batch_size', label='batch_size')
        gui.doubleSpin(line4, self, "dropout_rate", minv=0., maxv=1., step=0.0001, label="dropout_rate",)

        gui.lineEdit(line5, self, 'feature_dim', label='feature_dim')
        gui.lineEdit(line5, self, 'hidden_dim', label='hidden_dim')
       # gui.lineEdit(line6, self, 'decoder_neurons', label='decoder_neurons')
        
        gui.comboBox(line7, self, "activation", label='activation', items=['relu', 'sigmoid', 'selu', 'tanh', 'softplus', 'softsign'])
        gui.comboBox(line7, self, "diff_group_method", label='diff_group_method', items=['average', 'max', 'min'])

        gui.doubleSpin(
            box2, self,
            "contamination",
            minv=0.,
            maxv=1.,
            step=0.001,
            label="Input contamination, float in (0,0.5].",
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )

        gui.checkBox(box2, self, "return_subseq_inds", label='If return subsequence index.',  callback=None)
        gui.checkBox(box2, self, "use_semantic_types", label='Mannally select columns if active.',  callback=None)
        gui.lineEdit(box2, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)
        gui.lineEdit(box2, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)
        gui.comboBox(box2, self, "return_result", sendSelectedValue=True, label='Output results.', items=['new', 'append', 'replace'], )
        gui.checkBox(box2, self, "add_index_columns", label='Keep index in the outputs.',  callback=None)
        gui.checkBox(box2, self, "error_on_no_input", label='Error on no input.',  callback=None)
        gui.comboBox(box2, self, "return_semantic_type", sendSelectedValue=True, label='Semantic type attach with results.', items=['https://metadata.datadrivendiscovery.org/types/Attribute',
                                                                                        'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'], )
        # Only for test
        # gui.button(box, self, "Print Hyperparameters", callback=self._print_hyperparameter)

        gui.auto_apply(box2, self, "autosend", box=False)

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)


    

    

    

    

if __name__ == "__main__":
    WidgetPreview(OWPyodAE).run([[],0])
