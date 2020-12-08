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
from Orange.widgets.tods_base_widget import TODS_BaseWidget, PrimitiveInfo

class OWConstructPrediction(TODS_BaseWidget):
    name = "ConstructPrediction"
    description = ("Concate groundtruth into predicted results.")
    icon = "icons/predictive.svg"
    category = "Time Series Processing"
    keywords = []

    class Inputs:
        pipline_in1 = Input("Inputs", list)
        pipline_in2 = Input("Reference", list)

    class Outputs:
        pipline_out = Output("Output results", list)

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

    # def __del__(self):
    #     self.primitive.pop()
    #     print(self.primitive_list)

    def __init__(self):
        super().__init__()
        TODS_BaseWidget.count += 1
        self.primitive_list.append("primitive"+str(len(self.primitive_list)+1))
        print(self.primitive_list)
        self._init_ui()

        self.pipline_in1_flag, self.pipline_in2_flag = False, False
        
        # Info will be passed
        self.hyperparameter = {'use_columns':self.use_columns,
                                'exclude_columns':self.exclude_columns,                             
                            }
        self.python_path = 'd3m.primitives.tods.data_processing.construct_predictions'
        self.id = TODS_BaseWidget.count

        self.primitive_info = PrimitiveInfo(python_path = self.python_path,
                                            id = self.id,
                                            hyperparameter = self.hyperparameter,
                                            ancestors = {},
                                            )

    def _init_ui(self):
        # implement your user interface here (for setting hyperparameters)
        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Hyperparameter")

        gui.separator(self.controlArea)

        gui.lineEdit(box, self, "use_columns_buf", label='Column index to use when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._use_columns_callback)

        gui.lineEdit(box, self, "exclude_columns_buf", label='Column index to exclude when use_semantic_types is activated. Tuple, e.g. (0,1,2)',
                     validator=None, callback=self._exclude_columns_callback)

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


    @Inputs.pipline_in1
    def set_pipline_in1(self, pipline_in1):
        if pipline_in1 is not None:
            self.pipline_in1_flag = True
            self.in1 = pipline_in1          
        
        else:           
            self.pipline_in1_flag = False
        
        self.exist_both_inputs()

    @Inputs.pipline_in2
    def set_pipline_in2(self, pipline_in2):
        if pipline_in2 is not None:
            self.pipline_in2_flag = True
            self.in2 = pipline_in2

        else:           
            self.pipline_in2_flag = False
        
        self.exist_both_inputs()


    def settings_changed(self):
        self.commit()

    def commit(self):
        self.hyperparameter['use_columns'] = self.use_columns
        self.hyperparameter['exclude_columns'] = self.exclude_columns

        self.primitive_info.hyperparameter = self.hyperparameter

        if self.Inputs.pipline_in is not None:
            self.Outputs.pipline_out.send([self.output_list + [self.primitive_info], self.id])

    def exist_both_inputs(self):
        if self.pipline_in1_flag and self.pipline_in2_flag:
            output_list_sub1 = self.in1[0]
            ancestors_path_sub1 = self.in1[1]

            output_list_sub2 = self.in2[0]
            ancestors_path_sub2 = self.in2[1]

            output_list = []
            already_in_output_list=set()

            for i in output_list_sub1:
                if i.python_path not in already_in_output_list:
                    output_list.append(i)
                    already_in_output_list.add(i.python_path)

            for i in output_list_sub2:
                if i.python_path not in already_in_output_list:
                    output_list.append(i)
                    already_in_output_list.add(i.python_path)

            self.primitive_info.ancestors['inputs'] = ancestors_path_sub1
            self.primitive_info.ancestors['reference'] = ancestors_path_sub2

            output_list.append(self.primitive_info)
            self.Outputs.pipline_out.send([output_list, self.id])

            return

        elif self.pipline_in1_flag or self.pipline_in2_flag:
            self.primitive_info.ancestors = {}
            self.Outputs.pipline_out.send(None)

        else:
            self.primitive_info.ancestors = {}
            self.Outputs.pipline_out.send(None)


if __name__ == "__main__":
    WidgetPreview(OWConstructPrediction).run(Orange.data.Table("iris"))
