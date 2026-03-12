

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class representing the shared parameter model.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import json

from duHast.Utilities.Objects.base import Base

class ParameterModel(Base):

    """
    A class representing the shared parameter model.
    """
    def __init__(self, name = None, group=None, is_type_parameter = True, para_type=None, visibility=False, group_type_id=None, shared_parameter_file_path=None, parameter_value = None, value_is_formula = False, j=None):
        """
        Constructor for the parameter data class.

        :param name: The name of the parameter.
        :type name: str
        :param group: The group of the parameter. (within the sharted parameter file)
        :type group: str
        :param is_type_parameter: Is the parameter a type parameter (True) or instance parameter (False)
        :type is_type_parameter: bool
        :param para_type: The type of the parameter. (Text, Number, etc.)
        :type para_type: str
        :param visibility: The visibility of the parameter.
        :type visibility: bool
        :param group_type_id: The grouping of the parameter. (where it will appear in revit UI under)
        :type group_type_id: str
        :param shared_parameter_file_path: The path to the shared parameter file.
        :type shared_parameter_file_path: str

        """

        super(ParameterModel, self).__init__()

        self._name = name
        self._group = group
        self._is_type_parameter = is_type_parameter
        self._para_type = para_type
        self._visibility = visibility
        self._group_type_id = group_type_id
        self._shared_parameter_file_path = shared_parameter_file_path
        self._parameter_value = parameter_value
        self._value_is_formula = value_is_formula

        json_var = None
        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )
        
            try:
                self._name = (json_var.get("name",None,))
                self._group = (json_var.get("group",None,))
                self._is_type_parameter = (json_var.get("is_type_parameter",True,))
                self._para_type = (json_var.get("para_type",None,))
                self._visibility = (json_var.get("visibility",None,))
                self._group_type_id = (json_var.get("group_type_id",None,))
                self._shared_parameter_file_path = (json_var.get("shared_parameter_file_path",None,))
                self._parameter_value = (json_var.get("parameter_value",None,))
                self._value_is_formula = (json_var.get("value_is_formula",False,))
            
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value

    @property
    def is_type_parameter(self):
        return self._is_type_parameter
    
    @is_type_parameter.setter
    def is_type_parameter(self, value):
        self._is_type_parameter = value
    
    @property
    def para_type(self):
        return self._para_type

    @group.setter
    def para_type(self, value):
        self._para_type = value
    
    @property
    def visibility(self):
        return self._visibility
    
    @visibility.setter
    def visibility(self, value):
        self._visibility = value
    
    @property
    def group_type_id(self):
        return self._group_type_id
    
    @group_type_id.setter
    def group_type_id(self, value):
        self._group_type_id = value
    
    @property
    def shared_parameter_file_path(self):
        return self._shared_parameter_file_path
    
    @shared_parameter_file_path.setter
    def shared_parameter_file_path(self, value):
        self._shared_parameter_file_path = value

    @property
    def parameter_value(self):
        return self._parameter_value
    
    @parameter_value.setter
    def parameter_value(self, value):
        self._parameter_value = value
    
    @property
    def value_is_formula(self):
        return self._value_is_formula
    
    @value_is_formula.setter
    def value_is_formula(self, value):
        self._value_is_formula = value
