"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A custom exception raised when a family conflict occurs.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used by RevitFamiliesModel.

"""

# Define a custom exception by subclassing Exception
from families.reload.Models.RevitFamily import RevitFamily


class FamiliesConflictException(Exception):
    def __init__(self, message, existing_family, new_family):
        """
        A custom exception raised when a family conflict occurs.

        :param message: the message of the exception
        :type message: str
        :param existing_family: the existing family
        :type existing_family: :class:`.RevitFamily`
        :param new_family: the new family
        :type new_family: :class:`.RevitFamily`
        """

        if isinstance(existing_family, RevitFamily) == False:
            raise TypeError(
                "existing_reservation need to be of type RevitFamily. Got {} instead.".format(
                    type(existing_family)
                )
            )
        self.existing_reservation = existing_family

        if isinstance(new_family, RevitFamily) == False:
            raise TypeError(
                "new_reservation need to be of type RevitFamily. Got {} instead.".format(
                    type(new_family)
                )
            )
        self.new_reservation = new_family

        # Call the base class constructor with the message
        super(FamiliesConflictException, self).__init__(
            message, existing_family, new_family
        )

    def __str__(self):
        """
        Custom string representation of the exception
        """

        return "FamiliesConflictException: {}".format(self.args[0])
