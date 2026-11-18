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


class FakeFamilyType(_Named):
    pass


class _FakeTypeIterator(object):
    """FamilyTypeSet.ForwardIterator(): Reset / MoveNext / Current."""

    def __init__(self, types):
        self._types = list(types)
        self._index = -1

    def Reset(self):
        self._index = -1

    def MoveNext(self):
        self._index += 1
        return self._index < len(self._types)

    @property
    def Current(self):
        return self._types[self._index]


class FakeFamilyTypeSet(object):
    """FamilyTypeSet: iterable, with Size and ForwardIterator()."""

    def __init__(self, types):
        self._types = types

    @property
    def Size(self):
        return len(self._types)

    def ForwardIterator(self):
        return _FakeTypeIterator(self._types)

    def __iter__(self):
        return iter(list(self._types))


class FakeFamilyManager(object):
    """FamilyManager: parameters, family types, NewType / DeleteCurrentType like Revit (duplicate names are refused)."""

    def __init__(self, parameters=None, type_names=None):
        self._parameters = list(parameters or [])
        self._types = [FakeFamilyType(n) for n in (type_names or [])]
        self.Types = FakeFamilyTypeSet(self._types)
        self.CurrentType = self._types[0] if self._types else None

    # shared parameter lookup used by duHast
    def GetParameters(self):
        return list(self._parameters)

    # catalogue code reads the Parameters property
    @property
    def Parameters(self):
        return list(self._parameters)

    def get_Parameter(self, name):
        for p in self._parameters:
            if getattr(p, "Definition", None) is not None and p.Definition.Name == name:
                return p
        return None

    def NewType(self, name):
        if any(t.Name == name for t in self._types):
            raise ValueError("A type named '{}' already exists.".format(name))
        new_type = FakeFamilyType(name)
        self._types.append(new_type)
        self.CurrentType = new_type
        return new_type

    def DeleteCurrentType(self):
        if len(self._types) <= 1:
            raise ValueError("The last type cannot be deleted.")
        self._types.remove(self.CurrentType)
        self.CurrentType = self._types[0]

    @property
    def type_names(self):
        return [t.Name for t in self._types]


class _FakeDefinition(object):
    def __init__(self, name):
        self.Name = name


class FakeParameter(object):
    """A family parameter as the catalogue code reads it: Definition.Name, IsInstance, IsDeterminedByFormula."""

    def __init__(self, name, is_instance=False, formula=False):
        self.Definition = _FakeDefinition(name)
        self.IsInstance = is_instance
        self.IsDeterminedByFormula = formula


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
        type_names=None,
    ):
        self.Title = title
        self.PathName = path_name
        self.elements = list(elements or [])
        self.IsFamilyDocument = True
        self.Application = object()  # the Revit application (only handed on)
        self.OwnerFamily = FakeOwnerFamily(family_category_name)
        self.FamilyManager = FakeFamilyManager(family_parameters, type_names)
        self.saved_as = []
        self._warnings = list(warnings or [])

    def GetWarnings(self):
        return list(self._warnings)

    def SaveAs(self, path, options):
        self.saved_as.append(path)
