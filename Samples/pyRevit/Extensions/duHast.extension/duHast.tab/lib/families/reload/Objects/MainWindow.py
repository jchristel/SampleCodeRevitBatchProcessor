"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The class representing the main window of the app.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from duHast.UI.Objects.WPF.Windows.WPFWindowBase import WPFWindowBase


class Reloader(WPFWindowBase):

    def __init__(
        self, xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path
    ):
        """
        A window for the reloader app.

        :param xaml_path: path to the XAML file
        :type xaml_path: str
        :param main_view_model: the main view model
        :type main_view_model: :class:`.FamiliesSelectionViewModel`
        :param xaml_by_view_model: a dictionary mapping view models to XAML files
        :type xaml_by_view_model: dict
        :param resources_xaml_path: path to the resources XAML file
        :type resources_xaml_path: str
        """

        super(Reloader, self).__init__(
            xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path
        )

        # Set the height of the window
        self.Height = 400  # Set to your desired height

        # Additional window setup can go here
        self.Title = "Reload(er)"
