"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit exports related tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


from test.Revit.TestUtils.run_revit_tests import RevitRunTest
from duHast.Utilities import result as res

# import test classes
from test.Revit.Exports import export_model_to_nwc, export_model_to_ifc

def run_export_tests(doc):
    """
    Runs all annotation related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()

    # start tests -> should run ... tests first since they form
    # part of ... tests

    run_tests = [
        ['Export model to NWC', export_model_to_nwc.ExportModelToNWC],
        ['Export model to IFC', export_model_to_ifc.ExportModelToIFC],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value