from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase


from Objects.match_status_names import MatchStatusNames
from Models.RevitFamily import RevitFamily
class FamilyViewModel(ViewModelBase):
    
    def __init__(self, family):
        super(FamilyViewModel, self).__init__()
        
        
        if not (isinstance(family, RevitFamily)):
            raise ValueError("family needs to be of type RevitFamily, got {} instead.".format(type(family)))
        
        self._family = family

        self._match_status = MatchStatusNames.NO_MATCH.value
        self._is_selected = False
        self._family_file_path = None


    @property
    def IsSelected(self):
        return self._is_selected
    
    @IsSelected.setter
    def IsSelected(self, value):
        self._is_selected = value

    @property
    def FamilyName(self):
        return self._family.family_name

    @property
    def FamilyCategory(self):
        return self._family.family_category

    @property
    def FamilyIsShared(self):
        return self._family.is_shared
    
    @property
    def MatchStatus(self):
        return self._match_status
    
    @MatchStatus.setter
    def MatchStatus(self, value):
        self._match_status = value

    @property
    def FamilyFilePath(self):
        return self._family_file_path
    
    @FamilyFilePath.setter
    def FamilyFilePath(self, value):
        self._family_file_path = value