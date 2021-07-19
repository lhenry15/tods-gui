from d3m import index
from d3m.metadata.base import ArgumentType
from d3m.metadata.pipeline import Pipeline, PrimitiveStep
from d3m.metadata import hyperparams
import sys

def build_pipeline(pipepline_info, pipepline_mapping, stdout=None):

    default_stdout = sys.stdout
    if stdout is not None:
        sys.stdout = stdout

    # Creating pipeline
    pipeline_description = Pipeline()
    pipeline_description.add_input(name='inputs')

    for primitive_info in pipepline_info:
        print(primitive_info.python_path)
        print(primitive_info.hyperparameter)
        print(primitive_info.ancestors)

        if primitive_info.python_path == 'HEAD':
            dataset_fullname = primitive_info.hyperparameter['dataset_folder']
            print(dataset_fullname)
            continue

        elif primitive_info.python_path == 'ENDING':

            ancestors = primitive_info.ancestors
            end_step_num = pipepline_mapping[ancestors['inputs']] - 1
            pipeline_description.add_output(name='output predictions', data_reference='steps.' + str(end_step_num) + '.produce')

        else:
            # print(primitive_info.python_path)
            primitive = index.get_primitive(primitive_info.python_path)
            step = PrimitiveStep(primitive=primitive)

            hyperparameters = primitive_info.hyperparameter
            ancestors = primitive_info.ancestors

            # add add_inputs
            # print(ancestors)

            if ancestors['inputs'] != 0:
                for ances_key in ancestors.keys():
                    print(ances_key, ancestors[ances_key], pipepline_mapping[ancestors[ances_key]] - 1)

                    step_num = pipepline_mapping[ancestors[ances_key]] - 1
                    step.add_argument(name=ances_key, argument_type=ArgumentType.CONTAINER, data_reference='steps.' + str(step_num) + '.produce')

            else:
                step.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='inputs.0')

            # add add_hyperparameter
            for hyper in hyperparameters.keys():
                # print(hyper, hyperparameters[hyper], type(hyperparameters[hyper]))

                hyper_value = hyperparameters[hyper]

                step.add_hyperparameter(name=hyper, argument_type=ArgumentType.VALUE, data=hyper_value)

            step.add_output('produce')
            pipeline_description.add_step(step)

            # print('\n')

    # Output to json
    data = pipeline_description.to_json()
    with open('example_pipeline.json', 'w') as f:
        f.write(data)
        print(data)

    # yaml = pipeline_description.to_yaml()
    # with open('example_pipeline.yml', 'w') as f:
    #     f.write(yaml)
    # print(yaml)

    sys.stdout.flush()
    sys.stdout = default_stdout


import sys
import argparse
import os
import pandas as pd

from tods import generate_dataset, load_pipeline, evaluate_pipeline

from PyQt5.QtWidgets import QMessageBox, QWidget

def run_pipeline(pipepline_info, stdout=None):
    
    default_stdout = sys.stdout
    if stdout is not None:
        sys.stdout = stdout

    # this_path = os.path.dirname(os.path.abspath(__file__))

    dataset_folder = pipepline_info[0].hyperparameter['dataset_folder']
    if dataset_folder is None:
        tmp_QWidget = QWidget()
        QMessageBox.warning(tmp_QWidget, 'Attention!', 'You must choose a dataset folder!')
        del(tmp_QWidget)

    elif not os.path.exists(os.path.join(dataset_folder, 'datasetDoc.json')) \
            or not os.path.exists(os.path.join(dataset_folder, 'tables', 'learningData.csv')):
        tmp_QWidget = QWidget()
        QMessageBox.warning(tmp_QWidget, 'Attention!', 'No dataset in the folder!')
        del (tmp_QWidget)

    else:
        dataset_info = dataset_description(os.path.join(dataset_folder, 'datasetDoc.json'))
        dataset_fullname = os.path.join(dataset_folder, 'tables', 'learningData.csv')
        table_path = dataset_fullname
        target_index = dataset_info['ground_truth_index'] # what column is the target, up to revised!!!
        pipeline_path = './example_pipeline.json'
        metric = 'F1_MACRO' # F1 on both label 0 and 1

        print(target_index)

        # Read data and generate dataset
        df = pd.read_csv(table_path)
        dataset = generate_dataset(df, target_index)
        print(df)

        # df.to_csv('./temp.csv', index = False)

        print("------------------------------------------------------------------------------------------------")

        # Load the default pipeline
        pipeline = load_pipeline(pipeline_path)

        print("------------------------------------------------------------------------------------------------")
        
        # # Run the pipeline
        pipeline_result = evaluate_pipeline(dataset, pipeline, metric)
        # print(pipeline_result)
        # print(type(pipeline_result))
        # from axolotl.backend.d3m_grpc.server import encode_scores
        # import axolotl
        # axolotl.backend.d3m_grpc.server.encode_scores(pipeline_result)


        # ranking = {
        #     'metric': 'RANK',
        #     'value': pipeline_result.rank,
        #     'randomSeed': 0,
        #     'fold': 0,
        # }

        # all_scores = pipeline_result.scores.append(ranking, ignore_index=True)
        # print(all_scores)

        # print("------------------------------------------------------------------------------------------------")
        # print(pipeline_result.outputs[0])
        # print("------------------------------------------------------------------------------------------------")
        # print(pipeline_result.outputs[1])
        # print("------------------------------------------------------------------------------------------------")
        # print(type(pipeline_result.outputs[0]))
        # print("------------------------------------------------------------------------------------------------")
        # print("------------------------------------------------------------------------------------------------")
        # print("------------------------------------------------------------------------------------------------")
        # print("------------------------------------------------------------------------------------------------")
        # # print(pipeline_result.outputs[0]['outputs'])
        # print(pipeline_result.outputs[0].values())
        # print("------------------------------------------------------------------------------------------------")
        print(pipeline_result.outputs)

        # print(pipeline_result.outputs[0] == pipeline_result.outputs[1])

        # print(type(pipeline_result.outputs))


        # lst = pipeline_result.outputs[0].values()

        # for i in range(10):
        #     print(lst[i])

        # print(pipeline_result.outputs[0]['outputs.0'])
        # print(type(pipeline_result.outputs[0]['outputs.0']))
        # for i in range(10):
        #     print(pipeline_result.outputs[0]['outputs.0'][i])

        df2 = pipeline_result.outputs[0]['outputs.0']
        # df2.drop(['d3mIndex'], axis=1)
        df2 = df2.iloc[: , 1:]
        # df2.rename(columns={'ground_truth': 'pipeline_result_ground_truth'})
        # data.rename(columns={'groud_truth':'pipeline_result_groud_truth'}, inplace=True)
        # temp.to_csv('./temp2.csv', index = False)
        
        df_out = pd.concat([df, df2], axis=1)
        # df_out.columns = ['d3mIndex','timestamp','value','ground_truth','pipeline_result_ground_truth']
        # df_out.set_axis([*df.columns[:-1], 'pipeline_result_ground_truth'], axis=1, inplace=False)
        df_out.columns = [*df_out.columns[:-1], 'pipeline_result_ground_truth']
        df_out.to_csv('./temp2.csv', index = False)

        return df_out

    sys.stdout.flush()
    sys.stdout = default_stdout


import json

def dataset_description(description_fname):

    dataset_info = {}
    with open(description_fname, 'r') as f:
        description = json.loads(f.read())
        # print(description['dataResources'][0]['columns'][7]['colName'])
        for column_index, column in enumerate(description['dataResources'][0]['columns']):
            if column['colName'] == 'ground_truth':
                # print(column_index)
                dataset_info['ground_truth_index'] = column_index
                return dataset_info

