"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The class representing the int value of a revit family Id.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from duHast.Utilities.Objects.base import Base

class FamilyID(Base):
    
    def __init__(self, id):
        """
        A class representing the int value of a revit family Id.

        :param id: the id of the family
        :type id: int
        """
        
        super(FamilyID, self).__init__()
        
        
        if (isinstance(id, int)==False):
            raise TypeError ("id needs to be of type int, got {} instead.".format(type(id)))
        
        self.id = id

    
    def __eq__(self, other):
        """
        Custom compare is equal override 

        :param other: Another instance of  ID class
        :type other: :class:`.FamilyId`
        :return: True if name value of other colour class instance equal the name values of this instance, otherwise False.
        :rtype: Bool
        """

        if isinstance(other, FamilyID)== False:
            return False
        
        if other.id == self.id:
            return True
        else:
            return False
            
     
    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)
    
    
    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """
        try:
            return hash(self.__class__)
        except Exception as e:
            raise ValueError(
                "Exception {} occurred.".format(
                    e
                )
            )