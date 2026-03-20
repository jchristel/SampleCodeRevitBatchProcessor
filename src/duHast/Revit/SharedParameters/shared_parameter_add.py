"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a function to bind a shared parameter to a category.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
based on building coder article:
https://thebuildingcoder.typepad.com/blog/2012/04/adding-a-category-to-a-shared-parameter-binding.html

"""


import Autodesk.Revit.DB as rdb

# custom result class
from duHast.Utilities.Objects import result as res

# import InTransaction from common module
from duHast.Revit.Common import transaction as rTran
from duHast.Revit.Common.parameter_grouping import PARAMETER_GROUPING_TO_GROUP_TYPE_ID

from duHast.Revit.SharedParameters.shared_parameters import (
    check_whether_shared_parameters_by_name_is_family_parameter,
)

from duHast.Revit.SharedParameters.Objects.shared_parameter_data import ParameterModel
from duHast.Revit.SharedParameters.shared_parameter_load_def_file import load_shared_parameter_file

def bind_shared_parameter(
    doc,
    category,
    parameter_name,
    group_name,
    parameter_type,
    is_visible,
    is_instance,
    parameter_grouping,
    shared_parameter_filepath,
):
    """
    Binds a shared parameter to a revit category.

    Refer building coder article referenced in header


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param category: The built in category, to which the parameter will be bound.
    :type category: Autodesk.Revit.DB.BuiltInCategory
    :param parameter_name: The parameter name.
    :type parameter_name: str
    :param group_name: The group under which the parameter appears in shared parameter text file.
    :type group_name: str
    :param paramType: The parameter type. (Area, vs text vs... (deprecated in Revit 2022!)
    :type paramType: Autodesk.Revit.DB.ParameterType
    :param is_visible: Is parameter visible in UI to users.
    :type is_visible: bool
    :param is_instance: True parameter is an instance parameter, otherwise type parameter.
    :type is_instance: bool
    :param parameter_grouping: Where parameter appears in properties section in UI.
    :type parameter_grouping: str
    :param shared_parameter_filepath: Fully qualified file path to shared parameter text file.
    :type shared_parameter_filepath: str

    :return:
        Result class instance.

        - Parameter binding status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter.

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        app = doc.Application

        # check if we are going to get something valid:
        if doc.Settings.Categories.get_Item(category) != None:
            # This is needed already here to
            # store old ones for re-inserting
            cat_set = app.Create.NewCategorySet()

            # Loop all Binding Definitions
            # IMPORTANT NOTE: Categories.Size is ALWAYS 1 !?
            # For multiple categories, there is really one
            # pair per each category, even though the
            # Definitions are the same...

            iter = doc.ParameterBindings.ForwardIterator()
            iter.Reset()
            while iter.MoveNext():
                if iter.Key != None:
                    definition = iter.Key
                    elem_bind = iter.Current
                    # check parameter name match
                    if parameter_name == definition.Name:
                        try:
                            cat = doc.Settings.Categories.get_Item(category)
                            if elem_bind.Categories.Contains(cat):
                                # check parameter type
                                if definition.ParameterType != parameter_type:
                                    return_value.status = False
                                    return_value.append_message (
                                        "{}: wrong parameter type: {}".format(
                                            parameter_name, definition.ParameterType
                                        )
                                    )
                                    return return_value
                                # check binding type
                                if is_instance:
                                    if elem_bind.GetType() != rdb.InstanceBinding:
                                        return_value.status = False
                                        return_value.append_message ("{}: wrong binding type (looking for instance but got type)".format(
                                            parameter_name
                                        ))
                                        return return_value
                                else:
                                    if elem_bind.GetType() != rdb.TypeBinding:
                                        return_value.status = False
                                        return_value.append_message("{}: wrong binding type (looking for type but got instance)".format(
                                            parameter_name
                                        ))
                                        return return_value

                                # Check Visibility - cannot (not exposed)
                                # If here, everything is fine,
                                # ie already defined correctly
                                return_value.append_message ("{}: Parameter already bound to category: {}".format(
                                    parameter_name, cat.Name
                                ))
                                return return_value
                        except Exception as e:
                            return_value.append_message(
                                "{} : Failed to check parameter binding with exception: {}".format(
                                    parameter_name, e
                                )
                            )
                        # If here, no category match, hence must
                        # store "other" cats for re-inserting
                        else:
                            for cat_old in elem_bind.Categories:
                                cat_set.Insert(cat_old)

            # If here, there is no Binding Definition for
            # it, so make sure Param defined and then bind it!
            def_file = load_shared_parameter_file(doc, shared_parameter_filepath)
            def_group = def_file.Groups.get_Item(group_name)
            if def_group == None:
                def_group = def_file.Groups.Create(group_name)
            if def_group.Definitions.Contains(
                def_group.Definitions.Item[parameter_name]
            ):
                definition = def_group.Definitions.Item[parameter_name]
            else:
                opt = rdb.ExternalDefinitionCreationOptions(
                    parameter_name, parameter_type
                )
                opt.Visible = is_visible
                definition = def_group.Definitions.Create(opt)

            # get category from builtin category
            cat_object = doc.Settings.Categories.get_Item(category)
            cat_set.Insert(cat_object)

            bind = None
            if is_instance:
                bind = app.Create.NewInstanceBinding(cat_set)
            else:
                bind = app.Create.NewTypeBinding(cat_set)

            # There is another strange API "feature".
            # If param has EVER been bound in a project
            # (in above iter pairs or even if not there
            # but once deleted), Insert always fails!?
            # Must use .ReInsert in that case.
            # See also similar findings on this topic in:
            # http://thebuildingcoder.typepad.com/blog/2009/09/adding-a-category-to-a-parameter-binding.html
            # - the code-idiom below may be more generic:

            def action():
                action_return_value = res.Result()
                try:
                    if doc.ParameterBindings.Insert(
                        definition, bind, parameter_grouping
                    ):
                        action_return_value.append_message(
                            "{} : parameter successfully bound to: {}".format(
                                parameter_name, cat_object.Name
                            )
                        )
                        return action_return_value
                    else:
                        if doc.ParameterBindings.ReInsert(
                            definition, bind, parameter_grouping
                        ):
                            action_return_value.append_message (
                                "{} : parameter successfully bound to: {}".format(
                                    parameter_name, cat_object.Name
                                )
                            )
                            return action_return_value
                        else:
                            action_return_value.status = False
                            action_return_value.append_message (
                                "{} : failed to bind parameter to: {}".format(
                                    parameter_name, cat_object.Name
                                )
                            )
                except Exception as e:
                    action_return_value.status = False
                    action_return_value.append_message ("{} : Failed to bind parameter to: {} with exception: {}".format(
                        parameter_name, cat_object.Name, e
                    ))
                return action_return_value

            transaction = rdb.Transaction(doc, "Binding parameter")
            return_value = rTran.in_transaction(transaction, action)
        else:
            return_value.update_sep(
                False, "Failed to get category object for: {}".format(category)
            )
        return return_value

    except Exception as e:
        return_value.status = False
        return_value.append_message (
            "{} : Failed to bind parameter with exception: {}".format(parameter_name, e)
        )
    return return_value


def add_shared_parameter_to_family(para, mgr, doc, def_file, parameter_modifier=None):
    """
    Adds a shared parameter definition to a family document.

    :param para: shared parameter object containing parameter info
    :type para: :class:`.ParameterModel`
    :param mgr: The family manager object
    :type mgr: Autodesk.Revit.DB.FamilyManager
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param def_file: The shared parameter definition file.
    :type def_file: _type_
    :param parameter_modifier: (Optional) A function that takes the family manager, the parameter and the parameter value as input and modifies the parameter value after it has been added to the family. Can be used to set a default value, formula, or other modifications to the parameter value after it has been added to the family.
    :type parameter_modifier: function

    :return:
        Result class instance.

        - True if added successfully. False if an exception occurred.
        - result.message will contain the name of the shared parameter.
        - .result.result will contain the family parameter object.

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    found_para = False
    try:

        if isinstance(para, ParameterModel) == False:
            raise TypeError("para must be of type ParameterModel. Got {} instead.".format(type(para)))
        
        # check if a parameter with the same name already exists in the family, if so, return and do not add parameter
        family_shared_parameter = (
            check_whether_shared_parameters_by_name_is_family_parameter(doc, para.name)
        )

        if family_shared_parameter != None:
            # return existing parameter in result.result 
            return_value.result.append(family_shared_parameter)
            return_value.append_message (
                para.name + " : parameter already exists in family: " + family_shared_parameter.Definition.Name
            )
            return return_value
        
        # loop through parameters and try to find matching one to be added from parameter file
        # loop through all definition groups
        for group in def_file.Groups:
            # loop through para's within definition group
            for def_para in group.Definitions:
                # check whether this is the parameter we are after
                if def_para.Name != para.name:
                    # jump to next parameter
                    continue

                # check if we have a valid group type id:
                group_type_id = PARAMETER_GROUPING_TO_GROUP_TYPE_ID.get(para.group_type_id,None)
                if group_type_id == None:
                    raise ValueError("Invalid group type id: {}. Please provide one of the following: {}".format(
                        para.group_type_id, list(PARAMETER_GROUPING_TO_GROUP_TYPE_ID.keys())
                    ))
                
                # set up an action to add parameter
                def action():
                    action_return_value = res.Result()
                    try:
                        # add parameter depending on name, forge type id using the group type id and is_type_parameter
                        fam_para = mgr.AddParameter(
                            def_para, group_type_id, not(para.is_type_parameter)
                        )

                        # check if anything needs to be modified on the parameter (value, formula, etc.) using the parameter_modifier function, if provided
                        if parameter_modifier != None:
                            try:
                                modify_result = parameter_modifier(mgr, fam_para, para.parameter_value)
                                action_return_value.update(modify_result)
                            except Exception as e:
                                action_return_value.update_sep(False, "Failed to modify parameter value with exception: {}".format(e))
                        else:
                            action_return_value.append_message("No parameter modifier provided, skipping parameter value modification.")

                        action_return_value.append_message(
                            para.name + " : parameter successfully added."
                        )
                        action_return_value.result.append(fam_para)
                    except Exception as e:
                        action_return_value.status = False
                        action_return_value.append_message (
                            para.name
                            + " : Failed to add shared parameter: with exception: "
                            + str(e)
                        )
                    return action_return_value

                transaction = rdb.Transaction(doc, "Adding shared parameter")
                return_value = rTran.in_transaction(transaction, action)
                # set flag for parameter found
                found_para = True

            # check whether inner loop found matching parameter
            if found_para:
                # get out of outer loop
                break

    except Exception as e:
        return_value.status = False
        return_value.append_message (
            para.name + " : Failed to add parameter to family with exception: " + str(e)
        )

    if found_para == False:
        return_value.status = False
        return_value.append_message (
            para.name + " : No match for parameter found in shared parameter file."
        )

    return return_value


def add_multiple_shared_parameters_to_family(doc, parameter_data):
    """
    Adds multiple shared parameters to a family document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_data: List of ParameterModel objects containing parameter info for parameters to be added.
    :type parameter_data: list[tuple]

    :return:
        Result class instance.

        - True if added successfully. False if an exception occurred.
        - result.message will contain the name of the shared parameter.
        - .result.result will contain the family parameter object.

        On exception (handled by optimizer itself!):
    
    """

    return_value = res.Result()

    try:
        # check if parameter data is in correct format
        if isinstance(parameter_data, list) == False:
            raise TypeError("parameter_data must be of type list. Got {} instead.".format(type(parameter_data)))
        if all(isinstance(x, ParameterModel) for x in parameter_data) == False:
            raise TypeError("All items in parameter_data must be of type ParameterModel.")
        
        # check this is a family document
        if doc.IsFamilyDocument == False:
            return_value.update_sep(False, "Document is not a family document.")
            return return_value
        
        # get the family manager
        family_manager = doc.FamilyManager

        # add parameters and values
        for single_para in parameter_data:
            # get the shard parameter file definition ( there can be a different file for each parameter )
            return_value.append_message("Atempting to open share parameter file at: <{}>".format(single_para.shared_parameter_file_path))
            shared_parameter_definition_file = load_shared_parameter_file(doc=doc, path=single_para.shared_parameter_file_path)
            if shared_parameter_definition_file == None:
                raise Exception("Shared parameter file not found")
            
            return_value.append_message("Found shared parameter file: {}".format(single_para.shared_parameter_file_path))

            # check if the value of the parameter is set or if it is a formula, if so, set up a parameter modifier function to modify the parameter value after it has been added to the family
            # check if the parameter value is a function which needs to be evaluated, if so run that function first
            parameter_value_is_derived_from_function = False
            parameter_value_from_function = None
            if callable(single_para.parameter_value):
                return_value.append_message("Parameter value is a function, attempting to evaluate function to get parameter value.")
                parameter_value_is_derived_from_function = True
                try:
                    parameter_value_from_function = single_para.parameter_value(doc)
                    # check if the value is a string, is so add quotes around it to be able to set it as a formula later if needed
                    if isinstance(parameter_value_from_function, str):
                        parameter_value_from_function = '"{}"'.format(parameter_value_from_function)
                    return_value.append_message("Function evaluated successfully, got value: {}".format(parameter_value_from_function))
                except Exception as e:
                    return_value.update_sep(False, "Failed to evaluate parameter value function with exception: {}".format(e))
                    return return_value

            parameter_modifier = None
            if single_para.parameter_value != None and single_para.value_is_formula == True:
               
                # set up inline function to set parameter value as formula, this is needed to be able to pass the parameter value from the outer scope into the function which will be run in the transaction
                def parameter_modifier(mgr, parameter, parameter_value_original):
                    modifier_return_value = res.Result()
                    parameter_value_to_set=parameter_value_original
                    
                    # check if the parameter value is the result of a function call
                    if parameter_value_is_derived_from_function:
                        parameter_value_to_set = parameter_value_from_function
                   
                    modifier_return_value.append_message("Setting parameter value as formula: {}, {}".format(parameter_value_to_set, type(parameter_value_to_set)))
                    try:
                        mgr.SetFormula(parameter,parameter_value_to_set)
                    except Exception as e:
                        modifier_return_value.status = False
                        modifier_return_value.append_message("Failed to set parameter value as formula with exception: {}".format(e))
                    return modifier_return_value
            elif single_para.parameter_value != None and single_para.value_is_formula == False:
               
                # setup inline function to set parameter value as a simple value, this is needed to be able to pass the parameter value from the outer scope into the function which will be run in the transaction
                def parameter_modifier(mgr, parameter, parameter_value_original):
                    modifier_return_value = res.Result()
                    parameter_value_to_set=parameter_value_original

                    # check if the parameter value is the result of a function call
                    if parameter_value_is_derived_from_function:
                        parameter_value_to_set = parameter_value_from_function
                    modifier_return_value.append_message("Setting parameter value as value: {}, {}".format(parameter_value_to_set, type(parameter_value_to_set)))
                    
                    try:
                        mgr.Set(parameter, parameter_value_to_set)
                    except Exception as e:
                        modifier_return_value.status = False
                        modifier_return_value.append_message("Failed to set parameter value with exception: {}".format(e))
                    return modifier_return_value
            else:  
                parameter_modifier = None

            # add the parameter to the family
            add_para_result = add_shared_parameter_to_family(
                para=single_para, 
                mgr=family_manager, 
                doc=doc, 
                def_file=shared_parameter_definition_file,
                parameter_modifier=parameter_modifier
            )
            
            return_value.update(add_para_result)

    except Exception as e:
        return_value.update_sep(False,
            "Failed to add multiple shared parameters to family with exception: " + str(e)
        )
    return return_value


def bind_shared_parameters_to_new_category(
    rvt_doc, target_params, target_cat, target_param_grp, type_binding=False
):
    """
    Takes a list of shared parameter definitions and creates a binding to a new category. Will
    add category to an existing binding if one exists already
    :param rvt_doc: Revit document
    :type rvt_doc: Autodesk.Revit.DB.Document
    :param target_params: List of shared parameter definitions
    :type target_params: list[Autodesk.Revit.DB.ExternalDefinition]
    :param target_cat: Category to bind to
    :type target_cat: BuiltInCategory
    :param target_param_grp: Parameter Group new parameters will appear in
    :type target_param_grp: BuiltInParameterGroup
    :param type_binding: True if type binding, False if instance binding
    :type type_binding: bool
    :return: List of successful bindings, list of errors
    :rtype: tuple
    """
    new_cat_set = rvt_doc.Application.Create.NewCategorySet()
    new_cat_set.Insert(target_cat)
    if type_binding:
        new_binding = rvt_doc.Application.Create.NewTypeBinding(new_cat_set)
    else:
        new_binding = rvt_doc.Application.Create.NewInstanceBinding(new_cat_set)
    binding_map = rvt_doc.ParameterBindings
    target_cat_name = rdb.Category.GetCategory(rvt_doc, target_cat.Id).Name

    outlist = []
    errors = []

    t = rdb.Transaction(rvt_doc, "Bind new category to shared parameters")
    t.Start()

    for sp_def in target_params:
        ex_binding = binding_map.Item[sp_def]
        if ex_binding:
            ex_binding_cats = [cat.Name for cat in ex_binding.Categories]
            if target_cat_name in ex_binding_cats:
                outlist.append(
                    "{} already bound to {}".format(sp_def.Name, target_cat_name)
                )
                continue
            try:
                ex_binding.Categories.Insert(target_cat)
                rvt_doc.ParameterBindings.ReInsert(sp_def, ex_binding)
                outlist.append("Bound {} to {}".format(sp_def.Name, target_cat.Name))
            except:
                errors.append(
                    "Could add {} to existing binding for {}".format(
                        target_cat.Name, sp_def.Name
                    )
                )
        else:
            try:
                binding_map.Insert(sp_def, new_binding, target_param_grp)
                outlist.append("Bound {} to {}".format(sp_def.Name, target_cat.Name))
            except:
                errors.append(
                    "Could not add {} to new binding for {}".format(
                        target_cat.Name, sp_def.Name
                    )
                )

    t.Commit()

    return outlist, errors
