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

from tods.detection_algorithm.Telemanom import TelemanomPrimitive

class OWTelemanom(SingleInputWidget):
    name = "Telemanom"
    description = ("Pattern wise outlier detection based on the methods used in telemetry using a LSTM model")
    icon = 'icons/telemanom.svg'
    category = "Detection Algorithm"
    keywords = []

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    autosend = Setting(True)

    smoothing_perc = Setting(1.0)
    window_size = Setting(10)
    error_buffer = Setting(50)
    batch_size = Setting(70)
    dropout = Setting(0.3)
    validation_split = Setting(0.2)
    layers_buf = Setting([])
    layers =[]
    epoch = Setting(10)
    patience = Setting(5)
    min_delta = Setting(0.0003)
    l_s = Setting(50)
    n_predictions = Setting(10)
    p = Setting(0.05)



    contamination = Setting(0.1)
    use_columns_buf = Setting(())
    use_columns = ()
    exclude_columns_buf = Setting(())
    exclude_columns = ()
    return_result = Setting('new')
    use_semantic_types = Setting(False)
    add_index_columns = Setting(False)
    error_on_no_input = Setting(True)
    return_semantic_type = Setting('https://metadata.datadrivendiscovery.org/types/Attribute')

    BoundedInt = Setting(10)
    BoundedFloat = Setting(10.0)

    primitive = TelemanomPrimitive



    


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
        box1 = gui.widgetBox(self.controlArea, "Hyperparameter: Algorithm")
        box = gui.widgetBox(self.controlArea, "Hyperparameter: Columns")

        
        line1 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line2 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line3 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line4 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line5 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line6 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line7 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)


        

        # determines window size used in EWMA smoothing (percentage of total values for channel)
        gui.lineEdit(line1, self, "smoothing_perc", label='Smoothing Percentage',  callback=None)


        # number of trailing batches to use in error calculation
        gui.lineEdit(line1, self, "window_size", label='Input window size',  callback=None)


        # number of values surrounding an error that are brought into the sequence (promotes grouping on nearby sequences
        gui.lineEdit(line2, self, "error_buffer", label='Error Buffer',  callback=None)


        # Batch size while predicting
        gui.lineEdit(line2, self, "batch_size", label='Predicting Batch Size',  callback=None)


        # Dropout rate
        gui.doubleSpin(
            line3, self,
            "dropout",
            minv=0.,
            maxv=0.5,
            step=0.05,
            label="Input Dropout Rate, float in (0,0.5].",
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )

        # Validation Split
        gui.doubleSpin(
            line3, self,
            "validation_split",
            minv=0.,
            maxv=0.5,
            step=0.05,
            label="Input Validation Split ratio, float in (0,0.5].",
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )

        # layers
        gui.lineEdit(line4, self, "layers", label="LSTM layers for 2 LSTM units in array eg. [40,40]",
                     validator=None, callback=self._use_columns_callback)

        gui.lineEdit(line4, self, "layers_buf", label='LSTM layers for 2 LSTM units in array eg. [40,40]',  callback=self._layers_callback)

        #Epoch
        gui.lineEdit(line5, self, "epoch", label='Training Epochs',  callback=None)


        # Number of consequetive training iterations to allow without decreasing the val_loss by at least min_delta
        gui.lineEdit(line5, self, "patience", label='No of epochs to execute if validation loss does not decrease',  callback=None)


        #Min delta - amount of loss to be decreased to be considered for patience
        gui.lineEdit(line6, self, "min_delta", label='Training Epochs',  callback=None)



        #History - Number of previous time points to give for prediting a future time point
        gui.lineEdit(line6, self, "l_s", label='Number of previous timepoints to provide for predicting a future time point',  callback=None)



        # n-predcitions : number of time steps to predic ahead
        gui.lineEdit(line7, self, "n_predictions", label='Number of time steps to predict ahead',  callback=None)


        # #minimum percent decrease between max errors in anomalous sequences (used for pruning)
        # gui.lineEdit(box, self, "p", label='Percent decrease acceptable between max erros for pruning',  callback=None)


        # Contamination
        gui.doubleSpin(
            line7, self,
            "contamination",
            minv=0.,
            maxv=1.,
            step=0.001,
            label="Input contamination, float in (0,0.5].",
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )


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

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)

    def _print_hyperparameter(self):
        print(self.use_columns, type(self.use_columns))
        print(self.exclude_columns, type(self.exclude_columns))
        print(self.return_result, type(self.return_result))
        print(self.use_semantic_types, type(self.use_semantic_types))
        print(self.add_index_columns, type(self.add_index_columns))
        print(self.error_on_no_input, type(self.error_on_no_input))
        print(self.return_semantic_type, type(self.return_semantic_type))


        self.commit()

    def _layers_callback(self):
        self.layers = eval(''.join(self.layers_buf))
        print(self.layers)

    

    

    

if __name__ == "__main__":
    WidgetPreview(OWTelemanom).run([[], []])
