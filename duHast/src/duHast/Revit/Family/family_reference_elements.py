'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions to change the reference type of reference planes and curve based elements.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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


import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import parameter_get_utils as rParaGet, parameter_set_utils as rParaSet
from duHast.Utilities import result as res
from duHast.Revit.Family.family_element_utils import get_all_curve_based_elements_in_family


def set_ref_planes_to_not_a_reference(doc):
    ''' 
    This will set any reference plane with reference type 'weak' within a family to reference type 'not a reference'.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return:
        Result class instance.
        - result.status: (bool) True if at least one reference plane type was successfully changed otherwise False
        - result.message: one row entry per reference plane requiring reference type change
        - result.result: not used
    :rtype: :class:`.Result`
    '''

    '''    
    Revit API reference types and their int value:
    ('ref name ', 'Left', ' reference type as int ', 0, ' reference type as string ', 'Left')
    ('ref name ', 'Center (Left/Right)', ' reference type as int ', 1, ' reference type as string ', 'Center (Left/Right)')
    ('ref name ', 'Right', ' reference type as int ', 2, ' reference type as string ', 'Right')
    ('ref name ', 'Front', ' reference type as int ', 3, ' reference type as string ', 'Front')
    ('ref name ', 'Reference Plane', ' reference type as int ', 4, ' reference type as string ', 'Center (Front/Back)')
    ('ref name ', 'Back', ' reference type as int ', 5, ' reference type as string ', 'Back')
    ('ref name ', 'Reference Plane', ' reference type as int ', 6, ' reference type as string ', 'Bottom')
    ('ref name ', 'Reference Plane', ' reference type as int ', 7, ' reference type as string ', 'Center (Elevation)')
    ('ref name ', 'Top', ' reference type as int ', 8, ' reference type as string ', 'Top')
    ('ref name ', 'Reference Plane', ' reference type as int ', 12, ' reference type as string ', 'Not a Reference')
    ('ref name ', 'Reference Plane', ' reference type as int ', 13, ' reference type as string ', 'Strong Reference')
    ('ref name ', 'Reference Plane', ' reference type as int ', 14, ' reference type as string ', 'Weak Reference')
    '''

    result = res.Result()
    result.update_sep(True, 'Changing reference status of reference planes...')
    match_at_all = False
    collector_ref_planes = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
    for ref_p in collector_ref_planes:
        value_int = rParaGet.get_built_in_parameter_value(
            ref_p,
            rdb.BuiltInParameter.ELEM_REFERENCE_NAME,
            rParaGet.get_parameter_value_as_integer)
        # check if an update is required (id is greater then 12)
        if (value_int > 13):
            result_change = rParaSet.set_built_in_parameter_value(
                doc,
                ref_p,
                rdb.BuiltInParameter.ELEM_REFERENCE_NAME,
                '12'
                )
            # set overall flag to indicate that at least one element was changed
            if(result_change.status == True and match_at_all == False):
                match_at_all = True
            result.update(result_change)
    if(match_at_all == False):
        result.status = False
        result.message = 'No reference planes found requiring reference type update'
    return result


def set_symbolic_and_model_lines_to_not_a_reference(doc):
    ''' 
    This will set any model or symbolic curve in a family with reference type 'weak' to reference type 'not a reference'.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return:
        Result class instance.
        - result.status: (bool) True if at least one curve reference type was successfully changed otherwise False
        - result.message: one row entry per curve element requiring reference type change
        - result.result: not used
    :rtype: :class:`.Result`
    '''

    '''
    Revit API
    ('ref name ', 'Model Lines', ' reference type as int ', 0, ' reference type as string ', 'Not a Reference')
    ('ref name ', 'Model Lines', ' reference type as int ', 1, ' reference type as string ', 'Weak Reference')
    ('ref name ', 'Model Lines', ' reference type as int ', 2, ' reference type as string ', 'Strong Reference')
    ('ref name ', 'Symbolic Lines', ' reference type as int ', 0, ' reference type as string ', 'Not a Reference')
    ('ref name ', 'Symbolic Lines', ' reference type as int ', 1, ' reference type as string ', 'Weak Reference')
    ('ref name ', 'Symbolic Lines', ' reference type as int ', 2, ' reference type as string ', 'Strong Reference')
    '''

    result = res.Result()
    result.update_sep(True, 'Changing reference status of model and symbolic curves...')
    match_at_all = False
    curves = get_all_curve_based_elements_in_family(doc)
    for curve in curves:
        # get the current reference type
        value_int = rParaGet.get_built_in_parameter_value(
            curve,
            rdb.BuiltInParameter.ELEM_IS_REFERENCE,
            rParaGet.get_parameter_value_as_integer)
        # check if an update is required (id equals 1)
        if (value_int == 1):
            result_change = rParaSet.set_built_in_parameter_value(
                doc,
                curve,
                rdb.BuiltInParameter.ELEM_IS_REFERENCE,
                '0'
                )
            # set overall flag to indicate that at least one element was changed
            if(result_change.status == True and match_at_all == False):
                match_at_all = True
            result.update(result_change)
    if(match_at_all == False):
        result.status = False
        result.message = 'No curve elements found requiring reference type update'
    return result