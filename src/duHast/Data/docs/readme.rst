Intro
=====

The Data namespace is an attempt to collect rooms related data from a Revit model in order for it to be stored in 
a graph database.

Architecture
------------

The namespace is organised into two distinct layers:

**Layer 1 — Collector**

Collector classes (e.g. ``DataRoom``, ``DataDoor``, ``DataCeiling``) faithfully capture all Revit data as-is.
They are verbose by design. Their job is "capture everything from Revit." These classes are not changed or extended
for analysis purposes.

**Layer 2 — Analysis**

Analysis classes (e.g. ``DataRoomAnalysis``, ``DataFFEItem``) are lean, curated representations purpose-built for
comparison, templating, and storage in the graph database. They reference collector objects by id (e.g. ``IfcGUID``
or Revit element id) rather than embedding them, avoiding data duplication.

Analysis classes are **not** derived from collector classes via inheritance. The two layers have different
responsibilities and different lifecycles — composition by reference is used instead.

.. note::
   What this document refers to as the *analysis layer* corresponds to what is also called *blueprints* or
   *templates* elsewhere in this document. These terms are equivalent. *Analysis layer* is the preferred term
   going forward.

Refer to ``revit_data_architecture_guidance.md`` for the full architectural rationale behind this design.

Structure
---------
The proposed structure is:

- Project

    - Building

        - Levels
        - Elements

            - FF&E
            - Ceilings
            - doors
            - rooms

        - sheets

            - view ports

                - views

                    - element tags

    - generic rooms

As a first step each nested item will get exported from Revit as a separate json file describing the existing instances and their properties.

Side Effects / use cases
------------------------

Some of this data will be used for other purposes as well:

- Ceilings to Rooms : utilities used to determine which ceiling appears in which room with the help of a 3rd party library shapely


Initial data reporting (harvesting)
-----------------------------------

Elements
^^^^^^^^^
TO DO

needs to include:

- family and family type name of element tagged: in order for it to be linked to ffe tag.
- room id and name: in order for it to be linked to room
- insertion point / rotation of Elements
- bounding box
- Revit design set data
- host model information (Name)
- Revit phasing data


Doors
^^^^^^^^^
Doors are exported in a separate report. The report contains all door instance and type properties, as well as the door location in the model.

Currently the following door properties are exported:

- bounding box
- Revit design set data
- door type properties
- door instance properties
- door level name and id
- host model information (Name)
- Revit phasing data


Refer to duHast.Revit.Doors.Export.to_data_door.get_all_door_data(doc) for the initial export of door data. This will return a list of DataDoor() objects.


Ceilings
^^^^^^^^^
Ceilings are exported in a separate report. The report contains all ceiling instance and type properties, as well as the ceiling location in the model.

Currently the following ceiling properties are exported:
- bounding box
- Revit design set data
- ceiling type properties
- ceiling instance properties
- ceiling level name and id
- host model information (Name)
- Revit phasing data


Refer to duHast.Revit.Ceilings.Export.to_data_ceiling.get_all_ceiling_data(doc) for the initial export of ceiling data. This will return a list of DataCeiling() objects.


Rooms
^^^^^^^

Rooms are exported as a separate report.

Currently the following room properties are exported:

- 2D room boundary polygon
- Revit design set data
- all room instance properties (There are no room type properties in Revit)
- host model information (Name)
- Revit phasing data
- room level name and level id
- TODO : add room id

Refer to duHast.Revit.Rooms.Export.to_data_room.get_all_room_data() for the initial export of room data. This will return a list of DataRoom() objects.



Sheets
^^^^^^^

Sheets and all their properties are exported in one report. That will require extra post processing steps to sort sheets and items into analysis classes (see Architecture section above).

Properties are exported by view port and associated view:

+-----------------+-------------------------------------+---------------------------------------------------------------------------------------+
| view type       | view port                           | view                                                                                  |
+=================+=====================================+=======================================================================================+
| plan view       | centre point on sheet, bounding box | bounding box, aspect ration, tags                                                     |
+-----------------+-------------------------------------+---------------------------------------------------------------------------------------+
| elevation views | centre point on sheet, bounding box | bounding box, tags, view direction (?)                                                |
+-----------------+-------------------------------------+---------------------------------------------------------------------------------------+
| 3D view         | centre point on sheet, bounding box | bounding box, view eye location, view direction                                       |
+-----------------+-------------------------------------+---------------------------------------------------------------------------------------+
| schedule        | location on sheet, bounding box     | number of rows in schedule, is schedule split (0 no, > 0 yes, and number of columns ) |
+-----------------+-------------------------------------+---------------------------------------------------------------------------------------+

For sheet export functionality refer to:
duHast.Revit.Views.Export.sheets_to_data.get_all_sheet_data this return a list of DataSheet() objects.



TODO: separate report for ffe tags:

- tag insertion point
- tag leader / elbow data
- family and family type name of element tagged
- insertions point / rotation of element tagged


Setting up Analysis Classes for room layout sheets
----------------------------------------------------------

The end goal is to have sheet analysis classes per room size, where the size is sorted into bands of .25sqm increments. That is further refined by bands 
of room proportions ( band step size to be confirmed) and last but not least by bands of items in rooms (step size is 5)

The room size is taking from the room reports which include the room area.
The room proportions are calculated using the room bounding box length in X / length in Y. The assumption here is that rooms are axis parallel and view ports are not rotated on sheet.
The number of items in room is derived from the number of entries in the schedule.

From the initial exports the following analysis classes need to be extracted:

- sheets by room size, proportion and number of items in room
- tags by item and view type

That sorted data will then need to be culled in order to arrive at:

- one sheet analysis class per (note: an analysis class might contain multiple sheets)

    - room size

        - room proportion by room size

        - no of items by room size


Impact on code structure:

Data classes used to export all data (collector layer) are not suitable to represent analysis classes. Collector classes are for instance missing a unique identifier tying rooms and 
sheets together. They also contain a lot of data exported from the Revit model in their instance and type properties which is not required in the analysis layer.

A separate analysis namespace contains classes to represent analysis data for rooms and sheets. These classes reference collector objects by id rather than inheriting from or
embedding them. This keeps the two layers independent and avoids data duplication.


Analysis - Sheets
====================

These analysis classes are used to generate room layout sheets based on the size and proportion of the room and the number of items in the room.

Properties required for sheet analysis class:

- room properties:
    - room size in sqm
    - room proportion (length in X / length in Y)
    - number of items in room

- sheet properties:
    - number of sheets
    - sheet view ports
        - view type
        - for section it also needs to include:
            - view index on elevation marker
        - view port location on sheet
        - view port bounding box
        

That requires that room data and sheet data exported can be linked together. Assume that a specific parameter on the sheet contains a link to the room.

Process to generate sheet analysis classes:

1. Get all room data from the graph database
2. Get all sheet data from the graph database
3. For each room, get all sheets that are linked to the room
4. Discard room if there are no sheets linked to it
5. Sort rooms into bands by size, proportion and number of items (dictionary where key is area banded in 0.5sqm steps and values are two dictionaries where the first key is the proportion banded in 0.1 steps and the second key is the number of items banded in 5 steps):
    - room size: round to nearest 0.5sqm
    - room proportion: round to nearest 0.1
    - number of items: round to nearest 5
6. For each band, sort and cull data:
    - cull duplicate or similar room in terms of size and proportion number of items in room:
        - room size: round X, Y and Z to nearest 0.25m 
        - room proportion: round to nearest 0.1
        - number of items: round to nearest 5

7. For each band, and their values generate a sheet analysis class
