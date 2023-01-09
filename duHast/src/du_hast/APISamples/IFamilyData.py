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

# common data dictionary keys
ROOT = 'root'
ROOT_CATEGORY = 'rootCategory'
FAMILY_NAME =  'familyName'
FAMILY_FILE_PATH = 'familyFilePath'
USAGE_COUNTER = 'usageCounter'
USED_BY = 'usedBy'


class IFamilyData():

    def __init__(self, rootPath, dataType):
        self.data = []
        
        if(dataType != None):
            self.dataType = dataType
        else:
            self.dataType = 'not declared'
        
        if(rootPath != None):
            self.rootPath = rootPath
        else:
            self.rootPath = '-'

    def process(self, doc):
        pass

    def get_Data(self):
        pass
    
    def update_Data(self, identifyByThisPropertyName, identifyByThisPropertyValue, updateDic):
        match = False
        matchUpdate = True
        for d in self.data:
            #print(identifyByThisPropertyName, d)
            if(identifyByThisPropertyName in d):
                #print('identify by property found')
                if (d[identifyByThisPropertyName] == identifyByThisPropertyValue):
                    #print ('dic', updateDic)
                    for updateProp in updateDic:
                        if(updateProp in d):
                            oldValue = d[updateProp]
                            d[updateProp] = updateDic[updateProp]
                            #print ('updated:', updateProp, ' from value ', oldValue, ' to value ', d[updateProp])
                            matchUpdate = matchUpdate and True
                            
        if(matchUpdate):
            return matchUpdate
        else:
            return match

    def add_Data(self):
        pass

    def _stripFileExtension(self, famName):
        '''
        Strips the file extension '.rfa. , if exists, of the family  name.

        :param famName: The family name.
        :type famName: str
        :return: The truncated family name.
        :rtype: str
        '''

        if(famName.lower().endswith('.rfa')):
                famName = famName[:-4]
        return famName