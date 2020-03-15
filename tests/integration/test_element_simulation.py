# coding=utf-8
"""
Created on 07.03.2020

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2020 TODO

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (file named 'LICENCE').
"""
__author__ = ""  # TODO
__version__ = ""  # TODO

import unittest
import tempfile
import tests.utils as utils

from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock

from modules.request import Request
from modules.element_simulation import ElementSimulation
from modules.detector import Detector
from modules.foil import CircularFoil
from modules.layer import Layer
from modules.element import Element
from modules.simulation import Simulation
from modules.global_settings import GlobalSettings
from modules.recoil_element import RecoilElement
from modules.point import Point


class TestElementSimulationSettings(unittest.TestCase):
    @patch("modules.mcerd.MCERD.__init__", return_value=None)
    @patch("modules.mcerd.MCERD.run")
    def test_something(self, mock_mcerd_run: Mock,  mock_mcerd: Mock):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # File paths
            tmp_dir = Path(tmp_dir)
            mesu_file = tmp_dir / "mesu"
            det_dir = tmp_dir / "det"
            sim_dir = tmp_dir / "Sample_01-foo" / \
                      f"{Simulation.DIRECTORY_PREFIX}_01-bar"
            simu_file = sim_dir / "bar.simulation"

            # Request
            request = Request(tmp_dir, "test_req",
                              GlobalSettings(),
                              {})

            self.assertEqual(tmp_dir, request.directory)
            self.assertEqual("test_req", request.request_name)

            # Sample
            request.samples.add_sample(name="foo")
            sample = request.samples.samples[0]
            self.assertEqual("foo", sample.name)
            self.assertEqual(request, sample.request)

            # Simulation
            sim_foils = [CircularFoil("Foil1", 7.0, 256.0,
                                  [Layer("Layer_12C",
                                         [Element("C", 12.011, 1)],
                                         0.1, 2.25, 0.0)])]
            sim_detector = Detector(det_dir, mesu_file, foils=sim_foils)
            sample.simulations.add_simulation_file(
                sample, simu_file, 0)
            sim: Simulation = sample.simulations.get_key_value(0)
            sim.detector = sim_detector
            self.assertEqual("bar", sim.name)
            self.assertEqual(request, sim.request)
            self.assertEqual(sample, sim.sample)

            # ElementSimulation
            rec_elem = RecoilElement(Element.from_string("Fe"),
                                     [Point((1, 1))], name="recoil_name")
            sim.add_element_simulation(rec_elem)
            elem_sim: ElementSimulation = sim.element_simulations[0]
            elem_sim.number_of_preions = 2
            elem_sim.number_of_ions = 3
            self.assertEqual(request, elem_sim.request)
            self.assertEqual("Fe-Default", elem_sim.get_full_name())

            utils.disable_logging()

            # Setting both to True should mean request settings are used
            elem_sim.use_default_settings = True
            sim.use_request_settings = True
            self.assert_expected_settings(elem_sim, request, sim,
                                          mock_mcerd)

            elem_sim.use_default_settings = True
            sim.use_request_settings = False
            self.assert_expected_settings(elem_sim, request, sim,
                                          mock_mcerd)

            elem_sim.use_default_settings = False
            sim.use_request_settings = True
            elem_sim.start(1, 1)
            self.assert_expected_settings(elem_sim, request, sim,
                                          mock_mcerd)

            elem_sim.use_default_settings = False
            sim.use_request_settings = False
            self.assert_expected_settings(elem_sim, request, sim,
                                          mock_mcerd)

    def assert_expected_settings(self, elem_sim, request, sim, mock_mcerd):
        elem_sim.start(1, 1)
        settings = mock_mcerd.call_args[0][0]
        self.assertEqual(get_expected_settings(elem_sim, request, sim),
                         settings)


def get_expected_settings(elem_sim: ElementSimulation, request: Request,
                          simulation: Simulation):
    if simulation.use_request_settings:
        detector = request.default_detector
        target = request.default_target
        run = request.default_run
    else:
        detector = simulation.detector
        target = simulation.target
        run = simulation.run

    if elem_sim.use_default_settings:
        expected_sim = request.default_element_simulation
    else:
        expected_sim = elem_sim

    return {
        "simulation_type": elem_sim.simulation_type,
        "number_of_ions": expected_sim.number_of_ions,
        "number_of_ions_in_presimu": expected_sim.number_of_preions,
        "number_of_scaling_ions": expected_sim.number_of_scaling_ions,
        "number_of_recoils": elem_sim.number_of_recoils,
        "minimum_scattering_angle": expected_sim.minimum_scattering_angle,
        "minimum_main_scattering_angle":
            expected_sim.minimum_main_scattering_angle,
        "minimum_energy_of_ions": expected_sim.minimum_energy,
        "simulation_mode": expected_sim.simulation_mode,
        "seed_number": 1,
        "beam": run.beam,
        "target": target,
        "detector": detector,
        "recoil_element": elem_sim.recoil_elements[0],
        "sim_dir": elem_sim.directory
    }


if __name__ == '__main__':
    unittest.main()