import json

from duHast.Utilities.Objects import base


class ParameterDirectiveBase(base.Base):
    """Base class for all parameter directives."""

    data_type = "parameter_directive_base"

    def __init__(
        self,
        target_parameter_name="",
        parameter_modifier=None,
        parameter_value=None,
        j={},
        **kwargs
    ):
        """
        Constructor for the ParameterDirective class.

        :param target_parameter_name: The name of the parameter to be modified.
        :type target_parameter_name: str
        :param parameter_modifier: The modifier to be applied to the parameter value.
        :type parameter_modifier: A function accepting the value as an argument and returning the modified value.
        :param parameter_value: The value to be applied to the parameter.
        :type parameter_value: any
        :param j: A json object containing the properties of the class.
        :type j: json
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict

        :raises ValueError: If the target_parameter_name or parameter_value is not supplied in j.

        """
        super(ParameterDirectiveBase, self).__init__(**kwargs)

        self.target_parameter_name = target_parameter_name
        self.parameter_modifier = parameter_modifier
        self.parameter_value = parameter_value

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
                self.target_parameter_name = j["target_parameter_name"]
                self.parameter_value = j["parameter_value"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        ParameterDirectiveBase.data_type, e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override. Ignores properties:

        - parameter_modifier

        :param other: Another instance of  ParameterDirectiveBase  class
        :type other: :class:`. ParameterDirectiveBase`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, ParameterDirectiveBase) and (
            self.target_parameter_name,
            self.parameter_value,
        ) == (
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
        Ignores parameter modifier property

        :return: A Json object.
        :rtype: json
        """

        # properties excluded from json dump
        excluded_properties = [
            "parameter_modifier",
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
