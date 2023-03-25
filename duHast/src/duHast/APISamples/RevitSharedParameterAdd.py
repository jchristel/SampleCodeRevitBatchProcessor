'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a function to bind a shared parameter to a category.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
based on building coder article:
https://thebuildingcoder.typepad.com/blog/2012/04/adding-a-category-to-a-shared-parameter-binding.html

'''


import Autodesk.Revit.DB as rdb

# custom result class
from duHast.Utilities import Result as res
# import InTransaction from common module
from duHast.APISamples import RevitTransaction as rTran

def LoadSharedParameterFile(doc, path):
    '''
    Loads a shared parameter file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param path: Fully qualified file path to shared parameter text file.
    :type path: str

    :return: The opened shared parameter file.
    :rtype: Autodesk.Revit.DB.DefinitionFile
    '''

    app = doc.Application
    app.SharedParametersFilename = path
    return app.OpenSharedParameterFile()

def BindSharedParameter(doc, category, parameterName, groupName, parameterType, isVisible, isInstance, parameterGrouping, sharedParameterFilepath):
    '''
    Binds a shared parameter to a revit category.

    Refer building coder article referenced in header


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param category: The built in category, to which the parameter will be bound.
    :type category: Autodesk.Revit.DB.BuiltInCategory
    :param parameterName: The parameter name.
    :type parameterName: str
    :param groupName: The group under which the parameter appears in shared parameter text file.
    :type groupName: str
    :param paramType: The parameter type. (Area, vs text vs... (deprecated in Revit 2022!)
    :type paramType: Autodesk.Revit.DB.ParameterType
    :param isVisible: Is parameter visible in UI to users.
    :type isVisible: bool
    :param isInstance: True parameter is an instance parameter, otherwise type parameter.
    :type isInstance: bool
    :param parameterGrouping: Where parameter appears in properties section in UI.
    :type parameterGrouping: str
    :param sharedParameterFilepath: Fully qualified file path to shared parameter text file.
    :type sharedParameterFilepath: str

    :return: 
        Result class instance.

        - Parameter binding status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
    
        app = doc.Application

        #check if we are going to get something valid:
        if(doc.Settings.Categories.get_Item(category) != None):

            # This is needed already here to 
            # store old ones for re-inserting
            catSet = app.Create.NewCategorySet()
 
            # Loop all Binding Definitions
            # IMPORTANT NOTE: Categories.Size is ALWAYS 1 !?
            # For multiple categories, there is really one 
            # pair per each category, even though the 
            # Definitions are the same...
 
            iter = doc.ParameterBindings.ForwardIterator()
            iter.Reset()
            while iter.MoveNext():
                if(iter.Key != None):
                    definition = iter.Key
                    elemBind = iter.Current
                    # check parameter name match
                    if(parameterName == definition.Name):
                        try: 
                            cat = doc.Settings.Categories.get_Item(category)
                            if(elemBind.Categories.Contains(cat)):
                                # check parameter type
                                if(definition.ParameterType != parameterType):
                                    returnValue.status = False
                                    returnValue.message = parameterName + ': wrong parameter type: '+ str(definition.ParameterType)
                                    return returnValue
                                #check binding type
                                if(isInstance):
                                    if(elemBind.GetType() != rdb.InstanceBinding):
                                        returnValue.status = False
                                        returnValue.message = parameterName + ': wrong binding type (looking for instance but got type)'
                                        return returnValue
                                else:
                                    if(elemBind.GetType() != rdb.TypeBinding):
                                        returnValue.status = False
                                        returnValue.message = parameterName + ': wrong binding type (looking for type but got instance)'
                                        return returnValue
                    
                                # Check Visibility - cannot (not exposed)
                                # If here, everything is fine, 
                                # ie already defined correctly
                                returnValue.message = parameterName + ': Parameter already bound to category: ' + str(cat.Name)
                                return returnValue
                        except Exception as e:
                            returnValue.AppendMessage(parameterName + ' : Failed to check parameter binding with exception: ' + str(e))
                        # If here, no category match, hence must 
                        # store "other" cats for re-inserting
                        else:
                            for catOld in elemBind.Categories:
                                catSet.Insert(catOld)

            # If here, there is no Binding Definition for 
            # it, so make sure Param defined and then bind it!
            defFile = LoadSharedParameterFile(doc,sharedParameterFilepath)
            defGroup = defFile.Groups.get_Item(groupName)
            if defGroup == None:
                defGroup = defFile.Groups.Create(groupName)
            if defGroup.Definitions.Contains(defGroup.Definitions.Item[parameterName]):
                definition = defGroup.Definitions.Item[parameterName]
            else:
                opt = rdb.ExternalDefinitionCreationOptions(parameterName, parameterType)
                opt.Visible = isVisible
                definition = defGroup.Definitions.Create(opt)

            #get category from builtin category
            catObject = doc.Settings.Categories.get_Item(category)
            catSet.Insert(catObject)

            bind = None
            if(isInstance):
                bind = app.Create.NewInstanceBinding(catSet)
            else:
                bind = app.Create.NewTypeBinding(catSet)
    
            # There is another strange API "feature". 
            # If param has EVER been bound in a project 
            # (in above iter pairs or even if not there 
            # but once deleted), Insert always fails!? 
            # Must use .ReInsert in that case.
            # See also similar findings on this topic in: 
            # http://thebuildingcoder.typepad.com/blog/2009/09/adding-a-category-to-a-parameter-binding.html 
            # - the code-idiom below may be more generic:

            def action():
                actionReturnValue = res.Result()
                try:
                    if(doc.ParameterBindings.Insert(definition, bind, parameterGrouping)):
                        actionReturnValue.message =  parameterName + ' : parameter successfully bound to: ' + catObject.Name
                        return actionReturnValue
                    else:
                        if(doc.ParameterBindings.ReInsert(definition, bind, parameterGrouping)):
                            actionReturnValue.message = parameterName + ' : parameter successfully bound to: ' + catObject.Name
                            return actionReturnValue
                        else:
                            actionReturnValue.status = False
                            actionReturnValue.message = parameterName + ' : failed to bind parameter to: ' + catObject.Name
                except Exception as e:
                    actionReturnValue.status = False
                    actionReturnValue.message = parameterName + ' : Failed to bind parameter to: ' + catObject.Name + ' with exception: ' + str(e)
                return actionReturnValue
            transaction = rdb.Transaction(doc,'Binding parameter')
            returnValue = rTran.in_transaction(transaction, action)
        else:
            returnValue.UpdateSep(False, 'Failed to get category object for ' + str(category)) 
        return returnValue

    except Exception as e:
        returnValue.status = False
        returnValue.message = parameterName + ' : Failed to bind parameter with exception: ' + str(e)
    return returnValue

def AddSharedParameterToFamily(para, mgr, doc, defFile):
    '''
    Adds a shared parameter definition to a family document.

    :param para: Tuple containing parameter info
    :type para: tuple (refer module RevitSharedParametersTuple)
    :param mgr: The family manager object
    :type mgr: Autodesk.Revit.DB.FamilyManager
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param defFile: The shared parameter definition file.
    :type defFile: _type_

    :return: 
        Result class instance.

        - True if added successfully. False if an exception occurred.
        - result.message will contain the name of the shared parameter.
        - .result.result will contain the family parameter object.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    foundPara = False
    try:
        # loop through parameters and try to find matching one to be added from parameter file
        # loop through all definition groups
        for group in defFile.Groups:
            # loop through para's within definition group
            for defPara in group.Definitions:
                #check whether this is the parameter we are after
                if (defPara.Name != para.name):
                    # jump to next parameter
                    continue
                # set up an action to add parameter
                def action():
                    actionReturnValue = res.Result()
                    try:
                        # add parameter depending on name, parameter group and isInstance
                        famPara = mgr.AddParameter(defPara, para.builtInParameterGroup, para.isInstance)
                        actionReturnValue.message = para.name + ' : parameter successfully added.'
                        actionReturnValue.result.append(famPara)
                    except Exception as e:
                        actionReturnValue.status = False
                        actionReturnValue.message = para.name + ' : Failed to add shared parameter: with exception: ' + str(e)
                    return actionReturnValue
                transaction = rdb.Transaction(doc, "Adding shared parameter")
                returnValue = rTran.in_transaction(transaction, action)
                # set flag for parameter found
                foundPara = True

            # check whether inner loop found matching parameter
            if (foundPara):
                # get out of outer loop
                break
    except Exception as e:
        returnValue.status = False
        returnValue.message = para.name + ' : Failed to add parameter to family with exception: ' + str(e)
    
    if(foundPara == False):
       returnValue.status = False
       returnValue.message = para.name + ' : No match for parameter found in shared parameter file.'
    
    return returnValue