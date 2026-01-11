# Merge View - Add New Documents

## Overview

The Add New Documents dialog allows you to quickly add new documents to your database when you have files in your incoming folder that don't match any existing documents. This is the fastest way to expand your document register when processing new drawings, specifications, or other project documents.

The dialog displays all unmatched files from your incoming folder and helps you review and confirm document numbers and names before adding them to the database.

---

## When to Use This Feature

The Add New Documents dialog appears when you click the "Add New Documents" button in the Merge View. This button is only enabled when you have files in your incoming folder that don't match any documents in your database.

**Common Scenarios:**
- Adding the first batch of documents to a new project database
- Processing documents from a new discipline or package
- Adding newly issued document numbers to your register
- Expanding your document register as the project progresses

**What Happens:**
1. The application scans your incoming folder for files with revision indicators
2. Files that don't match any existing documents are identified
3. The dialog displays these files and lets you review the proposed document information
4. You can edit document numbers and names before adding them to the database
5. Once confirmed, the documents are added to your database

---

## Understanding the Dialog Layout

The Add New Documents dialog has four main sections:

### Header
Shows the dialog title: "Add New Documents to Database"

### Summary Bar
Displays three key counts to help you understand what's in the list:

**Total:** The number of files being processed

**Ready to Add:** Files that passed all validation checks (shown in green)

**Duplicates:** Files with duplicate document numbers or other errors (shown in red)

### Document List
A table showing all the files being added with the following columns:

**Status Indicator** (colored circle): Shows whether each file is ready to add or has issues
- Green: Ready to add
- Red: Has an error that must be fixed

**File Name:** The original filename from your incoming folder

**Extension:** The file type (e.g., .pdf, .dwg, .docx)

**Proposed Doc Number:** The document number extracted from the filename (editable)

**Proposed Doc Name:** The document name extracted from the filename (editable)

**Number Matches Filename:** Shows "Yes" or "No" to indicate if the document number matches the filename
- This helps you spot files where the document number modifier changed the number

**Status:** A description of the file's current status or any validation errors

### Action Buttons

**Add to Database:** Adds all ready documents to your database (disabled if no documents are ready)

**Cancel:** Closes the dialog without adding any documents

---

## Reading the Status Indicators

Each file has a colored circle that shows its status at a glance:

### Green Circle: Ready to Add
The file passed all validation checks and is ready to be added to your database.

**What This Means:**
- Document number is unique (not in the database)
- Document number is unique in the current list
- Document name is present
- File has a revision indicator in the filename

### Red Circle: Error - Needs Attention
The file has an issue that must be resolved before it can be added.

**Common Red Status Messages:**

**"Document number already exists in database"**
- This document number is already in your database
- You cannot add duplicate document numbers
- Options: Edit the proposed document number to make it unique, or cancel and check your database

**"Duplicate document number in list with same file type"**
- Another file in this list has the same document number and file extension
- You can only add one file of each type for each document number
- Options: Edit one of the document numbers to make them unique, or remove the duplicate file from your incoming folder

**"Missing document name"**
- The filename has the revision indicator at the very end with no document name after it
- Example: `ABC-001[A].pdf` has no name after the revision
- Options: Edit the Proposed Doc Name field, or rename the file in your incoming folder

**"Document number is required"**
- The Proposed Doc Number field is empty
- Options: Enter a document number in the editable field

**"Document name is required"**
- The Proposed Doc Name field is empty
- Options: Enter a document name in the editable field

**"Document number does not match file name"**
- The proposed document number doesn't match the filename
- This usually happens after you manually edit the document number
- This is a blocking error because it indicates a mismatch between the file and its metadata

---

## Editing Document Information

You can edit the document number and document name directly in the table.

### How to Edit

1. Click in the "Proposed Doc Number" or "Proposed Doc Name" cell you want to change
2. Type the new value
3. Press Enter or click outside the cell to confirm the change
4. The status will automatically update to show if the change fixed any errors

### Document Number Editing

**When You Shorten a Document Number:**

If you edit a document number to make it shorter, the application checks if there are related files that might belong to the same document.

**Example:**
- You have files: `ABC-001-01[A].pdf` and `ABC-001-02[A].dwg`
- You edit `ABC-001-01` to just `ABC-001`
- A dialog appears asking: "Found related files with document numbers starting with 'ABC-001'. Do you want to update them all to 'ABC-001'?"

**Your Options:**
- Click "Yes": All related files are updated to use the shorter document number
- Click "No": Only the file you edited is changed; other files keep their original numbers

**Why This Feature Exists:**

Some projects use sub-numbering (e.g., ABC-001-01, ABC-001-02) for related drawings. If you want to group them under a single document number (ABC-001), this feature saves you from manually editing each file.

### Document Name Editing

**Automatic Synchronization:**

When you change a document name, the application automatically synchronizes it across all files with the same document number.

**Example:**
- You have files: `ABC-001[A].pdf` and `ABC-001[A].dwg`
- Both have proposed document number "ABC-001"
- You edit the document name for the PDF to "Ground Floor Plan"
- The DWG file's document name automatically updates to "Ground Floor Plan"

**Why This Happens:**

Files with the same document number but different extensions (like PDF and DWG) represent the same document in different formats. They should have the same document name. The application keeps them synchronized to prevent inconsistencies.

---

## Understanding "Number Matches Filename"

This column shows whether the proposed document number matches what's in the filename.

### When You See "Yes"
The document number extracted from the filename matches the proposed document number. This is the normal case when no document number modifier is applied.

**Example:**
- Filename: `ABC-001[A] Floor Plan.pdf`
- Proposed Doc Number: `ABC-001`
- Number Matches Filename: `Yes`

### When You See "No"
The proposed document number is different from what's in the filename. This happens when:

1. **A document number modifier was applied:**
   - Your supported file type has a modifier that changes the document number
   - Example: File type has "Add Suffix" that adds "-PDF" to PDF files
   - Filename: `ABC-001[A].pdf` → Proposed Doc Number: `ABC-001-PDF`

2. **You manually edited the document number:**
   - You changed the Proposed Doc Number field
   - If the change makes the number not match the filename, you'll see a red error

**Why This Matters:**

The "Number Matches Filename" field helps you spot when document number modifiers are being applied, so you can verify the result is what you expect.

---

## Working with the Document List

### Sorting the List
Click on any column header to sort the list by that column. This helps you:
- Group files by extension
- Find duplicate document numbers
- Identify files with errors

### Selecting Multiple Files
You can select multiple rows in the table:
- Click and drag to select a range
- Hold Ctrl and click to select individual files
- Hold Shift and click to select everything between two rows

**Note:** Selecting files doesn't affect which ones are added. Only files with green status indicators will be added when you click "Add to Database."

### Scrolling Through Files
If you have many files to review:
- Use the scrollbar on the right
- Use your mouse wheel
- Use Page Up and Page Down keys

---

## Adding Documents to Your Database

### Prerequisites

Before you can add documents:
1. At least one file must have a green "Ready to Add" status
2. All duplicate errors must be resolved
3. All missing document names must be filled in

### Steps to Add Documents

1. **Review the Summary Bar:**
   - Check how many documents are ready to add
   - Check if any duplicates need to be resolved

2. **Fix Any Errors:**
   - Look for red status indicators
   - Read the status message to understand the issue
   - Edit document numbers or names as needed
   - Verify that your changes fixed the errors

3. **Click "Add to Database":**
   - The button is only enabled when at least one document is ready
   - Only documents with green status will be added
   - Documents with red status are skipped

4. **Wait for Completion:**
   - The application adds the documents to your database
   - Custom field values (if any) are initialized for the new documents
   - A success message appears when complete

5. **Dialog Closes:**
   - The dialog closes automatically after adding documents
   - The Merge View refreshes to show updated matching results
   - You'll see the newly added documents now match files in your incoming folder

### What Gets Added

For each ready document, the application creates:

**A document record in the database:**
- Document Number: From the Proposed Doc Number field
- Document Name: From the Proposed Doc Name field
- Initial Revision Indicator: Empty (no revisions yet)
- Revision ID: 0 (no revisions yet)

**Custom field placeholders (if you have custom fields defined):**
- One record for each custom field definition
- Initially empty values
- Ready to be filled in later through the database connection view

### Handling Files with Different Extensions

If you have multiple files with the same document number but different extensions (like ABC-001.pdf and ABC-001.dwg), the application creates only one document record in the database. This is the correct behavior because:

- Both files represent the same document in different formats
- The document register tracks document numbers, not individual files
- When you merge documents later, both file types will match this single document record

---

## Common Workflows

### Scenario 1: Adding Your First Documents to a New Project

**Situation:** You're starting a new project and need to add the first batch of documents.

**Steps:**
1. Place all your document files in the incoming folder
2. Click "Add New Documents" in the Merge View
3. Review the proposed document numbers and names
4. Verify that the extraction worked correctly (check "Number Matches Filename")
5. Click "Add to Database"
6. All documents are added to your empty database

**Tips:**
- Ensure all files follow your naming convention before adding them
- Review a few examples to confirm the revision separators are working correctly
- If document names are missing, check that your filename pattern is correct

### Scenario 2: Adding Documents from a New Discipline

**Situation:** You receive a new package of drawings from the structural engineer.

**Steps:**
1. Copy the structural drawings to your incoming folder
2. Click "Add New Documents" in the Merge View
3. Review the list - all structural drawing numbers should be new
4. Check for any duplicates (should be none if these are new disciplines)
5. Edit document names if needed to match your naming standards
6. Click "Add to Database"
7. The structural drawings are added to your database alongside existing documents

**Tips:**
- If you see duplicates, it might mean the document already exists under a different name
- Use the sort feature to group documents by number or extension
- Check that discipline prefixes are correct (e.g., all start with "STRUCT-")

### Scenario 3: Handling Multiple File Formats

**Situation:** You receive both PDF and DWG versions of the same drawings.

**Steps:**
1. Place all files in the incoming folder
2. Click "Add New Documents" in the Merge View
3. You'll see multiple rows for each document (one per file type)
4. The document numbers should match across file types
5. Edit the document name for any one file type
6. The application automatically synchronizes the name across all matching file types
7. Click "Add to Database"
8. One document record is created for each unique document number

**Tips:**
- Files with the same document number but different extensions are grouped together
- Editing the document name for any file updates all files with that document number
- After adding, both file types will match the single document in your database

### Scenario 4: Correcting Document Numbers Before Adding

**Situation:** Some files have incorrect document numbers in their filenames.

**Steps:**
1. Open the Add New Documents dialog
2. Find the file with the incorrect document number
3. Click in the "Proposed Doc Number" cell
4. Type the correct document number
5. The "Number Matches Filename" column will show "No" (this is expected)
6. The status message will show "Document number does not match file name" (red error)
7. You cannot add the document in this state

**Resolution Options:**

**Option A - Rename the file first:**
1. Click "Cancel" to close the dialog
2. Rename the file in your incoming folder to have the correct document number
3. Open the Add New Documents dialog again
4. The document number will now be correct and match the filename

**Option B - Add with the filename's document number:**
1. Leave the Proposed Doc Number as it was originally extracted
2. Make a note to rename the file later
3. Add the document to the database
4. After merging, rename both the database record and the file

**Recommended Approach:** Option A is preferred because it keeps your filenames and database in sync from the start.

---

## Troubleshooting

### The "Add to Database" Button Is Disabled

**Possible Causes:**
- All files have red status indicators (errors)
- The "Ready to Add" count is zero

**Solutions:**
- Fix the validation errors shown in the Status column
- Check for duplicate document numbers and edit one of them
- Ensure all document names are filled in
- Verify that files have revision indicators in their filenames

### I Don't See Any Files in the List

**Possible Causes:**
- No files in the incoming folder have revision indicators
- All files in the incoming folder already match documents in your database
- Files don't match any supported file types

**Solutions:**
- Check your incoming folder has files
- Verify files follow your naming convention (have revision prefix and suffix)
- Confirm the files are supported file types (check Settings → Current Documents → Supported File Types)
- Go back to the Merge View and check the Document Matching Results to see if files already match

### The Application Found Related Files When I Don't Want to Update Them

**Situation:** You shortened a document number and the dialog asked about updating related files, but you want to keep them separate.

**Solution:**
- Click "No" when prompted
- Only the file you edited will be changed
- Related files keep their original document numbers
- Each will create a separate document in the database

### Document Names Are All Empty

**Possible Causes:**
- Your files have the revision indicator at the very end of the filename
- Example: `ABC-001[A].pdf` instead of `ABC-001[A] Floor Plan.pdf`

**Solutions:**
- Rename files in your incoming folder to include document names after the revision indicator
- Or edit each Proposed Doc Name field manually in the dialog
- The first approach is recommended because it keeps filenames and database consistent

### I See "Number Matches Filename: No" for Many Files

**Possible Causes:**
- You have a document number modifier configured for that file type
- The modifier is adding or removing text from document numbers

**Solutions:**
- This is normal if you intentionally configured a modifier
- Review the Settings → Current Documents → Supported File Types to see the modifier rules
- If the modifier is wrong, cancel the dialog, fix the settings, and try again
- If the modifier is correct, proceed with adding the documents

### The Same Document Number Appears Multiple Times with Different Extensions

**Situation:** You see ABC-001 listed three times: once for PDF, once for DWG, and once for DOCX.

**Solution:**
- This is normal and expected behavior
- All three files represent the same document in different formats
- When you add them, only one document record is created in the database
- After merging, all three files will match the single document record
- Edit the document name for any one row, and it will synchronize to all rows with the same document number

---

## Best Practices

### Before Opening the Dialog

1. **Verify File Naming:** Ensure all files in your incoming folder follow your naming convention
2. **Check Revision Separators:** Confirm files have the correct revision prefix and suffix characters
3. **Remove Invalid Files:** Move out any files that don't belong or don't have revision indicators
4. **Organize by Batch:** Process documents in logical batches (e.g., all drawings from one package)

### While Reviewing Documents

1. **Check the Summary:** Look at the counts to see if most files are ready or if there are many errors
2. **Sort by Status:** Click the Status column header to group errors together
3. **Fix Duplicates First:** Resolve any duplicate document number errors before other issues
4. **Verify Names:** Ensure document names are meaningful and follow your standards
5. **Use Synchronization:** When editing multi-format documents, edit the name once and let it synchronize

### After Adding Documents

1. **Review the Results:** Check the Merge View to see the new matches
2. **Verify Counts:** Ensure the number of documents added matches your expectations
3. **Check Custom Fields:** If you use custom fields, remember to fill in values for new documents later
4. **Test Merge:** Try merging one document to verify the setup is correct

### Naming Standards

1. **Consistent Document Numbers:** Use a standard format across your project (e.g., DISC-NNN-NN)
2. **Descriptive Names:** Include enough information to identify the document without opening it
3. **Avoid Special Characters:** Stick to letters, numbers, hyphens, and underscores in document numbers
4. **Include Revision Indicators:** Always include the revision prefix and suffix in filenames

---

## Related Features

### Merge View Document Matching
After adding documents, return to the Merge View to see how the new documents match files in your incoming folder.

### Settings - Current Documents
Configure how document numbers are extracted from filenames, including revision separators and file type modifiers.

### Database Connection - Custom Fields
Define custom fields that will be available for all documents, including the ones you add through this dialog.

---

## Technical Notes

### How Document Numbers Are Extracted

1. The application reads the filename without extension
2. It finds the revision prefix character(s) in the filename
3. Everything before the revision prefix becomes the raw document number
4. The file type's document number modifier is applied (if configured)
5. The result is the Proposed Document Number

**Example:**
- Filename: `ABC-001[A] Floor Plan.pdf`
- Revision Prefix: `[`
- Raw document number: `ABC-001`
- File type modifier: None
- Proposed Doc Number: `ABC-001`

### How Document Names Are Extracted

1. The application finds the revision suffix character(s) in the filename
2. Everything after the revision suffix becomes the document name
3. Leading and trailing spaces are removed

**Example:**
- Filename: `ABC-001[A] Floor Plan.pdf`
- Revision Suffix: `]`
- Document Name: `Floor Plan`

### Validation Order

The application checks for errors in this order (first error found determines the status):

1. **No Revision Indicator:** File doesn't have revision prefix and suffix (filtered out, not shown)
2. **Missing Document Name:** Revision indicator is at the end of the filename with no name after it
3. **Duplicate Document Number:** Document number already exists in the database
4. **Duplicate in List:** Another file in the current list has the same document number and extension
5. **Number Does Not Match Filename:** Proposed document number doesn't match the filename (after editing)
6. **Ready to Add:** All checks passed

### Database Operations

When you click "Add to Database":

1. **Batch Insert:** All ready documents are inserted in a single database operation for speed
2. **Custom Field Initialization:** If custom fields exist, placeholder records are created
3. **Transaction Handling:** If any error occurs, no documents are added (all-or-nothing)
4. **Refresh:** The Merge View automatically refreshes to show the new matches

### Related Files Detection

The application uses filename comparison to find related files:

**For Document Number Changes:**
- When you shorten a document number, the application looks for other files where the full document number starts with your shortened version
- Example: Changing `ABC-001-01` to `ABC-001` will find `ABC-001-02`, `ABC-001-03`, etc.
- Case-insensitive comparison is used

**For Document Name Changes:**
- When you change a document name, the application looks for files with exactly the same document number
- All matches get the updated document name automatically
- This keeps multi-format documents consistent

---

## Glossary

**Document Number:** A unique identifier for a document in your database (e.g., ABC-001)

**Document Name:** A descriptive title for the document (e.g., "Ground Floor Plan")

**Proposed Doc Number:** The document number extracted from the filename, ready for your review and editing

**Proposed Doc Name:** The document name extracted from the filename, ready for your review and editing

**Revision Indicator:** The part of a filename that identifies the revision code (e.g., [A], [B1], [01])

**Revision Prefix:** The character(s) that mark the start of a revision indicator (e.g., `[`)

**Revision Suffix:** The character(s) that mark the end of a revision indicator (e.g., `]`)

**Supported File Type:** A file extension that the application knows how to process (e.g., .pdf, .dwg)

**Document Number Modifier:** A rule that changes how document numbers are extracted or stored for a specific file type

**Related Files:** Files that potentially belong to the same document based on document number patterns

**Custom Field:** User-defined metadata fields that can be attached to documents
