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
    def __init__(self, samples):
        """Inits a new simulation dialog.

        Args:
            samples: Samples of request.
        """
        super().__init__()
        # self.parent = parent
        
        self.ui = uic.loadUi(os.path.join("ui_files", "ui_new_simulation.ui"), self)

        self.ui.pushCreate.clicked.connect(self.__create_simulation)
        self.ui.pushCancel.clicked.connect(self.close)
        self.name = None

        for sample in samples:
            self.ui.samplesComboBox.addItem("Sample " + "%02d" % sample.serial_number + " " + sample.name)
        
        self.exec_()

    def __create_simulation(self):
        self.name = self.ui.simulationNameLineEdit.text().replace(" ", "_")
        self.sample = self.ui.samplesComboBox.currentText()
        if not self.name:
            print("Simulation name required!")
            return
        self.close()
