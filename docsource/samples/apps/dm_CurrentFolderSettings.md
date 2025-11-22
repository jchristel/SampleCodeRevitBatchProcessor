# Current Documents Settings

## Overview

The Current Documents section in the Settings view configures how the application handles incoming documents, including file naming conventions, folder locations, filing rules, and supported file types.

## Settings Sections

### 1. Revision Markers

These settings define the characters used to identify revision indicators in document filenames.

#### Revision Prefix

**Description:** Character(s) that mark the beginning of a revision identifier in a filename.

**Example:** In the filename `Document_Rev[A].pdf`, the revision prefix is `[`

**Validation:**
- Custom validation through `RevisionSeparatorValidator`
- Must be a valid revision marker character

**Usage:** The application uses this prefix to parse and identify revision information from filenames when matching documents against the database.

#### Revision Suffix

**Description:** Character(s) that mark the end of a revision identifier in a filename.

**Example:** In the filename `Document_Rev[A].pdf`, the revision suffix is `]`

**Validation:**
- Custom validation through `RevisionSeparatorValidator`
- Must be a valid revision marker character

**Usage:** Works in conjunction with Revision Prefix to extract revision information from filenames.

---

### 2. Folder Paths

Configuration for the directories used in document processing.

#### Incoming Folder Path

**Description:** Path to the folder containing documents to be processed by the application.

**Validation:**
- Folder must exist on the file system
- Validated using `FolderPathValidator.ValidateFolderExists`

**Features:**
- Text input with real-time validation
- Browse button to select folder via dialog
- Validation errors displayed as tooltips

**Usage:** The application monitors this folder for new documents to process and match against the database.

#### Archive Folder Path

**Description:** Path to the folder where superseded or archived documents are stored.

**Note:** This setting maps to `SupersededFolderPath` in the underlying configuration.

**Validation:**
- Folder must exist on the file system
- Validated using `FolderPathValidator.ValidateFolderExists`

**Features:**
- Text input with real-time validation
- Browse button to select folder via dialog
- Validation errors displayed as tooltips

**Usage:** When documents are superseded by newer revisions, the older versions are moved to this archive location.

---

### 3. Filing Rules

Filing rules determine where incoming documents are filed based on their filename patterns. Rules are evaluated from top to bottom, and the first matching rule determines the target directory.

#### Rule Evaluation Order

**Priority:** Rules are evaluated in the order they appear in the list (top to bottom). The first rule that matches a filename wins, and no further rules are evaluated.

**Reordering:** Use the Move Up and Move Down buttons to adjust rule priority.

#### Available Rule Types

##### BeginsWith

**Description:** Matches filenames that start with the specified filter value.

**Example:**
- Filter Value: `ARCH-`
- Matches: `ARCH-001-Drawing.pdf`, `ARCH-Floor-Plan.dwg`
- Does Not Match: `STRUCT-ARCH-001.pdf`

##### Contains

**Description:** Matches filenames that contain the specified filter value anywhere in the name.

**Example:**
- Filter Value: `MECHANICAL`
- Matches: `MECHANICAL-001.pdf`, `Project-MECHANICAL-Drawing.dwg`, `Test-MECHANICAL.pdf`
- Does Not Match: `ARCH-001.pdf`

##### NotBeginsWith

**Description:** Matches filenames that do NOT start with the specified filter value.

**Example:**
- Filter Value: `TEMP-`
- Matches: `ARCH-001.pdf`, `Drawing.dwg`, `Notes.docx`
- Does Not Match: `TEMP-File.pdf`, `TEMP-Drawing.dwg`

##### NotContains

**Description:** Matches filenames that do NOT contain the specified filter value anywhere in the name.

**Example:**
- Filter Value: `DRAFT`
- Matches: `ARCH-001.pdf`, `Final-Drawing.dwg`, `Report.pdf`
- Does Not Match: `DRAFT-Report.pdf`, `Drawing-DRAFT.dwg`

##### Default (CatchAll)

**Description:** Matches all files regardless of filename. This is the default/fallback rule.

**Special Properties:**
- Only one Default rule allowed in the system
- Cannot be deleted (can only be edited to change target path)
- Displayed in bold in the list view
- Automatically created on first initialization (points to user's Documents folder)
- Filter value is always empty for CatchAll rules

**Usage:** Ensures every file has a destination even if no other rules match.

#### Filing Rule Management

##### Adding a Rule

1. Click the "Add" button
2. Select a rule type from the dropdown
3. Enter a filter value (not required for CatchAll)
4. Browse or enter a target directory path
5. Click Save

**Validation:**
- Duplicate rules (same type and filter value) are not allowed
- Only one CatchAll rule is permitted
- Target path must be a valid directory

##### Editing a Rule

1. Select a rule from the list
2. Click the "Edit" button
3. Modify the rule properties
4. Click Save

**Note:** For CatchAll rules, only the target path can be modified.

##### Removing a Rule

1. Select a rule from the list
2. Click the "Remove" button

**Restrictions:**
- CatchAll rules cannot be removed
- Any other rule type can be removed

##### Reordering Rules

**Move Up:** Increases the priority of the selected rule (moves it higher in the list)

**Move Down:** Decreases the priority of the selected rule (moves it lower in the list)

**Note:** Rule order is critical because evaluation stops at the first match.

#### ListView Columns

- **Filter Type:** The type of rule (BeginsWith, Contains, NotBeginsWith, NotContains, Default)
- **Filter Value:** The text value used for matching (empty for CatchAll)
- **Target Path:** The directory where matching files will be filed

---

### 4. Supported File Types

Defines which file extensions the application will process and how document numbers should be modified for each file type.

#### File Type Configuration

Each supported file type consists of:

##### File Extension

**Description:** The file extension including the leading period.

**Example:** `.pdf`, `.dwg`, `.docx`

**Validation:**
- Must include the leading period
- Must be unique (no duplicate extensions allowed)
- Case-insensitive comparison

##### Description

**Description:** Human-readable description of the file type.

**Example:** "PDF Document", "AutoCAD Drawing", "Word Document"

**Purpose:** Provides context for users about what the file extension represents.

##### Number Modifier

**Description:** Optional modifier that transforms document numbers for specific file types when matching against the database.

**Purpose:** Allows different file types to have different document numbering schemes. For example, a CAD drawing might need a "-DWG" suffix added to its document number when stored.

**Available Modifiers:**

###### None (No Modifier)

**Description:** No modification applied to document numbers.

**Display:** "(None)" or empty display

**Usage:** Default for PDF files and file types that use standard document numbers.

###### Add Prefix (AddAtIndex with index 0)

**Description:** Adds a specified string to the beginning of the document number.

**Example:**
- Original Document Number: `ABC-123`
- Prefix: `DRAFT-`
- Modified Number: `DRAFT-ABC-123`

**Display:** `Add Prefix: DRAFT-`

###### Add Suffix (AddToEnd)

**Description:** Adds a specified string to the end of the document number.

**Example:**
- Original Document Number: `ABC-123`
- Suffix: `-DWG`
- Modified Number: `ABC-123-DWG`

**Display:** `Add Suffix: -DWG`

###### Add at Index (AddAtIndex)

**Description:** Inserts a specified string at a specific character position in the document number.

**Example:**
- Original Document Number: `ABC-123`
- Insert Value: `-REV`
- Index: 3
- Modified Number: `ABC-REV-123`

**Display:** `Add at Index 3: -REV`

**Note:** Index 0 is displayed as "Add Prefix" for clarity.

###### Replace

**Description:** Replaces all occurrences of one string with another in the document number.

**Example:**
- Original Document Number: `ABC-TEMP-123`
- Old Value: `TEMP`
- New Value: `FINAL`
- Modified Number: `ABC-FINAL-123`

**Display:** `Replace: TEMP → FINAL`

#### Required File Types

##### PDF

**Special Status:** PDF is a required file type and has special protections:

- Cannot be removed from the list
- Displayed in bold font in the list view
- Automatically created if missing during initialization
- File extension field is disabled during editing
- Default modifier is None

**Rationale:** PDF is the standard format for document management and must always be supported.

#### File Type Management

##### Adding a File Type

1. Click the "Add" button in the Supported File Types section
2. Enter the file extension (with leading period)
3. Enter a description
4. Select a number modifier (optional)
   - Choose modifier type from dropdown
   - Configure modifier-specific parameters
5. Click Save

**Validation:**
- File extension must be unique
- File extension must include leading period
- Modifier configuration must be valid (if specified)

##### Editing a File Type

1. Select a file type from the list
2. Click the "Edit" button
3. Modify the properties
4. Click Save

**Restrictions:**
- PDF file extension cannot be changed
- Description and modifier can always be edited

##### Removing a File Type

1. Select a file type from the list
2. Click the "Remove" button

**Restrictions:**
- PDF file type cannot be removed
- Any other file type can be removed

#### ListView Columns

- **File Extension:** The file extension (e.g., `.pdf`, `.dwg`)
- **Description:** Human-readable description of the file type
- **Number Modifier:** Display text showing the configured modifier (e.g., "Add Suffix: -DWG", "(None)")

---

## Data Persistence

All settings in the Current Documents section are:

1. **Synchronized** with the `CurrentFolderManager.Settings` object in real-time as values change
2. **Validated** immediately upon change using data annotations and custom validators
3. **Saved** to persistent storage when the user clicks the Save button in the Settings view
4. **Loaded** automatically when the Settings view is initialized

## Validation Summary

### Field-Level Validation

- **Incoming Folder Path:** Must exist as a valid directory
- **Archive Folder Path:** Must exist as a valid directory
- **Revision Prefix:** Must be a valid revision marker character
- **Revision Suffix:** Must be a valid revision marker character

### Operation-Level Validation

- **Filing Rules:**
  - No duplicate rules (same type and filter value)
  - Only one CatchAll rule allowed
  - Target path must be valid

- **File Types:**
  - No duplicate file extensions
  - PDF cannot be removed
  - File extension must include leading period

### Validation Feedback

- Field-level errors appear as tooltips on text boxes
- Operation-level errors appear in the message banner at the top of the Settings view
- Validation occurs in real-time as the user types
- Command buttons are disabled when validation fails

---

## Best Practices

### Filing Rules

1. **Order Matters:** Place more specific rules at the top, general rules at the bottom
2. **Test Your Rules:** Use the application's matching feature to verify rules work as expected
3. **Keep It Simple:** Use the minimum number of rules necessary to organize your documents
4. **Use CatchAll:** Always keep the CatchAll rule as your last rule to ensure all files have a destination

### Supported File Types

1. **Standard Extensions:** Use standard file extensions (e.g., `.pdf`, `.dwg`, `.docx`)
2. **Document Your Modifiers:** Use descriptive modifier configurations that make sense to your team
3. **Test Modifiers:** Verify that document number modifications work correctly with your naming scheme
4. **Minimal Modifications:** Only add modifiers when necessary for your workflow

### Folder Paths

1. **Use Absolute Paths:** Always specify complete, absolute folder paths
2. **Verify Permissions:** Ensure the application has read/write access to specified folders
3. **Backup Regularly:** Keep backups of your archive folder
4. **Network Paths:** Be cautious with network paths as they may have performance implications

---

## Troubleshooting

### Common Issues

**Issue:** Documents not filing to expected location
**Solution:** Check filing rule order. Remember that the first matching rule wins. Move more specific rules higher in the list.

**Issue:** Validation error on folder paths
**Solution:** Verify the folder exists and you have appropriate permissions. Use the Browse button to ensure correct path selection.

**Issue:** Cannot remove a file type
**Solution:** PDF file type is required and cannot be removed. This is by design.

**Issue:** Cannot create duplicate filing rule
**Solution:** Duplicate rules (same type and filter value) are prevented. Edit the existing rule or use a different filter value.

**Issue:** CatchAll rule disappeared
**Solution:** The CatchAll rule cannot be deleted. If it's missing, the application will recreate it automatically pointing to your Documents folder.

---

## Related Documentation

- **Merge View Documentation:** Details on how filing rules are applied during the merge process
- **Database Settings:** Configuration for database connection used for document matching
- **Cloud Document Manager:** Integration with cloud-based document management systems
