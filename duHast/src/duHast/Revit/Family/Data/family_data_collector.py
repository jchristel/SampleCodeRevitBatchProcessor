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

from duHast.Utilities import result as res
# import Autodesk
import Autodesk.Revit.DB as rdb
from duHast.Utilities import base

class RevitFamilyDataCollector(base.Base):

    def __init__(self, data_processors):
        '''
        Class constructor taking a list of processor instances as argument.

        :param data_processors: List of processor instances
        :type data_processors: [IFamilyProcessor]
        '''

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(RevitFamilyDataCollector, self).__init__() 

        self.dataProcessors = data_processors
    
    def _get_family_ids(self,doc):
        '''
        Get all loadable family ids in file.

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :return: list of family ids
        :rtype: [Autodesk.Revit.DB.ElementId]
        '''

        family_ids = []
        col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol) 
        # get families from symbols and filter out in place families
        for fam_symbol in col:
            if (fam_symbol.Family.Id not in family_ids and fam_symbol.Family.IsInPlace == False):
                family_ids.append(fam_symbol.Family.Id)
        return family_ids

    def _dive(self, doc, root_name, root_category, is_root = False):
        '''
        Loops recursively over each family nested into root family document and and calls processor instance\
             with the current family document.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document
        :param root_name: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_name: str
        :param is_root: Indicates whether document is that of the root family, defaults to False
        :type is_root: bool, optional
        '''

        return_value = res.Result()
        # only process current doc if not the root family
        # that family is processed already
        if(is_root == False):
            for pro in self.dataProcessors:
                try:
                    pro.process(doc, root_name, root_category)
                    return_value.append_message('Processor [{}] of family: {}  [OK]'.format(pro.dataType,doc.Title))
                except Exception as e:
                    return_value.update_sep(False, 'Processor [{}] of family: {} [EXCEPTION] {}'.format(pro.dataType, doc.Title,e))
        
        # check if family doc 
        if(doc.IsFamilyDocument):
            # get any nested families
            family_ids = self._get_family_ids(doc)
            # if there are any nested families open those for processing
            if(len(family_ids) > 0):
                for family_id in family_ids:
                    family = doc.GetElement(family_id)
                    try:
                        if(family.IsEditable and family.IsValidObject):
                            family_doc = doc.EditFamily(family)
                            fam_name = family.Name
                            # strip .rfa of name
                            if(fam_name.lower().endswith('.rfa')):
                                fam_name = fam_name[:-4]
                            # get category
                            fam_category_name = family.FamilyCategory.Name
                            # go recursive
                            dive_result = self._dive(
                                family_doc, 
                                root_name + ' :: ' + fam_name,
                                root_category + ' :: ' + fam_category_name
                            )
                            return_value.update(dive_result)
                    except Exception as e:
                        message = ''
                        if(family != None):
                            message = 'An exception occurred when opening family ' + rdb.Element.Name.GetValue(family) + '. Exception: ' + str(e)
                        else:
                            message = 'An exception occurred when attempting the get family element by id:' + str(family_id) + '. Exception: ' + str(e)
                        return_value.update_sep(False, message)
            else:
                # only close any nested family document...not the root one
                # since that is closed by batch processor!
                if(is_root == False):
                    try:
                        # no more families found. Close the active doc
                        doc.Close(False)
                    except Exception as e:
                        message = ''
                        if(doc != None):
                            message = 'An exception occurred when closing document: ' + doc.Title + '. Exception: ' + str(e)
                        else:
                            message = 'An exception occurred when closing document: ' + str(e)
                        return_value.update_sep(False, message)
        return return_value

    def process_family(self, doc, root_name, root_category):
        '''
        Entry point for recursive family looper.

        Processes root family as well as actions any post processing.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document
        :param root_name: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_name: str
        :param root_category: The path of the nested family category in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type root_category: str

        :return: 
            Result class instance.
            
            - .result = True if all data processor instances ran without an exception. Otherwise False.
            - .message will contain each processor type and its processing status'
        
        :rtype: :class:`.Result`
        '''

        return_value = res.Result()

        #TODO:
        # action any pre processing actions
        # loop over fam processor instances and process family with each of them
        for pro in self.dataProcessors:
            try:
                pre_action_result =  pro.preProcessActions(doc)
                return_value.update(pre_action_result)
            except Exception as e:
                return_value.update_sep(False, 'PreProcessor [' + pro.dataType + '] of family: ' + str(doc.Title) + ' [EXCEPTION] ' + str(e))

        # loop over fam processor instances and process family with each of them
        for pro in self.dataProcessors:
            try:
                pro.process(doc, root_name, root_category)
                return_value.append_message('Processor [{}] of family: {} [OK]'.format(pro.dataType, doc.Title))
            except Exception as e:
                return_value.update_sep(False, 'Processor [{}] of family: {} [EXCEPTION] {}'.format(pro.dataType,doc.Title,e))
        
        # check out any nested families
        dive_result = self._dive(doc, root_name, root_category, True)
        return_value.update(dive_result)
        
        #TODO:
        # action any post processing actions
        # loop over fam processor instances and process family with each of them
        for pro in self.dataProcessors:
            try:
                pro_action_result =  pro.postProcessActions(doc)
                return_value.update(pro_action_result)
            except Exception as e:
                return_value.update_sep(False, 'PostProcessor [{}] of family: {} [EXCEPTION] {}'.format(pro.dataTyp,doc.Title,e))

        return return_value