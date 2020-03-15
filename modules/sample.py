# coding=utf-8
"""
Created on 30.3.2018
Edited on 21.6.2018

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2018 Severi Jääskeläinen, Samuel Kaiponen, Heta Rekilä and
Sinikka Siironen

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (file named 'LICENCE').
"""
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä " \
             "\n Sinikka Siironen"
__version__ = "2.0"

import os
from modules.measurement import Measurements
from modules.measurement import Measurement
from modules.simulation import Simulations
from modules.simulation import Simulation


class Samples:
    """
    Class for handling multiple samples.
    """

    def __init__(self, request):
        """
        Initialize the Samples.

        Args:
            request: Which request the samples belong to.
        """
        self.request = request
        self.samples = []

        # These attributes are needed for handling tabs
        self.measurements = Measurements(self.request)
        self.simulations = Simulations(self.request)

    def add_sample(self, sample_path=None, name=""):
        """
        Create and add a Sample to the samples.

        Args:
            sample_path: The path of the sample to be added to the samples.
            name: Optional name for the sample.
        """
        if sample_path:
            sample_path, sample_dir = os.path.split(sample_path)
            dir_split = sample_dir.split("-")
            prefix = dir_split[0].split("_")
            serial_string = prefix[1]
            try:
                serial_number = int(serial_string)
                if name == "":
                    name = dir_split[1]
                sample = Sample(serial_number, self.request, sample_dir, name)
            except Exception as e:
                # Couldn't read sample's serial number from file path.
                print("Couldn't read sample's serial number from path. " +
                      str(e))
                return
        else:
            next_serial = self.request.get_running_int()
            sample_dir = "Sample_" + "%02d" % next_serial + "-" + name
            new_path = os.path.join(self.request.directory, sample_dir)
            sample = Sample(next_serial, self.request, sample_dir, name)
            self.request.increase_running_int_by_1()
            if not os.path.exists(new_path):
                os.makedirs(new_path)
        self.samples.append(sample)
        return sample

    def get_samples_and_measurements(self):
        """
        Collects all the samples and the measurement files under them into a
        dictionary.

        Return:
            A dictionary containing samples and their measurements.
        """
        all_samples_and_measurements = {}
        for sample in self.samples:
            all_samples_and_measurements[sample] = \
                sample.get_measurements_files()
        return all_samples_and_measurements

    def get_samples_and_simulations(self):
        """
        Collects all the samples and the simulation files under them into a
        dictionary.

        Return:
            A dictionary containing samples and their simulations.
        """
        all_samples_and_simulations = {}
        for sample in self.samples:
            all_samples_and_simulations[sample] = sample.get_simulation_files()
        return all_samples_and_simulations


class Sample:
    """
    Class for a sample.
    """

    def __init__(self, serial_number, request, directory, name=""):
        """
        Initialize the Sample.

        Args:
            serial_number: Serial number for sample.
            request: Which request the sample belongs to.
            name: Optional name for the sample.
        """
        self.name = name
        self.serial_number = serial_number
        self.request = request

        self.directory = directory

        self.measurements = Measurements(request)
        self.simulations = Simulations(request)

        self._running_int_measurement = 1
        self._running_int_simulation = 1

    def get_running_int_measurement(self):
        """
        Get running int for measurements,

        Return:
            Integer.
        """
        return self._running_int_measurement

    def increase_running_int_measurement_by_1(self):
        """
        Increase running int for measurement by one.
        """
        self._running_int_measurement = self._running_int_measurement + 1

    def get_running_int_simulation(self):
        """
        Get running int for simulations,

        Return:
            Integer.
        """
        return self._running_int_simulation

    def increase_running_int_simulation_by_1(self):
        """
            Increase running int for simulation by one.
        """
        self._running_int_simulation = self._running_int_simulation + 1

    def get_measurements_files(self):
        """
        Get measurements files inside sample folder.

        Return:
            A list of measurement file names.
        """
        all_measurements = []
        name_prefix = "Measurement_"
        all_dirs = os.listdir(os.path.join(self.request.directory,
                                           self.directory))
        all_dirs.sort()

        for directory in all_dirs:
            # Only handle directories that start with name_prefix
            if directory.startswith(name_prefix):
                try:
                    # Read measurment number from directory name
                    self._running_int_measurement = int(
                        directory[len(name_prefix):len(name_prefix) + 2])
                    for file in os.listdir(os.path.join(
                            self.request.directory, self.directory, directory)):
                        if file.endswith(".info"):
                            all_measurements.append(os.path.join(
                                self.request.directory, self.directory,
                                directory, file))
                except ValueError:
                    # Couldn't add measurement directory because the number
                    # could not be read
                    continue
        if all_measurements:
            # Increment running int so it's ready to use when creating new
            # measurement under this sample
            self.increase_running_int_measurement_by_1()
        return all_measurements

    def get_simulation_files(self):
        """Get .simulation files inside simulation directories.

        Return:
            A list of .simulation file paths.
        """
        all_simulations = []
        name_prefix = Simulation.DIRECTORY_PREFIX
        all_dirs = os.listdir(os.path.join(self.request.directory,
                                           self.directory))
        all_dirs.sort()

        for directory in all_dirs:
            # Only handle directories that start with name_prefix
            if directory.startswith(name_prefix):
                try:
                    # Read simulation number from directory name
                    self._running_int_simulation = int(
                        directory[len(name_prefix):len(name_prefix) + 2])
                    for file in os.listdir(os.path.join(
                            self.request.directory, self.directory, directory)):
                        if file.endswith(".simulation"):
                            all_simulations.append(os.path.join(
                                self.request.directory, self.directory,
                                directory, file))
                except ValueError:
                    # Couldn't add simulation directory because the number
                    # could not be read
                    continue
        if all_simulations:
            # Increment running int so it's ready to use when creating new
            # simulation under this sample
            self.increase_running_int_simulation_by_1()
        return all_simulations

    def remove_obj(self, obj_removed):
        """Removes given object from sample.
        Args:
            obj_removed: Object to remove.
        """
        if isinstance(obj_removed, Measurement):
            self.measurements.remove_obj(obj_removed)
        elif isinstance(obj_removed, Simulation):
            self.simulations.remove_obj(obj_removed)
