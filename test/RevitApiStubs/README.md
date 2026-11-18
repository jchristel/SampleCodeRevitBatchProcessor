# Revit API stubs for the python tests

duHast modules that import `Autodesk.Revit.DB` cannot be loaded outside Revit. The folder `2026` holds importable python stand-ins
for the Revit 2026 API (names only: classes, enums with their values, methods and properties as no-ops). The NUnit python tests
add it to the IronPython search path (see `PythonRunner.SetupEngine`), which lets the family / category / line pattern / shared
parameter / warnings processors load. Behaviour a test needs is supplied by the test itself, e.g. a fake document (see
`FamilyBaseProcessorTests`).

## Regenerating

`Generator` reads the reference assembly of the `Nice3point.Revit.Api.RevitAPI` NuGet package:

```
dotnet run -c Release --project test/RevitApiStubs/Generator -- <path to RevitAPI.dll> test/RevitApiStubs/2026 "Revit 2026"
```

e.g. `%USERPROFILE%\.nuget\packages\nice3point.revit.api.revitapi\2026.4.10\ref\net8.0-windows7.0\RevitAPI.dll`.

For another Revit version generate into a sibling folder (`2027`...) and point `PythonRunner` at it.

## Overrides and test doubles

`overrides/revit_api_fakes.py` is imported when the test engine is created and replaces the few stub classes whose behaviour duHast code
needs: a value based `ElementId`, the `Element.Name.GetValue(element)` shim and a `FilteredElementCollector` that reads the `elements`
list of a fake document. `overrides/revit_test_doubles.py` holds the fake documents / families / warnings / shared parameters the tests
build on (`FakeFamilyDoc`, `FakeFamily`, `FakeWarning`, `FakeSharedParameterElement`...).

`overrides/pyrevit/` is a minimal stand-in for the pyRevit modules the toolbar and duHast import (`pyrevit.script.get_output()` returns a recording
output). `PythonRunner` also puts the toolbar's `lib` folder (`Samples/pyRevit/.../duHast.tab/lib`) on the search path, so the modules behind the
pyRevit buttons can be tested. pyRevit dialogs (`forms`) are not tested: tests patch the function that asks the user.

## Limits

- Stubs only reproduce names. A stubbed `FilteredElementCollector(doc).OfClass(...)` returns `None`, so code that iterates
  collectors needs a fake supplied by the test.
- Only types in the `Autodesk.Revit.*` namespaces of `RevitAPI.dll` are generated (not `RevitAPIUI`).
- Nested types are skipped.
