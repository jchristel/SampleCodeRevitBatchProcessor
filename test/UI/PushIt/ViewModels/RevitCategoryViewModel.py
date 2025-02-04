from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase



from PushIt.Models.RevitCategory import RCategory
class RevitCategoryViewModel(ViewModelBase):
    
    def __init__(self, revit_category, is_selected=False):
        super(RevitCategoryViewModel, self).__init__()
        
        
        if not (isinstance(revit_category, RCategory)):
            raise ValueError("revit_category needs to be of type RCategory, got {} instead.".format(type(revit_category)))
        
        self._revit_category = revit_category.category_name
        self._is_selected = is_selected
        

    @property
    def IsSelected(self):
        return self._is_selected
    
    @IsSelected.setter
    def IsSelected(self, value):
        self._is_selected = value

    @property
    def CategoryName(self):
        return self._revit_category
