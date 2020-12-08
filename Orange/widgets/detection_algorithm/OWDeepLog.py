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

from tods.detection_algorithm.DeepLog import *

class OWDeepLog(SingleInputWidget):
    name = "DeepLog"
    description = ("Unsupervised Outlier Detection using DeepLog.")
    icon = "icons/DeepLog.svg"
    category = "Detection Algorithm"
    keywords = []

    # want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    autosend = Setting(True)

    hidden_size = Setting(64)
    loss = Setting('mean_squared_error')
    optimizer = Setting('Adam')
    epochs = Setting(10)
    batch_size = Setting(32)
    dropout_rate = Setting(0.2)
    l2_regularizer = Setting(0.1)
    validation_size = Setting(0.1)
    window_size = Setting(1)
    features = Setting(1)
    stacked_layers = Setting(1)
    preprocessing = Setting(True)
    verbose = Setting(1)
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

    # 

    hyperparameter_list = ['hidden_size',
                            'loss',
                            'optimizer',
                            'epochs',
                            'batch_size',
                            'dropout_rate',
                            'l2_regularizer',
                            'validation_size',
                            'window_size',
                            'features',
                            'stacked_layers',
                            'preprocessing',
                            'verbose',
                            'contamination',
                            'use_columns',
                            'exclude_columns',
                            'return_result',
                            'use_semantic_types',
                            'add_index_columns',
                            'error_on_no_input',
                            'return_semantic_type',
                            ]
    python_path = 'd3m.primitives.tods.detection_algorithm.deeplog'

    primitive = DeepLogPrimitive



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
        box2 = gui.widgetBox(self.controlArea, "Hyperparameter: Columns")

        line1 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line2 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line3 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line4 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line5 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line6 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)
        line7 = gui.widgetBox(box1, box=None, orientation=1, margin=None, spacing=20,)

        gui.lineEdit(line1, self, 'hidden_size', label='Hidden layer size of DeepLog network', callback=self.settings_changed)
        gui.lineEdit(line1, self, 'loss', label='loss', callback=self.settings_changed)
        gui.lineEdit(line2, self, 'optimizer', label='optimizer', callback=self.settings_changed)
        gui.lineEdit(line2, self, 'epochs', label='epochs', callback=self.settings_changed)
        gui.lineEdit(line3, self, 'batch_size', label='batch_size', callback=self.settings_changed)
        gui.lineEdit(line3, self, 'dropout_rate', label='dropout_rate', callback=self.settings_changed)
        gui.lineEdit(line4, self, 'l2_regularizer', label='l2_regularizer', callback=self.settings_changed)
        gui.lineEdit(line4, self, 'validation_size', label='validation_size', callback=self.settings_changed)
        gui.lineEdit(line5, self, 'window_size', label='window_size', callback=self.settings_changed)
        gui.lineEdit(line5, self, 'features', label='features', callback=self.settings_changed)
        gui.lineEdit(line6, self, 'stacked_layers', label='stacked_layers', callback=self.settings_changed)
        gui.lineEdit(line6, self, 'preprocessing', label='preprocessing', callback=self.settings_changed)
        gui.lineEdit(line7, self, 'verbose', label='verbose', callback=self.settings_changed)
        # gui.comboBox(box, self, 'algorithm', label='Algorithm used to compute the nearest neighbors.',
        #              items=['auto', 'ball_tree', 'kd_tree', 'brute'], callback=None)

        gui.doubleSpin(
            line7, self,
            "contamination",
            minv=0.,
            maxv=1.,
            step=0.001,
            label="Input contamination, float in (0,0.5].",
            callback=self.settings_changed
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )

        # return_subseq_inds = Setting(False)
        gui.checkBox(box2, self, "return_subseq_inds", label='If return subsequence index.',  callback=self.settings_changed)

        # use_semantic_types = Setting(False)
        gui.checkBox(box2, self, "use_semantic_types", label='Mannally select columns if active.',  callback=self.settings_changed)

        # use_columns = Setting(())
        gui.lineEdit(box2, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        # exclude_columns = Setting(())
        gui.lineEdit(box2, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

        # return_result = Setting(['append', 'replace', 'new'])
        gui.comboBox(box2, self, "return_result", label='Output results.', items=['new', 'append', 'replace'], sendSelectedValue = True, callback=self.settings_changed)

        # add_index_columns = Setting(False)
        gui.checkBox(box2, self, "add_index_columns", label='Keep index in the outputs.', callback=self.settings_changed)

        # error_on_no_input = Setting(True)
        gui.checkBox(box2, self, "error_on_no_input", label='Error on no input.', callback=self.settings_changed)

        # return_semantic_type = Setting(['https://metadata.datadrivendiscovery.org/types/Attribute',
        #                                 'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'])
        gui.comboBox(box2, self, "return_semantic_type", label='Semantic type attach with results.', 
                     items=['https://metadata.datadrivendiscovery.org/types/Attribute',
                            'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'], sendSelectedValue = True, callback=self.settings_changed)
        # Only for test
        #gui.button(box2, self, "Print Hyperparameters", callback=self._print_hyperparameter)

        gui.auto_apply(box2, self, "autosend", box=False)

        # self.data = None
        # self.info.set_input_summary(self.info.NoInput)
        # self.info.set_output_summary(self.info.NoOutput)

    # def _print_hyperparameter(self):
    #     print(self.IntVariable, type(self.IntVariable))
    #     print(self.FloatVariable, type(self.FloatVariable))
    #     print(self.BoolVariable, type(self.BoolVariable))
    #     print(self.TupleVariable, type(self.TupleVariable))
    #     print(self.ListVariable, type(self.ListVariable))
    #     print(self.EnumVariable, type(self.EnumVariable))
    #     print(self.BoundedInt, type(self.BoundedInt))
    #     print(self.BoundedFloat, type(self.BoundedFloat))
    #     print(self.contamination, type(self.contamination))
    #     print(self.return_subseq_inds, type(self.return_subseq_inds))
    #     print(self.use_columns, type(self.use_columns))
    #     print(self.exclude_columns, type(self.exclude_columns))
    #     print(self.return_result, type(self.return_result))
    #     print(self.use_semantic_types, type(self.use_semantic_types))
    #     print(self.add_index_columns, type(self.add_index_columns))
    #     print(self.error_on_no_input, type(self.error_on_no_input))
    #     print(self.return_semantic_type, type(self.return_semantic_type))


    #     self.commit()

    # 

    def _use_columns_callback(self):
        self.use_columns = eval(''.join(self.use_columns_buf))
        self.settings_changed()

    def _exclude_columns_callback(self):
        self.exclude_columns = eval(''.join(self.exclude_columns_buf))
        self.settings_changed()

#     @Inputs.ancestor
#     def set_ancestor(self, ancestor):
#         pass

#     def settings_changed(self):
#         self.commit()

#     def commit(self):
#         pass

# if __name__ == "__main__":
#     WidgetPreview(OWDeepLog).run(Orange.data.Table("iris"))