"""

"""
import os
import sysconfig

import pkg_resources

import Orange


# Entry point for main Orange categories/widgets discovery
def widget_discovery(discovery):
    dist = pkg_resources.get_distribution("Orange3")
    pkgs = [
        "Orange.widgets.data",
        "Orange.widgets.visualize",
        "Orange.widgets.data_processing",
        "Orange.widgets.timeseries_processing",
        "Orange.widgets.feature_analysis",
        "Orange.widgets.detection_algorithm",
        "Orange.widgets.reinforcement"
    ]
    for pkg in pkgs:
        discovery.process_category_package(pkg, distribution=dist)


WIDGET_HELP_PATH = (
    ("{DEVELOP_ROOT}/doc/visual-programming/build/htmlhelp/index.html", None),
    (os.path.join(sysconfig.get_path("data"),
                  "share/help/en/orange3/htmlhelp/index.html"),
     None),
    ("https://docs.biolab.si/orange/3/visual-programming/", ""),
)
