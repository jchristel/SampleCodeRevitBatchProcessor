"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A simple navigate command implementation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since this app only uses one view and one view model, the navigation is very simple.

"""

from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase


class NavigateCommand(CommandBase):

    def __init__(self, navigation_service):
        """
        A simple navigate command implementation.

        :param navigation_service: the navigation service
        :type navigation_service: :class:`.NavigationService`
        """

        super(NavigateCommand, self).__init__()

        self._navigation_service = navigation_service

    def Execute(self, parameter):
        """
        Execute the navigate command.

        :param parameter: the parameter
        :type parameter: object
        """

        # print("navi command")
        self._navigation_service.Navigate()
