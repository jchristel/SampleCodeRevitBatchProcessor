"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Base class for objects.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class provides some utility functions to all child classes:

- __repr__() a way of providing detailed debug output through print
- to_json() A json formatted dump of the class

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

import json


class Base(object):
    def __init__(self, **kwargs):
        """
        Class constructor
        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!

        super(Base, self).__init__(**kwargs)

    def __repr__(self):
        """
        Enables detailed debug output of all class properties using: rep(obj)

        :return: A string listing class properties and their respective values.
        :rtype: string
        """

        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def to_json(self):
        """
        Convert the instance of this class to json.

        :return: A Json object.
        :rtype: json
        """

        return json.dumps(self, indent=None, default=lambda o: o.__dict__)


    def string_to_utf(self, o):
        '''
        Used to convert any properties stored as string to utf-8 in to json conversion of all class properties...

        :param o: _description_
        :type o: _type_
        :return: _description_
        :rtype: _type_
        '''

        if isinstance(o, str):
            return o.encode('utf-8').decode('utf-8')  # Encoding and decoding to ensure the type is str
        return o.__dict__

    def to_json_utf(self):
        '''
        Convert the instance of this class to json, any string properties are converted to utf-8

        :return: A Json object.
        :rtype: json
        '''

        return json.dumps(self, indent=None, default=self.string_to_utf, ensure_ascii=False)



    def _is_primitive(self, obj):
        """
        Checks whether object past in is a python primitive

        :param obj: The object to be tested.
        :type obj: obj
        :return: True if object is a python primitive, Otherwise False.
        :rtype: Bool
        """

        return isinstance(obj, (int, float, str, bool))

    def class_to_dict(self):
        """
        Returns all class properties and their values as a dictionary

        :return: A dictionary of all class properties names and their values
        :rtype: {str:var,}
        """

        if isinstance(self, object):
            class_dict = {}
            for key, value in self.__dict__.items():
                if self._is_primitive(value):
                    class_dict[key] = value
                else:
                    class_dict[key] = value.class_to_dict()
            return class_dict
        else:
            return self
