'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family warnings data class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Family.Data import ifamily_data as IFamData
#from duHast.Utilities import Utility as util
from duHast.Revit.Warnings import warnings as rWarn

# import Autodesk
#import Autodesk.Revit.DB as rdb

WARNING_TEXT = 'warningText'
WARNING_GUID = 'warningGUID'
WARNING_RELATED_IDS = 'warningRelatedIds' 
WARNING_OTHER_IDS = 'warningOtherIds' 

class WarningsData(IFamData.IFamilyData):
    
    def __init__(self, root_path=None, root_category_path=None, data_type=None):
        
        super(WarningsData, self).__init__(root_path=root_path, root_category_path=root_category_path, data_type=data_type)


    def process(self, doc):
        # get all warnings in document
        warnings = rWarn.get_warnings(doc)
        # loop over warnings and extract data
        for warning in warnings:
            # check for a guid
            war_guid = ''
            try:
                war_guid = warning.GetFailureDefinitionId().Guid
            except Exception as e:
                pass
            # warning text
            war_text = ''
            try:
                war_text = warning.GetDescriptionText()
            except Exception as e:
                pass
            # affected element ids
            war_element_ids_as_integer = []
            try:
                for el in warning.GetFailingElements():
                    war_element_ids_as_integer.append(el.IntegerValue)
            except Exception as e:
                pass
            # other element ids
            war_other_element_ids_as_integer = []
            try:
                for el in warning.GetAdditionalElements():
                    war_other_element_ids_as_integer.append(el.IntegerValue)
            except Exception as e:
                pass

            # build data
            self.data.append({
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : doc.Title,
                IFamData.FAMILY_FILE_PATH : doc.PathName,
                WARNING_TEXT : war_text,
                WARNING_GUID : war_guid,
                WARNING_RELATED_IDS : war_element_ids_as_integer,
                WARNING_OTHER_IDS: war_other_element_ids_as_integer
                }
            )
        
        # check if any shared parameter was found
        if(len(self.data) == 0):
            # add message no warnings found
            # build data
            self.data.append({
                IFamData.ROOT : self.rootPath,
                IFamData.ROOT_CATEGORY : self.rootCategoryPath,
                IFamData.FAMILY_NAME : doc.Title,
                IFamData.FAMILY_FILE_PATH : doc.PathName,
                WARNING_TEXT : 'No warnings present in family.',
                WARNING_GUID : '',
                WARNING_RELATED_IDS : [],
                WARNING_OTHER_IDS: []
                }
            )

    def get_data(self):
        return self.data