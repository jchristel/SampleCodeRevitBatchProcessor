CORE NAMESPACE CLASSES WITHOUT TESTS (OR WITH INCOMPLETE COVERAGE)
Generated: 2026-01-07 | Last reviewed: 2026-04-25
Project: duHastNet.DocManager

This document lists classes in the .Core namespace that do not have corresponding
test files, or that have partial coverage with identified gaps. Classes are
organised by priority and category.

================================================================================
SERVICES (High Priority for Testing)
================================================================================

1. CloudMetadataExportService
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: High (CSV export, metadata mapping)
   - Dependencies: ICloudMetaData, Document, Revision, CustomProperty

2. CurrentFolderManager
   - Location: duHastNet.DocManager.Core.Models.CurrentFolder
   - Complexity: Very High (partial class with multiple files)
   - Dependencies: ICurrentFolderManager, CurrentFolderManagerSettings
   - Files: CurrentFolderManager.cs, CurrentFolderManager_GetMatched.cs,
     CurrentFolderManager_MoveFiles.cs, CurrentFolderManager_Settings.cs,
     CurrentFolderManager_Supersede.cs

3. CustomFieldDefinitionRepository (async)
   - Location: duHastNet.DocManager.Core.Services.Repositories
   - Complexity: Medium (Repository pattern)
   - Dependencies: SQLiteAsyncConnection, BaseRepository
   - Note: Verify whether CustomFieldDefinitionRepositoryTests.cs exists
     alongside the sync equivalent. If so, remove this item.

4. DatabaseService
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: Very High (Critical database operations)
   - Dependencies: IDataBaseService, SQLiteAsyncConnection, SQLiteConnection

   ASYNC PATH — Substantial coverage exists across:
     DatabaseServiceTests_Initialization.cs
     DatabaseServiceTests_ConnectionManagement.cs
     DatabaseServiceTests_TablesAndIndexes.cs
     DatabaseServiceTests_SqlOperations.cs
     DatabaseServiceTests_MaintenanceOperations.cs
     DatabaseServiceTests_Dispose.cs
     DatabaseServiceTests_AdditionalScenarios.cs

   ASYNC PATH GAPS (missing tests, to be added):
   - GetDataVersionAsync_AfterInitialization_ReturnsNonNegativeValue
   - GetDataVersionAsync_AfterWrite_ReturnsIncrementedValue
   - GetDataVersionAsync_AfterReadOnly_ReturnsSameValue
   - InitializeAsync_ConfiguresBusyTimeout (verifies PRAGMA busy_timeout = 5000)

   SYNC PATH — No coverage exists. A new test file is required:
     DatabaseServiceTests_Sync.cs
   
   Required sync tests:
   - Initialize_WithValidPath_InitializesSuccessfully
   - Initialize_WithNullPath_ThrowsArgumentNullException
   - Initialize_WithEmptyPath_ThrowsArgumentException
   - Initialize_WithWhitespacePath_ThrowsArgumentException
   - Initialize_ConfiguresBusyTimeout (verifies BusyTimeout = TimeSpan.FromSeconds(5))
   - Initialize_WithNonExistentDirectory_CreatesDirectory
   - CreateTables_CreatesAllRequiredTables
   - Close_AfterInitialization_ClosesConnection
   - Close_WithoutInitialization_DoesNotThrow
   - CheckDatabaseIntegrity_AfterInitialization_ReturnsTrue
   - GetDataVersion_AfterInitialization_ReturnsNonNegativeValue
   - GetDataVersion_AfterWrite_ReturnsIncrementedValue
   - GetDataVersion_AfterReadOnly_ReturnsSameValue

5. DocumentExportService
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: High (CSV export with dynamic columns)
   - Dependencies: Document, CustomFieldDefinition, Revision

6. DocumentImportService
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: High (CSV import, validation)
   - Dependencies: Document, Revision, CustomProperty

7. FilePropertyProvider
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: Medium (File system interaction)
   - Dependencies: File system access

8. Manager
   - Location: duHastNet.DocManager.Core.Models
   - Complexity: High (Core business logic manager)
   - Dependencies: IManager, DocumentContainer, RevisionContainer,
     CustomFieldsContainer, CloudDocumentManager

9. MetaDataTemplateService
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: Medium (Template file handling)
   - Dependencies: IMetaDataTemplateService

10. RevisionExportService
    - Location: duHastNet.DocManager.Core.Services
    - Complexity: Medium (Export functionality)
    - Dependencies: Revision

11. RevisionImportService
    - Location: duHastNet.DocManager.Core.Services
    - Complexity: High (Import with validation)
    - Dependencies: Revision

12. SettingsService
    - Location: duHastNet.DocManager.Core.Services
    - Complexity: High (Settings persistence)
    - Dependencies: ISettingsService

================================================================================
UNIT OF WORK — TRANSACTION COVERAGE GAPS (High Priority)
================================================================================

These classes exist in test files but have incomplete coverage for the
transaction hardening methods added during the SQLite concurrency implementation.

13. UnitOfWork (async)
    - Test file: UnitOfWorkTests.cs
    - Status: PARTIALLY COVERED — transaction tests are stale and missing

    STALE TESTS TO REMOVE:
    - BeginTransactionAsync_CompletesSuccessfully
    - CommitTransactionAsync_CompletesSuccessfully
    - RollbackTransactionAsync_CompletesSuccessfully
    These test methods that no longer exist on IUnitOfWork or UnitOfWork.

    MISSING TESTS TO ADD:
    - RunInTransactionAsync_OnSuccess_CommitsAllWrites
    - RunInTransactionAsync_OnException_RollsBackAllWrites

14. UnitOfWorkSync
    - Test file: UnitOfWorkSyncTests.cs
    - Status: PARTIALLY COVERED — RunInTransaction has no tests

    MISSING TESTS TO ADD:
    - RunInTransaction_OnSuccess_CommitsAllWrites
    - RunInTransaction_OnException_RollsBackAllWrites

================================================================================
MODELS - BUSINESS LOGIC (Medium Priority)
================================================================================

15. CloudDocumentManager
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager
    - Complexity: Medium (Event handling, metadata mapping)
    - Dependencies: ICloudMetaData

16. CustomFieldsContainer
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low-Medium (Container logic)
    - Dependencies: CustomFieldDefinition

17. DocumentContainer
    - Location: duHastNet.DocManager.Core.Models
    - Complexity: Medium (Collection management)
    - Dependencies: Document

18. IncomingDocumentProcessingStatus
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Complexity: Medium (Status tracking)
    - Dependencies: Document

19. MetaDataMapperAconex
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager.MetaData
    - Complexity: High (Metadata mapping logic)
    - Dependencies: ICloudMetaData, MetaDataMap

20. RevisionContainer
    - Location: duHastNet.DocManager.Core.Models
    - Complexity: Medium (Collection management)
    - Dependencies: Revision

21. ResultBase
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Abstract base class)
    - Note: Abstract class with error/warning collections

================================================================================
MODELS - FILING RULES (Medium Priority)
================================================================================

Document Number Modifiers:
22. AddAtIndex
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
    - Dependencies: IDocumentNumberModifier

23. AddToEnd
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
    - Dependencies: IDocumentNumberModifier

24. Replace
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
    - Dependencies: IDocumentNumberModifier

Filing Rules:
25. BeginsWith
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

26. CatchAll
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

27. Contains
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

28. NotBeginsWith
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

29. NotContains
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

================================================================================
MODELS - CONFIGURATION/DATA (Lower Priority)
================================================================================

30. CustomFieldDefinition
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low (Data model with SQLite attributes)

31. DatabaseConnectionSettings
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low (Configuration model)

32. DatabaseSetupConfig
    - Location: duHastNet.DocManager.Core.Models.Config
    - Complexity: Low (Configuration model)

33. DatabaseStatistics
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low (Data model)

34. DocumentImportConfig
    - Location: duHastNet.DocManager.Core.Models.Config
    - Complexity: Low (Configuration model)

35. DocumentImportData
    - Location: duHastNet.DocManager.Core.Models
    - Complexity: Low (Data transfer object)

36. MetaDataMap
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager.MetaData
    - Complexity: Low (Data model)

37. MetaDataTemplateResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result model)

38. SupportedFileType
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Complexity: Low (Configuration model)

================================================================================
RESULT CLASSES (Lower Priority - Simple DTOs)
================================================================================

39. ImportResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result DTO)

40. SaveResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result DTO)

41. SetupResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result DTO)

================================================================================
ENUMS/SIMPLE TYPES (Lowest Priority)
================================================================================

42. CloudProviderType
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager
    - Type: Enum

43. DocumentMatchStatus
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Type: Enum

44. FilingRuleType
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Type: Enum

45. ProcessMessageType
    - Location: duHastNet.DocManager.Core.Models
    - Type: Enum

================================================================================
EXCEPTION CLASSES (Lower Priority)
================================================================================

46. CustomFieldDuplicateException
    - Location: duHastNet.DocManager.Core.Models.Database

47. DocumentDuplicateException
    - Location: duHastNet.DocManager.Core.Models

48. DocumentNotFoundException
    - Location: duHastNet.DocManager.Core.Models

49. FileLockedException
    - Location: duHastNet.DocManager.Core.Services

50. FolderDoesNotExistException
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder

51. IncomingFileDuplicateException
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder

52. IncomingFolderEmptyException
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder

53. InvalidRevisionFormatException
    - Location: duHastNet.DocManager.Core.Models

54. MetaMapperDuplicateException
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager.MetaData

55. RevisionDuplicateException
    - Location: duHastNet.DocManager.Core.Models

================================================================================
TESTING NOTES
================================================================================

- Follow test style guide in testStyles.md
- For database interaction, use instructions in databaseTests.md
- Use sqlite-net-pcl for all database interaction (ORM wherever possible)
- Apply MVVM pattern with MVVM Community Toolkit for WPF components
- Use Windows line endings (CRLF)
- Assume CsvHelper library is installed for CSV operations
- Do not provide summary documents unless specifically asked
- Apply interface implementations per InterfaceBestPractices.md

PRIORITY RECOMMENDATIONS:
1. Resolve the hardening gaps first (items 4, 13, 14) — these are regressions
   against implemented production code, not new work
2. Then address high-priority services (items 1, 2, 5, 6, 8, 11, 12)
3. Then models with business logic (items 15-21)
4. Filing rules (items 22-29) are self-contained and straightforward to test
5. Configuration/data models (items 30-38) are lower priority
6. Enums and exceptions can be tested last if at all

================================================================================
END OF DOCUMENT
================================================================================
