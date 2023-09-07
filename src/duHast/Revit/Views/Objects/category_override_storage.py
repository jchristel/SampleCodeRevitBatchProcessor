from duHast.Utilities.Objects import base

class RevitCategoryOverride(base.Base):
    def __init__(self, main_category_name="", sub_category_name="", category_id = -1, revit_override = None, is_category_hidden = False, **kwargs):
        """
        Class constructor.

        """

        super(RevitCategoryOverride, self).__init__(**kwargs)

        # set default values
        self.main_category_name = main_category_name
        self.sub_category_name = sub_category_name
        self.category_id = category_id
        self.revit_override =revit_override
        self.is_category_hidden = is_category_hidden
