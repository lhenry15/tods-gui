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

class OWColumnParser(SingleInputWidget):
    name = "ColumnParser"
    description = ("Convert each column into specific data type.")
    icon = "icons/Continuize.svg"
    category = "Time Series Processing"
    keywords = []

    # class Inputs:
    #     pipline_in = Input("One Input Primitve", list)

    # class Outputs:
    #     pipline_out = Output("Output results", list)

    want_main_area = False
    buttons_area_orientatio = Qt.Vertical
    resizing_enabled = False


    # set default hyperparameters here
    test_treatment = Setting(0)
    autosend = Setting(True)
    
    use_columns_buf = Setting(())
    use_columns = ()
    exclude_columns_buf = Setting(())
    exclude_columns = ()
    return_result = Setting('replace')

    add_index_columns = Setting(True)
    parse_categorical_target_columns = Setting(False)
    replace_index_columns = Setting(True)
    fuzzy_time_parsing = Setting(True)

    hyperparameter_list = ['use_columns',
                            'exclude_columns',
                            'return_result',
                            'add_index_columns',
                            'parse_categorical_target_columns',
                            'replace_index_columns',
                            'fuzzy_time_parsing',                             
                            ]
    python_path = 'd3m.primitives.tods.data_processing.column_parser'
    # def __init__(self):
    #     super().__init__()
    #     self.primitive_list.append("primitive"+str(len(self.primitive_list)+1))
    #     print(self.primitive_list)
    #     self._init_ui()

    #     self.hyperparameter = {'use_columns':self.use_columns,
    #                             'exclude_columns':self.exclude_columns,
    #                             'return_result':self.return_result,
    #                             'add_index_columns':self.add_index_columns,
    #                             'parse_categorical_target_columns':self.parse_categorical_target_columns,
    #                             'replace_index_columns':self.replace_index_columns,
    #                             'fuzzy_time_parsing':self.fuzzy_time_parsing,                               
    #                         }
    #     

    #     self.primitive_info = PrimitiveInfo(python_path = self.python_path,
    #                                     hyperparameter = self.hyperparameter,
    #                                     ancestors = {},
    #                                     )


    def _init_ui(self):
        # implement your user interface here (for setting hyperparameters)
        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Hyperparameter")

        gui.separator(self.controlArea)       

        gui.lineEdit(box, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        gui.lineEdit(box, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

        gui.comboBox(box, self, "return_result", label='Output results.', items=['new', 'append', 'replace'],
                    sendSelectedValue = True,
                    callback=self.settings_changed)

        gui.checkBox(box, self, "add_index_columns", label='add_index_columns',  callback=self.settings_changed)

        gui.checkBox(box, self, "parse_categorical_target_columns", label='parse_categorical_target_columns',  callback=self.settings_changed)

        gui.checkBox(box, self, "replace_index_columns", label='replace_index_columns',  callback=self.settings_changed)

        gui.checkBox(box, self, "fuzzy_time_parsing", label='fuzzy_time_parsing',  callback=self.settings_changed)         

        gui.auto_apply(box, self, "autosend", box=False)

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)

    
    def _use_columns_callback(self):
        self.use_columns = eval(''.join(self.use_columns_buf))
        self.settings_changed()

    def _exclude_columns_callback(self):
        self.exclude_columns = eval(''.join(self.exclude_columns_buf))
        self.settings_changed()


    # @Inputs.pipline_in
    # def set_pipline_in(self, pipline_in):
    #     if pipline_in is not None:
    #         self.output_list = pipline_in[0]
    #         self.ancestors_path = pipline_in[1]

    #         self.primitive_info.ancestors['inputs'] = self.ancestors_path
    #         self.Outputs.pipline_out.send([self.output_list + [self.primitive_info], self.python_path])
        
    #     else:           
    #         self.primitive_info.ancestors = {}
    #         self.Outputs.pipline_out.send(None)

    # def settings_changed(self):
    #     self.commit()

    # def commit(self):
    #     self.hyperparameter['use_columns'] = self.use_columns
    #     self.hyperparameter['exclude_columns'] = self.exclude_columns
    #     self.hyperparameter['return_result'] = self.return_result
    #     self.hyperparameter['add_index_columns'] = self.add_index_columns
    #     self.hyperparameter['parse_categorical_target_columns'] = self.parse_categorical_target_columns
    #     self.hyperparameter['replace_index_columns'] = self.replace_index_columns
    #     self.hyperparameter['fuzzy_time_parsing'] = self.fuzzy_time_parsing

    #     self.primitive_info.hyperparameter = self.hyperparameter

    #     if self.Inputs.pipline_in is not None:
    #         self.Outputs.pipline_out.send([self.output_list + [self.primitive_info], self.python_path])


if __name__ == "__main__":
    WidgetPreview(OWColumnParser).run(Orange.data.Table("iris"))
