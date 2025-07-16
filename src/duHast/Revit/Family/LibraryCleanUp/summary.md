# Summary

Purpose of these scripts is to take a library of Revit families with the following characteristics:

- Unique Item Code per Family type stored in a specific parameter

    - Item codes represent groupings. i.e.  ITSE-001
    - one family may contain types with different codes: i.e. ITSE-001 and ITSE-002

- Family name is missing Item Code

And:

- Split families by item code and append the code to the family name:

    - Sample.rfa becomes:

        - Sample_ITSE_001.rfa
        - Sample_ITSE_002.rfa
    
- only keep types in split families which have the same grouping code



##  Process swapping families based on single library

1. Run script to generate family type data report using part atom exports per family
2. Combine type data report per family into a single report
3. Manually remove any family from that report not to be processed, because it may already match the new naming scheme
4. In Revit batch processor as a pre - process: Analyse report and build a report per family identifying:
    4.1 new family names including grouping code - > build in memory copy directives and execute them
    4.2 Swap directives identifying old family name and type name to new family name and type name ( save to file )
    4.3 list of types to be included in new family (save to file)
5. Copy family files and assign new name into a temp directory (Use copy directives)
6. Build a process list for Revit batch processor including these new family files
7. in Revit batch processor - open each family and remove types where grouping code does not match family
8. Create report of all the new families and their types
9. Optional : Rename types and update swap directives accordingly
10. in batch processor: Swap nested families using swap directives (entire library)
11. Reload families to project files
11. swap families in project files (pyRevit) using swap directives



##  Process swapping families based on two libraries

1. Define parameter name in each library containing the key by which to match families by
2. Read family reports from Library A and B, where A is the library containing the target families and B is the library containing the source families to be swapped out
3. loop over all families in B and try to find a match in A based on key parameter.
    3.1. check if match based on key, is of the same revit category, if so create swap directive
4. write all swap directives to file
