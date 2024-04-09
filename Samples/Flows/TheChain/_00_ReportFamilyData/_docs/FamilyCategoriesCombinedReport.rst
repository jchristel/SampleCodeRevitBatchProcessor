#############################################
FamilyCategoriesCombinedReport Report
#############################################

Summary
=======

This report list all sub categories, their properties and their usage in a family.

- File name: FamilyCategoriesCombinedReport.csv
- File type: comma separated
- Header row: yes

Properties listed
=====================

One row per sub catgeory per family processed.

- root

    - Describes the location of the family within the (tree like) nesting structure of the root (top most) family.
    - Each nesting level is indicated by a ' :: '
    - Always contains, as a last entry, the actual family name

- rootCategory

    - Similar to root, this describes the category nesting structure.
    - Always contains, as a last entry, the actual family category

- familyName

    - The family name (without file extension)

- familyFilePath

    - The fully qualified file path of the family file.

- usageCounter

    - Counter of how often this sub category is used by elements within the family.

- usedBy

    - List of 

        - Element ids if element is within family processed 
        - Family root path: if subcatgeory is used in a nested family somwhere within the nesting structre. This is only shown in root families!

- categoryName

    - The Revit category name. Exceptions are:
        - Import in families: 
        - Reference planes:

- subCategoryName

    - The sub category name.

- subCategoryId

    - The element id of the sub category

- graphicProperty_3D

    - TBC (reports NULL for now)

- graphicProperty_Cut

    - TBC (reports NULL for now)

- graphicProperty_Projection

    - TBC (reports NULL for now)

- graphicProperty_MaterialName

    - The name of the material assigned to this sub-category. Default in 'None'

- graphicProperty_MaterialId

    - The element id of the materail assigned to the sub-category. Default is '-1' which is no material.

- graphicProperty_LineWeightCut

    - The line weight of this sub-category when cut. Default in 'None' which is used for families which always appear in elevation.

- graphicProperty_LineWeightProjection

    - The line weight of this sub-category when projected. This will always have a value.

- graphicProperty_Red

    - The red property of the sub-category RGB colour.

- graphicProperty_Green

    - The green property of the sub-category RGB colour.

- graphicProperty_Blue	

    - The blue property of the sub-category RGB colour.


Notes
=====================

Nill