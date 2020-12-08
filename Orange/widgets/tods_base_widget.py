from functools import reduce
from types import SimpleNamespace

from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import QGridLayout

from Orange.widgets import gui, widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.utils.state_summary import format_summary_details
from Orange.widgets.widget import Input, Output

from d3m.primitive_interfaces.base import PrimitiveBase

class TODS_BaseWidget(widget.OWWidget):
    primitive_list = []
    icon = None
    count = 0

    def __init__(self):
        super().__init__()
        gui.rubber(self.controlArea)

    def settings_changed(self):
        self.commit()
        return conzer


    def commit(self):
        pass


class PrimitiveInfo:
    def __init__(self, python_path, id, hyperparameter, ancestors):
        self.python_path = python_path
        self.id = id
        self.hyperparameter = hyperparameter
        self.ancestors = ancestors

    def display(self):
        print('python_path:', self.python_path)
        print('id:', self.id)
        print('hyperparameter:', self.hyperparameter)
        print('ancestors:', self.ancestors)


class SingleInputWidget(TODS_BaseWidget):

    primitive = PrimitiveBase

    class Inputs:
        pipline_in = Input("One Input Primitve", list)

    class Outputs:
        pipline_out = Output("Output results", list)

    def __init__(self):
        super().__init__()
        TODS_BaseWidget.count += 1
        # self.primitive_list.append("primitive"+str(len(self.primitive_list)+1))
        # print(self.primitive_list)
        self._init_ui()

        if self.primitive.metadata is not None:
            self.hyperparameter_list = list(self.primitive.metadata.get_hyperparams().defaults().keys())
            self.python_path = self.primitive.metadata._generate_metadata_for_primitive()['original_python_path']

        # else:
        #     self.hyperparameter_list = []
        #     self.python_path = 'd3m.primitives.tods.'

        # self.hyperparameter: {'hyperparameter name': hyperparameter value}
        # self.hyperparameter_list: {'hyperparameter name'}
        self.hyperparameter = {}
        for i in self.hyperparameter_list:
            hyper_tmp = getattr(self, i, None)
            if hyper_tmp is not None:
                self.hyperparameter[i] = hyper_tmp # eval('self.' + i)

        self.id = TODS_BaseWidget.count
        self.primitive_info = PrimitiveInfo(python_path = self.python_path,
                                            id = self.id,
                                            hyperparameter = self.hyperparameter,
                                            ancestors = {},)

    @Inputs.pipline_in
    def set_pipline_in(self, pipline_in):
        if pipline_in is not None:
            self.output_list = pipline_in[0]
            self.ancestors_id = pipline_in[1]

            self.primitive_info.ancestors['inputs'] = self.ancestors_id
            self.Outputs.pipline_out.send([self.output_list + [self.primitive_info], self.id])
        
        else:
            self.primitive_info.ancestors = {}
            self.Outputs.pipline_out.send(None)

    def settings_changed(self):
        self.commit()
        
    def commit(self):
        for i in self.hyperparameter_list:
            hyper_tmp = getattr(self, i, None)
            if hyper_tmp is not None:
                self.hyperparameter[i] = hyper_tmp # eval('self.' + i)

        self.primitive_info.hyperparameter = self.hyperparameter

        if self.Inputs.pipline_in is not None:
            self.Outputs.pipline_out.send([self.output_list + [self.primitive_info], self.id])

# if __name__ == "__main__":
#     WidgetPreview(OWPyodAE).run([[],0])
