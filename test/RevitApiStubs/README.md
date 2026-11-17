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

## Limits

- Stubs only reproduce names. A stubbed `FilteredElementCollector(doc).OfClass(...)` returns `None`, so code that iterates
  collectors needs a fake supplied by the test.
- Only types in the `Autodesk.Revit.*` namespaces of `RevitAPI.dll` are generated (not `RevitAPIUI`).
- Nested types are skipped.
