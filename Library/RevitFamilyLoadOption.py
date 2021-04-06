from Autodesk.Revit.DB import *

class FamilyLoadOption(IFamilyLoadOptions):

	def OnFamilyLoad(familyInUse, overwriteParameterValues):
		overwriteParameterValues = True
		return True

	def OnSharedFamilyFound(sharedFamily, familyInUse, source, overwriteParameterValues):
		overwriteParameterValues = True
		return True