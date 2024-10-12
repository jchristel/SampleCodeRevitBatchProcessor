import clr

clr.AddReference("System.Core")

from duHast.UI.Objects.CommandBase import CommandBase


class RefreshRoomsInRevitModelCommand(CommandBase):

    def __init__(self, execute):
        """
        A command which triggers an external Revit event which in turn will update the Revit room data for this application.

        """
        # ini super class with arguments
        super(RefreshRoomsInRevitModelCommand, self).__init__(execute=execute)

    def Execute(self, parameter):
        """
        Trigger external event (Revit api)

        Args:
            parameter (_type_): _description_
        """

        self.execute()
