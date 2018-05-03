# coding=utf-8
# TODO: Add licence information

from modules.beam import Beam

__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n" \
             "Sinikka Siironen"
__version__ = "2.0"


class Run:

    def __init__(self, beam=Beam(), fluence=1.00e+12, current=1.07,
                 charge=0.641, time=600):
        self.beam = beam
        self.fluence = fluence
        self.current = current
        self.charge = charge
        self.time = time

