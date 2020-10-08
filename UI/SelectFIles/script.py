import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# xaml file name
xamlfile = 'ui.xaml'

# import WPF creator and base window
import wpf
from System import Windows


class MyWindow (Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self,xamlfile)


# let show the window
MyWindow().ShowDialog()

