from duHast.Utilities.Objects import base

class RevitWarning(base.Base):
    def __init__(self, file_name = "", id="", description="", element_ids = [], **kwargs):
        """
        Class constructor.

        """

        super(RevitWarning, self).__init__(**kwargs)

        # set default values
        self.file_name = file_name
        self.id = id
        self.description = description
        self.element_ids = element_ids
    
    def class_to_csv(self, headers):
        if isinstance(self, object):
            csv_list = []
            for prop in headers:
                if(prop in self.__dict__):
                    csv_list.append(self.__dict__[prop])
                else:
                    csv_list.append("Property {} does not exist!".format(prop))
            return csv_list
        else:
            return []
