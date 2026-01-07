CORE NAMESPACE CLASSES WITHOUT TESTS
Generated: 2026-01-07
Project: duHastNet.DocManager

This document lists classes in the .Core namespace that do not have corresponding test files.
Classes are organized by priority and category.

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

3. CustomFieldDefinitionRepository
   - Location: duHastNet.DocManager.Core.Services.Repositories
   - Complexity: Medium (Repository pattern)
   - Dependencies: SQLiteAsyncConnection, BaseRepository

4. DatabaseService
   - Location: duHastNet.DocManager.Core.Services
   - Complexity: Very High (Critical database operations)
   - Status: Has partial tests but may need more coverage
   - Dependencies: IDataBaseService, SQLiteAsyncConnection

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
MODELS - BUSINESS LOGIC (Medium Priority)
================================================================================

13. CloudDocumentManager
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager
    - Complexity: Medium (Event handling, metadata mapping)
    - Dependencies: ICloudMetaData

14. CustomFieldsContainer
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low-Medium (Container logic)
    - Dependencies: CustomFieldDefinition

15. DocumentContainer
    - Location: duHastNet.DocManager.Core.Models
    - Complexity: Medium (Collection management)
    - Dependencies: Document

16. IncomingDocumentProcessingStatus
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Complexity: Medium (Status tracking)
    - Dependencies: Document

17. MetaDataMapperAconex
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager.MetaData
    - Complexity: High (Metadata mapping logic)
    - Dependencies: ICloudMetaData, MetaDataMap

18. RevisionContainer
    - Location: duHastNet.DocManager.Core.Models
    - Complexity: Medium (Collection management)
    - Dependencies: Revision

19. ResultBase
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Abstract base class)
    - Note: Abstract class with error/warning collections

================================================================================
MODELS - FILING RULES (Medium Priority)
================================================================================

Document Number Modifiers:
20. AddAtIndex
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
    - Dependencies: IDocumentNumberModifier

21. AddToEnd
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
    - Dependencies: IDocumentNumberModifier

22. Replace
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers
    - Dependencies: IDocumentNumberModifier

Filing Rules:
23. BeginsWith
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

24. CatchAll
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

25. Contains
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

26. NotBeginsWith
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

27. NotContains
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules
    - Dependencies: IFilingRule

================================================================================
MODELS - CONFIGURATION/DATA (Lower Priority)
================================================================================

28. CustomFieldDefinition
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low (Data model with SQLite attributes)

29. DatabaseConnectionSettings
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low (Configuration model)

30. DatabaseSetupConfig
    - Location: duHastNet.DocManager.Core.Models.Config
    - Complexity: Low (Configuration model)

31. DatabaseStatistics
    - Location: duHastNet.DocManager.Core.Models.Database
    - Complexity: Low (Data model)

32. DocumentImportConfig
    - Location: duHastNet.DocManager.Core.Models.Config
    - Complexity: Low (Configuration model)

33. DocumentImportData
    - Location: duHastNet.DocManager.Core.Models
    - Complexity: Low (Data transfer object)

34. MetaDataMap
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager.MetaData
    - Complexity: Low (Data model)

35. MetaDataTemplateResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result model)

36. SupportedFileType
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Complexity: Low (Configuration model)

================================================================================
RESULT CLASSES (Lower Priority - Simple DTOs)
================================================================================

37. ImportResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result DTO)

38. SaveResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result DTO)

39. SetupResult
    - Location: duHastNet.DocManager.Core.Models.Results
    - Complexity: Low (Result DTO)

================================================================================
ENUMS/SIMPLE TYPES (Lowest Priority)
================================================================================

40. CloudProviderType
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager
    - Type: Enum

41. DocumentMatchStatus
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Type: Enum

42. FilingRuleType
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder
    - Type: Enum

43. ProcessMessageType
    - Location: duHastNet.DocManager.Core.Models
    - Type: Enum

================================================================================
EXCEPTION CLASSES (Lower Priority - Can be tested but simpler)
================================================================================

44. CustomFieldDuplicateException
    - Location: duHastNet.DocManager.Core.Models.Database

45. DocumentDuplicateException
    - Location: duHastNet.DocManager.Core.Models

46. DocumentNotFoundException
    - Location: duHastNet.DocManager.Core.Models

47. FileLockedException
    - Location: duHastNet.DocManager.Core.Services

48. FolderDoesNotExistException
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder

49. IncomingFileDuplicateException
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder

50. IncomingFolderEmptyException
    - Location: duHastNet.DocManager.Core.Models.CurrentFolder

51. InvalidRevisionFormatException
    - Location: duHastNet.DocManager.Core.Models

52. MetaMapperDuplicateException
    - Location: duHastNet.DocManager.Core.Models.CloudDocManager.MetaData

53. RevisionDuplicateException
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
1. Start with Services (items 1-12) as they contain critical business logic
2. Then test Models with Business Logic (items 13-19)
3. Filing Rules (items 20-27) are self-contained and easier to test
4. Configuration/Data models (items 28-36) are lower priority
5. Enums and exceptions can be tested last if at all

================================================================================
END OF DOCUMENT
================================================================================
