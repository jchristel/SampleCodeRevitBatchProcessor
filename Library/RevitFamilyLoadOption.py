import os
import clr
import Autodesk.Revit.DB
from Autodesk.Revit.DB import *

class FamilyLoadOption(IFamilyLoadOptions):

	def OnFamilyFound(self, familyInUse, overwriteParameterValues):
		'Defines behavior when a family is found in the model.'
		overwriteParameterValues = True
		return True

	def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
		'Defines behavior when a shared family is found in the model.'
		source = FamilySource.Project
		overwriteParameterValues = True
		return True