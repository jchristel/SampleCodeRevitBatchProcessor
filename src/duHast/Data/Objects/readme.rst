=======
Goals
========


The Data namespace contains classes that are used to store room based data in a structured way.

The intend is to use this data either to simply query what elements are in a room or to create new elements in a room based on the data.

2 step process




1 Harvest data from Revit

The classes in the Collector namespace are used to collect data from Revit. They contain element properties that are used to establish relation ships between elements as well as geometry data defining location, size, rotation etc.


2 Classify data into blue prints

The classes in the Objects namespace are used to classify the data collected from Revit into blue prints. They contain only properties required for the element creation as opposed to properties of existing elements. The blue prints are used to create new elements in Revit.


3 Apply Data