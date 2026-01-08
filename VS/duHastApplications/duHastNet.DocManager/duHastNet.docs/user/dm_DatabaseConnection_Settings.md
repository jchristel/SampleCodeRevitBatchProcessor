# Database Connection Settings

## Overview

The Database Connection section in the Settings view manages your project's database. The database stores all document and revision information that the application uses for matching incoming files, tracking document history, and managing metadata. This section allows you to create new databases, connect to existing ones, import and export data, and define custom fields for your documents.

---

## Database Path and Connection

### Database Path

**Description:** The location where your database file is stored or will be created. This is a file on your computer or network that contains all your project's document and revision data.

**Type:** Text field with Browse button

**Sample Values:**
- `C:\ProjectData\DocumentDatabase.db` - Local drive location
- `\\FileServer\Projects\ABC\Documents.db` - Network shared location
- `D:\MyProjects\Construction2024.db` - Alternative drive location

**Requirements:**
- Must be a complete file path (not just a folder)
- File extension should be `.db` or `.sqlite`
- Directory must exist (or will be created when you create a new database)
- You must have read/write access to the location

**Usage Notes:**
- Use the Browse button to select an existing database or navigate to where you want to create a new one
- The path is validated when you click Connect or Create Database
- Network paths are supported but may be slower than local drives

### Browse Button

**Description:** Opens a file selection dialog to help you find an existing database file or choose a location for a new database.

**Type:** Button

**Usage Notes:**
- Click to open the file browser
- Shows database files (*.db), SQLite files (*.sqlite), and all files
- Available unless the application is busy with another operation
- After selecting a file, the path appears in the Database Path field

### Connect Button

**Description:** Connects to an existing database file at the path you specified. After connecting, you can import/export data and manage custom fields.

**Type:** Button

**Requirements:**
- Database Path must be filled in
- The database file must exist at that location
- The application must not be busy with another operation

**What Happens When You Click:**
1. The application checks that the file exists
2. Opens the database and checks that it's valid
3. Loads all documents and revisions into memory
4. Enables the Import/Export buttons
5. Makes the Custom Fields section available
6. Shows a success message

**Success Indicators:**
- Import Documents and Export Documents buttons become active
- Custom Fields section becomes accessible
- Your data is ready to use

**Common Errors:**
- **File doesn't exist:** Check that you typed the path correctly or use Browse
- **Database is locked:** Another program might have the file open
- **Database is corrupted:** The file may be damaged - try restoring from a backup
- **Wrong format:** The file might not be a valid database

### Create Database Button

**Description:** Creates a brand new, empty database file at the location you specify. Use this when starting a new project.

**Type:** Button

**Requirements:**
- The application must not be busy with another operation

**What Happens When You Click:**
1. A Save File dialog opens for you to choose location and name
2. The application creates a new database file
3. Sets up the required structure (document and revision tables)
4. Automatically connects to the new database
5. Shows a success message with the filename

**Important Warning:** If you choose a location where a database file already exists, the old file will be overwritten and permanently deleted. Make sure you have backups before creating a database at an existing location.

**After Creating:**
- The database is empty and ready for you to import data or add documents
- Import/Export buttons become active
- Custom Fields section becomes accessible
- Import/Export buttons enabled
- Custom Fields expander accessible

**Warning:** Creating a new database will overwrite any existing file at the same path. Ensure you have backups before creating a database at an existing location.

---

## Import and Export Operations

All import and export operations require that you're connected to a database. These operations use CSV (comma-separated values) files, which can be opened in Excel or any spreadsheet application.

### Revision History Mode

**Description:** A checkbox that controls how much revision history information is included when you export documents.

**Type:** Checkbox

**Options:**

#### Include Full Revision History (Checked)

**What This Does:**
- Exports every document for every revision, even if a document wasn't part of that revision
- Creates a complete grid showing which documents were in which revisions
- Produces larger CSV files with many blank cells
- Gives you a complete picture of your document history

**When to Use This:**
- You need to see the complete revision matrix
- You're analyzing which documents were part of each revision
- You're exporting to a system that expects a full grid
- You want comprehensive revision tracking

**Example:** If you have 100 documents and 10 revisions, the export will create up to 1,000 rows (one for each document in each revision). Many cells will be blank where a document wasn't included in a particular revision.

#### Revision History Only (Unchecked - Default)

**What This Does:**
- Exports only documents that actually have revision information
- Skips documents that weren't part of a revision
- Creates smaller, more compact CSV files
- Focuses on documents with explicit revision markers

**When to Use This:**
- You only need documents that have revision history
- You want smaller, more manageable files
- Most of your documents don't appear in every revision
- You're doing focused revision analysis

**Example:** If you have 100 documents but only 30 were actually revised, the export will only include those 30 documents with their revision information.

---

## Working with Documents

### Import Documents Button

**Description:** Brings document information from a CSV file into your database. Use this to add many documents at once or update existing documents.

**Type:** Button

**Requirements:**
- Database must be connected
- You must have a properly formatted CSV file

**What Happens When You Click:**
1. A file selection dialog opens
2. Choose your CSV file
3. The application reads and validates the file
4. New documents are created in the database
5. Existing documents are updated with new information
6. A success message shows how many documents were added or updated

**CSV File Format:**

Your CSV file must have these columns:
- **Number** - The document number (like ABC-001)
- **Name** - The document name or title
- **Revision** - The current revision code (like A, B, or P01)

Your CSV file can also have:
- **Custom field columns** - Any custom fields you've defined (column name must match exactly)
- **Revision columns** - If using Full Revision History mode (column names are revision codes)

**How It Works:**

**For New Documents:**
- A new document is created with the information from the CSV
- All custom fields are set (blank if not in CSV)
- Document is added to the database

**For Existing Documents:**
- The document number is used to find the existing document
- All information is updated with the CSV values
- Custom fields are updated or added as needed

**Example CSV:**
```
Number,Name,Revision,DrawingType,Discipline
ABC-001,Floor Plan,A,Architectural,Architecture
ABC-002,Site Plan,B,Civil,Civil Engineering
```

**Success Message:** "Imported 45 documents (23 new, 22 updated)"

**If There's a Problem:**
- Check that your CSV has the required columns
- Make sure document numbers aren't empty
- Verify custom field names match exactly
- The application will show which documents had issues

### Export Documents Button

**Description:** Saves your document information from the database to a CSV file. Use this to back up your data or share it with other systems.

**Type:** Button

**Requirements:**
- Database must be connected
- Documents must be loaded

**What Happens When You Click:**
1. A Save File dialog opens
2. Choose where to save and what to name the file
3. The application gathers all document information
4. A CSV file is created with all your documents
5. A success message shows how many documents were exported

**What's Included in the Export:**

**Always Included:**
- Document Number
- Document Name
- Current Revision code

**Also Included:**
- All active custom fields (one column per field)
- Revision history (if Full Revision History mode is checked)

**File Naming:** The default filename is `Documents.csv`, but you can change it to anything you want.

**Example of What You Get:**
```
Number,Name,Revision,DrawingType,Discipline
ABC-001,Floor Plan,A,Architectural,Architecture  
ABC-002,Site Plan,B,Civil,Civil Engineering
```

**Success Message:** "Exported 156 documents to Documents.csv"

**Usage Tips:**
- Export regularly as a backup
- Use exports to share document lists with team members
- Open the CSV in Excel for bulk editing, then import back
- Keep dated backups before making major changes

---

## Working with Revisions

---

## Working with Revisions

Revisions represent milestones in your project (like "Issued for Construction" or "Planning Submittal"). Each revision has a code (like A, B, P01), a date, and a description.

### Import Revisions Button

**Description:** Brings revision information from a CSV file into your database. Use this to add multiple revisions at once or update existing revision information.

**Type:** Button

**Requirements:**
- Database must be connected
- You must have a properly formatted CSV file

**What Happens When You Click:**
1. A file selection dialog opens
2. Choose your CSV file
3. The application reads and validates the file
4. New revisions are created in the database
5. Existing revisions are updated with new information
6. A success message shows how many revisions were added or updated

**CSV File Format:**

Your CSV file must have these three columns:
- **RevisionCode** - The revision identifier (like A, B, P01, etc.)
- **RevisionDate** - The date in YYYY-MM-DD format (like 2024-01-15)
- **Description** - What this revision represents (like "Issued for Construction")

**Example CSV:**
```
RevisionCode,RevisionDate,Description
A,2024-01-15,Issued for Construction
B,2024-02-20,Client Comments Incorporated
P01,2024-03-10,Planning Submission
```

**How It Works:**

**For New Revisions:**
- A new revision is created with the code, date, and description from the CSV
- The revision is added to your project's revision list

**For Existing Revisions:**
- The revision code is used to find the existing revision
- The date and description are updated with the CSV values

**Requirements:**
- Revision codes must be unique in your CSV file
- Dates must be in YYYY-MM-DD format
- All three columns are required

**Success Message:** "Imported 8 revisions (3 new, 5 updated)"

**If There's a Problem:**
- Check that your CSV has all three required columns
- Make sure dates are in the correct format (YYYY-MM-DD)
- Verify revision codes are unique

### Export Revisions Button

**Description:** Saves your revision information from the database to a CSV file. Use this to back up your revision list or share it with others.

**Type:** Button

**Requirements:**
- Database must be connected
- Revisions must be loaded

**What Happens When You Click:**
1. A Save File dialog opens
2. Choose where to save and what to name the file
3. The application gathers all revision information
4. A CSV file is created with all your revisions
5. A success message shows how many revisions were exported

**What's Included in the Export:**
- Revision Code (like A, B, P01)
- Revision Date (in YYYY-MM-DD format)
- Description (what the revision represents)

**File Naming:** The default filename is `Revisions.csv`, but you can change it to anything you want.

**Example of What You Get:**
```
RevisionCode,RevisionDate,Description
A,2024-01-15,Issued for Construction
B,2024-02-20,Client Comments Incorporated
P01,2024-03-10,Planning Submission
```

**Success Message:** "Exported 12 revisions to Revisions.csv"

**Usage Tips:**
- Export regularly as a backup of your revision schedule
- Share the revision list with project team members
- Use this to synchronize revisions between multiple databases
- Open in Excel to edit revision descriptions, then import back
- Documentation of project timeline

---

## Custom Fields

Custom Fields allow you to extend the document data model with additional properties specific to your project needs. Custom fields are stored in the database and can be used throughout the application for filtering, metadata export, and reporting.

### Custom Fields Expander

**Visibility:** Only visible when database is connected

**Behavior:**
- Automatically expands when database connected
- Collapses when database disconnected
- Contains ListView and management buttons

### Custom Field Properties

Each custom field has the following properties:

#### Field Name (Property Name)

**Description:** The name of the custom property field

**Constraints:**
- Must be unique within the database
- Case-sensitive
- Should follow naming conventions (e.g., PascalCase, no spaces)
- Becomes a property on the Document model

**Examples:** 
- `Discipline`
- `BuildingName`
- `ContractorCompany`
- `DrawingType`
- `ProjectPhase`

**Best Practice:** Use descriptive, meaningful names that clearly indicate the field's purpose

#### Status (Active/Inactive)

**Description:** Whether the custom field is currently active and usable

**Values:**
- **Active:** Field can be used in metadata mappings, exports, and throughout the application
- **Inactive:** Field is hidden from most operations but data is preserved in database

**Displayed As:**
- "Active" in green (in ListView)
- "Inactive" in gray (in ListView)

**Purpose:** Allows temporarily disabling fields without deleting data

#### Id

**Description:** Database identifier for the custom field

**Values:**
- `0` - New field not yet saved to database
- `> 0` - Existing field persisted in database

**Visibility:** Not displayed in UI, used internally for operations

---

### Custom Field Management

#### Adding a Custom Field

**Button:** Add

**Enabled When:** Database is connected

**Process:**
1. Click Add button
2. Dialog opens prompting for field name
3. Enter desired custom field name
4. Click OK in dialog
5. Field added to list with Status "Active" (not saved yet)
6. Status shows as unsaved (Id = 0)

**Validation in Dialog:**
- Field name cannot be empty
- Field name must be unique (checked against existing fields)
- Field name should follow property naming conventions

**Important:** New fields are NOT saved to the database immediately. You must click "Update Database" to persist changes.

**Success Message:** Displays confirmation that field was added with instruction to update database

**Use Case:** Add project-specific properties needed for document categorization or reporting

#### Removing a Custom Field

**Button:** Remove

**Enabled When:**
- Database is connected
- A custom field is selected
- Selected field has Id = 0 (not yet saved to database)

**Restriction:** Can only remove fields that haven't been saved yet

**Process:**
1. Select an unsaved custom field (Status shows Id = 0)
2. Click Remove button
3. Field removed from list immediately
4. Pending changes flag updated

**Rationale:** Once a custom field is saved to the database and has data, it should be deactivated rather than deleted to preserve data integrity.

**For Saved Fields:** Use "Toggle Active" instead to deactivate the field

#### Toggling Active Status

**Button:** Toggle Active

**Enabled When:**
- Database is connected
- A custom field is selected

**Process:**
1. Select a custom field from the list
2. Click Toggle Active button
3. Field's IsActive status toggles (Active â†” Inactive)
4. Status display updates in ListView
5. Pending changes flag set

**Important:** Status change is NOT saved immediately. Click "Update Database" to persist the change.

**Behavior by Status:**

**Activating a Field:**
- Field becomes available for use in metadata mappings
- Field appears in document property lists
- Field available for import/export

**Deactivating a Field:**
- Field removed from available properties in mappings
- Existing metadata mappings using this field are removed automatically
- Data preserved in database (custom property records remain)
- Field hidden from import/export by default
- Can be reactivated later without data loss

**Warning:** Deactivating a custom field will remove any cloud metadata mappings that use it. This cleanup happens automatically when you click Update Database.

#### Update Database Button

**Description:** Saves all your custom field changes to the database. This button applies any pending changes like new fields, activated fields, or deactivated fields.

**Type:** Button

**Requirements:**
- Database must be connected
- You must have pending changes (new fields added or status toggles)

**When This Button Is Available:**

The button becomes active when you have unsaved changes:
- You've added new custom fields
- You've toggled the Active status on any fields

**What Happens When You Click:**

1. A confirmation dialog appears showing all the changes you're about to make
2. Review the summary carefully
3. Click Yes to proceed with the changes
4. The application saves all changes to the database
5. A success message confirms what was changed

**The Confirmation Dialog Shows:**

The dialog lists all pending changes:
- **New Fields:** Names of fields being added
- **Activated Fields:** Names of fields being reactivated
- **Deactivated Fields:** Names of fields being hidden

**Example Dialog:**
```
Apply Custom Field Changes?

New Fields: 2
  - ProjectPhase
  - ContractorName

Deactivated Fields: 1
  - OldFieldName

Note: New fields will create records for all documents.
```

**What Each Change Does:**

**Adding New Fields:**
- The field becomes available throughout the application
- Every document in your database gets this field added (initially blank)
- This may take a moment if you have many documents
- The field appears in dropdown lists and metadata mappings

**Activating Fields:**
- The field becomes visible and usable again
- Data that was preserved is now accessible
- Field appears in dropdown lists and metadata mappings

**Deactivating Fields:**
- The field becomes hidden from most places in the application
- Any cloud metadata mappings using this field are automatically removed
- **Data is preserved** - nothing is deleted
- You'll see a notification if any mappings were removed

**Success Message:** "Database updated successfully. Added 2 fields, deactivated 1 field. Removed 3 metadata mappings."

**If Something Goes Wrong:**
- If any part of the update fails, nothing is saved (all-or-nothing)
- An error message tells you which field caused the problem
- Fix the issue and try again

**Usage Notes:**
- Always review the confirmation dialog carefully before clicking Yes
- If you have many documents, adding new fields may take a minute
- You can't undo this operation, but you can add/remove fields later
- Make sure you really want to deactivate fields before proceeding

---

### Understanding the Custom Fields List

The custom fields list shows all your custom fields in a table with two columns:

#### Field Name Column

**Shows:** The name of each custom field

**Sorted:** Alphabetically by default

**What You See:**
- Standard naming (like Discipline, BuildingName, ProjectPhase)
- This is the name you'll see throughout the application

#### Status Column

**Shows:** Whether each field is Active or Inactive

**Visual Display:**
- **Active** appears in green text - Field is currently in use
- **Inactive** appears in gray text - Field is hidden but data is preserved

**What This Means:**
- Active fields appear in dropdown menus and can be used
- Inactive fields are hidden but can be reactivated later

**Selection:**
- Click on a row to select that field
- The selected field is highlighted
- Selected field determines which buttons are enabled

**Visual Indicators:**
- **New fields (Id = 0):** May be shown in different style (implementation-specific)
- **Active fields:** Standard display
- **Inactive fields:** Grayed out or dimmed

**Selection:**
- Single selection mode
- Selected field determines which buttons are enabled
- Click to select, click away to deselect

---

## Database Schema Overview

The SQLite database contains the following core tables:

### Document Table

**Purpose:** Stores document master records

**Key Fields:**
- Id (Primary Key)
- Number (Unique)
- Name
- Revision

**Indexes:** Number (for fast lookups)

### Revision Table

**Purpose:** Stores revision definitions and schedule

**Key Fields:**
- Id (Primary Key)
- RevisionCode (Unique)
- RevisionDate
- Description

### CustomProperty Table

**Purpose:** Stores custom field values for documents

**Key Fields:**
- Id (Primary Key)
- DocumentId (Foreign Key to Document)
- PropertyName
- PropertyValue

**Relationship:** Many-to-one with Document (one document can have many custom properties)

### CustomFieldDefinition Table

**Purpose:** Stores custom field definitions (metadata about custom fields)

**Key Fields:**
- Id (Primary Key)
- PropertyName (Unique)
- IsActive

**Usage:** Defines which custom fields exist and their status

---

## Data Model Relationships

### Document â†” CustomProperty

**Relationship:** One document has many custom properties

**Cascade:** When document deleted, custom properties deleted

**Purpose:** Allows flexible extension of document data model

### Document â†” Revision

**Relationship:** Many-to-many through DocumentRevision join table

**Purpose:** Tracks which documents are in which revisions

**Indicators:** Each relationship has an indicator string (e.g., "S0", "S1")

---

## Validation

### Database Path Validation

**Rules:**
- Must have valid path format
- Directory must exist or be creatable
- Filename must be valid (no invalid characters)
- Extension typically .db or .sqlite

**Validated When:**
- Path is entered or changed
- Connect or Create button is clicked

### Database Connection Validation

**Rules:**
- Must be connected before saving settings
- Must be connected to enable import/export
- Must be connected to manage custom fields

**Error Message:** "Database must be connected"

### Custom Field Validation

**Rules:**
- Field name cannot be empty
- Field name must be unique in database
- Should follow naming conventions (no spaces, special characters)

**Validated When:**
- Adding new custom field in dialog
- Updating database schema

---

## Best Practices

### Managing Your Database

**1. Choose a Good Location**
- Store your database in a stable location that gets backed up regularly
- Use a local drive rather than a network drive (network drives are slower)
- Make sure you have read and write permissions to that location

**2. Use Descriptive Names**
- Name your database file to indicate the project (like `ProjectABC_Documents.db`)
- Include version numbers if you maintain multiple database versions
- Avoid generic names like `database.db` or `docs.db`

**3. Back Up Regularly**
- Export your documents and revisions to CSV files monthly
- Keep database file backups before making major changes
- Store backups in a different location than your main database
- Test your backups occasionally to make sure they work

**4. Version Control**
- Make a backup copy before adding many custom fields
- Save a backup before importing large amounts of data
- Keep dated backups so you can recover old versions if needed

### Working with CSV Files

**Before You Import:**
- Always back up your database first
- Open the CSV in Excel and check for errors
- Make sure there are no duplicate document numbers
- Verify that custom field names match your database exactly (including capitalization)

**When You Export:**
- Use descriptive filenames with dates (like `Documents_2024-03-15.csv`)
- Export regularly as a backup strategy
- Keep your exported CSV files for historical records
- Test the import/export cycle periodically to ensure it works

**Editing CSV Files:**
- You can edit exported CSVs in Excel or Google Sheets
- Don't change document numbers (they're used to match existing documents)
- Keep all the required columns (Number, Name, Revision)
- Keep dates in YYYY-MM-DD format

### Planning Custom Fields

**Before Creating Fields:**
- Think about what information you really need to track
- Use consistent naming (like ProjectPhase, not project-phase or projectphase)
- Write down what each field is for
- Consider how you'll use the fields in exports and reports

**Naming Your Fields:**
- Use PascalCase: capitalize the first letter of each word (like `BuildingName`)
- Avoid spaces - use `ProjectPhase` not `Project Phase`
- Avoid special characters like hyphens, underscores, or punctuation
- Be descriptive but concise

**Managing Fields Over Time:**
- Add new fields when you have a clear need for them
- Deactivate fields you no longer need (don't delete them - the data stays safe)
- Test new fields with a few sample documents first
- Keep notes about when and why you added or changed fields

**Performance Tips:**
- Don't create fields "just in case" - only add what you need
- Each field adds a small amount of processing time
- If you have thousands of documents, adding a field takes longer (it adds the field to every document)
- Plan ahead rather than adding fields one at a time

---

## Troubleshooting Common Issues

### Cannot Connect to Database

**What's Happening:** You get an error when clicking the Connect button

**Why This Happens:**
- The file doesn't exist at the path you specified
- Another program has the database file open and locked
- You don't have permission to access that location
- The database file is corrupted

**How to Fix:**
1. Double-check that you typed the path correctly
2. Use the Browse button to navigate to the file
3. Close any other programs that might have the file open
4. Check file permissions - you need read and write access
5. If the file is corrupted, restore from a backup

### Create Database Button Is Disabled

**What's Happening:** The Create Database button is grayed out and you can't click it

**Why This Happens:**
- No path is entered in the Database Path field
- The path has invalid characters
- You don't have write permission to that location

**How to Fix:**
1. Enter a valid file path in the Database Path field
2. Make sure the directory exists (or can be created by you)
3. Check for special characters in the path that aren't allowed
4. Verify you have permission to create files in that location
5. Try selecting a different location using Save File dialog

### Import Fails with Format Error

**What's Happening:** You get an error about CSV format when trying to import documents or revisions

**Why This Happens:**
- The CSV file doesn't have the required columns
- Column names are misspelled or have wrong capitalization
- The file has extra commas or quotes that confuse the parser
- The file is actually an Excel file, not a true CSV

**How to Fix:**
1. Open the CSV file in Excel or a text editor
2. Check that all required columns are present (Number, Name, Revision for documents)
3. Make sure column names match exactly (including capitalization)
4. Look for data cells that have unexpected commas or quotation marks
5. If you saved from Excel, make sure you chose CSV format, not Excel format
6. Try creating a fresh CSV with just a few rows to test

### Custom Field Not Appearing

**What's Happening:** You added a custom field, but it doesn't show up in dropdown lists or metadata mappings

**Why This Happens:**
- The field is set to Inactive status
- You didn't click Update Database after adding the field
- The field wasn't saved properly

**How to Fix:**
1. Check that the custom field shows as "Active" (green) in the list
2. Make sure you clicked Update Database button after adding the field
3. Try disconnecting and reconnecting to the database
4. If working with Cloud Document Manager, click the Refresh button on the template

### Update Database Fails

**What's Happening:** You get an error when clicking Update Database to save custom field changes

**Why This Happens:**
- The database file is read-only
- You don't have write permission
- Another program has the database locked
- There's not enough disk space
- A specific field name is causing an issue

**How to Fix:**
1. Check the database file properties - make sure it's not read-only
2. Verify you have write permissions to the database location
3. Close any other programs that might have the database open
4. Check that you have enough disk space
5. Try applying changes one field at a time to identify problem fields
6. Read the error message carefully - it usually tells you which field caused the issue

### All Documents Gone After Import

**What's Happening:** After importing a CSV file, your document count shows zero

**Why This Happens:**
- The import file was empty or had format errors
- The import operation failed but appeared to succeed

**How to Fix:**
1. Don't panic - disconnect and reconnect to see if documents reappear
2. If documents are truly gone, restore from your last CSV export backup
3. Check the CSV file you imported - was it empty or corrupted?
4. Review any error messages that appeared during import
5. In the future, always back up before importing

### Common Validation Messages

**"Database must be connected"**
- **What It Means:** You're trying to do something that requires a database connection
- **How to Fix:** Click Connect to connect to an existing database, or Create Database to make a new one

**"No data loaded"**
- **What It Means:** The database is connected but the data isn't loaded
- **How to Fix:** Try disconnecting and reconnecting, or restart the application

**"Custom field name already exists"**
- **What It Means:** You're trying to add a field with a name that's already in use
- **How to Fix:** Choose a different, unique name for your field

**"Import file not found"**
- **What It Means:** The CSV file you selected doesn't exist anymore
- **How to Fix:** Make sure the file wasn't moved or deleted, then browse to its correct location

---

## How Settings Are Saved

When you make changes in the Database Connection section, those changes are saved when you click the **Save** button at the bottom of the Settings view. The application automatically loads your saved settings the next time you open the Settings view.

**Important:** Changes are not permanent until you click Save. If you navigate away without saving, your database path and connection settings will be lost.

**What Gets Saved:**
- Database file path
- Custom field changes (after clicking Update Database)
- Revision History Mode checkbox setting

---

## Related Settings

**Current Folder Settings:** Uses the database for matching incoming files to documents

**Cloud Document Manager:** Exports metadata using custom fields you've defined

**Merge View:** The main screen where database information is used for document processing

---

## Quick Reference: CSV Format Examples

### Document Import/Export CSV

```csv
Number,Name,Revision,Discipline,ProjectPhase
ABC-001,Floor Plan,A,Architecture,Construction
ABC-002,Site Plan,B,Civil,Planning
ABC-003,Elevation,A,Architecture,Construction
```

**Notes:**
- Number, Name, and Revision are required
- Additional columns are custom fields (must match field names exactly)
- If using Full Revision History mode, you'll also see columns for each revision code

### Revision Import/Export CSV

```csv
RevisionCode,RevisionDate,Description
A,2024-01-15,Issued for Construction
B,2024-02-20,Client Comments Incorporated
P01,2024-03-10,Planning Submission
```

**Notes:**
- All three columns are required
- Date must be in YYYY-MM-DD format
- Description can contain spaces and most characters

