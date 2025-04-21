# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025 Jan Christel
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

from duHast.Utilities.console_out import output
from duHast.Utilities.Objects.base import Base


class FamilyTypeConfig(Base):
    def __init__(
        self,
        room_type,
        generic_nested_name,
        generic_nested_path,
        generic_nested_coarse_name,
        generic_nested_coarse_path,
        wall_host_path,
        curve_loops,
        output_directory,
        **kwargs
    ):

        """
        Constructor for the FamilyTypeConfig class.

        :param room_type: The type of room (default is "Bay").
        :type room_type: str
        :param generic_nested_path: Path to the generic nested family.
        :type generic_nested_path: str
        :param generic_nested_coarse_path: Path to the generic nested coarse family.
        :type generic_nested_coarse_path: str
        :param wall_host_path: Path to the wall host family.
        :type wall_host_path: str
        :param curve_loops: The curve loops for the family.
        :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
        :param output_directory: The directory for output files.
        :type output_directory: str
        :param kwargs: Additional keyword arguments.
        """

        super(FamilyTypeConfig, self).__init__(**kwargs)

        self.room_type=room_type
        self.generic_nested_name =generic_nested_name
        self.generic_nested_path=generic_nested_path
        self.generic_nested_coarse_name = generic_nested_coarse_name
        self.generic_nested_coarse_path=generic_nested_coarse_path
        self.wall_host_path =wall_host_path
        self.fcurve_loops = curve_loops
        self.output_directory=output_directory
