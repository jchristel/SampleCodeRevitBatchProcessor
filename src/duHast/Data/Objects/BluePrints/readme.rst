Blueprints

The classes in this name space are used as blue prints to create elements in Revit.

They contain only properties required for the element creation as opposed to properties of existing elements.


Room Layout Sheets

This class has the following properties:

- room size
- room proportion
- number of items in room
- sheets

The first 3 properties are used to identify a suitable room layout sheet blueprint for a room depending on its size, proportions
and  number of items in room.

Sheets contains the blueprints of each sheet of this room layout sheet blueprint. Note: Number of sheets can vary per room layout sheet blueprint.

Sheets themselves contain any number of view ports (similar to Revit Viewports), which define the location of views on the sheet,
and in case of schedules, how many schedule segments, and the segment size.



