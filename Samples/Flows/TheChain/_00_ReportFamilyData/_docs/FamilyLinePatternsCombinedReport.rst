#############################################
FamilyLinePatternsCombinedReport Report
#############################################

Summary
=======

This report list line pattern properties of families and their nested families.

- File name: FamilyLinePatternsCombinedReport.csv
- File type: comma separated
- Header row: yes

Properties listed
=====================

One row per line pattern per family processed.

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

    - Counter of how often this line pattern is used by elements within the family.

- usedBy

    - List of 

        - category elements using this line pattern in format:

            - {'categoryId': -2009527, 'categoryName': 'Hidden Lines'}
        
        - level elements using this line pattern in format:
        
            - {'levelTypeName': 'Ref. Level', 'levelId': 10225521}
        
        - nested families where elements use this line pattern (This is only shown in root families!):

            - {'patternId': 1436489, 'root': 'family name root :: family name nested'}

- patternName

    - The line pattern name.

- patternId

    - The line pattern id.

Notes
=====================

Nill
