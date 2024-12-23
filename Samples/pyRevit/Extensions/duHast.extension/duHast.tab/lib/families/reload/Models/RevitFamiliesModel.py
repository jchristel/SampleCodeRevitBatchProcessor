"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The class representing a revit model and the families within.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used by the view model to store 

- the families to be reloaded 
- app settings
- the families container containing all the families in the model.

"""

from duHast.Utilities.Objects.base import Base

from families.reload.Models.RevitFamily import RevitFamily
from families.reload.Models.FamilyContainer import FamiliesContainer
from families.reload.Objects.Settings import Settings


class RevitFamiliesModel(Base):

    def __init__(self):
        """
        A class representing a revit model and the families within.
        """

        super(RevitFamiliesModel, self).__init__()

        # self.library_path = library_path
        self._families_container = FamiliesContainer()
        self._settings = Settings()
        self._families_to_reload = []

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        if not (isinstance(value, Settings)):
            raise ValueError(
                "Value must be of type Setting, got {} instead.".format(type(value))
            )
        self._settings = value

    def get_all_families(self):
        """
        Get all the families in the model.

        :return: all the families in the model
        :rtype: list of :class:`.RevitFamily`
        """

        return self._families_container.get_all_families()

    def add_family(self, family_model):
        """
        Add a family to the model.

        :param family_model: the family to add
        :type family_model: :class:`.RevitFamily`
        """

        # check type
        if isinstance(family_model, RevitFamily) == False:
            raise TypeError(
                "family_model needs to be of type RevitFamily, got {} instead".format(
                    type(family_model)
                )
            )

        # add the family
        self._families_container.add_family(family_model)

    def reload_families(self, families):
        """
        A command to reload the families in the model. (not implemented)
        """

        for fam in families:
            # check type
            if isinstance(fam, RevitFamily) == False:
                raise TypeError(
                    "family needs to be of type RevitFamily, got {} instead".format(
                        type(fam)
                    )
                )

            # reload ...

    @property
    def families_to_reload(self):
        return self._families_to_reload

    def add_family_to_reload(self, value):
        """
        Add a family to the list of families to reload.

        :param value: the family to add
        :type value: :class:`.RevitFamily`
        """

        if isinstance(value, RevitFamily) == False:
            raise TypeError(
                "family needs to be of type RevitFamily, got {} instead".format(
                    type(value)
                )
            )
        self._families_to_reload.append(value)
