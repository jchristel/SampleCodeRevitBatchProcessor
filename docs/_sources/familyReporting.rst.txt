Revit API family property reporting.
=================================================================================

This collection of modules demonstrates how to report varies family properties and analyze some of the data returned.

Modules defining interfaces
----------------------------

.. autoclass:: IFamilyAction.IFamilyAction
    :members:

Data classes are used to store the information retrieved per family.

.. autoclass:: IFamilyData.IFamilyData
    :members:

Processor classes are used to retrieve specific bits of information from a family and store it in a data class.

.. autoclass:: IFamilyProcessor.IFamilyProcessor
    :members:

Utility class used to collect family data
------------------------------------------------

.. autoclass:: RevitFamilyDataCollector.RevitFamilyDataCollector
    :members:

Modules used to collect family category data
------------------------------------------------

.. autoclass:: RevitCategoryData.CategoryData
    :members:

.. autoclass:: RevitCategoryDataProcessor.CategoryProcessor
    :members:

Modules used to collect family base data
------------------------------------------------

.. autoclass:: RevitFamilyBaseData.FamilyBaseData
    :members:

.. autoclass:: RevitFamilyBaseDataProcessor.FamilyBaseProcessor
    :members:

Modules used to collect family line pattern data
------------------------------------------------

.. autoclass:: RevitLinePatternData.LinePatternData
    :members:

.. autoclass:: RevitLinePatternDataProcessor.LinePatternProcessor
    :members:

Modules used to collect family shared parameter data
------------------------------------------------------

.. autoclass:: RevitSharedParameterData.SharedParameterData
    :members:

.. autoclass:: RevitSharedParameterDataProcessor.SharedParameterProcessor
    :members:

Modules used to collect family warnings data
------------------------------------------------------

.. autoclass:: RevitWarningsData.WarningsData
    :members:

.. autoclass:: RevitWarningsDataProcessor.WarningsProcessor
    :members:

Utility modules used to read varies report types
------------------------------------------------------

.. automodule:: RevitFamilyReportUtils
    :members:

.. automodule:: RevitFamilyBaseDataUtils
    :members:

.. automodule:: RevitFamilyCategoryDataUtils
    :members:

Modules used to analyze family base data
------------------------------------------------------

.. automodule:: RevitFamilyBaseDataAnalysisCircularReferencing
    :members:

.. automodule:: RevitFamilyBaseDataAnalysisMissingFamilies
    :members:

.. automodule:: RevitFamilyBaseDataAnalysisReloadAdvanced
    :members:

.. automodule:: RevitFamilyReloadAdvancedUtils
    :members:

.. automodule:: RevitFamilyRenameFiles
    :members:

.. automodule:: RevitFamilyRenameFilesUtils
    :members:

.. automodule:: RevitFamilyRenameFindHostFamilies
    :members:

.. automodule:: RevitFamilyRenameLoadedFamilies
    :members:

