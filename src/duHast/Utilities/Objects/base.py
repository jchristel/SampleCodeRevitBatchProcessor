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
from collections import OrderedDict
from duHast.Utilities.utility import encode_ascii

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

        # this class inherits from object directly

        super(Base, self).__init__()

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

    def __str__(self):
        return self.default_format()
    
    def default_format(self):
        """
        Provides a formatted output of all class properties and their values without indentation.
        
        :return: A string representing all class properties and their values
        :rtype: str
        """
        output = []
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, list):
                output.append("{}:".format(attr_name))
                output.append(self._default_format_list(attr_value))
            elif isinstance(attr_value, dict):
                output.append("{}:".format(attr_name))
                output.append(self._default_format_dict(attr_value))
            elif isinstance(attr_value, Base):
                output.append("{}:".format(attr_name))
                output.append(attr_value.default_format())
            else:
                output.append("{}: {}".format(attr_name, attr_value))
        return "\n".join(output)

    def _default_format_list(self, lst):
        """
        A helper function to format list properties without indentation.
        
        :param lst: A list
        :type lst: []
        :return: A string formatted representation of the list passed in without indentation.
        :rtype: str
        """
        output = []
        for item in lst:
            if isinstance(item, Base):
                output.append(item.default_format())
            elif isinstance(item, dict):
                output.append(self._default_format_dict(item))
            else:
                output.append(str(item))
        return "\n".join(output)

    def _default_format_dict(self, d):
        """
        A helper function to format dictionary properties without indentation.
        
        :param d: A dictionary
        :type d: {}
        :return: A string formatted representation of the dictionary passed in without indentation.
        :rtype: str
        """
        output = []
        for key, value in d.items():
            output.append("{}:".format(key))
            if isinstance(value, Base):
                output.append(value.default_format())
            elif isinstance(value, dict):
                output.append(self._default_format_dict(value))
            elif isinstance(value, list):
                output.append("{}:".format(key))
                output.append(self._default_format_list(value))
            else:
                output.append(str(value))
        return "\n".join(output)

    
    def formatted_indented_str(self, indent=0, indent_character=" "):
        """
        formatted output including indentation

        :param indent: The level of indentation, defaults to 0
        :type indent: int, optional
        :param indent_character: the indentation character used, defaults to " "
        :type indent_character: str

        :return: A string representing all class properties and their values
        :rtype: str
        """

        output = []
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, list):
                output.append(indent_character * indent + "{}:".format(attr_name))
                output.append(self._indented_format_list(attr_value, indent + 2, indent_character))
            elif isinstance(attr_value, dict):
                output.append(indent_character * indent + "{}:".format(attr_name))
                output.append(self._indented_format_dict(attr_value, indent + 2, indent_character))
            elif isinstance(attr_value, Base):
                output.append(indent_character * indent + "{}".format(attr_name, indent))
                output.append(attr_value.formatted_indented_str(indent + 2, indent_character))
            else:
                output.append(indent_character * indent + "{}: {}".format(attr_name, attr_value))
        return "\n".join(output)

    def _indented_format_list(self, lst, indent, indent_character):
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
                output.append(item.formatted_indented_str(indent, indent_character))
            elif isinstance(item, dict):
                output.append(self._indented_format_dict(item, indent, indent_character))
            else:
                output.append(indent_character * indent + str(item))
        return "\n".join(output)

    def _indented_format_dict(self, d, indent, indent_character):
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
            output.append(indent_character * indent + "{}:".format(key))
            if isinstance(value, Base):
                output.append(value.formatted_indented_str(indent + 2, indent_character))
            elif isinstance(value, dict):
                output.append(self._indented_format_dict(value, indent + 2, indent_character))
            elif isinstance(value, list):
                output.append(indent_character * (indent + 2) + "{}:".format(key))
                output.append(self._indented_format_list(value, indent + 4, indent_character))
            else:
                output.append(indent_character * (indent + 2) + str(value))
        return "\n".join(output)

    def __eq__(self, other):
        """
        Custom compare is equal override

        :param other: Another instance of this class
        :type other: :class:`.Base`
        :return: True if other is a base instance, otherwise False.
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
        Convert the instance of this class to JSON, including public attributes and properties.

        :return: A JSON object.
        :rtype: str
        """

        return json.dumps(self.class_to_dict(), ensure_ascii=False)

    def to_json_ordered(self):
        """
        Convert the instance of this class to JSON, including public attributes and properties.
        Properties and attributes are ordered alphabetically.
        Note: This method takes about double the time of to_json()

        :return: A JSON object.
        :rtype: str
        """

        return json.dumps(self.class_to_ordered_dict(), ensure_ascii=False)
    
    def to_json_utf(self):
        """
        Convert the instance of this class to json, any string properties are converted to utf-8

        :return: A Json object.
        :rtype: json
        """

        json_string = self.to_json()
        ascii_encoded = encode_ascii(json_string)
        return ascii_encoded
    
    
    def to_json_utf_ordered(self):
        """
        Convert the instance of this class to json, any string properties are converted to utf-8
        Properties and attributes are ordered alphabetically.
        Note: This method takes about double the time of to_json_utf()
        :return: A Json object.
        :rtype: json
        """

        json_string = self.to_json_ordered()
        ascii_encoded = encode_ascii(json_string)
        return ascii_encoded


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

        def serialize(obj):
            """Helper function to recursively serialize objects."""
            if isinstance(obj, Base):
                return obj.class_to_dict()  # Call if it's an instance of Base
            elif isinstance(obj, list):
                return [
                    serialize(item) for item in obj
                ]  # Recursively serialize list items
            elif isinstance(obj, dict):
                return {
                    key: serialize(value) for key, value in obj.items()
                }  # Recursively serialize dict values
            else:
                return obj  # Return the object as is

        if isinstance(self, object):
            class_dict = {}
            # Include instance attributes
            for key, value in self.__dict__.items():
                if not key.startswith("_"):  # Exclude private properties
                    if self._is_primitive(value):
                        class_dict[key] = value
                    else:
                        class_dict[key] = serialize(value)
            # Include properties
            for key in dir(self):
                if isinstance(getattr(type(self), key, None), property):
                    value = getattr(self, key)
                    if self._is_primitive(value):
                        class_dict[key] = value
                    else:
                        class_dict[key] = serialize(value)
            return class_dict
        else:
            return self
    
    def class_to_ordered_dict(self):
        """
        Returns all class properties and their values as an OrderedDict in alphabetical order of the property names.
        (This takes about double the time of class_to_dict)

        :return: An OrderedDict of all class properties names and their values
        :rtype: OrderedDict
        """

        def serialize(obj):
            """Helper function to recursively serialize objects."""
            if isinstance(obj, Base):
                return obj.class_to_ordered_dict()  # Call if it's an instance of Base
            elif isinstance(obj, list):
                return [
                    serialize(item) for item in obj
                ]  # Recursively serialize list items
            elif isinstance(obj, dict):
                return OrderedDict(
                sorted(
                    ((key, serialize(value)) for key, value in obj.items()),
                    key=lambda item: item[0]
                )
            )  # Recursively serialize and sort dict values
            else:
                return obj  # Return the object as is

        if isinstance(self, object):
            items = []
            class_dict = OrderedDict()
            # Include instance attributes
            for key, value in self.__dict__.items():
                if not key.startswith("_"):  # Exclude private properties
                    if self._is_primitive(value):
                        items.append((key, value))
                    else:
                        items.append((key, serialize(value)))
            # Include properties
            for key in dir(self):
                if isinstance(getattr(type(self), key, None), property):
                    value = getattr(self, key)
                    if self._is_primitive(value):
                        items.append((key, value))
                    else:
                        items.append((key, serialize(value)))
            
            # Sort items alphabetically by key
            items.sort(key=lambda item: item[0])
            
            # Add sorted items to OrderedDict
            for key, value in items:
                class_dict[key] = value
            
            return class_dict
        else:
            return self

