# Related Files Synchronization - Implementation Summary

## Overview
Implemented automatic detection and synchronization of related document files (same document number, different file types) when users edit document numbers or names in the Add New Documents dialog.

## Modified Files

### 1. NewDocumentRowViewModel.cs

#### Added Fields:
- `_relatedFilesCallback` - Callback to handle related files when document number or name changes
- `_previousDocumentNumber` - Tracks previous document number value for detecting shortening
- `_isUpdatingProgrammatically` - Flag to prevent recursive callback invocations

#### Modified Constructor:
- Added `relatedFilesCallback` parameter
- Initializes `_previousDocumentNumber` after setting `ProposedDocumentNumber`

#### Modified Property Change Handlers:

**OnProposedDocumentNumberChanged:**
- Checks if programmatic update is in progress (returns early if true)
- Detects if document number was shortened (new length < previous length)
- Invokes `_relatedFilesCallback` if shortened
- Updates `_previousDocumentNumber` for next change
- Invokes validation callback

**OnProposedDocumentNameChanged:**
- Checks if programmatic update is in progress (returns early if true)
- Invokes `_relatedFilesCallback` for document name synchronization
- Invokes validation callback

#### Added Methods:
- `SetProgrammaticUpdate(bool)` - Enables/disables the programmatic update flag
- `UpdateDocumentNumberProgrammatically(string)` - Updates document number without triggering callbacks
- `UpdateDocumentNameProgrammatically(string)` - Updates document name without triggering callbacks

---

### 2. AddNewDocumentsDialogViewModel.cs

#### Added Using Statements:
- `duHastNet.DocManager.UI.Shared.Interfaces` - For IDialogService
- `System.Text` - For StringBuilder in confirmation messages

#### Added Field:
- `_dialogService` - IDialogService for user interactions

#### Modified Constructor:
- Added `dialogService` parameter (required, non-nullable)
- Stores reference to `_dialogService`

#### Modified LoadUnknownDocuments Method:
- Updated NewDocumentRowViewModel instantiation to pass `HandleRelatedFiles` callback

#### Added Methods:

**HandleRelatedFiles:**
- Main callback invoked when document number or name changes
- Detects if document number was shortened and finds related files
- If related files found: calls `HandleDocumentNumberShorteningWithConfirmation`
- If no related files but same document number exists: calls `SynchronizeDocumentNames`

**FindRelatedFilesByDocumentNumber:**
- Finds files where document number starts with the changed row's document number
- Filters to different file extensions only
- Ensures related files have longer document numbers (indicating they may belong to same document)

**FindFilesBySameDocumentNumber:**
- Finds files with identical document number but different file extensions
- Used for document name synchronization

**HandleDocumentNumberShorteningWithConfirmation:**
- Builds confirmation message listing all related files
- Shows message box with Yes/No options
- If user confirms: calls `UpdateRelatedFilesDocumentNumber`

**UpdateRelatedFilesDocumentNumber:**
- Updates document number for all related files programmatically
- Re-validates each updated row
- Updates counts after all changes

**SynchronizeDocumentNames:**
- Silently updates document names for all files with same document number
- Updates programmatically without user confirmation
- Re-validates each updated row
- Updates counts after all changes

---

## Behavior

### Document Number Shortening (User Confirmation Required)

**Trigger:**
- User edits document number to a shorter value

**Detection:**
```
newValue.Length < previousValue.Length
```

**Related File Criteria:**
```
- Different file extension
- Document number starts with changed row's document number
- Document number is longer than changed row's document number
```

**Example:**
1. User changes `.dwg` file from `AWH-HSL-AR-MW-CSB-00-DWG-XX001-DRAWING INDEX` to `AWH-HSL-AR-MW-CSB-00-DWG-XX001`
2. System finds `.pdf` file with `AWH-HSL-AR-MW-CSB-00-DWG-XX001-DRAWING INDEX`
3. Dialog shows:
   ```
   The following files may belong to the same document:
   
     • AWH-HSL-AR-MW-CSB-00-DWG-XX001-DRAWING INDEX.pdf
   
   Update these files to use the same document number?
   [Yes] [No]
   ```
4. If Yes: `.pdf` document number becomes `AWH-HSL-AR-MW-CSB-00-DWG-XX001`
5. If No: No action taken

---

### Document Name Synchronization (Silent/Automatic)

**Trigger:**
- User edits document name (any change including clearing)

**Related File Criteria:**
```
- Different file extension
- Identical document number (case-insensitive)
```

**Example:**
1. `.dwg` and `.pdf` both have document number `AWH-HSL-AR-MW-CSB-00-DWG-XX001`
2. User changes `.dwg` document name from `DRAWING INDEX` to `DRAWING REGISTER`
3. System automatically updates `.pdf` document name to `DRAWING REGISTER`
4. No confirmation dialog shown

---

## Recursion Prevention

**Mechanism:**
- `_isUpdatingProgrammatically` flag in NewDocumentRowViewModel
- Set to `true` before programmatic updates
- Property change handlers return early if flag is `true`
- Prevents cascading callbacks when multiple rows are updated

**Usage:**
```csharp
// In UpdateDocumentNumberProgrammatically
_isUpdatingProgrammatically = true;
ProposedDocumentNumber = documentNumber;  // Won't trigger OnProposedDocumentNumberChanged callback
_previousDocumentNumber = documentNumber;
_isUpdatingProgrammatically = false;
```

---

## Edge Cases Handled

1. **Empty document number/name** - Methods check for null/whitespace before processing
2. **No related files found** - Methods return empty lists, no dialogs shown
3. **Self-match excluded** - Filters ensure changed row is not included in matches
4. **Case-insensitive matching** - Uses `StringComparison.OrdinalIgnoreCase` throughout
5. **Multiple file types** - Single confirmation dialog handles all matches
6. **Validation after updates** - All programmatic updates trigger validation to ensure correct status

---

## Testing Recommendations

### Document Number Tests:
1. Shorten document number with no matches - verify no dialog appears
2. Shorten document number with 1 match - verify dialog shows, update on confirm
3. Shorten document number with multiple matches - verify all files listed, all updated on confirm
4. Shorten document number but cancel - verify no updates occur
5. Lengthen document number - verify no dialog appears
6. Change to same length - verify no dialog appears

### Document Name Tests:
1. Change document name with no matches - verify no updates
2. Change document name with 1 match - verify silent update
3. Change document name with multiple matches - verify all updated silently
4. Clear document name - verify empty value synced to matches
5. Change name on file with different document number - verify no updates

### Integration Tests:
1. Change number then change name - verify both sync correctly
2. Rapid consecutive changes - verify each handled independently
3. Programmatic updates don't trigger additional callbacks - verify no recursion

---

## Breaking Changes

### AddNewDocumentsDialogViewModel Constructor
**Before:**
```csharp
public AddNewDocumentsDialogViewModel(
    CurrentFolderManager currentFolderManager,
    List<Document> existingDocuments,
    List<IncomingDocumentProcessingStatus> unknownDocuments,
    List<CustomFieldDefinition>? customFieldDefinitions = null)
```

**After:**
```csharp
public AddNewDocumentsDialogViewModel(
    CurrentFolderManager currentFolderManager,
    List<Document> existingDocuments,
    List<IncomingDocumentProcessingStatus> unknownDocuments,
    IDialogService dialogService,  // NEW REQUIRED PARAMETER
    List<CustomFieldDefinition>? customFieldDefinitions = null)
```

**Impact:**
- All instantiations of `AddNewDocumentsDialogViewModel` must be updated to pass `IDialogService`
- This is typically injected via dependency injection in the view or parent view model

---

## Files Not Modified

- AddNewDocumentsDialog.xaml (View) - No changes required
- Dialog behavior is handled entirely in the ViewModel
- UI will automatically reflect the synchronized values through data binding
