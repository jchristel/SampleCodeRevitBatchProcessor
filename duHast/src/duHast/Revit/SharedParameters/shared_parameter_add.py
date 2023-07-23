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


def load_shared_parameter_file(doc, path):
    """
    Loads a shared parameter file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param path: Fully qualified file path to shared parameter text file.
    :type path: str

    :return: The opened shared parameter file.
    :rtype: Autodesk.Revit.DB.DefinitionFile
    """

    app = doc.Application
    app.SharedParametersFilename = path
    return app.OpenSharedParameterFile()


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
                                    return_value.message = (
                                        "{}: wrong parameter type: {}".format(
                                            parameter_name, definition.ParameterType
                                        )
                                    )
                                    return return_value
                                # check binding type
                                if is_instance:
                                    if elem_bind.GetType() != rdb.InstanceBinding:
                                        return_value.status = False
                                        return_value.message = "{}: wrong binding type (looking for instance but got type)".format(
                                            parameter_name
                                        )
                                        return return_value
                                else:
                                    if elem_bind.GetType() != rdb.TypeBinding:
                                        return_value.status = False
                                        return_value.message = "{}: wrong binding type (looking for type but got instance)".format(
                                            parameter_name
                                        )
                                        return return_value

                                # Check Visibility - cannot (not exposed)
                                # If here, everything is fine,
                                # ie already defined correctly
                                return_value.message = "{}: Parameter already bound to category: {}".format(
                                    parameter_name, cat.Name
                                )
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
                        action_return_value.message = (
                            "{} : parameter successfully bound to: {}".format(
                                parameter_name, cat_object.Name
                            )
                        )
                        return action_return_value
                    else:
                        if doc.ParameterBindings.ReInsert(
                            definition, bind, parameter_grouping
                        ):
                            action_return_value.message = (
                                "{} : parameter successfully bound to: {}".format(
                                    parameter_name, cat_object.Name
                                )
                            )
                            return action_return_value
                        else:
                            action_return_value.status = False
                            action_return_value.message = (
                                "{} : failed to bind parameter to: {}".format(
                                    parameter_name, cat_object.Name
                                )
                            )
                except Exception as e:
                    action_return_value.status = False
                    action_return_value.message = "{} : Failed to bind parameter to: {} with exception: {}".format(
                        parameter_name, cat_object.Name, e
                    )
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
        return_value.message = (
            "{} : Failed to bind parameter with exception: {}".format(parameter_name, e)
        )
    return return_value


def add_shared_parameter_to_family(para, mgr, doc, def_file):
    """
    Adds a shared parameter definition to a family document.

    :param para: Tuple containing parameter info
    :type para: tuple (refer module RevitSharedParametersTuple)
    :param mgr: The family manager object
    :type mgr: Autodesk.Revit.DB.FamilyManager
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param def_file: The shared parameter definition file.
    :type def_file: _type_

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
        # loop through parameters and try to find matching one to be added from parameter file
        # loop through all definition groups
        for group in def_file.Groups:
            # loop through para's within definition group
            for def_para in group.Definitions:
                # check whether this is the parameter we are after
                if def_para.Name != para.name:
                    # jump to next parameter
                    continue
                # set up an action to add parameter
                def action():
                    action_return_value = res.Result()
                    try:
                        # add parameter depending on name, parameter group and isInstance
                        fam_para = mgr.AddParameter(
                            def_para, para.builtInParameterGroup, para.isInstance
                        )
                        action_return_value.message = (
                            para.name + " : parameter successfully added."
                        )
                        action_return_value.result.append(fam_para)
                    except Exception as e:
                        action_return_value.status = False
                        action_return_value.message = (
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
        return_value.message = (
            para.name + " : Failed to add parameter to family with exception: " + str(e)
        )

    if found_para == False:
        return_value.status = False
        return_value.message = (
            para.name + " : No match for parameter found in shared parameter file."
        )

    return return_value
