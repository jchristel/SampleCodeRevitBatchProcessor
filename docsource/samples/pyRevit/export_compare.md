# Compare Exports

**Panel:** Export | **Button:** Compare

Compares two sets of previously exported PDF or DWG files to identify sheets that have changed, been added, or been removed between exports.

## What it does

- Prompts you to select two export folders (or two snapshot report files) to compare.
- Identifies sheets present in one export but not the other.
- Highlights sheets where the file content has changed between the two exports.
- Outputs a summary report showing additions, removals, and changes.

## When to use this

Use this button when you need to produce a change register between two issue rounds, or to verify that only the expected sheets have been updated before a formal issue.

## Notes

- Both export sets must have been produced with the same filename naming convention for comparison to work correctly.
- The comparison is based on filenames and file hashes; it does not perform a visual page-by-page diff.
