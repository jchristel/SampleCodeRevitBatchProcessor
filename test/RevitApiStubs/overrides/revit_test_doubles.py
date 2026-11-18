"""
Fake documents and elements for tests driving duHast code which expects Revit objects.
Built on the generated Revit API stubs and the fakes in revit_api_fakes.
"""

import Autodesk.Revit.DB as db
from revit_api_fakes import ElementId


class FakeGuid(str):
    """A guid: compares by value, has ToString() like System.Guid."""

    def ToString(self):
        return str(self)


class _Named(object):
    def __init__(self, name):
        self.Name = name


class FakeFamilyCategory(_Named):
    pass


class FakeFamilyManager(object):
    def __init__(self, parameters=None):
        self._parameters = list(parameters or [])

    def GetParameters(self):
        return list(self._parameters)


class FakeFamilyParameter(object):
    """Family parameter; only shared parameters carry a GUID."""

    def __init__(self, guid=None):
        if guid is not None:
            self.GUID = FakeGuid(guid)


class FakeFailureDefinitionId(object):
    def __init__(self, guid):
        self.Guid = FakeGuid(guid)


class FakeWarning(object):
    def __init__(self, guid="", text="", failing=None, additional=None):
        self._guid = guid
        self._text = text
        self._failing = [ElementId(i) for i in (failing or [])]
        self._additional = [ElementId(i) for i in (additional or [])]

    def GetFailureDefinitionId(self):
        return FakeFailureDefinitionId(self._guid)

    def GetDescriptionText(self):
        return self._text

    def GetFailingElements(self):
        return list(self._failing)

    def GetAdditionalElements(self):
        return list(self._additional)


class FakeFamily(db.Family):
    """A family loaded into a document (db.Family), as returned by FilteredElementCollector(doc).OfClass(Family)."""

    def __init__(self, name, category_name):
        self.Name = name
        self.FamilyCategory = FakeFamilyCategory(category_name)


class FakeOwnerFamily(object):
    def __init__(self, category_name):
        self.FamilyCategory = FakeFamilyCategory(category_name)


class FakeSharedParameterElement(db.SharedParameterElement):
    def __init__(self, element_id, name, guid):
        self.Id = ElementId(element_id)
        self.Name = name
        self.GuidValue = FakeGuid(guid)


class FakeFamilyDoc(object):
    """A family document. 'elements' feeds FilteredElementCollector."""

    def __init__(
        self,
        title,
        path_name="",
        elements=None,
        warnings=None,
        family_parameters=None,
        family_category_name="Generic Models",
    ):
        self.Title = title
        self.PathName = path_name
        self.elements = list(elements or [])
        self.IsFamilyDocument = True
        self.OwnerFamily = FakeOwnerFamily(family_category_name)
        self.FamilyManager = FakeFamilyManager(family_parameters)
        self.saved_as = []
        self._warnings = list(warnings or [])

    def GetWarnings(self):
        return list(self._warnings)

    def SaveAs(self, path, options):
        self.saved_as.append(path)
