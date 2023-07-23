"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This class is the default implementation for family load call backs.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import clr

import Autodesk.Revit.DB as rdb


class FamilyLoadOption(rdb.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        """
        Defines behavior when a family is found in the model.

        Overwrite parameter values is set to True.

        :param familyInUse: _description_
        :type familyInUse: _type_
        :param overwriteParameterValues: _description_
        :type overwriteParameterValues: _type_
        :return: True
        :rtype: bool
        """
        overwriteParameterValues = True
        return True

    def OnSharedFamilyFound(
        self, sharedFamily, familyInUse, source, overwriteParameterValues
    ):
        """
        Defines behavior when a shared family is found in the model.

        Overwrite parameter values is set to True. In case of any shared sub components already in the model but different in family loaded, the project version will be used.

        :param sharedFamily: _description_
        :type sharedFamily: _type_
        :param familyInUse: _description_
        :type familyInUse: _type_
        :param source: _description_
        :type source: _type_
        :param overwriteParameterValues: _description_
        :type overwriteParameterValues: _type_
        :return: True
        :rtype: bool
        """
        source = rdb.FamilySource.Project
        overwriteParameterValues = True
        return True
