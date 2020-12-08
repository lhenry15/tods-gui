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

class OWExtractColumn(SingleInputWidget):
    name = "ExtractColumn"
    description = ("Extract column from data frame.")
    icon = "icons/scaler.svg"
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
    autosend = Setting(True)

    semantic_types_buf = Setting(('https://metadata.datadrivendiscovery.org/types/Attribute',))
    semantic_types = ('https://metadata.datadrivendiscovery.org/types/Attribute',)
    match_logic = Setting('any')
    negate = Setting(False)
    use_columns_buf = Setting(())
    use_columns = ()
    exclude_columns_buf = Setting(())
    exclude_columns = ()
    add_index_columns = Setting(False)

    python_path = 'd3m.primitives.tods.data_processing.extract_columns_by_semantic_types'
    hyperparameter_list = ['semantic_types',
                            'match_logic',
                            'negate',
                            'exclude_columns',
                            'use_columns',
                            'add_index_columns',                    
                            ]

    # def __init__(self):
    #     super().__init__()
    #     self.primitive_list.append("primitive"+str(len(self.primitive_list)+1))
    #     print(self.primitive_list)
    #     self._init_ui()
    #     self.hyperparameter = {'semantic_types':self.semantic_types,
    #                         'match_logic':self.match_logic,
    #                         'negate':self.negate,
    #                         'exclude_columns':self.exclude_columns,
    #                         'use_columns':self.use_columns,
    #                         'add_index_columns':self.add_index_columns,                       
    #                         }
    #     
    #     self.primitive_info = PrimitiveInfo(python_path = self.python_path,
    #                                     hyperparameter = self.hyperparameter,
    #                                     ancestors = {},
    #                                     )
        
    #     print(type(self.hyperparameter['semantic_types']))


    def _init_ui(self):
        # implement your user interface here (for setting hyperparameters)
        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Hyperparameter")

        gui.separator(self.controlArea)


        gui.lineEdit(box, self, "semantic_types_buf", label='semantic_types_buf',
                    callback=self._semantic_types_callback)

        gui.comboBox(box, self, "match_logic", label='Output match_logic.', items=['all', 'any', 'equal'],
                    sendSelectedValue = True,
                    callback=self.settings_changed)       

        gui.checkBox(box, self, "negate", label='negate', callback=self.settings_changed)

        gui.lineEdit(box, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        gui.lineEdit(box, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

        gui.checkBox(box, self, "add_index_columns", label='Keep index in the outputs.',  callback=self.settings_changed)         

        gui.auto_apply(box, self, "autosend", box=False)

        self.data = None
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)

    
    def _strtuple_inttuple(self, strtuple):
        inttuple = ()
        for index_str in strtuple:
            if index_str.isdigit():
                inttuple += (int(index_str),)
        print(inttuple)
        return inttuple

    def _use_columns_callback(self):
        self.use_columns = self._strtuple_inttuple(self.use_columns_buf)
        # print(self.use_columns)
        self.settings_changed()

    def _exclude_columns_callback(self):
        self.exclude_columns = self._strtuple_inttuple(self.exclude_columns_buf)
        # print(self.exclude_columns)
        self.settings_changed()
    
    def _semantic_types_callback(self):
        self.semantic_types = eval(''.join(self.semantic_types_buf))
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
    #     self.hyperparameter['semantic_types'] = self.semantic_types
    #     self.hyperparameter['match_logic'] = self.match_logic
    #     self.hyperparameter['negate'] = self.negate
    #     self.hyperparameter['use_columns'] = self.use_columns
    #     self.hyperparameter['exclude_columns'] = self.exclude_columns      
    #     self.hyperparameter['add_index_columns'] = self.add_index_columns
    #     self.primitive_info.hyperparameter = self.hyperparameter

    #     print(type(self.hyperparameter['semantic_types']))

    #     if self.Inputs.pipline_in is not None:
    #         self.Outputs.pipline_out.send([self.output_list + [self.primitive_info], self.python_path])

if __name__ == "__main__":
    WidgetPreview(OWExtractColumn).run(Orange.data.Table("iris"))
