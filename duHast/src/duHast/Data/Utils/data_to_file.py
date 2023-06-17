'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions writing data objects to file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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
from duHast.Utilities import date_stamps as dateStamp

import codecs
import json

def build_json_for_file(dic, model_name):
    '''
    Adds two header keys to json output to be saved to file.

    - file name
    - date processed

    :param dic: A dictionary containing all data items. Key is the data tpe, value the data objects
    :type dic: {str:[]}
    :param model_name: The revit model name.
    :type model_name: str

    :return: A dictionary
    :rtype: {str:[]}
    '''

    data_json = {
        "file name": model_name,
        "date processed": dateStamp.get_date_stamp(dateStamp.FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC),
    }
    for key,item in dic.items():
        data_json[key] = item
    
    return data_json
