from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import (
    QFormLayout, QCheckBox, QLineEdit, QWidget, QVBoxLayout, QLabel
)
from orangecanvas.application.settings import UserSettingsDialog
from orangecanvas.document.usagestatistics import UsageStatistics
from orangecanvas.utils.overlay import NotificationOverlay

from orangewidget.workflow.mainwindow import OWCanvasMainWindow

from AnyQt.QtCore import (
    Qt, QObject, QEvent, QSize, QUrl, QFile, QByteArray, QFileInfo,
    QSettings, QStandardPaths, QAbstractItemModel, QT_VERSION)

from AnyQt.QtWidgets import (
    QMainWindow, QWidget, QAction, QActionGroup, QMenu, QMenuBar, QDialog,
    QFileDialog, QMessageBox, QVBoxLayout, QSizePolicy, QToolBar, QToolButton,
    QDockWidget, QApplication, QShortcut, QPlainTextEdit,
    QPlainTextDocumentLayout, QFileIconProvider
)

from AnyQt.QtGui import (
    QColor, QIcon, QDesktopServices, QKeySequence, QTextDocument,
    QWhatsThisClickedEvent, QShowEvent, QCloseEvent
)

from orangecanvas.application.canvastooldock import CanvasToolDock, QuickCategoryToolbar, \
                            CategoryPopupMenu, popup_position_from_source

from orangecanvas.gui.quickhelp import QuickHelpTipEvent

from orangecanvas.gui.utils import message_critical, message_question, message_warning, message_information

from orangecanvas import config

from typing import (
    Optional, List, Union, Any, cast, Dict, Callable, IO, Sequence, Iterable,
    Tuple, TypeVar,
)

import pkg_resources

import os, logging

log = logging.getLogger(__name__)

class OUserSettingsDialog(UserSettingsDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        w = self.widget(0)  # 'General' tab
        layout = w.layout()
        assert isinstance(layout, QFormLayout)
        cb = QCheckBox(self.tr("Automatically check for updates"))
        cb.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        layout.addRow("Updates", cb)
        self.bind(cb, "checked", "startup/check-updates")

        # Reporting Tab
        tab = QWidget()
        self.addTab(tab, self.tr("Reporting"),
                    toolTip="Settings related to reporting")

        form = QFormLayout()
        line_edit_mid = QLineEdit()
        self.bind(line_edit_mid, "text", "reporting/machine-id")
        form.addRow("Machine ID:", line_edit_mid)

        box = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        cb1 = QCheckBox(
            self.tr("Share"),
            toolTip=self.tr(
                "Share anonymous usage statistics to improve Orange")
        )
        self.bind(cb1, "checked", "reporting/send-statistics")
        cb1.clicked.connect(UsageStatistics.set_enabled)
        layout.addWidget(cb1)
        box.setLayout(layout)
        form.addRow(self.tr("Anonymous Statistics"), box)
        label = QLabel("<a "
                       "href=\"https://orange.biolab.si/statistics-more-info\">"
                       "More info..."
                       "</a>")
        label.setOpenExternalLinks(True)
        form.addRow(self.tr(""), label)

        tab.setLayout(form)

        # Notifications Tab
        tab = QWidget()
        self.addTab(tab, self.tr("Notifications"),
                    toolTip="Settings related to notifications")

        form = QFormLayout()

        box = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        cb = QCheckBox(
            self.tr("Enable notifications"), self,
            toolTip="Pull and display a notification feed."
        )
        self.bind(cb, "checked", "notifications/check-notifications")

        layout.addWidget(cb)
        box.setLayout(layout)
        form.addRow(self.tr("On startup"), box)

        notifs = QWidget(self, objectName="notifications-group")
        notifs.setLayout(QVBoxLayout())
        notifs.layout().setContentsMargins(0, 0, 0, 0)

        cb1 = QCheckBox(self.tr("Announcements"), self,
                        toolTip="Show notifications about Biolab announcements.\n"
                                "This entails events and courses hosted by the developers of "
                                "Orange.")

        cb2 = QCheckBox(self.tr("Blog posts"), self,
                        toolTip="Show notifications about blog posts.\n"
                                "We'll only send you the highlights.")
        cb3 = QCheckBox(self.tr("New features"), self,
                        toolTip="Show notifications about new features in Orange when a new "
                                "version is downloaded and installed,\n"
                                "should the new version entail notable updates.")

        self.bind(cb1, "checked", "notifications/announcements")
        self.bind(cb2, "checked", "notifications/blog")
        self.bind(cb3, "checked", "notifications/new-features")

        notifs.layout().addWidget(cb1)
        notifs.layout().addWidget(cb2)
        notifs.layout().addWidget(cb3)

        form.addRow(self.tr("Show notifications about"), notifs)
        tab.setLayout(form)


class MainWindow(OWCanvasMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_overlay = NotificationOverlay(self.scheme_widget)
        self.notification_server = None

        # add build and run pipeline buttons
        # self._tods_run()

    def _tods_run(self):

        self.run_pipeline_action = QAction(
            self.tr("Run"), self,
            objectName="run-action",
            toolTip=self.tr("Run Pipeline"),
            triggered=self.run_pipeline,
        )

        self.build_pipeline_action = QAction(
            self.tr("Build"), self,
            objectName="build-action",
            toolTip=self.tr("Build Pipeline"),
            triggered=self.run_pipeline,
        )

        # self.zoom_in_action.setIcon(canvas_icons("arrow-right.svg"))
        # self.welcome_action.setIcon(canvas_icons("arrow-right.svg"))
        self.run_pipeline_action.setIcon(canvas_icons("arrow-right.svg"))
        self.build_pipeline_action.setIcon(canvas_icons("default-widget.svg"))

        dock_actions = [
            self.show_properties_action,
            self.canvas_align_to_grid_action,
            self.canvas_text_action,
            self.canvas_arrow_action,
            self.freeze_action,
            self.dock_help_action,
            # self.zoom_in_action,
            # self.welcome_action,
            self.build_pipeline_action,
            self.run_pipeline_action,
        ]

        # Tool bar in the collapsed dock state (has the same actions as
        # the tool bar in the CanvasToolDock
        actions_toolbar = QToolBar(orientation=Qt.Vertical)
        actions_toolbar.setFixedWidth(38)
        actions_toolbar.layout().setSpacing(0)

        actions_toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        for action in dock_actions:
            self.canvas_toolbar.addAction(action)
            button = self.canvas_toolbar.widgetForAction(action)
            button.setPopupMode(QToolButton.DelayedPopup)

            actions_toolbar.addAction(action)
            button = actions_toolbar.widgetForAction(action)
            button.setFixedSize(38, 30)
            button.setPopupMode(QToolButton.DelayedPopup)


    def run_pipeline(self):
        pass

    def build_pipeline(self):
        pass


    def open_canvas_settings(self):
        # type: () -> None
        """Reimplemented."""
        dlg = OUserSettingsDialog(self, windowTitle=self.tr("Preferences"))
        dlg.show()
        status = dlg.exec_()
        if status == 0:
            self.user_preferences_changed_notify_all()

    def set_notification_server(self, notif_server):
        self.notification_server = notif_server

        # populate notification overlay with current notifications
        for notif in self.notification_server.getNotificationQueue():
            self.notification_overlay.addNotification(notif)

        notif_server.newNotification.connect(self.notification_overlay.addNotification)
        notif_server.nextNotification.connect(self.notification_overlay.nextWidget)

    def create_new_window(self):  # type: () -> CanvasMainWindow
        window = super().create_new_window()
        window.set_notification_server(self.notification_server)
        return window

    # def event(self, event):
    #     # type: (QEvent) -> bool
    #     if event.type() == QEvent.StatusTip and \
    #             isinstance(event, QuickHelpTipEvent):
    #         if event.priority() == QuickHelpTipEvent.Normal:
    #             self.dock_help2.showHelp(event.html())
    #         elif event.priority() == QuickHelpTipEvent.Temporary:
    #             self.dock_help2.showHelp(event.html(), event.timeout())
    #         elif event.priority() == QuickHelpTipEvent.Permanent:
    #             self.dock_help2.showPermanentHelp(event.html())
    #         return True
    #
    #     elif event.type() == QEvent.WhatsThisClicked:
    #         event = cast(QWhatsThisClickedEvent, event)
    #         url = QUrl(event.href())
    #         if url.scheme() == "help" and url.authority() == "search":
    #             try:
    #                 url = self.help.search(url)
    #                 self.show_help(url)
    #             except KeyError:
    #                 log.info("No help topic found for %r", url)
    #                 message_information(
    #                     self.tr("There is no documentation for this widget."),
    #                     parent=self)
    #         elif url.scheme() == "action" and url.path():
    #             action = self.findChild(QAction, url.path())
    #             if action is not None:
    #                 action.trigger()
    #             else:
    #                 log.warning("No target action found for %r", url.toString())
    #         return True
    #
    #     return super().event(event)

def canvas_icons(name):
    # type: (str) -> QIcon
    """
    Return the named canvas icon.
    """
    icon_file = QFile("canvas_icons:" + name)
    if icon_file.exists():
        return QIcon("canvas_icons:" + name)
    else:
        return QIcon(resource_filename(os.path.join("icons", name)))

def resource_filename(path):
    """
    Return the resource filename path relative to the top level package.
    """
    return pkg_resources.resource_filename(config.__name__, path)





