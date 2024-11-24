
from duHast.Utilities.Objects.base import Base
from Models.RevitFamilyId import FamilyID

class RevitFamily(Base):
    
    def __init__(self, id, family_name,family_category, is_shared, match_status):
        
        super(RevitFamily, self).__init__()
        
        # set the id
        self.id = id
        
        # check type
        if(isinstance(family_name, str)==False):
            raise TypeError ("family_name needs to be of type string, got {} instead".format(type(family_name)))
        self.family_name = family_name
        
        if (isinstance(family_category, str)==False):
            raise TypeError("family_category needs to be of type string. Got {} instead".format(id))
        self.family_category = family_category
        
        if (isinstance(is_shared, bool)==False):
            raise TypeError("is_shared needs to be of type bool. Got {} instead".format(id))
        self.is_shared = is_shared

        if (isinstance(match_status, str)==False):
            raise TypeError("match_status needs to be of type string. Got {} instead".format(id))
        self.match_status = match_status
    
        # filed to store the file path to reload famiy from in
        self.family_file_path = None


    def Conflicts(self, revit_family):
        
        # check type
        if(isinstance(revit_family,RevitFamily)==False):
            raise TypeError ("revit_family needs to be of type RevitFamily, got {} instead".format(type(revit_family)))
        
        # check the  id
        if (revit_family.id != self.id):
            return False
        else:
            return True
    
    @property
    def id(self):
        return self._id.id
    
    @id.setter
    def id(self, value):
        # ini values
        if(isinstance(value, FamilyID)==False):
            raise TypeError("id needs to be of type RoomID. Got {} instead".format(value))
        self._id = value