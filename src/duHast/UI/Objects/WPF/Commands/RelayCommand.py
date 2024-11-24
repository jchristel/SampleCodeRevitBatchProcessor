
from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase

class RelayCommand(CommandBase):
    def __init__(self, execute):
        """
        A class to handle wpf command bindings.

        Args:
            execute (function): The method to execute when the command is invoked.
        """
        
        super(RelayCommand, self).__init__(execute=execute)
       
    def Execute(self, parameter):
        self.execute(parameter)