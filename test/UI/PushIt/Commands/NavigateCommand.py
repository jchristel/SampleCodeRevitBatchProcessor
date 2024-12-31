from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase

class NavigateCommand(CommandBase):
    
    def __init__(self, navigation_service):
        
        super(NavigateCommand, self).__init__()
        
        self._navigation_service = navigation_service
    
    
    def Execute(self, parameter):
        print("navi command")
        self._navigation_service.Navigate()