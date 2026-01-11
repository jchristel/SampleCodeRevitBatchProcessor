# Cloud Document Manager Settings (Aconex Implementation)

## Overview

The Cloud Document Manager integration enables the application to export document metadata to cloud-based document management systems. The current implementation supports Aconex, a widely-used construction document management platform. This integration allows you to generate metadata CSV files that can be uploaded to Aconex along with your documents.

## General Settings

### Enable Cloud Document Manager Integration

**Description:** Master switch that enables or disables the entire cloud document manager integration.

**Type:** Checkbox

**Default:** Disabled (unchecked)

**Behavior:**
- When **enabled**: Provider selection and configuration sections become active
- When **disabled**: All provider controls are collapsed and disabled. No metadata export will occur during the merge process.

**Usage:** Enable this checkbox when you need to export document metadata for cloud document management systems. Leave disabled if you don't use cloud-based document management.

---

### Cloud Provider Selection

**Description:** Dropdown menu to select which cloud document management provider to configure.

**Available Options:**
- **None:** No provider selected (default state)
- **Aconex:** Aconex document management system

**Behavior:**
- Only enabled when "Enable Cloud Document Manager Integration" is checked
- Switching providers will display a warning if existing configuration data exists
- Changing providers will clear the current provider configuration (after confirmation)

**Future Expansion:** Additional cloud providers (Procore, Autodesk Docs, PlanGrid, etc.) will be added as options in future versions.

**Validation:**
- When cloud integration is enabled, a provider must be selected (cannot remain on "None")

---

## Aconex Provider Configuration

When "Aconex" is selected as the cloud provider, the following configuration options become available.

### Template File Configuration

#### Template File Path

**Description:** Path to the CSV metadata template file that defines the structure and fields for Aconex metadata export.

**Type:** Text input with Browse and Refresh buttons

**Validation:**
- **Required:** Cannot be empty when Aconex provider is selected
- **Must Exist:** File must exist at the specified path
- **Format:** Must be a CSV (.csv) file

**Features:**

##### Browse Button

**Function:** Opens a file dialog to select the metadata template file

**Dialog Filter:** CSV files (*.csv)

**Usage:** Click to navigate to and select your Aconex metadata template file

##### Refresh Button

**Function:** Re-reads the template file and updates available column headers

**Enabled When:**
- A valid template file path is set
- The file exists

**Behavior:**
- Reloads column headers from the CSV template
- Updates the list of available metadata fields
- Removes any mappings that reference fields no longer in the template
- Displays success message with the number of columns loaded
- Shows warnings for any issues (e.g., duplicate column headers)
- Notifies user if any existing mappings were removed due to missing fields

**Use Case:** Use this when you've modified the Aconex template file and need to update the application to reflect the changes.

#### Template File Loading

**Automatic Loading:** When a template file path is set or changed, the application automatically loads the column headers from the file.

**Column Headers:** The first row of the CSV file is read as the column headers. These headers represent the metadata fields that Aconex expects.

**Success Indicators:**
- Information message showing number of columns loaded
- Metadata field mappings section becomes active

**Error Conditions:**
- File cannot be read
- File is not a valid CSV
- File has no headers
- Duplicate column headers detected (shown as warning)

---

### Metadata Field Mappings

The Metadata Field Mappings section allows you to define how data from your document database maps to the metadata fields expected by Aconex. Each mapping connects an Aconex metadata field to either a static value, a document property, or a file property.

#### Prerequisites

Before adding mappings, you must:
1. Select and load a valid template file
2. The template must contain column headers (available fields)

#### Mapping Concept

Each mapping has three components:

1. **Meta Field:** The column name from the Aconex template (the destination field)
2. **Value Source:** Where the value comes from (static value, document property, or file property)
3. **Type:** The type of mapping (Fixed, Document Property, or File Property)

#### Mapping Types

##### Fixed Value Mapping

**Description:** Maps a metadata field to a static, unchanging value.

**Use Case:** Use this for values that are the same for all documents in an export, such as:
- Project name
- Discipline
- Status codes
- Standard categories

**Example:**
- Meta Field: `Project`
- Value: `Building ABC Construction`
- Type: `Fixed`

**Result:** Every exported document will have "Building ABC Construction" in the Project field.

##### Document Property Mapping

**Description:** Maps a metadata field to a property from the document database.

**Use Case:** Use this for values that vary per document and come from your database, such as:
- Document number
- Document name
- Revision code
- Revision date
- Revision description
- Custom field values

**Available Document Properties:**

###### Standard Document Properties
- **Number:** The document number from the database
- **Name:** The document name/title
- **Revision:** The revision code (e.g., "A", "B", "P01")

###### Standard Revision Properties
- **RevisionDate:** The date of the revision
- **Description:** The revision description

###### Custom Field Properties
- Any active custom field definitions in the database
- Custom fields appear by their property name
- Only active custom fields are available for mapping

**Example:**
- Meta Field: `Document Number`
- Property: `Number`
- Type: `Document Property`

**Result:** Each exported document will have its database document number in the "Document Number" field.

##### File Property Mapping

**Description:** Maps a metadata field to a property extracted from the physical file being processed.

**Use Case:** Use this for values derived from the file itself, such as:
- File name
- File extension
- Directory path
- File name without extension

**Available File Properties:**

###### FileName
- **Description:** The file name including extension
- **Example:** `Document-Rev-A.pdf`
- **Use Case:** When Aconex needs the actual filename that will be uploaded

###### FileNameWithoutExtension
- **Description:** The file name without the file extension
- **Example:** `Document-Rev-A`
- **Use Case:** When you need the filename but not the extension

###### Extension
- **Description:** The file extension without the leading dot
- **Example:** `pdf`
- **Use Case:** To categorize or filter documents by file type

###### FullPath
- **Description:** The complete file path including directory and filename
- **Example:** `C:\Incoming\Document-Rev-A.pdf`
- **Use Case:** For audit trails or when full path context is needed

###### DirectoryName
- **Description:** The directory containing the file
- **Example:** `C:\Incoming`
- **Use Case:** When directory location provides context (e.g., discipline folders)

**Example:**
- Meta Field: `File Name`
- Property: `FileName`
- Type: `File Property`

**Result:** Each exported document will have its actual filename in the "File Name" field.

#### Mapping Management

##### Adding a Mapping

**Prerequisites:**
- Template file must be loaded
- At least one unmapped field must be available

**Steps:**
1. Click the "Add" button
2. Select a metadata field from the dropdown (shows only unmapped fields)
3. Choose the mapping type:
   - **Fixed Value:** Enter a static value
   - **Document Property:** Select a document property from dropdown
   - **File Property:** Select a file property from dropdown
4. Click Save in the dialog

**Validation:**
- Meta field must be selected
- For Fixed Value: Value cannot be empty
- For Document Property: Property must be selected
- For File Property: Property must be selected
- Cannot map the same field twice

**Success:** 
- Mapping added to the list
- Information message displayed
- Selected field removed from available unmapped fields

**Error Conditions:**
- Template not loaded: Warning message displayed
- All fields already mapped: Information message displayed
- Validation failure: Error displayed in dialog

##### Editing a Mapping

**Prerequisites:**
- A mapping must be selected in the list
- Template file must be loaded

**Steps:**
1. Select a mapping from the list
2. Click the "Edit" button
3. Modify the mapping properties in the dialog
4. Click Save

**Available Changes:**
- Can change the value/property
- Can change the mapping type (Fixed ↔ Document Property ↔ File Property)
- Cannot change the meta field (create a new mapping instead)

**Note:** When editing, all template fields are available (not just unmapped ones), allowing you to reassign a mapping to a different source.

##### Removing a Mapping

**Prerequisites:**
- A mapping must be selected in the list

**Steps:**
1. Select a mapping from the list
2. Click the "Remove" button

**Behavior:**
- Mapping removed from the model
- Mapping removed from the display list
- Selection cleared
- Success message displayed
- The metadata field becomes available for remapping

**Use Case:** Remove mappings for fields you no longer need to export, or to reconfigure a mapping completely.

#### ListView Columns

The Metadata Field Mappings list displays the following columns:

##### Meta Field
**Description:** The name of the metadata field from the Aconex template

**Example:** `Document Number`, `Revision`, `Project Name`

##### Value/Property
**Description:** The actual value or property name that provides the data

**Examples:**
- For Fixed Value: `"Building ABC"` (the actual static value)
- For Document Property: `Number` (the property name)
- For File Property: `FileName` (the property name)

##### Type
**Description:** The type of mapping

**Values:**
- `Fixed` - Static value
- `Document Property` - Value from database
- `File Property` - Value from file

#### Automatic Cleanup

**Trigger:** When a custom field is deactivated in the database settings

**Behavior:** 
- The application automatically scans all Aconex mappings
- Removes any mappings that reference the deactivated custom field
- Displays a notification about removed mappings
- Updates the ListView to reflect changes

**Purpose:** Prevents invalid mappings from causing export errors

---

## How Metadata Export Works

### Export Process Overview

When documents are merged/processed by the application with Cloud Document Manager integration enabled:

1. **For Each Document:** The application evaluates all configured metadata mappings
2. **Value Resolution:** For each mapping:
   - Fixed values are used as-is
   - Document properties are looked up in the database
   - File properties are extracted from the physical file
3. **CSV Generation:** A metadata CSV file is generated with:
   - Column headers matching the Aconex template
   - One row per document
   - Values populated according to mappings
4. **File Placement:** The metadata CSV is saved alongside the processed documents
5. **Upload to Aconex:** The CSV can then be used when uploading documents to Aconex

### Mapping Priority

When a metadata field has a mapping configured:
- The mapped value takes precedence
- Empty or null values are written as empty strings in the CSV
- Missing document properties result in empty values (with warning)

### Unmapped Fields

Fields in the Aconex template that have no configured mapping:
- Will appear as empty columns in the exported CSV
- Can be filled manually in the CSV before upload
- Can be populated by Aconex's default values (if configured in Aconex)

---

## Configuration Workflow

### Initial Setup

1. **Obtain Aconex Template**
   - Download the metadata template CSV from your Aconex project
   - Save it to a accessible location on your computer

2. **Enable Integration**
   - Check "Enable Cloud Document Manager Integration"
   - Select "Aconex" from the Cloud Provider dropdown

3. **Load Template**
   - Click Browse to select your template file
   - Wait for automatic loading confirmation
   - Verify the column count in the success message

4. **Configure Mappings**
   - Review the required Aconex fields in your template
   - Add mappings for all required fields (marked in Aconex documentation)
   - Add mappings for optional fields as needed
   - Use appropriate mapping types based on data source

5. **Test Configuration**
   - Save settings
   - Process a test document
   - Verify the exported metadata CSV structure
   - Check that values are correct
   - Upload test CSV to Aconex to verify compatibility

### Updating Configuration

#### When Template Changes

If your Aconex project template is updated:

1. Replace the template file with the new version (or select new file)
2. Click the "Refresh" button
3. Review the notification about column changes
4. Update mappings for new fields
5. Verify removed mappings (if any fields were removed from template)
6. Test with a sample document

#### When Database Changes

If custom fields are added/removed/modified:

1. For new custom fields: Add mappings as needed
2. For removed/deactivated fields: Automatic cleanup occurs, review notifications
3. For renamed fields: Update mappings to reference the new property name

#### When Requirements Change

If Aconex requirements change (new required fields, etc.):

1. Obtain updated template from Aconex
2. Load new template
3. Add mappings for new required fields
4. Update existing mappings if field purposes changed
5. Test thoroughly before production use

---

## Data Persistence

All Cloud Document Manager settings are:

1. **Synchronized** with the `CloudDocumentManager` model in real-time
2. **Validated** when changes are made (template file path, mappings)
3. **Saved** to persistent storage when the Settings Save button is clicked
4. **Loaded** automatically when the Settings view is opened

### What Gets Saved

- **Enabled State:** Whether cloud integration is enabled
- **Provider Type:** Selected provider (Aconex, or None)
- **Template Path:** Path to the Aconex template file
- **Available Fields:** Column headers from the template (loaded at runtime)
- **Mappings:** All configured metadata field mappings

### Configuration Files

The configuration is stored in the application's settings file format and persists across application restarts.

---

## Validation Summary

### Integration Level

- **When Enabled:** A cloud provider must be selected (cannot be None)
- **When Disabled:** No validation, all settings inactive

### Template File

- **Required:** Must be specified when Aconex provider is active
- **Must Exist:** File path must point to an existing file
- **Format:** Must be a CSV file (.csv extension)
- **Content:** Must contain at least one column header

### Mappings

- **Unique Fields:** Each metadata field can only be mapped once
- **Valid Properties:** Document/File properties must exist in the system
- **Complete Mappings:** Each mapping must have a value source configured
- **Template Synchronization:** Mappings automatically cleaned when fields removed from template

### Validation Feedback

- **Field-level errors:** Displayed as validation messages in dialogs
- **Template errors:** Displayed in message banner after file operations
- **Mapping errors:** Displayed when adding/editing mappings
- **Warnings:** Shown for non-critical issues (duplicate headers, removed mappings)

---

## Best Practices

### Template Management

1. **Version Control:** Keep versions of your Aconex template files with dates in filename
2. **Test First:** Always test template changes with sample data before production use
3. **Backup:** Keep a backup of your working template file
4. **Document Changes:** Note what changed between template versions

### Mapping Strategy

1. **Required Fields First:** Map all Aconex-required fields before optional ones
2. **Use Fixed Values Sparingly:** Prefer document properties for data that varies
3. **Consistent Naming:** Use consistent property names across your database
4. **Document Mappings:** Keep notes on what each mapping represents and why it's configured that way

### Data Quality

1. **Validate Sources:** Ensure document properties are consistently populated in your database
2. **Handle Missing Data:** Plan for missing values (empty fields in Aconex)
3. **Test Thoroughly:** Process test documents before bulk operations
4. **Review Exports:** Periodically review exported CSV files for accuracy

### Workflow Integration

1. **Training:** Train users on the importance of accurate database entry
2. **Custom Fields:** Design custom fields with Aconex export needs in mind
3. **Automation:** Leverage document properties to minimize manual metadata entry
4. **Quality Checks:** Implement checks before uploading to Aconex

---

## Troubleshooting

### Common Issues

#### Issue: Template file won't load
**Symptoms:** Error message when selecting template, or no column headers loaded

**Solutions:**
- Verify file is a valid CSV format (open in Excel to check)
- Check file is not locked by another application
- Ensure file path doesn't contain special characters
- Verify you have read permissions on the file
- Check the CSV has a header row

#### Issue: Cannot add mappings
**Symptoms:** "Template not loaded" warning when clicking Add

**Solutions:**
- Ensure template file is selected and loaded
- Click Refresh button to reload template
- Verify template file still exists at the specified path
- Check that template has valid column headers

#### Issue: Mappings removed after refresh
**Symptoms:** Warning about removed mappings after clicking Refresh

**Solutions:**
- Compare old and new template files to see what changed
- Re-add mappings for fields that still exist (may have been renamed)
- If fields truly removed from Aconex requirements, no action needed
- Update template file if changes were unintentional

#### Issue: Exported CSV doesn't match Aconex expectations
**Symptoms:** Aconex rejects CSV upload or data appears incorrect

**Solutions:**
- Verify template file matches current Aconex project template exactly
- Check all required Aconex fields have mappings
- Review mapping values in exported CSV
- Verify document properties are correctly populated in database
- Test with Aconex's CSV validation tool (if available)

#### Issue: Custom field mappings showing errors
**Symptoms:** Mappings referencing custom fields show errors or produce empty values

**Solutions:**
- Verify custom field is still active in database settings
- Check custom field property name hasn't changed
- Ensure documents in database have values for the custom field
- Re-map if custom field was recreated with different property name

#### Issue: File property mappings produce unexpected values
**Symptoms:** File properties in CSV don't match expectations

**Solutions:**
- Verify files are in the expected location (check FullPath)
- Check for special characters in filenames
- Ensure file extensions match expected format
- Review file naming conventions for consistency

### Validation Errors

#### "Template file path is empty (null)"
**Cause:** Template file path not set

**Solution:** Click Browse and select a template file

#### "Template file does not exist"
**Cause:** File was moved or deleted

**Solution:** Browse to the correct file location or restore the file

#### "Template file must be a CSV (.csv) file"
**Cause:** Selected file has wrong extension

**Solution:** Select a CSV file, not Excel or other format

#### "No provider selected"
**Cause:** Cloud integration enabled but provider set to "None"

**Solution:** Select "Aconex" from the Cloud Provider dropdown

### Warning Messages

#### "Duplicate column headers detected in template"
**Meaning:** Template CSV has duplicate column names

**Impact:** Mappings may not work correctly for duplicate columns

**Solution:** Fix the template file to have unique column names

#### "Removed X mapping(s) for fields no longer in template"
**Meaning:** Template was updated and some fields were removed

**Impact:** Those mappings won't export data anymore

**Solution:** Review removed fields, re-add if they were mistakenly removed from template

---

## Integration with Other Features

### Document Database

The Cloud Document Manager relies heavily on the document database:
- Document properties (Number, Name, Revision) must be populated
- Custom fields used in mappings must have values
- Inactive custom fields cannot be used in mappings

### Current Folder Settings

Works in conjunction with Current Folder settings:
- Files processed through the incoming folder workflow
- Metadata exported during the merge operation
- File properties extracted from incoming files

### Merge Process

The metadata export occurs during the merge process:
- After documents are matched to database
- Before final file organization
- One CSV per batch of processed documents
- CSV placed in output location with documents

---

## Security and Privacy Considerations

### Template Files

- Template files may contain sensitive project information
- Store templates in secure locations
- Control access to template files
- Consider encryption for highly sensitive projects

### Metadata Content

- Review what data is being exported to Aconex
- Ensure compliance with data privacy regulations
- Be cautious with personal information in metadata
- Follow organizational data governance policies

### File Properties

- Be aware that file paths may reveal internal structure
- Consider implications of exporting directory names
- Review full path exports for sensitive location information

---

## Future Enhancements

### Planned Features

- **Additional Providers:** Procore, Autodesk Docs, PlanGrid support
- **Field Transformations:** Apply formatting or transformations to values
- **Conditional Mappings:** Map different values based on conditions
- **Bulk Mapping:** Configure multiple similar mappings at once
- **Mapping Templates:** Save and reuse mapping configurations
- **Import/Export:** Share mapping configurations between installations

### Version Compatibility

The current Aconex implementation is designed to be:
- **Forward-compatible:** New features won't break existing mappings
- **Extensible:** Additional providers use the same architecture
- **Configurable:** Settings can be updated without code changes

---

## Related Documentation

- **Current Folder Settings:** Document processing and filing rules
- **Database Settings:** Custom field configuration used in mappings
- **Merge View:** Where metadata export actually occurs
- **Document/Revision Models:** Available properties for mapping

---

## Glossary

**Aconex:** Cloud-based construction document management and collaboration platform

**Cloud Provider:** The document management system being integrated with

**Metadata:** Information about documents (properties, attributes) separate from document content

**Template File:** CSV file defining the structure and fields for metadata export

**Mapping:** Connection between an Aconex field and a data source (fixed value, property, or file attribute)

**Fixed Value Mapping:** Mapping with a static value used for all documents

**Document Property Mapping:** Mapping that pulls values from the document database

**File Property Mapping:** Mapping that extracts values from the physical file

**Column Header:** Field name from the first row of the CSV template

**Meta Field:** A metadata field in the Aconex template that needs to be populated

**Custom Field:** User-defined property in the document database
