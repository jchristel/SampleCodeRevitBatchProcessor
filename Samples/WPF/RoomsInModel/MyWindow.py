from duHast.Revit.UI.Objects.WPFWindowBase import WPFWindowBase


class MyWindow(WPFWindowBase):

    def __init__(self, xaml_path, view_model, external_event, external_event_handler):
        """
        Constructor for the WPFWindowBase class

        :param xaml_path: path to the XAML file
        :param view_model: view model instance
        :param external_event: ExternalEvent instance
        :param external_event_handler: ExternalEventHandler instance
        """

        # make sure to initialize the base class
        super(MyWindow, self).__init__(xaml_path=xaml_path, view_model=view_model)

        self.external_event = external_event
        self.external_event_handler = external_event_handler

    def on_closed(self, sender, event):
        # Handle cleanup here
        self.external_event.Dispose()
        self.external_event = None
        self.external_event_handler = None
        # print("Window closed")
        pass
