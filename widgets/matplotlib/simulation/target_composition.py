# coding=utf-8
"""
Created on 26.3.2018
Updated on 26.3.2018
"""
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n Sinikka Siironen"

from PyQt5 import QtCore, QtWidgets
import matplotlib.pyplot as pyplot
import matplotlib.patches as patches

from widgets.matplotlib.base import MatplotlibWidget


class MatplotlibTargetCompositionWidget(MatplotlibWidget):
    """Matplotlib target composition widget. Using this widget, the user
    can edit target composition for the simulation.
    """

    def __init__(self, parent, icon_manager):
        """Inits

        Args:
            parent: A SimulationDepthProfileWidget class object.
            icon_manager: An iconmanager class object.
        """

        super().__init__(parent)
        self.canvas.manager.set_title("Target Composition")
        self.axes.fmt_xdata = lambda x: "{0:1.0f}".format(x)
        self.axes.fmt_ydata = lambda y: "{0:1.0f}".format(y)
        self.__icon_manager = icon_manager

        self.name_y_axis = "Concentration"
        self.name_x_axis = "Depth"

        self.on_draw()

    def on_draw(self):
        """Draw method for matplotlib.
        """
        self.axes.clear()  # Clear old stuff

        self.axes.set_ylabel(self.name_y_axis.title())
        self.axes.set_xlabel(self.name_x_axis.title())

        # Remove axis ticks and draw
        self.remove_axes_ticks()
        self.canvas.draw()

    def add_layer(self):
        """Adds a layer in the target composition.
        """
        layer = patches.Rectangle(
                (0.0, 0.0),  # (x,y)
                0.3,  # width
                1.0,  # height
            )
        self.axes.add_patch(layer)
        self.canvas.draw_idle()


    def __toggle_tool_drag(self):
        if self.__button_drag.isChecked():
            self.mpl_toolbar.mode_tool = 1
        else:
            self.mpl_toolbar.mode_tool = 0
            # self.elementSelectionButton.setChecked(False)
        # self.elementSelectUndoButton.setEnabled(False)
        # self.elementSelectionSelectButton.setChecked(False)
        self.canvas.draw_idle()

    def __toggle_tool_zoom(self):
        if self.__button_zoom.isChecked():
            self.mpl_toolbar.mode_tool = 2
        else:
            self.mpl_toolbar.mode_tool = 0
            # self.elementSelectionButton.setChecked(False)
        # self.elementSelectUndoButton.setEnabled(False)
        # self.elementSelectionSelectButton.setChecked(False)
        self.canvas.draw_idle()

    def __toggle_drag_zoom(self):
        self.__tool_label.setText("")
        if self.__button_drag.isChecked():
            self.mpl_toolbar.pan()
        if self.__button_zoom.isChecked():
            self.mpl_toolbar.zoom()
        self.__button_drag.setChecked(False)
        self.__button_zoom.setChecked(False)
