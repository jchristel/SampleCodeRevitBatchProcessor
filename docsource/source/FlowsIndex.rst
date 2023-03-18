Flows
---------------------------

Flows are Python modules which use the functions provided in the sample library and the Revit Batch Processor to solve a particular task.
They can be as simple as a single module which can be run using the GUI version of Revit Batch Processor only, or, on the other end of the spectrum, can be made up of a number of modules which are run in parallel through batch or powershell scripts.

Modifying element properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule::  ModifyAddSharedParas
    :members:

.. automodule::  ModifyDeleteSheetsAndViews
    :members:

.. automodule::  ModifyExportNWC_IFC
    :members:

.. automodule::  ModifyLevelGridScopeboxWorsket
    :members:

.. automodule::  ModifyModelMilestone
    :members:

.. automodule::  ModifyModelReloadLinks
    :members:

.. automodule::  ModifyRenameLoaded
    :members:

.. automodule::  ModifyRevisionAndApplyToSheets
    :members:

.. automodule::  ModifyRevisionSimple
    :members:

.. automodule::  ModifyRevitFileSaveAs
    :members:

.. automodule::   ModifyRevitLinksWorksetByList
    :members:

.. automodule::   ModifyRevitLinksWorksetInstanceToType
    :members:

.. automodule::   ModifyRevitLinksWorksetTypeToInstance
    :members:

Reporting element properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: ReportGridsLevels
    :members:

.. automodule:: ReportLinks
    :members:

.. automodule:: ReportMatts
    :members:

.. automodule:: ReportSharedParameters
    :members:

.. automodule:: ReportWallsDetails
    :members:

.. automodule:: ReportWorksets
    :members:


Batch Process - Pre processing Flows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modules useful when running batch processor without its user interface.

.. automodule:: Pre_BuildFileList
    :members:

.. _UI Flow :

File selection UI
""""""""""""""""""""

.. automodule:: script
    :members:

.. automodule:: UIFileSelect
    :members:


Batch Process - Post processing Flows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: Post_CombineReports
    :members:

.. automodule:: Post_AutoFiling
    :members:

Using Shapely and data extracted from Revit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: CeilingsToRooms
    :members: