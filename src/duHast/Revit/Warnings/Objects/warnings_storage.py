"""
A class used to store Revit warnings information.

This class represents Revit warnings and provides attributes to store information about them, such as the filename, warning ID, description, and associated element IDs.
"""


#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Utilities.Objects import base
from duHast.Utilities.date_stamps import (
    get_date_stamp,
    FILE_DATE_STAMP_YYYYMMDD_SPACE,
    TIME_STAMP_HHMMSEC_COLON,
)


class RevitWarning(base.Base):
    """
    A class representing a warning in a Revit file. This class inherits from the base.Base class.

    Attributes:
        - file_name (str): The name of the Revit file associated with the warning.
        - id (str): The ID of the warning.
        - description (str): The description of the warning.
        - element_ids (list of str): A list of element IDs associated with the warning.

    This class is used to store information about warnings that occur in a Revit file, such as the filename, warning ID, description, and associated element IDs.
    """

    def __init__(self, file_name="", id="", description="", element_ids=[], **kwargs):
        """
        Initializes a RevitWarning object.

        Args:
            file_name (str, optional): The name of the Revit file associated with the warning. Defaults to "".
            id (str, optional): The ID of the warning. Defaults to "".
            description (str, optional): The description of the warning. Defaults to "".
            element_ids (list, optional): A list of element IDs associated with the warning. Defaults to [].
            `**kwargs` (optional): Additional keyword arguments to be passed to the base.Base class constructor.
        """

        super(RevitWarning, self).__init__(**kwargs)

        self.file_name = file_name
        self.id = id
        self.description = description
        self.element_ids = element_ids
        self.date = get_date_stamp(FILE_DATE_STAMP_YYYYMMDD_SPACE)
        self.time = get_date_stamp(TIME_STAMP_HHMMSEC_COLON)

    def class_to_csv(self, headers):
        """
        Converts the warning object to a CSV list based on the provided headers.

        Args:
            headers (list): A list of headers for the CSV list.

        Returns:
            list: The warning object converted to a CSV list.
        """

        if isinstance(self, object):
            csv_list = []
            for prop in headers:
                if prop in self.__dict__:
                    if isinstance(self.__dict__[prop], str):
                        csv_list.append(self.__dict__[prop])
                    else:
                        csv_list.append("{}".format(self.__dict__[prop]))
                else:
                    csv_list.append("Property {} does not exist!".format(prop))
            return csv_list
        else:
            return []
