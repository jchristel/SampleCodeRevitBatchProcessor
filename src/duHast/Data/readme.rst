Intro
=====

The Data namespace is an attempt to collect rooms related data from a Revit model in order for it to be stored in 
a graph database.

Structure
---------
THe proposed structure is:

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



Sheets
^^^^^^^

Sheets and all their properties are exported in one report.

