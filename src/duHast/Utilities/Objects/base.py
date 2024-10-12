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


"""
The `Base` class is a parent class that provides common functionalities and methods for its subclasses. It includes a constructor, a debug output method, a comparison method, a hash method, a method to convert the instance to JSON, a method to convert string properties to UTF-8 in JSON conversion, a method to check if an object is a Python primitive, and a method to convert the class to a dictionary.

Example Usage:
    # Creating a subclass of Base
    class MyClass(Base):
        def __init__(self, name):
            super(MyClass, self).__init__()
            self.name = name

    # Creating an instance of MyClass
    obj = MyClass("example")

    # Printing the debug output
    print(obj)

    # Comparing two instances
    obj1 = MyClass("example")
    obj2 = MyClass("example")
    print(obj1 == obj2)

    # Converting the instance to JSON
    json_data = obj.to_json()

    # Converting the instance to JSON with UTF-8 string properties
    json_data_utf = obj.to_json_utf()

    # Converting the instance to a dictionary
    dict_data = obj.class_to_dict()

Main functionalities:
- The `Base` class allows for multi-inheritance in its subclasses.
- It provides a debug output method that returns a string representation of the class properties.
- It provides a comparison method that checks if two instances are of the same class.
- It provides a hash method required for the custom comparison method.
- It provides a method to convert the instance to JSON.
- It provides a method to convert string properties to UTF-8 in JSON conversion.
- It provides a method to check if an object is a Python primitive.
- It provides a method to convert the class to a dictionary.

Methods:
- `__init__(self, **kwargs)`: The class constructor that forwards all unused arguments to the super class.
- `__repr__(self)`: Enables detailed debug output of all class properties.
- `__eq__(self, other)`: Custom compare is equal override.
- `__hash__(self)`: Custom hash override.
- `to_json(self)`: Convert the instance of this class to JSON.
- `string_to_utf(self, o)`: Convert any properties stored as string to UTF-8 in JSON conversion.
- `to_json_utf(self)`: Convert the instance of this class to JSON with UTF-8 string properties.
- `_is_primitive(self, obj)`: Checks whether an object is a Python primitive.
- `class_to_dict(self)`: Returns all class properties and their values as a dictionary.

Fields:
- No specific fields are defined in the `Base` class.
"""


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

    def __str__(self, indent=0):
        """
        formatted output including indentation

        :param indent: The level of indentation, defaults to 0
        :type indent: int, optional

        :return: A string representing all class properties and their values
        :rtype: str
        """

        output = []
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, list):
                output.append(" " * indent + "{}:".format(attr_name))
                output.append(self._format_list(attr_value, indent + 2))
            elif isinstance(attr_value, dict):
                output.append(" " * indent + "{}:".format(attr_name))
                output.append(self._format_dict(attr_value, indent + 2))
            elif isinstance(attr_value, Base):
                output.append(" " * indent + "{}:".format(attr_name))
                output.append(attr_value.__str__(indent + 2))
            else:
                output.append(" " * indent + "{}: {}".format(attr_name, attr_value))
        return "\n".join(output)

    def _format_list(self, lst, indent):
        """
        A helper function to format list properties

        :param lst: A list
        :type lst: []
        :param indent: level of indentation to be provided to the string output
        :type indent: int

        :return: A string formatted representation of the list past in with indentation.
        :rtype: str
        """
        output = []
        for item in lst:
            if isinstance(item, Base):
                output.append(item.__str__(indent))
            elif isinstance(item, dict):
                output.append(self._format_dict(item, indent))
            else:
                output.append(" " * indent + str(item))
        return "\n".join(output)

    def _format_dict(self, d, indent):
        """
        A helper function to format dictionary properties.

        :param d: A dictionary
        :type d: {}
        :param indent: level of indentation to be provided to the string output
        :type indent: int

        :return: A string formatted representation of the dictionary past in with indentation.
        :rtype: str
        """
        output = []
        for key, value in d.items():
            output.append(" " * indent + "{}:".format(key))
            if isinstance(value, Base):
                output.append(value.__str__(indent + 2))
            elif isinstance(value, dict):
                output.append(self._format_dict(value, indent + 2))
            elif isinstance(value, list):
                output.append(" " * (indent + 2) + "{}:".format(key))
                output.append(self._format_list(value, indent + 4))
            else:
                output.append(" " * (indent + 2) + str(value))
        return "\n".join(output)

    def __eq__(self, other):
        """
        Custom compare is equal override

        :param other: Another instance of pattern class
        :type other: :class:`.PatternBase`
        :return: True if name value of other colour class instance equal the name values of this instance, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, self.__class__)

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """
        try:
            return hash(self.__class__)
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: name:{}".format(
                    e, self.data_type, self.name
                )
            )

    def to_json(self):
        """
        Convert the instance of this class to json.

        :return: A Json object.
        :rtype: json
        """

        return json.dumps(self, indent=None, default=lambda o: o.__dict__)

    def string_to_utf(self, o):
        """
        Used to convert any properties stored as string to utf-8 in to json conversion of all class properties...

        :param o: _description_
        :type o: _type_
        :return: _description_
        :rtype: _type_
        """

        if isinstance(o, str):
            return o.encode("utf-8").decode(
                "utf-8"
            )  # Encoding and decoding to ensure the type is str
        return o.__dict__

    def to_json_utf(self):
        """
        Convert the instance of this class to json, any string properties are converted to utf-8

        :return: A Json object.
        :rtype: json
        """

        return json.dumps(
            self, indent=None, default=self.string_to_utf, ensure_ascii=False
        )

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
