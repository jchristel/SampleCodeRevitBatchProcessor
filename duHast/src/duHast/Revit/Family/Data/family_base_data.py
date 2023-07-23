"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family base data class.
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

from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Utilities import directory_io as dirIO, files_io as fileIO
from duHast.Revit.Common import file_io as rFile
from duHast.Revit.Family.Data import family_base_data_utils as rFamBaseDataUtils

# import Autodesk
# import Autodesk.Revit.DB as rdb

# data dictionary key values specific to this class
CATEGORY_NAME = "categoryName"


class FamilyBaseData(IFamData.IFamilyData):
    def __init__(self, root_path=None, root_category_path=None, data_type=None):
        """
        Class constructor

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param dataType: Human readable data type descriptor
        :type dataType: str
        """

        # store data type  in base class
        super(FamilyBaseData, self).__init__(
            root_path=root_path,
            root_category_path=root_category_path,
            data_type=data_type,
        )
        # super(CategoryData, self).__init__(rootPath, dataType)

        """
        self.data = []
        
        if(dataType != None):
            self.dataType = dataType
        else:
            self.dataType = 'not declared'
        
        if(rootPath != None):
            self.rootPath = rootPath
        else:
            self.rootPath = '-'

        if(rootCategoryPath != None):
            self.rootCategoryPath = rootCategoryPath
        else:
            self.rootCategoryPath = '-'
        """

        if root_category_path != None:
            category_chunks = root_category_path.split(" :: ")
            self.category = category_chunks[-1]
        else:
            self.category = "unknown"

    def _save_out(
        self,
        doc,
        reference_file_path,
        doc_name,
        doc_category,
        family_out_folder_path,
        session_id,
    ):
        """
        Saves a family to file if there is no match for it in the provided reference file. 
        The reference file is a FamilyBaseDataCombinedReport and is read into tuples using RevitFamilyBaseDataUtils.

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        :param referenceFilePath: Fully qualified file path to FamilyBaseDataCombinedReport file.
        :type referenceFilePath: str
        :param docName: The current family name.
        :type docName: str_
        :param docCategory: The family Revit category.
        :type docCategory: str
        :param familyOutFolderPath: The root directory path to which a family is saved. The script will create a sub directory\
            based on the revit batch processor session id and within that folder another sub directory based on the family Revit category:\
                familyOutFolderPath\\SessionId\\RevitCategory\\Myfamily.rfa
        :type familyOutFolderPath: str
        :param sessionId: The batchprocessor session Id (formatted so it can be used as a folder name)
        :type sessionId: str
        """

        # process reference file list and look for a match:
        # based on file name and category
        if fileIO.file_exist(reference_file_path):
            # read overall family base data from file
            (
                overall_family_base_root_data,
                overall_family_base_nested_data,
            ) = rFamBaseDataUtils.read_overall_family_data_list(reference_file_path)
            found_match = False
            for root_fam in overall_family_base_root_data:
                # check whether name and category are a match
                if root_fam.name == doc_name and root_fam.category == doc_category:
                    found_match = True
                    break
            # check if family needs saving out
            if found_match == False:
                # check session id folder exists
                if dirIO.create_target_directory(family_out_folder_path, session_id):
                    # check category folder exists
                    if dirIO.create_target_directory(
                        family_out_folder_path + "\\" + session_id, doc_category
                    ):
                        # save family out
                        rFile.save_as_family(
                            doc,
                            family_out_folder_path
                            + "\\"
                            + session_id
                            + "\\"
                            + doc_category,
                            doc_name,
                            [[doc_name, doc_name]],
                        )

    def process(self, doc, reference_file_path, family_out_directory_path, session_id):
        """
        Collects all base data from the document and stores it in the class property .data

        :param doc: Current family document
        :type doc: Autodesk.Revit.DB.Document
        """

        # get the family category name
        # famCatName = doc.OwnerFamily.FamilyCategory.Name

        # check if a reference file list was provided and if so if family needs to be saved out
        if (
            reference_file_path != None
            and family_out_directory_path != None
            and session_id != None
        ):
            self._save_out(
                doc,
                reference_file_path,
                self._strip_file_extension(doc.Title),
                self.category,
                family_out_directory_path,
                session_id,
            )

        # build data
        self.data.append(
            {
                IFamData.ROOT: self.root_path,
                IFamData.ROOT_CATEGORY: self.root_category_path,
                IFamData.FAMILY_NAME: self._strip_file_extension(doc.Title),
                IFamData.FAMILY_FILE_PATH: doc.PathName,  # this property will often be an empty string in nested families
                CATEGORY_NAME: self.category,
            }
        )

    def get_data(self):
        return self.data
