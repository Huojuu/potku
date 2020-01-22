# coding=utf-8
"""
Created on 19.1.2020

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2013-2020 TODO

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

__author__ = "Juhani Sundell"
__version__ = ""  # TODO

import unittest
import os
import platform
import math

from modules.depth_files import DepthProfileHandler
from modules.element import Element
from tests.utils import verify_files, get_sample_data_dir

# These tests require reading files from the sample data directory
# Path to the depth file directory
_DIR_PATH = os.path.join(get_sample_data_dir(),
                         "Ecaart-11-mini",
                         "Tof-E_65-mini",
                         "depthfiles")

# List of depth files to be read from the directory
_FILE_NAMES = [
    "depth.C",
    "depth.F",
    "depth.H",
    "depth.Li",
    "depth.Mn",
    "depth.O",
    "depth.Si",
    "depth.total"
]

_DEFAULT_MSG = "reading files in TestDepthProfileHandling"

# Combined absolute file paths
_file_paths = [os.path.join(_DIR_PATH, fname) for fname in _FILE_NAMES]

__os = platform.system()

# Expected checksum for all depth files
# Checksums are valid as of 20.1.2020
# If depths files are modified or removed, some of the tests will be skipped
if __os == "Windows":
    _CHECKSUM = "a74f489d60475d4ef36963a093f109d1"
elif __os == "Linux":
    _CHECKSUM = "4aafa2ba9142642c5f9393bf298c6280"
elif __os == "Darwin":
    _CHECKSUM = ""  # TODO
else:
    _CHECKSUM = None


class TestDepthProfileHandling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_elements = [
            Element.from_string("C"),
            Element.from_string("F"),
            Element.from_string("H"),
            Element.from_string("Li"),
            Element.from_string("Mn"),
            Element.from_string("O"),
            Element.from_string("Si")
        ]
        cls.some_elements = [
            Element.from_string("F"),
            Element.from_string("H"),
            Element.from_string("Mn"),
            Element.from_string("Si")
        ]
        cls.handler = DepthProfileHandler()

    @verify_files(_file_paths, _CHECKSUM, msg=_DEFAULT_MSG)
    def test_file_reading(self):
        """Tests that the files can be read and all given elements are
        stored in the profile handler"""
        self.handler.read_directory(_DIR_PATH, self.all_elements)
        self.check_handler_profiles(self.handler, self.all_elements)

        # Read just some of the elements. This should remove existing
        # profiles from the handler
        self.handler.read_directory(_DIR_PATH, self.some_elements)
        self.check_handler_profiles(self.handler, self.some_elements)

    def check_handler_profiles(self, handler, elements):
        """Checks that handler contains all the expected element
        profiles"""
        # Check that the handler contains absolute profiles
        # of all elements and a profile called total
        elem_set = set(str(elem) for elem in elements)
        abs_profiles = handler.get_absolute_profiles()
        self.assertEqual(
            set(abs_profiles.keys()).difference(elem_set),
            set(["total"]))

        # Relative profiles also contain all elements, but no total
        # profile
        rel_profiles = handler.get_relative_profiles()
        self.assertEqual(set(rel_profiles.keys()),
                         elem_set)

    @verify_files(_file_paths, _CHECKSUM, msg=_DEFAULT_MSG)
    def test_calculate_ratios(self):
        all_elem_names = set(str(elem) for elem in self.all_elements)
        some_elem_names = set(str(elem) for elem in self.all_elements)
        self.handler.read_directory(_DIR_PATH, self.all_elements)

        # All elements are ignored, so all values returned by the calculation
        # are None
        percentages, moes = self.handler.calculate_ratios(
            all_elem_names, -math.inf, math.inf, 3)

        self.assertEqual(all_elem_names, set(percentages.keys()))
        self.assertEqual(all_elem_names, set(moes.keys()))
        for pval, mval in zip(percentages.values(), moes.values()):
            self.assertIsNone(pval)
            self.assertIsNone(mval)

        # Only some elements are ignored
        percentages, moes = self.handler.calculate_ratios(
            some_elem_names, -math.inf, math.inf, 3)
        self.assertEqual(all_elem_names, set(percentages.keys()))
        self.assertEqual(all_elem_names, set(moes.keys()))
        for p, m in zip(percentages, moes):
            if p in some_elem_names:
                self.assertIsNone(percentages[p])
            else:
                self.assertTrue(0 <= percentages[p] <= 100)
            if m in some_elem_names:
                self.assertIsNone(moes[m])
            else:
                self.assertTrue(0 <= moes[m])


if __name__ == "__main__":
    unittest.main()