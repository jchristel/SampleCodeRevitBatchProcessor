"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
match status  names enum class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""



from enum import Enum


class MatchStatusNames(Enum):
    """
    Contains property names used in matcch status
    """

    NO_MATCH = "No Match!"
    MATCH_OK = "OK"
    MULTIPLE_MATCHES="Multiple matches found!"
    