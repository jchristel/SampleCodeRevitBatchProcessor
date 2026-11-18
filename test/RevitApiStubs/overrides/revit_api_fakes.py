"""
Behaviour for the generated Revit API stubs which tests rely on.

The generated stubs (test/RevitApiStubs/<version>) only carry names. This module replaces the few classes whose behaviour the
duHast code needs with small working fakes. It is imported once, when the test python engine is created, before any duHast
module is loaded, so that both 'import Autodesk.Revit.DB as rdb' and 'from Autodesk.Revit.DB import ...' see the fakes.

A fake document is any python object. The collector reads its elements from the document's 'elements' list.
"""

import Autodesk.Revit.DB as _db


class ElementId(object):
    """Value based element id: equal and hashable by value, like the real one."""

    def __init__(self, value=-1):
        self.Value = int(value)

    @property
    def IntegerValue(self):
        return self.Value

    def __eq__(self, other):
        return isinstance(other, ElementId) and other.Value == self.Value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.Value)

    def __repr__(self):
        return "ElementId({})".format(self.Value)


class _ElementNameProperty(object):
    """Stands in for the .net property object 'Element.Name': Element.Name.GetValue(element)."""

    def GetValue(self, element):
        return element.Name


class FilteredElementCollector(object):
    """Collector over the 'elements' list of a fake document."""

    def __init__(self, doc, *args):
        self._elements = list(getattr(doc, "elements", []))

    def OfClass(self, cls):
        self._elements = [e for e in self._elements if isinstance(e, cls)]
        return self

    def OfCategory(self, category):
        self._elements = [e for e in self._elements if getattr(e, "BuiltInCategory", None) == category]
        return self

    def WhereElementIsNotElementType(self):
        self._elements = [e for e in self._elements if not getattr(e, "IsElementType", False)]
        return self

    def WhereElementIsElementType(self):
        self._elements = [e for e in self._elements if getattr(e, "IsElementType", False)]
        return self

    def ToElements(self):
        return list(self._elements)

    def ToElementIds(self):
        return [e.Id for e in self._elements]

    def GetElementCount(self):
        return len(self._elements)

    def FirstElement(self):
        return self._elements[0] if self._elements else None

    def __iter__(self):
        return iter(self._elements)

    def __len__(self):
        return len(self._elements)


_db.ElementId = ElementId
_db.FilteredElementCollector = FilteredElementCollector
_db.Element.Name = _ElementNameProperty()
