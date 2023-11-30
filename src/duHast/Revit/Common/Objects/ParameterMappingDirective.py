import json

from duHast.Revit.Common.Objects.ParameterDirectiveBase import ParameterDirectiveBase


class ParameterMappingDirective(ParameterDirectiveBase):
    data_type = "parameter_mapping_directive"

    def __init__(
        self,
        source_parameter_name="",
        source_parameter_is_instance=True,
        parameter_getter=None,
        j={},
        **kwargs
    ):
        super(ParameterMappingDirective, self).__init__(**kwargs)

        self.source_parameter_name = source_parameter_name
        self.source_parameter_is_instance = source_parameter_is_instance
        self.target_parameter_name = target_parameter_name
        self.parameter_modifier = parameter_modifier
        self.parameter_getter = parameter_getter
        self.parameter_value = None

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
                self.target_parameter_name = j["target_parameter_name"]
                self.parameter_value = j["parameter_value"]
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


        :param other: Another instance of  ParameterDirective  class
        :type other: :class:`. ParameterDirective`
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
