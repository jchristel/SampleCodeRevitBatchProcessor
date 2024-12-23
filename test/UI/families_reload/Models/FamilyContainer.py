
from Models.RevitFamily import RevitFamily
from Exceptions.FamilyConflictException import FamiliesConflictException

from duHast.Utilities.Objects.base import Base

class FamiliesContainer (Base):
    
    def __init__(self):
        
        super(FamiliesContainer, self).__init__()
        
        # ini list
        self._revit_families = []
    
    
    def get_all_families(self):
        
        return self._revit_families
    
    
    def add_family(self, revit_family):
    
        # type checking
        if(isinstance(revit_family,RevitFamily)==False):
            raise TypeError ("revit_family needs to be of type RevitFamily, got {} instead".format(type(revit_family)))
        
        # check if any reservations conflicts with the new one
        for existing_revit_family in self._revit_families:
            if(existing_revit_family.Conflicts(revit_family)):
                raise FamiliesConflictException(
                    message="New revit family conflicts existing family",
                    existing_family=existing_revit_family, 
                    new_family=revit_family
                )
        
        self._revit_families.append(revit_family)