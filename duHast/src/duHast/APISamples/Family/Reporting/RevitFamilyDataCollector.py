'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family data collector class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Collects data from current family document and then recursively from any nested family.

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

from duHast.Utilities import Result as res
# import Autodesk
import Autodesk.Revit.DB as rdb

class RevitFamilyDataCollector():

    def __init__(self, dataProcessors):
        '''
        Class constructor taking a list of processor instances as argument.

        :param dataProcessors: List of processor instances
        :type dataProcessors: [IFamilyProcessor]
        '''

        self.dataProcessors = dataProcessors
    
    def _getFamilyIds(self,doc):
        '''
        Get all loadable family ids in file.

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :return: list of family ids
        :rtype: [Autodesk.Revit.DB.ElementId]
        '''

        familyIds = []
        col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol) 
        # get families from symbols and filter out in place families
        for famSymbol in col:
            if (famSymbol.Family.Id not in familyIds and famSymbol.Family.IsInPlace == False):
                familyIds.append(famSymbol.Family.Id)
        return familyIds

    def _dive(self, doc, rootName, rootCategory, isRoot = False):
        '''
        Loops recursively over each family nested into root family document and and calls processor instance\
             with the current family document.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document
        :param rootName: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootName: str
        :param isRoot: Indicates whether document is that of the root family, defaults to False
        :type isRoot: bool, optional
        '''

        returnValue = res.Result()
        # only process current doc if not the root family
        # that family is processed already
        if(isRoot == False):
            for pro in self.dataProcessors:
                try:
                    pro.process(doc, rootName, rootCategory)
                    returnValue.AppendMessage('Processor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [OK]')
                except Exception as e:
                    returnValue.UpdateSep(False, 'Processor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [EXCEPTION] ' + str(e))
        
        # check if family doc 
        if(doc.IsFamilyDocument):
            # get any nested families
            familyIds = self._getFamilyIds(doc)
            # if there are any nested families open those for processing
            if(len(familyIds) > 0):
                for familyId in familyIds:
                    family = doc.GetElement(familyId)
                    try:
                        if(family.IsEditable and family.IsValidObject):
                            familyDoc = doc.EditFamily(family)
                            famName = family.Name
                            # strip .rfa of name
                            if(famName.lower().endswith('.rfa')):
                                famName = famName[:-4]
                            # get category
                            famCategoryName = family.FamilyCategory.Name
                            # go recursive
                            diveResult = self._dive(
                                familyDoc, 
                                rootName + ' :: ' + famName,
                                rootCategory + ' :: ' + famCategoryName
                            )
                            returnValue.Update(diveResult)
                    except Exception as e:
                        message = ''
                        if(family != None):
                            message = 'An exception occurred when opening family ' + rdb.Element.Name.GetValue(family) + '. Exception: ' + str(e)
                        else:
                            message = 'An exception occurred when attempting the get family element by id:' + str(familyId) + '. Exception: ' + str(e)
                        returnValue.UpdateSep(False, message)
            else:
                # only close any nested family document...not the root one
                # since that is closed by batch processor!
                if(isRoot == False):
                    try:
                        # no more families found. Close the active doc
                        doc.Close(False)
                    except Exception as e:
                        message = ''
                        if(doc != None):
                            message = 'An exception occurred when closing document: ' + doc.Title + '. Exception: ' + str(e)
                        else:
                            message = 'An exception occurred when closing document: ' + str(e)
                        returnValue.UpdateSep(False, message)
        return returnValue

    def processFamily(self, doc, rootName, rootCategory):
        '''
        Entry point for recursive family looper.

        Processes root family as well as actions any post processing.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document
        :param rootName: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootName: str
        :param rootCategory: The path of the nested family category in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategory: str

        :return: 
            Result class instance.
            
            - .result = True if all data processor instances ran without an exception. Otherwise False.
            - .message will contain each processor type and its processing status'
        
        :rtype: :class:`.Result`
        '''

        returnValue = res.Result()

        #TODO:
        # action any pre processing actions
        # loop over fam processor instances and process family with each of them
        for pro in self.dataProcessors:
            try:
                preActionResult =  pro.preProcessActions(doc)
                returnValue.Update(preActionResult)
            except Exception as e:
                returnValue.UpdateSep(False, 'PreProcessor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [EXCEPTION] ' + str(e))

        # loop over fam processor instances and process family with each of them
        for pro in self.dataProcessors:
            try:
                pro.process(doc, rootName, rootCategory)
                returnValue.AppendMessage('Processor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [OK]')
            except Exception as e:
                returnValue.UpdateSep(False, 'Processor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [EXCEPTION] ' + str(e))
        
        # check out any nested families
        diveResult = self._dive(doc, rootName, rootCategory, True)
        returnValue.Update(diveResult)
        
        #TODO:
        # action any post processing actions
        # loop over fam processor instances and process family with each of them
        for pro in self.dataProcessors:
            try:
                proActionResult =  pro.postProcessActions(doc)
                returnValue.Update(proActionResult)
            except Exception as e:
                returnValue.UpdateSep(False, 'PostProcessor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [EXCEPTION] ' + str(e))

        return returnValue