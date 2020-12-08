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

from tods.feature_analysis.AutoCorrelation import *

class OWAutocorrelation(SingleInputWidget):
    name = "AutoCorrelation"
    description = ("AutoCorrelation.")
    icon = "icons/Autocorrelation.svg"
    category = "Feature Analysis"
    keywords = []

    # want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    autosend = Setting(True)

    unbiased = Setting(False)
    nlags = Setting(40)
    qstat = Setting(False)
    fft = Setting(False)
    alpha = Setting(0)
    missing = Setting("none")

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

    hyperparameter_list = ['unbiased',
                            'nlags',
                            'qstat',
                            'fft',
                            'alpha',
                            'missing',
                            'use_columns',
                            'exclude_columns',
                            'return_result',
                            'use_semantic_types',
                            'add_index_columns',
                            'error_on_no_input',
                            'return_semantic_type',
                            ]
    python_path = 'd3m.primitives.tods.feature_analysis.auto_correlation'

    primitive = AutoCorrelationPrimitive



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

        gui.comboBox(box, self, "unbiased", label='Unbiased (If True, then denominators for autocovariance are n-k, otherwise n)', 
                        items=[False, True],  sendSelectedValue = True, callback=self.settings_changed)
        gui.doubleSpin(
            box, self,
            'nlags',
            minv=0,
            maxv=100,  #TODO:Define upper bound correctly
            step=1,
            label="nlags (Number of lags to return autocorrelation for)",
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )

        gui.comboBox(box, self, 'qstat', label='qstat (If True, returns the Ljung-Box q statistic for each autocorrelationcoefficient)', 
                        items=[False, True], sendSelectedValue = True, callback=self.settings_changed)

        gui.comboBox(box, self, 'fft', label='fft (If True, computes the ACF via FFT)', items=[False, True], sendSelectedValue = True, callback=self.settings_changed)

        gui.doubleSpin(
            box, self,
            'alpha',
            minv=0.,
            maxv=1.,
            step=0.001,
            label="""If a number is given, the confidence intervals for the given level are returned.
                    For instance if alpha=.05, 95 % confidence intervals are returned where the standard deviation is computed according to Bartlett"s formula.""",
            callback=self.settings_changed
            # callbackOnReturn = True,
            # checked = "BoundedFloat"
        )


        gui.comboBox(box, self, 'missing',
                     label="""Specifying how the NaNs are to be treated. "none" performs no checks. "raise" raises an exception if NaN values are found. 
                            "drop" removes the missing observations and then estimates the autocovariances treating the non-missing as contiguous. 
                            "conservative" computes the autocovariance using nan-ops so that nans are removed when computing the mean
                            and cross-products that are used to estimate the autocovariance.
                            When using "conservative", n is set to the number of non-missing observations.""",
                     items=["none", "raise", "conservative", "drop"], sendSelectedValue = True, callback=self.settings_changed)

        # use_semantic_types = Setting(False)
        gui.checkBox(box, self, "use_semantic_types", label='Mannally select columns if active.',  callback=self.settings_changed)

        # use_columns = Setting(())
        gui.lineEdit(box, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        # exclude_columns = Setting(())
        gui.lineEdit(box, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

        # return_result = Setting(['append', 'replace', 'new'])
        gui.comboBox(box, self, "return_result", sendSelectedValue=True, label='Output results.', items=['new', 'append', 'replace'], callback=self.settings_changed)

        # add_index_columns = Setting(False)
        gui.checkBox(box, self, "add_index_columns", label='Keep index in the outputs.',  callback=self.settings_changed)

        # error_on_no_input = Setting(True)
        gui.checkBox(box, self, "error_on_no_input", label='Error on no input.',  callback=self.settings_changed)

        # return_semantic_type = Setting(['https://metadata.datadrivendiscovery.org/types/Attribute',
        #                                 'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'])
        gui.comboBox(box, self, "return_semantic_type", sendSelectedValue=True, label='Semantic type attach with results.', 
                        items=['https://metadata.datadrivendiscovery.org/types/Attribute',
                               'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'], callback=self.settings_changed)
        # Only for test
        #gui.button(box, self, "Print Hyperparameters", callback=self._print_hyperparameter)

        gui.auto_apply(box, self, "autosend", box=False)

    #     self.data = None
    #     self.info.set_input_summary(self.info.NoInput)
    #     self.info.set_output_summary(self.info.NoOutput)

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
        self.use_columns = eval(''.join(self.use_columns_buf))
        self.settings_changed()

#     @Inputs.ancestor
#     def set_ancestor(self, ancestor):
#         pass

#     def settings_changed(self):
#         self.commit()

#     def commit(self):
#         pass

# if __name__ == "__main__":
#     WidgetPreview(OWPyodKNN).run(Orange.data.Table("iris"))
