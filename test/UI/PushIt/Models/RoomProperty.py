from duHast.Utilities.Objects.base import Base

class RoomProperty(Base):
    
    def __init__(self, name, value, parameter_guid, unit_converter = None):
        
        super(RoomProperty, self).__init__()
        
        
        if (isinstance(name, str)==False):
            raise TypeError ("name needs to be of type str, got {} instead.".format(type(id)))
        
        self.name = name
        
        if (isinstance(value, str)==False):
            raise TypeError("value needs to be of type str. Got {} instead.".format(id))
        self.value = value
        
        if (isinstance(parameter_guid, str)==False):
            raise TypeError("parameter_guid needs to be of type str. Got {} instead.".format(id))
        self.parameter_guid = parameter_guid
        
        # unit converter used when pushing data to revit (some data is read as string but needs to be float in revit)
        self.unit_converter = unit_converter

    
    def __eq__(self, other):
        """
        Custom compare is equal override 

        :param other: Another instance of  RoomProperty class
        :type other: :class:`.RoomProperty`
        :return: True if name value of other colour class instance equal the name values of this instance, otherwise False.
        :rtype: Bool
        """

        if isinstance(other, RoomProperty)== False:
            return False
        
        if other.name == self.name and other.value == self.value and other.parameter_guid == self.parameter_guid:
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