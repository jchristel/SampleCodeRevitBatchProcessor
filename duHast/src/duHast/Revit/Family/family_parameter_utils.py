"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families parameter helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import clr
import System

# import common library
# utility functions for most commonly used Revit API tasks
from duHast.Revit.Common import transaction as rTran

# class used for stats reporting
from duHast.Utilities.Objects import result as res

# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb


def set_family_parameter_value_by_storage_type(param_w, manager, value):
    return_value = res.Result()
    try:
        if param_w.StorageType == rdb.StorageType.Double:
            # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
            # whatever internal units of measure Revit uses. SetValueString expects your value to
            # be in whatever the current DisplayUnitType (units of measure) the document is set to
            # for the UnitType associated with the parameter.
            #
            # So SetValueString is basically how the Revit GUI works.
            manager.SetValueString(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        elif param_w.StorageType == rdb.StorageType.ElementId:
            manager.Set(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        elif param_w.StorageType == rdb.StorageType.Integer:
            manager.Set(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        elif param_w.StorageType == rdb.StorageType.String:
            manager.Set(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        else:
            return_value.update_sep(False, "Parameter storage type is not supported!")

    except Exception as e:
        return_value.update_sep(
            False, "failed to set parameter value with exception: {}".format(e)
        )
    return return_value


def set_family_parameter_value(doc, manager, fam_para, value):
    # get the parameter
    param_w = manager.get_Parameter(fam_para.Definition.Name)
    # set-up action to be executed in transaction
    def action():
        action_return_value = res.Result()
        try:
            # attempt to change parameter value
            action_return_value = set_family_parameter_value_by_storage_type(
                param_w, manager, value
            )
        except Exception as e:
            action_return_value.status = False
            action_return_value.message = (
                fam_para.Definition.Name
                + " : Failed to set parameter value: with exception: "
                + str(e)
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "Setting parameter value")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def set_parameter_formula(doc, manager, fam_para, formula):
    def action():
        action_return_value = res.Result()
        try:
            # set parameter formula
            manager.SetFormula(fam_para, formula)
            action_return_value.message = (
                fam_para.Definition.Name + " : parameter formulas successfully set."
            )
            action_return_value.result.append(fam_para)
        except Exception as e:
            action_return_value.status = False
            action_return_value.message = (
                fam_para.Definition.Name
                + " : Failed to set parameter formula: with exception: "
                + str(e)
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "Setting parameter formula")
    return_value = rTran.in_transaction(transaction, action)
    return return_value
