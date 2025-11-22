# Database Connection Settings

## Overview

The Database Connection section in the Settings view manages all aspects of the SQLite database used by the application. This includes database creation, connection management, data import/export, and custom field definitions. The database stores all document and revision information used by the application for matching, tracking, and metadata management.

## Technology

The application uses **SQLite** as its database engine with the **sqlite-net-pcl** library as the Object-Relational Mapping (ORM) layer. This provides a lightweight, file-based database solution that requires no separate database server installation.

---

## Database Path and Connection Management

### Database Path

**Description:** The file path where the SQLite database is located or will be created.

**Type:** Text input

**Format:** Full file path with `.db` or `.sqlite` extension

**Example:** `C:\ProjectData\DocumentDatabase.db`

**Validation:**
- **When Connected:** Path must be valid and database must be connected
- **When Disconnected:** No validation (allows entering path before connection)
- **For Creation:** Directory must exist or be creatable, filename must be valid

**Features:**

#### Browse Button

**Function:** Opens a file browser dialog to select an existing database file

**Dialog Filter:** 
- Database files (*.db)
- SQLite files (*.sqlite)
- All files (*.*)

**Enabled When:**
- Not busy with database operations

**Usage:** 
- Select an existing database to connect to
- Navigate to the desired location when creating a new database

#### Connect Button

**Function:** Establishes connection to an existing database at the specified path

**Enabled When:**
- Database path is specified
- File exists at the specified path
- Not busy with database operations

**Process:**
1. Validates file exists
2. Opens database connection
3. Verifies database schema
4. Loads data into the application's Manager
5. Updates connection status
6. Initializes custom fields collection
7. Enables import/export operations

**Success Indicators:**
- Import/Export buttons become enabled
- Custom Fields expander becomes accessible
- Data is loaded and available for use

**Error Conditions:**
- File doesn't exist at specified path
- Database file is corrupted
- Database schema is incompatible
- Database is locked by another process

#### Create Database Button

**Function:** Creates a new SQLite database at the specified path with the required schema

**Enabled When:**
- Database path is specified
- Path is valid (directory exists or can be created)
- Not busy with database operations

**Process:**
1. Shows Save File Dialog to select location and name
2. Creates database file at specified location
3. Initializes schema (Document, Revision, CustomProperty tables)
4. Creates indexes for performance
5. Establishes connection to new database
6. Loads (empty) data into Manager
7. Updates connection status

**Overwrite Behavior:** If file already exists, will overwrite it with a new empty database

**Success Indicators:**
- Success message displayed with database filename
- Database path updated
- Connection established
- Import/Export buttons enabled
- Custom Fields expander accessible

**Warning:** Creating a new database will overwrite any existing file at the same path. Ensure you have backups before creating a database at an existing location.

---

## Import/Export Operations

All import and export operations require an active database connection. These operations work with CSV format files for easy data exchange with external systems and spreadsheet applications.

### Revision History Mode Selection

**Description:** Checkbox that controls how revision history is handled during import/export operations.

**Options:**

#### Include Full Revision History (Checked)

**Behavior:**
- Exports ALL documents in ALL revisions
- Documents not in a particular revision appear with blank revision indicators
- Creates a complete matrix of documents × revisions
- Results in larger CSV files with many blank cells

**Use Case:** 
- When you need to see which documents are present in each revision
- For comprehensive revision tracking across all documents
- When importing/exporting to systems that expect a full matrix

**Example:** If you have 100 documents and 10 revisions, the export will have up to 1000 rows (100 × 10), with blanks where a document wasn't part of that revision.

#### Revision History Only (Unchecked - Default)

**Behavior:**
- Exports only documents that have revision indicators in each revision
- Skips documents that weren't part of a revision
- Creates more compact CSV files
- Only includes meaningful revision history entries

**Use Case:**
- When you only care about documents that have explicit revision markers
- For smaller, more focused exports
- When most documents don't participate in every revision

**Example:** If you have 100 documents but only 30 have revision indicators, the export will only include those 30 documents' revision entries.

---

### Document Operations

#### Import Documents

**Function:** Imports document data from a CSV file into the database

**Button:** Import Documents

**Enabled When:**
- Database is connected
- Not busy with other operations

**Process:**
1. Opens file dialog to select CSV file
2. Parses CSV and validates format
3. Creates or updates documents in database
4. Creates custom property records for new documents
5. Reloads data into Manager
6. Displays success/error statistics

**CSV Format Expected:**

**Required Columns:**
- `Number` - Document number (unique identifier)
- `Name` - Document name/title
- `Revision` - Current revision code

**Optional Columns:**
- `[CustomFieldName]` - Any active custom field property name
- Custom fields must match those defined in the database

**Revision History Columns (if using Full Revision History Mode):**
- Columns named after revision codes (e.g., `A`, `B`, `C`, `P01`)
- Values are revision indicators (e.g., `S0`, `S1`, `AS`, `-`)
- Blank cells indicate document was not in that revision

**Import Behavior:**

**New Documents:**
- Created with specified properties
- Custom property records created for all active custom fields
- Blank custom fields set to empty string

**Existing Documents:**
- Updated with new values
- Document number used as primary key for matching
- Custom properties updated or created as needed

**Validation:**
- CSV must have required columns
- Document numbers must be valid (not null/empty)
- Warns about documents with issues but continues with others

**Success Message:** Shows count of documents created and updated

**Error Handling:**
- Displays first error encountered if import fails
- Partial imports possible (some documents may succeed)
- Check message banner for detailed error information

#### Export Documents

**Function:** Exports document data from the database to a CSV file

**Button:** Export Documents

**Enabled When:**
- Database is connected
- Data is loaded into Manager
- Not busy with other operations

**Process:**
1. Validates data is loaded
2. Opens Save File Dialog for output location
3. Retrieves all documents from Manager
4. Retrieves all active custom field definitions
5. Retrieves all revisions (if applicable)
6. Generates CSV with appropriate columns
7. Writes file to specified location
8. Displays success message with count

**CSV Format Generated:**

**Standard Columns:**
- `Number` - Document number
- `Name` - Document name
- `Revision` - Current revision code

**Custom Field Columns:**
- One column per active custom field
- Column header matches custom field property name
- Values from custom property records

**Revision History Columns (if Full Revision History Mode enabled):**
- One column per revision code
- Contains revision indicators for that document in that revision
- Blank for documents not in that revision

**File Naming:** Default filename is `Documents.csv` but can be changed in Save dialog

**Success Message:** Shows count of documents exported and output filename

**Use Cases:**
- Backup document data
- Share document list with external systems
- Bulk editing in spreadsheet applications
- Data migration between databases

---

### Revision Operations

#### Import Revisions

**Function:** Imports revision definitions from a CSV file into the database

**Button:** Import Revisions

**Enabled When:**
- Database is connected
- Data is loaded into Manager
- Not busy with other operations

**Process:**
1. Opens file dialog to select CSV file
2. Parses CSV and validates format
3. Creates or updates revisions in database
4. Reloads data into Manager
5. Displays success/error statistics

**CSV Format Expected:**

**Required Columns:**
- `RevisionCode` - Unique revision identifier (e.g., "A", "B", "P01")
- `RevisionDate` - Date of revision in ISO format (YYYY-MM-DD)
- `Description` - Description of the revision

**Example:**
```
RevisionCode,RevisionDate,Description
A,2024-01-15,Issued for Construction
B,2024-02-20,Client Comments Incorporated
P01,2024-03-10,Planning Submission
```

**Import Behavior:**

**New Revisions:**
- Created with specified properties
- Added to the revisions collection

**Existing Revisions:**
- Updated with new date and description
- RevisionCode used as primary key for matching

**Validation:**
- CSV must have required columns
- Revision codes must be unique within file
- Dates must be valid format

**Success Message:** Shows count of revisions created and updated

**Error Handling:**
- Displays errors if CSV format invalid
- Shows first error if revisions fail to import

#### Export Revisions

**Function:** Exports revision definitions from the database to a CSV file

**Button:** Export Revisions

**Enabled When:**
- Database is connected
- Data is loaded into Manager
- Not busy with other operations

**Process:**
1. Validates data is loaded
2. Opens Save File Dialog for output location
3. Retrieves all revisions from Manager
4. Generates CSV with revision columns
5. Writes file to specified location
6. Displays success message with count

**CSV Format Generated:**
- `RevisionCode` - The revision identifier
- `RevisionDate` - Date in ISO format (YYYY-MM-DD)
- `Description` - Revision description

**File Naming:** Default filename is `Revisions.csv` but can be changed in Save dialog

**Success Message:** Shows count of revisions exported and output filename

**Use Cases:**
- Backup revision list
- Share revision schedule with project team
- Synchronize revisions between databases
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
3. Field's IsActive status toggles (Active ↔ Inactive)
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

**Warning:** Deactivating a custom field will remove any cloud metadata mappings that reference it. This cleanup happens automatically when "Update Database" is clicked.

#### Updating Database Schema

**Button:** Update Database

**Enabled When:**
- Database is connected
- There are pending custom field changes

**Pending Changes Include:**
- New fields added (Id = 0)
- Active status toggled on existing fields

**Process:**
1. Click Update Database button
2. Confirmation dialog appears showing summary of changes:
   - New fields to be added
   - Fields to be activated
   - Fields to be deactivated
3. Review changes and click Yes to proceed
4. Application applies changes to database:
   - New fields: Schema updated, custom property records created for ALL documents
   - Activations: IsActive flag updated in database
   - Deactivations: IsActive flag updated, metadata mappings cleaned up
5. Data reloaded into Manager
6. Custom Fields list refreshed
7. Success message displayed

**Change Summary Dialog Contents:**

The confirmation dialog shows:
- Count of new fields with their names
- Count of activated fields with their names  
- Count of deactivated fields with their names
- Warning if new fields will create records for all documents

**Example:**
```
Apply Custom Field Changes?

New Fields: 2
  - ProjectPhase
  - ContractorName

Deactivated Fields: 1
  - OldFieldName

Note: New fields will create records for all documents.
```

**Database Operations Performed:**

**For New Fields:**
- Adds CustomFieldDefinition record to database
- Creates CustomProperty record for EVERY existing document
- Initial values set to empty string
- May take time if many documents exist

**For Status Changes:**
- Updates IsActive flag on CustomFieldDefinition
- For deactivations: Removes metadata mappings referencing the field
- CustomProperty data preserved in database

**Automatic Cleanup:**

When fields are deactivated:
- Scans all cloud metadata mappings
- Removes any mappings referencing deactivated fields
- Shows notification of removed mappings
- Triggers refresh in Cloud Document Manager view

**Success Message:** Displays count of changes applied and any mappings removed

**Error Handling:**
- If any change fails, entire operation rolls back (transaction)
- Error message shows which field caused the failure
- Changes are not persisted if errors occur

**Use Cases:**
- Adding custom fields for new project requirements
- Deactivating fields no longer needed
- Batch applying multiple custom field changes

---

### Custom Fields ListView

**Columns:**

#### Field Name
- Displays the property name of the custom field
- Sorted alphabetically by default
- Primary identifier for the field

#### Status
- Shows "Active" or "Inactive"
- Indicates current usability of the field
- Determines availability in metadata mappings

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

### Document ↔ CustomProperty

**Relationship:** One document has many custom properties

**Cascade:** When document deleted, custom properties deleted

**Purpose:** Allows flexible extension of document data model

### Document ↔ Revision

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

### Database Management

1. **Location:** Store database in a stable location with regular backups
2. **Naming:** Use descriptive names indicating project and purpose
3. **Backups:** Regularly export documents and revisions as CSV backups
4. **Version Control:** Keep database backups when making major changes
5. **Network Drives:** Avoid network drives for database location (performance issues)

### Data Import/Export

1. **Before Import:**
   - Backup current database
   - Validate CSV format in spreadsheet first
   - Check for duplicate document numbers
   - Ensure custom field names match exactly

2. **Export Workflow:**
   - Export regularly for backup purposes
   - Use descriptive filenames with dates
   - Keep exported CSVs for audit trail
   - Test import/export cycle periodically

3. **CSV Editing:**
   - Edit exported CSVs in Excel or similar
   - Don't modify document numbers (primary keys)
   - Keep required columns
   - Maintain date formats (ISO 8601)

### Custom Fields

1. **Planning:**
   - Plan custom fields before creation
   - Use consistent naming conventions
   - Document field purposes and usage
   - Consider export requirements

2. **Naming Conventions:**
   - Use PascalCase (e.g., `ProjectPhase`)
   - Avoid spaces and special characters
   - Be descriptive but concise
   - Follow property naming standards

3. **Lifecycle:**
   - Add fields as needed for new requirements
   - Deactivate rather than delete obsolete fields
   - Test with sample documents before production use
   - Update documentation when fields change

4. **Performance:**
   - Limit to necessary fields (each adds database operations)
   - Create fields with data population plan
   - Consider indexing needs for large databases

---

## Troubleshooting

### Common Issues

#### Issue: Cannot connect to database
**Symptoms:** Error when clicking Connect button

**Solutions:**
- Verify file exists at specified path
- Check file is not locked by another application
- Ensure you have read/write permissions
- Check database file is not corrupted
- Verify it's a valid SQLite database

#### Issue: Create Database button disabled
**Symptoms:** Button grayed out, cannot create database

**Solutions:**
- Enter a valid path in the Database Path field
- Ensure directory exists or can be created
- Check path doesn't contain invalid characters
- Verify you have write permissions to directory

#### Issue: Import fails with format error
**Symptoms:** Error message about CSV format during import

**Solutions:**
- Open CSV in spreadsheet and verify columns
- Check required columns are present
- Ensure column names match exactly
- Look for extra commas or quotes in data
- Verify file is saved as CSV (not Excel format)
- Check for BOM or encoding issues

#### Issue: Custom field not appearing in metadata mappings
**Symptoms:** New custom field doesn't show in Cloud Document Manager

**Solutions:**
- Verify custom field is Active status
- Check "Update Database" was clicked after adding field
- Confirm database was reloaded
- Refresh the Cloud Document Manager template

#### Issue: Update Database fails
**Symptoms:** Error when clicking Update Database button

**Solutions:**
- Check database is not read-only
- Verify you have write permissions
- Ensure database is not locked
- Check disk space available
- Try smaller batch of changes
- Review error message for specific field causing issue

#### Issue: All documents gone after import
**Symptoms:** Document count shows 0 after import operation

**Solutions:**
- Check if import file was empty or had errors
- Restore from backup database or CSV export
- Verify import file had correct format
- Review import error messages

### Validation Errors

#### "Database must be connected"
**Cause:** Attempting operation without database connection

**Solution:** Click Browse to select database, then Connect

#### "No data loaded"
**Cause:** Database connected but data not loaded into Manager

**Solution:** Reconnect to database, or restart application

#### "Custom field name already exists"
**Cause:** Attempting to add duplicate custom field name

**Solution:** Choose a different, unique field name

#### "Import file not found"
**Cause:** Selected import file doesn't exist or was moved

**Solution:** Browse to correct file location

---

## Data Persistence

### What Gets Saved

**In Database:**
- All document records with properties
- All revision definitions
- All custom field definitions (schema)
- All custom property values (data)

**In Settings File:**
- Database path
- Last connection state
- UI preferences (expander states, etc.)

### When Saving Occurs

**Automatic:**
- When database operations complete (Connect, Create)
- When import/export succeeds
- When Update Database applies changes

**Manual:**
- Click Save button in Settings view to save path
- Custom field changes require explicit Update Database click

### Backup Strategy

**Recommended:**
1. **Regular Database Backups:** Copy .db file to backup location
2. **CSV Exports:** Export documents and revisions monthly
3. **Version Control:** Keep dated backups before major changes
4. **Test Restores:** Periodically verify backups are valid

---

## Performance Considerations

### Database Size

- SQLite handles databases up to 140 TB (theoretical)
- Practical limit depends on disk space and performance needs
- Thousands of documents: No issues
- Tens of thousands: Some operations may take seconds
- Hundreds of thousands: Consider indexing and optimization

### Custom Fields Impact

- Each custom field adds:
  - One column in conceptual data model
  - One record per document in CustomProperty table
  - Overhead in import/export operations
- Limit to 20-30 custom fields for best performance
- More fields = larger database and slower operations

### Import/Export Performance

- CSV operations are relatively fast
- Large files (>10,000 rows) may take 10-30 seconds
- Progress not shown during operation (appears busy)
- Database operations are transactional (all or nothing)

---

## Integration with Other Features

### Current Folder Settings

Database provides:
- Document numbers for filename matching
- Revision codes for revision extraction
- Custom fields for metadata enrichment

### Cloud Document Manager

Database provides:
- Document properties for metadata mappings
- Revision information for document context
- Custom field values for dynamic metadata

### Merge View

Database provides:
- Document master records for matching incoming files
- Revision history for superseded tracking
- Custom properties for enriched document data

---

## Security Considerations

### Database Access

- SQLite is file-based with no user authentication
- File system permissions control access
- Anyone with file access can read/modify database
- No encryption by default (consider encrypted containers)

### Data Privacy

- Database may contain sensitive project information
- Store in secure locations with appropriate permissions
- Consider access control at file system level
- Include in data governance policies

### Backup Security

- Exported CSVs contain all project data
- Secure backup locations with access controls
- Encrypt backups if required by policy
- Control access to historical exports

---

## Related Documentation

- **Current Folder Settings:** Document processing that uses database for matching
- **Cloud Document Manager:** Metadata export that uses custom fields
- **Merge View:** The main interface for document matching and processing
- **Document/Revision Models:** The data structures stored in database

---

## Appendix: CSV Format Reference

### Document Export CSV Format

```csv
Number,Name,Revision,[CustomField1],[CustomField2],...,[Rev1],[Rev2],...
ABC-001,Floor Plan,A,Value1,Value2,...,S0,S1,...
ABC-002,Elevation,B,Value1,Value2,...,-,S0,...
```

**Notes:**
- Custom field columns match active custom field property names
- Revision columns (if Full History Mode) are revision codes
- Revision indicators: S0, S1, S2, AS, etc. or blank/dash

### Revision Export CSV Format

```csv
RevisionCode,RevisionDate,Description
A,2024-01-15,Issued for Construction
B,2024-02-20,Client Comments
P01,2024-03-10,Planning Submission
```

**Notes:**
- Date must be ISO format (YYYY-MM-DD)
- Description can contain spaces and special characters
- RevisionCode should be concise (typically 1-4 characters)
