import json

from duHast.Revit.Common.Objects.ParameterDirectiveBase import ParameterDirectiveBase


class ParameterMappingDirective(ParameterDirectiveBase):
    """Class for parameter mapping directives."""

    data_type = "parameter_mapping_directive"

    def __init__(
        self,
        target_parameter_name="",
        source_parameter_name="",
        parameter_modifier=None,
        parameter_value=None,
        source_parameter_is_instance=True,
        parameter_getter=None,
        j=None,
        **kwargs
    ):
        """ Constructor for the ParameterMappingDirective class.

        :param target_parameter_name: The name of the parameter to be modified.
        :type target_parameter_name: str
        :param source_parameter_name: The name of the parameter to be used as the source.
        :type source_parameter_name: str
        :param parameter_modifier: The modifier to be applied to the parameter value.
        :type parameter_modifier: A function accepting the value as an argument and returning the modified value.
        :param parameter_value: The value to be applied to the parameter.
        :type parameter_value: any
        :param source_parameter_is_instance: Indicates if the source parameter is an instance parameter.
        :type source_parameter_is_instance: bool
        :param parameter_getter: A function that returns the value of the source parameter.
        :type parameter_getter: A function that returns the value of the source parameter.
        :param j: A json object containing the properties of the class.
        :type j: json
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict

        :raises ValueError: If the source_parameter_name or source_parameter_is_instance is not supplied in j.

        """

        super(ParameterMappingDirective, self).__init__(
            target_parameter_name=target_parameter_name,
            parameter_modifier=parameter_modifier,
            parameter_value=parameter_value,
            **kwargs
        )

        self.source_parameter_name = source_parameter_name
        self.source_parameter_is_instance = source_parameter_is_instance
        self.parameter_getter = parameter_getter

        # check if any data was past in with constructor!
        if j != None and len(j) > 0:
            # check type of data that came in:
            if type(j) == str:
                # a string
                j = json.loads(j)
            elif type(j) == dict:
                # no action required
                pass
            else:
                raise ValueError(
                    "Argument supplied must be of type string or type dictionary"
                )

            # load values and throw exception if something is missing!
            # do not load parameter modifier and getter functions...
            try:
                self.source_parameter_name = j["source_parameter_name"]
                self.source_parameter_is_instance = j["source_parameter_is_instance"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        ParameterMappingDirective.data_type, e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override. Ignores properties:

        - parameter_modifier
        - parameter_getter


        :param other: Another instance of  ParameterMappingDirective  class
        :type other: :class:`. ParameterMappingDirective`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, ParameterMappingDirective) and (
            self.source_parameter_name,
            self.source_parameter_is_instance,
            self.target_parameter_name,
            self.parameter_value,
        ) == (
            other.source_parameter_name,
            other.source_parameter_is_instance,
            other.target_parameter_name,
            other.parameter_value,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    # overwrite the base class to_json function
    def to_json(self):
        """
        Convert the instance of this class to json.
        Ignores parameter modifier and parameter getter class properties

        :return: A Json object.
        :rtype: json
        """

        # properties excluded from json dump
        excluded_properties = [
            "parameter_modifier",
            "parameter_getter",
        ]

        return json.dumps(
            self,
            indent=None,
            default=lambda o: {
                key: value
                for key, value in o.__dict__.items()
                if key not in excluded_properties
            },
        )
