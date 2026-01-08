# User Manual Writing Guidelines

## Document Overview

This document provides guidelines for writing user manuals for the DocManager application. User manuals should focus on helping end users understand and effectively use the application's features without reference to technical implementation details.

---

## General Principles

### Audience
- **Target Users:** End users who will interact with the application interface
- **Assumed Knowledge:** Basic computer skills, familiarity with document management concepts
- **Not Included:** Developers, system administrators, or technical staff

### Content Restrictions
- **NO code references:** Never include class names, method names, or code snippets
- **NO technical jargon:** Avoid terms like "ViewModel", "Command", "Binding", "Repository"
- **NO implementation details:** Focus on what users see and do, not how it works internally
- **User-focused language:** Use terms like "button", "field", "list", "section" instead of technical terms

### Clarity Requirements
- **Ask, don't guess:** If the purpose of a view, section, or control is unclear, ask for clarification
- **Be specific:** Provide concrete examples and sample values where applicable
- **Be concise:** Use clear, direct language without unnecessary elaboration

---

## User Manual Structure

### Document Hierarchy

```
User Manual
â"œâ"€â"€ View Summary (Overview section)
â"œâ"€â"€ Chapter 1: [View Section Name]
â"‚   â"œâ"€â"€ Section Overview
â"‚   â"œâ"€â"€ Control 1 Documentation
â"‚   â"œâ"€â"€ Control 2 Documentation
â"‚   â""â"€â"€ Control N Documentation
â"œâ"€â"€ Chapter 2: [View Section Name]
â"‚   â"œâ"€â"€ Section Overview
â"‚   â""â"€â"€ ...
â""â"€â"€ Chapter N: [View Section Name]
```

---

## Content Components

### 1. View Summary

**Purpose:** Provide a high-level overview of what the entire view accomplishes

**Contents:**
- Brief description of the view's purpose (2-4 sentences)
- Main tasks users can accomplish
- When users would access this view
- Relationships to other views (if relevant)

**Example:**
```markdown
## Settings View

The Settings view allows you to configure all aspects of document management, 
including folder locations, database connections, filing rules, and cloud 
integration. Use this view to set up your document processing workflow before 
merging documents. Access the Settings view from the main menu or before 
beginning your first document merge operation.
```

**Guidelines:**
- Keep it brief and high-level
- Focus on user goals, not features
- Answer: "Why would I use this view?"

---

### 2. Chapter: View Section

**Purpose:** Document a logical grouping of related controls (e.g., an Expander, Border, or visual section)

**Identification Criteria:**
- Visual grouping in the interface (bordered areas, expanders, tabs)
- Functionally related controls
- Named sections or headers in the UI

**Chapter Structure:**
```markdown
## [Section Name]

### Overview
[Brief description of section purpose - 1-2 sentences]

### Controls

#### [Control Name]
[Control documentation - see below]

#### [Control Name]
[Control documentation - see below]
```

**Example:**
```markdown
## Folder Paths

### Overview
Configure the directories where incoming documents are processed and where 
superseded documents are archived.

### Controls
[Control documentation follows...]
```

**Guidelines:**
- Use the exact section name as it appears in the UI
- Section overview should explain the collective purpose of controls in the section
- If a section contains subsections, use additional heading levels

---

### 3. Control Documentation

**Purpose:** Explain what each control does, how to use it, and what values are acceptable

**Required Information:**

1. **Control Name/Label**
   - Use the exact label text from the UI
   - Example: "Incoming Folder Path", "Revision Prefix", "Connect Button"

2. **Description**
   - Clear explanation of what the control does
   - 1-3 sentences
   - Focus on user action and outcome

3. **Control Type** (contextual to user)
   - Text field
   - Dropdown list
   - Checkbox
   - Button
   - List view
   - Date picker
   - (Use common user-facing terms, not technical UI component names)

4. **Sample Values** (when applicable)
   - Provide realistic examples
   - Show correct format
   - Include multiple examples if format varies

5. **Value Requirements** (when applicable)
   - What makes a value valid
   - Format requirements
   - Constraints (required, optional, min/max length)
   - Dependencies on other settings

6. **Usage Notes** (when applicable)
   - Best practices
   - Common mistakes to avoid
   - Related controls or features
   - When to change this setting

**Control Documentation Template:**

```markdown
#### [Control Label/Name]

**Description:** [What does this control do? What happens when users interact with it?]

**Type:** [Text field | Dropdown | Checkbox | Button | etc.]

**Sample Values:**
- `[Example 1]`
- `[Example 2]`
- `[Example 3]` - [Optional context for example]

**Requirements:**
- [Validation rule or constraint]
- [Format requirement]
- [Required/Optional status]

**Usage Notes:**
- [Best practice or helpful tip]
- [Common use case]
- [Related controls or dependencies]
```

**Example:**

```markdown
#### Revision Prefix

**Description:** The character or characters that mark the beginning of a 
revision identifier in a document filename. The application uses this to 
identify which revision a document belongs to when matching files.

**Type:** Text field

**Sample Values:**
- `[` - Used with filename format: `Document_Rev[A].pdf`
- `_Rev` - Used with filename format: `Document_RevA.pdf`
- `-R` - Used with filename format: `Document-RA.pdf`

**Requirements:**
- Must be a valid filename character
- Cannot be empty
- Must be different from Revision Suffix
- Must appear consistently in all document filenames

**Usage Notes:**
- This setting works together with Revision Suffix to extract revision codes
- Common practice is to use bracket notation: `[` and `]`
- Ensure all incoming documents follow the same naming convention
```

---

## Special Control Types

### Buttons

**Documentation Focus:**
- What action does clicking the button perform?
- What happens after the button is clicked?
- When is the button enabled/disabled?
- What should users verify before clicking?

**Example:**
```markdown
#### Connect Button

**Description:** Establishes a connection to the specified database file. 
After clicking, the application verifies the database structure and enables 
import/export functionality.

**Type:** Button

**Requirements:**
- Database Path must be specified before clicking
- The database file must exist or will be created
- User must have read/write permissions to the database location

**Usage Notes:**
- The button becomes enabled when a valid path is entered
- A success message appears when connection is established
- If connection fails, check that the path is correct and accessible
```

### Lists and Tables

**Documentation Focus:**
- What items appear in the list?
- How do users add, edit, or remove items?
- How are items ordered or sorted?
- What happens when users select an item?

**Example:**
```markdown
#### Filing Rules List

**Description:** Displays all defined filing rules that determine where incoming 
documents are moved based on their filenames. Rules are evaluated from top to 
bottom, and the first matching rule wins.

**Type:** List view

**Usage Notes:**
- Use "Add" button to create new rules
- Use "Edit" button to modify the selected rule
- Use "Delete" button to remove the selected rule
- Use "Move Up" and "Move Down" buttons to change rule priority
- The order of rules matters: higher rules are checked first
- Only one rule can be selected at a time
```

### Validation Messages

**Documentation Focus:**
- What triggers the validation message?
- What does the message mean?
- How do users correct the issue?

**Example:**
```markdown
#### Folder Path Validation

**Description:** Appears below the folder path field when an invalid path is entered.

**Type:** Validation message (red text or tooltip)

**Common Messages:**
- "Folder does not exist" - The specified path cannot be found
- "Invalid path format" - The path contains invalid characters or format

**Resolution:**
- Click the Browse button to select an existing folder
- Verify the path is typed correctly
- Ensure you have permission to access the folder
- Create the folder manually if it should exist
```

---

## Documentation Standards

### Writing Style

**Do:**
- âœ… Use active voice: "Click the Connect button" (not "The Connect button should be clicked")
- âœ… Use present tense: "The application moves files" (not "The application will move files")
- âœ… Use second person: "You can configure" (not "Users can configure")
- âœ… Be specific: "Enter a folder path" (not "Specify the location")
- âœ… Use consistent terminology throughout the manual

**Don't:**
- ❌ Use passive voice excessively
- ❌ Use future tense unless describing future actions
- ❌ Use first person plural ("we", "our application")
- ❌ Use vague terms like "the system", "the program"
- ❌ Include technical jargon or implementation details

### Formatting Conventions

**Headings:**
- View Summary: `##` (H2)
- Chapter/Section: `##` or `###` (H2 or H3, depending on nesting)
- Control Name: `####` (H4)
- Subsections: `#####` (H5)

**Emphasis:**
- **Bold** for field names, button labels, and UI elements when referenced in text
- *Italic* for emphasis or new terms (use sparingly)
- `Code formatting` for sample values, file paths, and exact input examples

**Lists:**
- Use bulleted lists for unordered information
- Use numbered lists for step-by-step procedures
- Use description lists (or bold headings) for structured information like requirements

**Examples:**
- Always include relevant examples
- Use realistic, meaningful sample data
- Provide context for examples when helpful

---

## Writing Process

### Step 1: Identify View Structure

1. Open the view's XAML file
2. Identify major sections (Expanders, Borders, Groups)
3. Note section headers or titles
4. List controls within each section

### Step 2: Understand Purpose

**For each view/section/control:**
- What is its purpose?
- When would a user interact with it?
- What does it accomplish?

**If unclear:**
- âš ï¸ **STOP and ASK** - Do not guess or make assumptions
- Request clarification from stakeholders
- Review related documentation or specifications
- Test the application to observe behavior

### Step 3: Document Systematically

1. Write View Summary first
2. Document each section as a chapter
3. Document each control within its section
4. Add cross-references where controls relate to each other

### Step 4: Include Examples

For each control that accepts input:
- Provide at least one realistic example
- Show correct format
- Include edge cases if relevant (max length, special characters, etc.)

### Step 5: Review for Clarity

- Read as if you're a new user
- Verify all instructions are clear and actionable
- Check that no technical terms remain
- Ensure consistent terminology
- Validate all sample values are realistic

---

## Quality Checklist

Before finalizing a user manual section, verify:

- [ ] **No Code References:** No class names, namespaces, or technical terms
- [ ] **Clear Purpose:** Every view, section, and control has a clear purpose statement
- [ ] **User-Focused:** Written from user's perspective, describes what they see and do
- [ ] **Examples Included:** Sample values provided for all input controls
- [ ] **Requirements Documented:** Validation rules and constraints are clear
- [ ] **Consistent Terminology:** Same UI elements called by the same names throughout
- [ ] **Active Voice:** Instructions use active voice and direct address ("you")
- [ ] **No Assumptions:** Nothing left unclear - all ambiguities resolved with stakeholders
- [ ] **Formatting Correct:** Headings, lists, and emphasis used consistently
- [ ] **Actionable:** Users can follow the documentation to accomplish tasks

---

## Examples of Good vs. Poor Documentation

### Poor Example (Too Technical)

```markdown
#### DocumentNumberTextBox

The DocumentNumberTextBox control is bound to the ViewModel's DocumentNumber 
property using two-way binding with PropertyChanged update trigger. The 
ValidationRule evaluates the input string against the IDocumentValidator 
interface implementation.
```

**Problems:**
- Uses technical terms (ViewModel, binding, ValidationRule)
- Focuses on implementation, not user action
- No examples or practical guidance

### Good Example (User-Focused)

```markdown
#### Document Number

**Description:** Enter the unique document number that identifies this document 
in your project. The application checks that the number doesn't already exist 
in the database.

**Type:** Text field

**Sample Values:**
- `ABC-001-A` - Typical project document number
- `DWG-1234` - Drawing number format
- `SPEC-2025-001` - Specification document number

**Requirements:**
- Must be unique in the database
- Can contain letters, numbers, and hyphens
- Maximum length: 50 characters
- Required field (cannot be empty)

**Usage Notes:**
- The field shows an error if you enter a duplicate number
- Use a consistent numbering scheme across your project
- If you're unsure of the format, consult your project's numbering standard
```

**Why This Is Better:**
- No technical jargon
- Clear purpose statement
- Realistic examples with context
- Explicit requirements
- Helpful usage guidance

---

## Template for Complete View Documentation

```markdown
# [View Name] User Manual

## Overview

[2-4 sentence description of the view's purpose and when users would access it]

---

## [Section Name]

### Overview

[1-2 sentence description of what this section accomplishes]

### Controls

#### [Control 1 Name]

**Description:** [What it does and what happens when users interact with it]

**Type:** [Control type in user terms]

**Sample Values:**
- `[Example 1]`
- `[Example 2]`

**Requirements:**
- [Validation/format requirement]
- [Optional/required status]

**Usage Notes:**
- [Best practice or tip]
- [Related functionality]

#### [Control 2 Name]

[Follow same pattern...]

---

## [Next Section Name]

[Continue pattern...]

---

## Common Tasks

### [Task 1 Name]

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Result:** [What users should see after completing these steps]

### [Task 2 Name]

[Follow same pattern...]
```

---

## Review and Approval Process

1. **Draft:** Write documentation following these guidelines
2. **Internal Review:** Technical reviewer checks accuracy
3. **Clarification:** Resolve any unclear purposes or behaviors
4. **User Testing:** Have representative users test the documentation
5. **Revision:** Update based on feedback
6. **Approval:** Obtain sign-off from product owner
7. **Publication:** Make available to end users

---

## Maintenance

User manuals should be updated when:
- UI changes (labels, layouts, sections added/removed)
- Functionality changes (new features, changed behavior)
- User feedback reveals confusion or gaps
- New examples or best practices emerge

Maintain a change log within each manual showing:
- Date of update
- Section(s) changed
- Reason for change
- Reviewer/approver

---

## Summary

**Key Principles:**
1. Focus on the user, not the code
2. Ask when unclear, never guess
3. Provide concrete examples
4. Write clearly and directly
5. Maintain consistency

**Document Structure:**
- View Summary (high-level purpose)
- Chapters for each section
- Control documentation with examples and requirements

**Quality Standards:**
- No technical terms
- Clear, actionable instructions
- Realistic examples
- User-focused language
- Complete coverage of all controls

By following these guidelines, user manuals will be clear, comprehensive, and genuinely helpful to end users navigating the application.
