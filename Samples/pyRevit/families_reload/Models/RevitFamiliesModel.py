from duHast.Utilities.Objects.base import Base

from Models.RevitFamily import RevitFamily
from Models.FamilyContainer import FamiliesContainer
from Objects.Settings import Settings

class RevitFamiliesModel(Base):
    
    def __init__(self):
        
        super(RevitFamiliesModel, self).__init__()
        
        #self.library_path = library_path
        self._families_container = FamiliesContainer()
        self._settings = Settings()
        self._families_to_reload = []
    
    @property
    def settings(self):
        return self._settings
    
    @settings.setter
    def settings(self, value):
        if not(isinstance (value,Settings)):
            raise ValueError("Value must be of type Setting, got {} instead.".format(type(value)))
        self._settings = value
    
    def get_all_families(self):
        return self._families_container.get_all_families()
    

    def add_family(self, family_model):
        # check type
        if(isinstance(family_model,RevitFamily)==False):
            raise TypeError ("family_model needs to be of type RevitFamily, got {} instead".format(type(family_model)))
        
        # add the family
        # todo 
        self._families_container.add_family(family_model)


    def reload_families(self, families):
        for fam in families:
            # check type
            if(isinstance(fam,RevitFamily)==False):
                raise TypeError ("family needs to be of type RevitFamily, got {} instead".format(type( fam)))
        
            # reload ...
    
    @property
    def families_to_reload(self):
        return self._families_to_reload
    
    def add_family_to_reload(self, value):
        if(isinstance(value,RevitFamily)==False):
            raise TypeError ("family needs to be of type RevitFamily, got {} instead".format(type(value)))
        self._families_to_reload.append(value)