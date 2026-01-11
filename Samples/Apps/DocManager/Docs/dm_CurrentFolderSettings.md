# Current Documents Settings

## Overview

The Current Documents section in the Settings view configures how the application handles incoming documents, including file naming conventions, folder locations, filing rules, and supported file types.

---

## Revision Markers

These settings define the characters used to identify revision indicators in document filenames.

### Revision Prefix

**Description:** Character or characters that mark the beginning of a revision identifier in a filename. The application uses this to identify where the revision code starts when reading document filenames.

**Type:** Text field

**Sample Values:**
- `[` - Used with filename format: `Document_Rev[A].pdf`
- `_Rev` - Used with filename format: `Document_RevA.pdf`
- `-R` - Used with filename format: `Document-RA.pdf`

**Requirements:**
- Must be a valid filename character
- Cannot be empty
- Must be different from Revision Suffix

**Usage Notes:**
- This setting works together with Revision Suffix to extract revision codes from filenames
- Common practice is to use bracket notation: `[` and `]`
- Ensure all incoming documents follow the same naming convention
- The application will look for this character sequence to find where the revision code begins

### Revision Suffix

**Description:** Character or characters that mark the end of a revision identifier in a filename. The application uses this to identify where the revision code ends when reading document filenames.

**Type:** Text field

**Sample Values:**
- `]` - Used with filename format: `Document_Rev[A].pdf`
- `-` - Used with filename format: `Document_RevA-.pdf`
- `_` - Used with filename format: `Document_RevA_.pdf`

**Requirements:**
- Must be a valid filename character
- Cannot be empty
- Must be different from Revision Prefix

**Usage Notes:**
- Works in conjunction with Revision Prefix to extract revision information from filenames
- Common practice is to use closing bracket when prefix is opening bracket
- Must match the pattern used in your document naming standard

---

## Folder Paths

These settings specify the directories used for document processing and archiving.

### Incoming Folder Path

**Description:** The folder location containing documents that will be processed by the application. The application reads files from this folder to match them against the database and prepare them for merging.

**Type:** Text field with Browse button

**Sample Values:**
- `C:\Projects\ABC\Incoming` - Local project folder
- `\\FileServer\Projects\Documents\Incoming` - Network shared folder
- `D:\DocumentProcessing\New` - Alternative drive location

**Requirements:**
- Folder must exist before connecting
- You must have read access to the folder
- Path must be a valid folder location
- Can be a local drive or network path

**Usage Notes:**
- Use the Browse button to select the folder location
- If you see an error tooltip, the folder doesn't exist or isn't accessible
- The application checks this folder for new documents to process

### Archive Folder Path

**Description:** The folder location where older document versions are stored after they are superseded by newer revisions. When the application processes a new revision of a document, it moves the previous version to this archive location.

**Type:** Text field with Browse button

**Sample Values:**
- `C:\Projects\ABC\Archive` - Local archive folder
- `\\FileServer\Projects\Documents\Archive` - Network archive location
- `D:\DocumentProcessing\Superseded` - Alternative archive location

**Requirements:**
- Folder must exist before saving settings
- You must have read and write access to the folder
- Path must be a valid folder location
- Can be a local drive or network path

**Usage Notes:**
- Use the Browse button to select the folder location
- If you see an error tooltip, the folder doesn't exist or isn't accessible
- Archived documents are moved here automatically during the merge process
- Keep this folder backed up as it contains historical document versions
- a current date stamp is attached to a file name if a file gets archived multiple times

---

## Filing Rules

Filing rules determine where incoming documents are moved based on their filename patterns. Rules are evaluated from top to bottom, and the first matching rule determines the target directory.

### Rule Evaluation Order

Rules are evaluated in the order they appear in the list (top to bottom). The first rule that matches a filename wins, and no further rules are evaluated. Use the Move Up and Move Down buttons to adjust rule priority when you need to change which rules are checked first.

### Available Rule Types

### Available Rule Types

#### BeginsWith

**Description:** Matches filenames that start with the specified filter text. Use this rule type when you want to file documents based on how their filename begins.

**Sample Values:**
- `ARCH-` matches `ARCH-001-Drawing.pdf`, `ARCH-Floor-Plan.dwg`
- `ARCH-` does not match `STRUCT-ARCH-001.pdf`
- `MEP-` matches `MEP-001.pdf`, `MEP-HVAC-Drawing.pdf`

**Usage Notes:**
- This is one of the most commonly used rule types
- Useful for filing documents by discipline or project code
- Case-sensitive matching

#### Contains

**Description:** Matches filenames that contain the specified filter text anywhere in the name. Use this rule type when the identifying text might appear in the middle of the filename.

**Sample Values:**
- `MECHANICAL` matches `MECHANICAL-001.pdf`, `Project-MECHANICAL-Drawing.dwg`, `Test-MECHANICAL.pdf`
- `MECHANICAL` does not match `ARCH-001.pdf`
- `DRAFT` matches `ABC-DRAFT-01.pdf`, `DRAFT-Document.pdf`, `Report-DRAFT.docx`

**Usage Notes:**
- More flexible than BeginsWith but may match unintended files
- Useful when your naming convention has keywords in variable positions
- Be specific with your filter value to avoid false matches

#### NotBeginsWith

**Description:** Matches filenames that do NOT start with the specified filter text. Use this rule type to file documents by excluding those with certain prefixes.

**Sample Values:**
- `TEMP-` matches `ARCH-001.pdf`, `Drawing.dwg`, `Notes.docx`
- `TEMP-` does not match `TEMP-File.pdf`, `TEMP-Drawing.dwg`
- `DRAFT-` matches all files except those starting with `DRAFT-`

**Usage Notes:**
- Useful for routing non-draft documents to a specific location
- Often used in combination with other rules
- Can help separate temporary from permanent documents

#### NotContains

**Description:** Matches filenames that do NOT contain the specified filter text anywhere in the name. Use this rule type to file documents by excluding those with certain keywords.

**Sample Values:**
- `DRAFT` matches `ARCH-001.pdf`, `Final-Drawing.dwg`, `Report.pdf`
- `DRAFT` does not match `DRAFT-Report.pdf`, `Drawing-DRAFT.dwg`
- `TEMP` matches all files except those containing `TEMP`

**Usage Notes:**
- Useful for ensuring only finalized documents go to certain locations
- Be careful with short filter values that might accidentally match
- Can help keep working files separate from final deliverables

#### Default (CatchAll)

**Description:** Matches all files regardless of filename. This is the default fallback rule that ensures every file has a destination even if no other rules match.

**Special Properties:**
- Only one Default rule is allowed in the application
- Cannot be deleted (can only edit the target folder)
- Displayed in bold text in the rules list
- Automatically created if missing (points to your Documents folder)
- Does not use a filter value

**Usage Notes:**
- This should always be your last rule (lowest priority)
- Acts as a safety net for files that don't match other rules
- Edit this rule to change where unmatched files are filed
- Good practice to regularly check this folder for unexpected files

### Managing Filing Rules

#### Adding a New Rule

To add a new filing rule:

1. Click the **Add** button in the Filing Rules section
2. Select a rule type from the dropdown menu
3. Enter a filter value (leave empty for CatchAll rules)
4. Click Browse or type a target folder path where matching files should be moved
5. Click **Save** to add the rule

**Important Notes:**
- You cannot create duplicate rules (same type and filter value)
- Only one CatchAll rule is allowed
- The target folder must be a valid directory location
- New rules are added to the bottom of the list (lowest priority)

#### Editing an Existing Rule

To modify a filing rule:

1. Click on a rule in the list to select it
2. Click the **Edit** button
3. Make your changes to the rule properties
4. Click **Save** to apply the changes

**Note:** For CatchAll rules, you can only change the target folder path, not the rule type.

#### Removing a Rule

To delete a filing rule:

1. Click on a rule in the list to select it
2. Click the **Remove** button
3. The rule is immediately removed from the list

**Restriction:** The CatchAll (Default) rule cannot be removed as it ensures all files have a destination.

#### Changing Rule Priority

To adjust when a rule is evaluated:

**Move Up:** Click to increase the priority (check this rule earlier)
**Move Down:** Click to decrease the priority (check this rule later)

**Why This Matters:** Rules are evaluated from top to bottom, and the first match wins. Moving a rule up makes it more likely to match files before other rules.

### Understanding the Filing Rules List

The filing rules list displays three columns:

**Filter Type:** Shows the type of rule (BeginsWith, Contains, NotBeginsWith, NotContains, or Default)

**Filter Value:** Shows the text used for matching (empty for CatchAll rules)

**Target Path:** Shows the folder where matching files will be moved

**Visual Indicators:**
- The Default (CatchAll) rule appears in bold text
- The currently selected rule is highlighted

---

## Supported File Types

This section defines which file types the application will process and how document numbers should be modified for each file type. This allows the application to handle different file formats and apply naming transformations when matching documents against the database.

### File Type Components

Each supported file type has three parts that you configure:

#### File Extension

**Description:** The file extension that identifies this file type, including the leading period.

**Type:** Text field

**Sample Values:**
- `.pdf` - PDF documents
- `.dwg` - AutoCAD drawings
- `.docx` - Microsoft Word documents
- `.xlsx` - Microsoft Excel spreadsheets
- `.rvt` - Revit models

**Requirements:**
- Must start with a period (`.`)
- Must be unique (no duplicate extensions)
- Case doesn't matter (`.PDF` and `.pdf` are treated as the same)

**Usage Notes:**
- Always include the leading period
- Use standard file extensions for your industry
- Cannot change the extension for PDF files (it's fixed)

#### Description

**Description:** A friendly name that describes what this file type is used for. This helps you identify the file type in the list.

**Type:** Text field

**Sample Values:**
- `PDF Document` - For `.pdf` files
- `AutoCAD Drawing` - For `.dwg` files
- `Microsoft Word Document` - For `.docx` files
- `Revit Model File` - For `.rvt` files

**Requirements:**
- Can be any descriptive text
- Not required to be unique (but recommended for clarity)

**Usage Notes:**
- Use clear, recognizable descriptions
- Include the software name if applicable
- Keep descriptions concise but informative

#### Number Modifier

**Description:** An optional setting that changes how document numbers are matched for this file type. This is useful when different file types use different numbering schemes in your document database.

**Type:** Dropdown selection with additional configuration

For example, if CAD drawings have `-DWG` appended to their document numbers in the database, but the PDF versions don't, you can configure the `.dwg` file type with an "Add Suffix: -DWG" modifier.

**Available Modifiers:**

###### None (No Modifier)

**Description:** No modification is applied to document numbers. The filename document number must exactly match the database document number.

**Display in List:** `(None)` or empty

**Sample Values:** N/A - no modification occurs

**Usage Notes:**
- This is the default for PDF files
- Use this when your file naming matches your database numbering exactly
- Most common option for standard document workflows

###### Add Prefix

**Description:** Adds text to the beginning of the document number before matching against the database.

**Sample Values:**
- **Configuration:** Prefix text: `DRAFT-`
- **Original Filename:** `ABC-123.pdf`
- **Searched As:** `DRAFT-ABC-123`
- **Display in List:** `Add Prefix: DRAFT-`

**Usage Notes:**
- Useful when draft versions have a prefix in the database but not in filenames
- The prefix is added automatically during matching
- Common for separating working documents from issued documents

###### Add Suffix

**Description:** Adds text to the end of the document number before matching against the database.

**Sample Values:**
- **Configuration:** Suffix text: `-DWG`
- **Original Filename:** `ABC-123.dwg`
- **Searched As:** `ABC-123-DWG`
- **Display in List:** `Add Suffix: -DWG`

**Usage Notes:**
- Very common for CAD drawings that have a suffix in the database
- Allows PDF and DWG versions of the same document to have different database entries
- The suffix is added automatically during matching

###### Add at Index

**Description:** Inserts text at a specific character position in the document number before matching against the database.

**Sample Values:**
- **Configuration:** Text: `-REV`, Position: `3`
- **Original Filename:** `ABC123.pdf`
- **Searched As:** `ABC-REV123`
- **Display in List:** `Add at Index 3: -REV`

**Requirements:**
- Position must be a valid number
- Position 0 is the same as Add Prefix
- If position is beyond the end of the number, text is added at the end

**Usage Notes:**
- Use this when you need to insert text at a specific location
- Positions are counted starting from 0 (first character)
- Less common than Prefix or Suffix modifiers

**Display:** `Add at Index 3: -REV`

**Note:** Index 0 is displayed as "Add Prefix" for clarity.

###### Replace

**Description:** Replaces all occurrences of one string with another in the document number.

**Example:**
- Original Document Number: `ABC-TEMP-123`
- Old Value: `TEMP`
- New Value: `FINAL`
- Modified Number: `ABC-FINAL-123`

**Display:** `Replace: TEMP â†’ FINAL`

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

## How Settings Are Saved

When you make changes to any setting in the Current Documents section, those changes are saved when you click the **Save** button at the bottom of the Settings view. The application automatically loads your saved settings the next time you open the Settings view.

**Important:** Changes are not permanent until you click Save. If you navigate away without saving, your changes will be lost.

---

## Understanding Validation Messages

The application checks your settings as you enter them to help prevent errors. Here's what different types of validation mean:

### Field Validation

These checks happen as you type:

**Incoming Folder Path:** Must be an existing folder that you can access
- If you see an error, the folder doesn't exist or you don't have permission to access it

**Archive Folder Path:** Must be an existing folder that you can access
- If you see an error, the folder doesn't exist or you don't have permission to access it

**Revision Prefix and Suffix:** Must be valid filename characters
- If you see an error, you've entered a character that isn't allowed in filenames

### List Operation Validation

These checks happen when you add or edit items:

**Filing Rules:**
- Cannot create duplicate rules (same type and filter value)
- Only one CatchAll rule is allowed
- Target folder path must be valid

**File Types:**
- Cannot use duplicate file extensions
- PDF file type cannot be removed
- File extension must include the leading period (`.`)

### Where Validation Messages Appear

**Field Errors:** Hover over a field with a red border to see the error in a tooltip

**Operation Errors:** Appear in the message banner at the top of the Settings view

**Button States:** Save and action buttons are disabled (grayed out) when there are validation errors

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

## Troubleshooting Common Issues

### Documents Not Filing to Expected Location

**What's Happening:** Your files are being moved to the wrong folder or not being moved at all.

**Why This Happens:** Filing rules are evaluated from top to bottom, and the first matching rule wins. A rule higher in the list might be catching your files before the rule you expect.

**How to Fix:**
1. Review your filing rules in order from top to bottom
2. Check which rule would match first for the problem filenames
3. Move more specific rules higher in the list
4. Use the Move Up button to adjust rule priority
5. Test with a few files to verify the change works

### Validation Error on Folder Paths

**What's Happening:** You see a red border or error message on a folder path field.

**Why This Happens:** The folder doesn't exist at the location you specified, or you don't have permission to access it.

**How to Fix:**
1. Verify the folder exists using Windows Explorer
2. Check that you typed the path correctly (or use the Browse button)
3. Confirm you have read/write permissions to the folder
4. If it's a network path, ensure you're connected to the network
5. Ask your IT administrator if you need access permissions

### Cannot Remove a File Type

**What's Happening:** The Remove button is disabled for the PDF file type.

**Why This Happens:** PDF is a required file type and cannot be removed by design.

**This is Normal:** The application requires PDF support for document management. You can add other file types, but PDF will always be in the list.

### Cannot Create Duplicate Filing Rule

**What's Happening:** You get an error when trying to add a filing rule that already exists.

**Why This Happens:** You already have a rule with the same type and filter value. Duplicate rules are not allowed because they would be redundant.

**How to Fix:**
1. Edit the existing rule if you need to change its target folder
2. Use a different filter value if you need a similar but distinct rule
3. Check your existing rules list to see what's already configured

### CatchAll Rule Disappeared

**What's Happening:** You can't find the Default (CatchAll) rule in your list.

**Why This Can't Happen:** The CatchAll rule cannot be deleted. It's a required rule that ensures every file has a destination.

**If You Think It's Missing:** 
- The rule might be scrolled out of view at the bottom of the list
- The application will automatically recreate it if it's truly missing
- The rule is always displayed in bold text to make it easy to spot

---

## Related Documentation

- **Merge View Documentation:** Details on how filing rules are applied during the merge process
- **Database Settings:** Configuration for database connection used for document matching
- **Cloud Document Manager:** Integration with cloud-based document management systems
