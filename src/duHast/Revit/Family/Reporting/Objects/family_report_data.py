"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class is used to store data from families placed in a project environment.


"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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


class FamilyReportData(base.Base):
    def __init__(self):

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(FamilyReportData, self).__init__(None)

        self.project_name = None
        self.family_category = None
        self.family_name = None
        self.family_type_name = None
        self.family_instances_placed = -1
        self.nested_families = []
        self.is_host = False
        self.type_properties = []
        self.is_shared = False


    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def family_category(self):
        return self._family_category

    @family_category.setter
    def family_category(self, value):
        self._family_category = value

    @property
    def family_name(self):
        return self._family_name

    @family_name.setter
    def family_name(self, value):
        self._family_name = value

    @property
    def family_type_name(self):
        return self._family_type_name

    @family_type_name.setter
    def family_type_name(self, value):
        self._family_type_name = value

    @property
    def family_instances_placed(self):
        return self._family_instances_placed

    @family_instances_placed.setter
    def family_instances_placed(self, value):
        self._family_instances_placed = value

    @property
    def nested_families(self):
        return self._nested_families

    def add_nested_family(self, family):
        self._nested_families.append(family)
        # set the host attribute
        self.is_host = True

    @property
    def is_host(self):
        return self._is_host

    @is_host.setter
    def is_host(self, value):
        self._is_host = value

    @property
    def type_properties(self):
        return self._type_properties

    def add_type_property(self, property):
        self._type_properties(property)
       
    @property
    def is_shared(self):
        return self._is_shared

    @is_shared.setter
    def is_shared(self, value):
        self._is_shared = value