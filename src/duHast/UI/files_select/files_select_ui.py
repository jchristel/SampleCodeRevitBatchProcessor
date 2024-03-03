import clr, os, sys

clr.AddReferenceByPartialName("PresentationCore")
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName("WindowsBase")
clr.AddReferenceByPartialName("IronPython")
clr.AddReferenceByPartialName("Microsoft.Scripting")

from System.Windows import Application, SizeToContent
from System.Windows.Media import Brushes

# define path to duHast
# to get to the root folder of this repo if this script is called directly from a powershell, batch or similar 
ROOT_REPO_DIRECTORY = os.path.join(os.path.realpath(__file__), os.pardir, os.pardir, os.pardir, os.pardir)
sys.path.append(ROOT_REPO_DIRECTORY)


from ViewModel import ViewModel
from duHast.UI.Objects.XamlLoader import XamlLoader

# Define the path to your XAML file
CURRENT_SCRIPT_DIRECTORY = os.path.dirname(__file__)
XAML_FILE = "ui_v2.xaml"  # Replace with your XAML file name
XAML_FULL_FILE_NAME = os.path.join(CURRENT_SCRIPT_DIRECTORY, XAML_FILE)


# load xaml
xaml = XamlLoader(XAML_FULL_FILE_NAME)
# form window
window = xaml.Root
# view model
xaml.Root.DataContext = ViewModel(
    window,
    r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\SelectFiles\SelectFiles",
    r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor",
    ".rvt",
    3,
    False,
    "filter one"
    )
# Set the SizeToContent property of the window
#xaml.Root.SizeToContent = SizeToContent.WidthAndHeight




xaml.grid1.Background = Brushes.DarkSalmon
Application().Run(xaml.Root)
print ("Destination Path {}".format(xaml.Root.DataContext.destination_path))
print ("Source Path {}".format(xaml.Root.DataContext.source_path))
print ("Source File Extension {}".format(xaml.Root.DataContext.source_file_extension))
print ("Include sub dirs {}".format(xaml.Root.DataContext.include_sub_dirs))
