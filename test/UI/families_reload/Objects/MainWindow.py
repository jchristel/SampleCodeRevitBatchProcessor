from duHast.UI.Objects.WPF.Windows.WPFWindowBase import WPFWindowBase


class Reloader(WPFWindowBase):

    def __init__(self, xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path):

        super(Reloader, self).__init__(xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path)

        # Set the height of the window
        self.Height = 400  # Set to your desired height

        # Additional window setup can go here
        self.Title = "Reload(er)"
    