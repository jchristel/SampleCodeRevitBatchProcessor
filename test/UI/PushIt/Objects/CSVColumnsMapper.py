"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
csvmapper enum class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""



from enum import Enum


class CSVColumnMapper(Enum):
    """
    Contains column indexes used in CSV file
    """

    COLUMN_ROOM_ID = 0
    COLUMN_AREA_BRIEFED = 1
    COLUMN_AREA_DESIGNED = 2
    
    ROW_PROPERTY_DESCRIPTION= 0
    ROW_PARAMETER_GUID= 1
    ROW_DATA_START = 2
    
