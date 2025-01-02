#######################
PushIt
#######################

PushIt is a simple tool to push room data into families or rooms in Revit. It consists of two major components:

1. A Revit add-in to push data into Revit
2. A set of families representing rooms



***********************
PushIt Add-in
***********************

The PushIt add-in is a Revit add-in that allows users to push data into Revit. The add-in is written in IronPython and uses the Revit API to interact with Revit. The add-in is designed to work with Revit 2023 and later versions.
It has its own tab in the Revit ribbon, which contains the following buttons:

1. PushIt: Pushes data into Revit
2. Settings: Opens the settings dialog


=======================
User interface
=======================

The add-in provides a simple user interface to push data into Revit. The user interface consists of the following components:

1. A list of rooms


=======================
Room data
=======================

Room data is stored in a csv file. 

The first two rows of the csv file contain parameter information. The first row contains a human readable description per column, which will also be displayed in the header row of the user interface.
The second row contains the GUID's of the shared parameter that the data of that column will be pushed into.

The csv file contains as an absolute minimum the following columns (in this order):

1. Room unique id. This is a unique identifier for the room and is used to match the room in Revit to the data in the csv file.
2. Briefed area. The briefed area of the room.


As an absolute minimum, the csv file should contain columns 1 and 2. The csv file can contain more columns, which will be pushed into Revit as well. 

| For a sample refer to \Samples\Data_Min.csv

When the csv file is loaded into the add-in, the add-in will check if:

- The values in the first column are indeed unique.
- The shared parameters exist in the Revit model.

If either of these checks fail, the add-in will display a warning message with details about the issue and will not load the data.