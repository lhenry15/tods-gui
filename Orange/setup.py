import os


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config = Configuration('Orange', parent_package, top_path)
    config.add_subpackage('data')
    config.add_subpackage('misc')
    config.add_subpackage('preprocess')
    config.add_subpackage('statistics')
    config.add_subpackage('tests')
    config.add_subpackage('widgets')

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
