"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reload families command implementation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implements:

- Can Execute ( if the file is valid)
- Execute: Store selected families in the revit model property to be reloaded.

"""

from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase
from duHast.Utilities.directory_io import directory_exists
from families.reload.Models.RevitFamily import RevitFamily


class ReloadFamiliesCommand(CommandBase):

    def __init__(
        self,
        revit_model,
        families_selection_view_model,
        family_selection_view_navigation_service,
        execute=None,
    ):

        super(ReloadFamiliesCommand, self).__init__(execute=None)
        """
        Reload families command implementation.

        :param revit_model: the revit model
        :type revit_model: :class:`.RevitFamiliesModel`
        :param families_selection_view_model: the view model
        :type families_selection_view_model: :class:`.FamiliesSelectionViewModel`
        :param family_selection_view_navigation_service: the navigation service
        :type family_selection_view_navigation_service: :class:`.NavigateCommand`
        :param execute: the execute function
        :type execute: function
        """
        
        self.revit_model = revit_model
        self.families_selection_view_model = families_selection_view_model
        self.family_selection_view_navigation_service = (
            family_selection_view_navigation_service
        )
        self._execute = execute

        # sub scribe to property change event to enable or disable submit button
        self.families_selection_view_model.add_PropertyChanged(
            self.OnViewModelPropertyChanged
        )

    def CanExecute(self, parameter):
        """
        This method returns True if the file path  value is set  and points to a valid directory.
        """
        # print("in can execute check: {}".format(self.families_selection_view_model.LibraryPath ))
        return (
            self.families_selection_view_model.LibraryPath is not None
            and directory_exists(self.families_selection_view_model.LibraryPath)
        )

    def Execute(self, parameter):
        """
        Store selected families in the revit model property to be reloaded.
        """
        # print("In execute")
        families_in_model = self.revit_model.get_all_families()

        # TODO: store selected families in revit model property
        for fam in self.families_selection_view_model.Families:
            if fam.IsSelected:
                # find the family in the revit family model
                # Finding the object
                result = [
                    obj
                    for obj in families_in_model
                    if obj.family_name == fam.FamilyName
                    and obj.family_category == fam.FamilyCategory
                ]
                if result:
                    result[0].family_file_path = fam.FamilyFilePath
                    # add to list to be reloaded
                    self.revit_model.add_family_to_reload(result[0])

        if self._execute:
            self._execute(parameter)

    def OnViewModelPropertyChanged(self, sender, property_changed_args):
        """
        Forces to re-evaluate the reload button availability.

        Number of arg to this function is not optional!!

        Args:
            sender (_type_): _description_
            property_changed_args (_type_): _description_

        """
        # print("command property changed value: {}".format(property_changed_args.PropertyName))
        # check if a library path is provided and if
        if property_changed_args.PropertyName == "LibraryPath":
            self.on_can_execute_changed()
