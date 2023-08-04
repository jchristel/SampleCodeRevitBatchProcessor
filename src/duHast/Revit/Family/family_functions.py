"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Family elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

from Autodesk.Revit.DB import FilteredElementCollector, Family

def get_name_to_family_dict(rvt_doc):
    '''
    Create a dictionary of family name and the Family element
    :param rvt_doc: Revit document
    :type rvt_doc: Autodesk.Revit.DB.Document
    :return: Dictionary of family name and Family element
    :rtype: dict
    '''

    #Get all the families in the model
    all_families = FilteredElementCollector(rvt_doc).OfClass(Family).ToElements()
    #create a dictionary of family name and family object
    family_dict = {fam.Name: fam for fam in all_families}
    return family_dict