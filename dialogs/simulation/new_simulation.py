# coding=utf-8
"""
Created on 26.2.2018
Updated on 6.4.2018

#TODO Description of Potku and copyright
#TODO Licence

"""
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n Sinikka Siironen"
__version__ = "2.0"


import logging
import os
from PyQt5 import uic, QtWidgets


class SimulationNewDialog(QtWidgets.QDialog):
    """Dialog creating a new simulation.
    """
    # def __init__(self, parent):
    def __init__(self):
        """Inits a new simulation dialog.
        TODO: Right now only the Cancel button works.
        Args:
            parent: Ibasoft class object.
        """
        super().__init__()
        # self.parent = parent
        
        self.ui = uic.loadUi(os.path.join("ui_files", "ui_new_simulation.ui"), self)

        self.ui.pushCreate.clicked.connect(self.__create_simulation)
        self.ui.pushCancel.clicked.connect(self.close)
        self.name = None
        
        self.exec_()

    def __create_simulation(self):
        self.name = self.ui.simulationNameLineEdit.text().replace(" ", "_")
        # TODO: Remove replace above to allow spaces in request names.
        # TODO: Get rid of print -> message window perhaps
        if not self.name:
            print("Request name required!")
            return
        self.close()
