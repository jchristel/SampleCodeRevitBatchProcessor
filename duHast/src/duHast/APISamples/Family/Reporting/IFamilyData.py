'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family data storage / processing class.
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

from duHast.Utilities import Base

# common data dictionary keys
ROOT = 'root'
ROOT_CATEGORY = 'rootCategory'
FAMILY_NAME =  'familyName'
FAMILY_FILE_PATH = 'familyFilePath'
USAGE_COUNTER = 'usageCounter'
USED_BY = 'usedBy'


class IFamilyData(Base.Base):

    def __init__(self, root_path, root_category_path=None, data_type=None, **kwargs):

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFamilyData, self).__init__(**kwargs) 

        self.data = []
        
        if(data_type != None):
            self.data_type = data_type
        else:
            self.data_type = 'not declared'
        
        if(root_path != None):
            self.root_path = root_path
        else:
            self.root_path = '-'
        
        if(root_category_path != None):
            self.root_category_path = root_category_path
        else:
            self.root_category_path = '-'

    def process(self, doc):
        pass

    def get_data(self):
        pass
    
    def update_data(self, identify_by_this_property_name, identify_by_this_property_value, update_dic):
        match = False
        matchUpdate = True
        for d in self.data:
            #print(identifyByThisPropertyName, d)
            if(identify_by_this_property_name in d):
                #print('identify by property found')
                if (d[identify_by_this_property_name] == identify_by_this_property_value):
                    #print ('dic', updateDic)
                    for updateProp in update_dic:
                        if(updateProp in d):
                            oldValue = d[updateProp]
                            d[updateProp] = update_dic[updateProp]
                            #print ('updated:', updateProp, ' from value ', oldValue, ' to value ', d[updateProp])
                            matchUpdate = matchUpdate and True
                            
        if(matchUpdate):
            return matchUpdate
        else:
            return match

    def add_data(self):
        pass

    def _strip_file_extension(self, fam_name):
        '''
        Strips the file extension '.rfa. , if exists, of the family  name.

        :param famName: The family name.
        :type famName: str
        :return: The truncated family name.
        :rtype: str
        '''

        if(fam_name.lower().endswith('.rfa')):
                fam_name = fam_name[:-4]
        return fam_name