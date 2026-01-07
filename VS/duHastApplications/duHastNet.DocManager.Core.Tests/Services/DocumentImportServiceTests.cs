//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Tests.Services;

/// <summary>
/// Tests for DocumentImportService
/// This test class covers CSV import functionality including:
/// - Creating new documents from CSV
/// - Updating existing documents from CSV
/// - Custom field handling during import
/// - Revision history import
/// - Error handling and validation
/// - Integration with UnitOfWork and repositories
/// </summary>
[TestFixture]
public class DocumentImportServiceTests
{
    private DocumentImportService _service;
    private UnitOfWork _unitOfWork;
    private SQLiteAsyncConnection _connection;
    private string _testDirectory;
    private string _testDatabasePath;

    [SetUp]
    public async Task Setup()
    {
        _testDirectory = Path.Combine(Path.GetTempPath(), "DocumentImportServiceTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);

        _testDatabasePath = Path.Combine(_testDirectory, "test.db");
        _connection = new SQLiteAsyncConnection(_testDatabasePath);

        // Create tables
        await _connection.CreateTablesAsync<Revision, Document, CustomFieldDefinition, CustomProperty>();

        // Create UnitOfWork with real repositories
        _unitOfWork = new UnitOfWork(_connection);
        _service = new DocumentImportService(_unitOfWork);
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_unitOfWork != null)
        {
            _unitOfWork.Dispose();
        }

        if (_connection != null)
        {
            await _connection.CloseAsync();
        }

        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region Helper Methods

    private async Task<string> CreateTestCsvFile(string fileName, string content)
    {
        var filePath = Path.Combine(_testDirectory, fileName);
        await File.WriteAllTextAsync(filePath, content);
        return filePath;
    }

    private async Task SetupTestRevision()
    {
        var revision = new Revision(new DateTime(2024, 1, 1), "Initial Issue");
        await _unitOfWork.Revisions.InsertAsync(revision);
    }

    private async Task SetupTestCustomFields()
    {
        var field1 = new CustomFieldDefinition("Discipline", true);
        var field2 = new CustomFieldDefinition("Zone", true);
        await _unitOfWork.CustomFieldDefinitions.InsertAsync(field1);
        await _unitOfWork.CustomFieldDefinitions.InsertAsync(field2);
    }

    #endregion

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidUnitOfWork_InitializesSuccessfully()
    {
        // Arrange & Act
        var service = new DocumentImportService(_unitOfWork);

        // Assert
        Assert.That(service, Is.Not.Null);
    }

    [Test]
    public void Constructor_WithNullUnitOfWork_ThrowsArgumentNullException()
    {
        // Arrange, Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(
            () => new DocumentImportService(null));
        
        Assert.That(exception.ParamName, Is.EqualTo("unitOfWork"));
    }

    #endregion

    #region Basic Import Tests - New Documents

    [Test]
    public async Task ImportDocumentsAsync_WithSingleNewDocument_CreatesDocument()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
new,A-101,Floor Plan,A,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(1));
            Assert.That(result.DocumentsCreated, Is.EqualTo(1));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(0));
        });

        // Verify document in database
        var documents = await _unitOfWork.Documents.GetAllAsync();
        Assert.Multiple(() =>
        {
            Assert.That(documents, Has.Count.EqualTo(1));
            Assert.That(documents[0].Number, Is.EqualTo("A-101"));
            Assert.That(documents[0].Name, Is.EqualTo("Floor Plan"));
            Assert.That(documents[0].Revision, Is.EqualTo("A"));
        });
    }

    [Test]
    public async Task ImportDocumentsAsync_WithMultipleNewDocuments_CreatesAll()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
new,A-101,Floor Plan,A,1,Architecture,Ground Floor
new,A-102,Ceiling Plan,A,1,Architecture,Ground Floor
new,S-201,Structural Layout,A,1,Structural,All Levels";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(3));
            Assert.That(result.DocumentsCreated, Is.EqualTo(3));
        });

        var documents = await _unitOfWork.Documents.GetAllAsync();
        Assert.That(documents, Has.Count.EqualTo(3));
    }

    [Test]
    public async Task ImportDocumentsAsync_WithNewDocument_CreatesCustomProperties()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
new,A-101,Floor Plan,A,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        var documents = await _unitOfWork.Documents.GetAllAsync();
        var document = documents[0];
        var properties = await _unitOfWork.CustomProperties.GetPropertiesByDocumentAsync(document.Id);

        Assert.Multiple(() =>
        {
            Assert.That(properties, Has.Count.EqualTo(2));
            Assert.That(properties.Any(p => p.PropertyValue == "Architecture"), Is.True);
            Assert.That(properties.Any(p => p.PropertyValue == "Ground Floor"), Is.True);
        });
    }

    #endregion

    #region Update Existing Documents Tests

    [Test]
    public async Task ImportDocumentsAsync_WithExistingDocumentId_UpdatesDocument()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // Create existing document
        var existingDoc = new Document("A-101", "Old Name", "A", 1);
        await _unitOfWork.Documents.InsertAsync(existingDoc);

        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{existingDoc.Id},A-101,New Name,A,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(1));
            Assert.That(result.DocumentsCreated, Is.EqualTo(0));
        });

        var updated = await _unitOfWork.Documents.GetByIdAsync(existingDoc.Id);
        Assert.That(updated.Name, Is.EqualTo("New Name"));
    }

    [Test]
    public async Task ImportDocumentsAsync_WithMixedNewAndExisting_HandlesCorrectly()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // Create existing document
        var existingDoc = new Document("A-101", "Existing", "A", 1);
        await _unitOfWork.Documents.InsertAsync(existingDoc);

        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{existingDoc.Id},A-101,Updated Existing,A,1,Architecture,Ground Floor
new,A-102,New Document,A,1,Architecture,First Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(2));
            Assert.That(result.DocumentsCreated, Is.EqualTo(1));
        });

        var allDocuments = await _unitOfWork.Documents.GetAllAsync();
        Assert.That(allDocuments, Has.Count.EqualTo(2));
    }

    #endregion

    #region Custom Field Validation Tests

    [Test]
    public async Task ImportDocumentsAsync_WithMissingCustomFieldColumn_ReturnsFailure()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();
        
        // Verify custom fields were actually created (debugging step)
        var customFields = await _unitOfWork.CustomFieldDefinitions.GetAllAsync();
        Assert.That(customFields, Has.Count.EqualTo(2), 
            "Setup should have created 2 custom field definitions");
        
        // Log what custom fields exist
        Console.WriteLine($"Custom fields in database: {string.Join(", ", customFields.Select(cf => cf.PropertyName))}");

        // CSV missing the "Zone" column
        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline
new,A-101,Floor Plan,A,1,Architecture";

        var filePath = await CreateTestCsvFile("import.csv", csv);
        
        // Read the CSV back to verify what headers it actually has
        var csvLines = await File.ReadAllLinesAsync(filePath);
        Console.WriteLine($"CSV header line: {csvLines[0]}");
        Console.WriteLine($"CSV has 'Discipline' column: {csvLines[0].Contains("Discipline")}");
        Console.WriteLine($"CSV has 'Zone' column: {csvLines[0].Contains("Zone")}");

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Console.WriteLine($"Import result IsImportSuccessful: {result.IsImportSuccessful}");
        Console.WriteLine($"Import result Message: {result.Message}");
        Console.WriteLine($"Import result DocumentsProcessed: {result.DocumentsProcessed}");
        Console.WriteLine($"Import result DocumentsCreated: {result.DocumentsCreated}");
        Console.WriteLine($"Import result Errors count: {result.Errors?.Count ?? 0}");
        if (result.Errors?.Any() == true)
        {
            Console.WriteLine($"Errors: {string.Join(", ", result.Errors)}");
        }
        
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False, 
                "Import should fail when required custom field column is missing");
            Assert.That(result.Message, Does.Contain("missing required custom field columns"),
                "Error message should indicate missing columns");
            Assert.That(result.Message, Does.Contain("Zone"),
                "Error message should specifically mention the missing 'Zone' column");
        });
    }

    [Test]
    public async Task ImportDocumentsAsync_WithExtraCustomFieldColumn_ImportsSuccessfully()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // CSV has extra column that's not in custom field definitions
        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone,ExtraColumn
new,A-101,Floor Plan,A,1,Architecture,Ground Floor,ExtraValue";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert - should succeed, extra columns are ignored
        Assert.That(result.IsImportSuccessful, Is.True);
    }

    #endregion

    #region Error Handling Tests

    [Test]
    public async Task ImportDocumentsAsync_WithNonExistentFile_ReturnsFailure()
    {
        // Arrange
        var nonExistentPath = Path.Combine(_testDirectory, "nonexistent.csv");

        // Act
        var result = await _service.ImportDocumentsAsync(nonExistentPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.Message, Does.Contain("Import failed"));
        });
    }

    [Test]
    public async Task ImportDocumentsAsync_WithInvalidRevisionId_SkipsRow()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // RevisionId 999 doesn't exist
        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
new,A-101,Floor Plan,A,999,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(1));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.Errors, Has.Count.GreaterThan(0));
        });
    }

    [Test]
    public async Task ImportDocumentsAsync_WithInvalidDocumentId_SkipsRow()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
999,A-101,Floor Plan,A,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.Errors.Any(e => e.Contains("not found")), Is.True);
        });
    }

    #endregion

    #region Empty File Tests

    [Test]
    public async Task ImportDocumentsAsync_WithEmptyFile_ReturnsSuccess()
    {
        // Arrange
        await SetupTestCustomFields();

        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone";

        var filePath = await CreateTestCsvFile("empty.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(0));
            Assert.That(result.DocumentsCreated, Is.EqualTo(0));
        });
    }

    [Test]
    public async Task ImportDocumentsAsync_WithHeaderOnly_ReturnsSuccess()
    {
        // Arrange
        await SetupTestCustomFields();

        var csv = "Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone";
        var filePath = await CreateTestCsvFile("headeronly.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);
    }

    #endregion

    #region Custom Property Update Tests

    [Test]
    public async Task ImportDocumentsAsync_UpdateExistingDocumentCustomProperty_Updates()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // Create document with custom property
        var doc = new Document("A-101", "Floor Plan", "A", 1);
        await _unitOfWork.Documents.InsertAsync(doc);

        var customFieldDefs = await _unitOfWork.CustomFieldDefinitions.GetAllAsync();
        var disciplineField = customFieldDefs.First(f => f.PropertyName == "Discipline");

        var prop = new CustomProperty(doc.Id, disciplineField.Id, "Architecture");
        await _unitOfWork.CustomProperties.InsertAsync(prop);

        // Import CSV with updated property value
        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{doc.Id},A-101,Floor Plan,A,1,Structural,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        var properties = await _unitOfWork.CustomProperties.GetPropertiesByDocumentAsync(doc.Id);
        var disciplineProp = properties.First(p => p.CustomFieldDefinitionId == disciplineField.Id);

        Assert.That(disciplineProp.PropertyValue, Is.EqualTo("Structural"));
    }

    [Test]
    public async Task ImportDocumentsAsync_AddNewCustomPropertyToExisting_Adds()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // Create document with only one custom property
        var doc = new Document("A-101", "Floor Plan", "A", 1);
        await _unitOfWork.Documents.InsertAsync(doc);

        var customFieldDefs = await _unitOfWork.CustomFieldDefinitions.GetAllAsync();
        var disciplineField = customFieldDefs.First(f => f.PropertyName == "Discipline");

        var prop = new CustomProperty(doc.Id, disciplineField.Id, "Architecture");
        await _unitOfWork.CustomProperties.InsertAsync(prop);

        // Import CSV with both properties
        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{doc.Id},A-101,Floor Plan,A,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        var properties = await _unitOfWork.CustomProperties.GetPropertiesByDocumentAsync(doc.Id);
        Assert.That(properties, Has.Count.EqualTo(2));
    }

    #endregion

    #region Document Number Change Tests

    [Test]
    public async Task ImportDocumentsAsync_ChangeDocumentNumber_UpdatesAndAddsToHistory()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // Create document with original number
        var doc = new Document("A-101", "Floor Plan", "A", 1);
        await _unitOfWork.Documents.InsertAsync(doc);

        // Import CSV with new document number
        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{doc.Id},A-201,Floor Plan,A,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        var updated = await _unitOfWork.Documents.GetByIdAsync(doc.Id);
        Assert.Multiple(() =>
        {
            Assert.That(updated.Number, Is.EqualTo("A-201"));
            Assert.That(updated.DocumentNumberHistory.ContainsKey("A-101"), Is.True);
        });
    }

    #endregion

    #region Revision Change Tests

    [Test]
    public async Task ImportDocumentsAsync_ChangeRevisionIndicator_Updates()
    {
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        var doc = new Document("A-101", "Floor Plan", "A", 1);
        await _unitOfWork.Documents.InsertAsync(doc);

        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{doc.Id},A-101,Floor Plan,B,1,Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        var updated = await _unitOfWork.Documents.GetByIdAsync(doc.Id);
        Assert.That(updated.Revision, Is.EqualTo("B"));
    }

    [Test]
    public async Task ImportDocumentsAsync_ChangeRevisionId_Updates()
    {
        // Arrange
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial");
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Review");
        await _unitOfWork.Revisions.InsertAsync(revision1);
        await _unitOfWork.Revisions.InsertAsync(revision2);
        await SetupTestCustomFields();

        var doc = new Document("A-101", "Floor Plan", "A", revision1.Id);
        await _unitOfWork.Documents.InsertAsync(doc);

        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{doc.Id},A-101,Floor Plan,B,{revision2.Id},Architecture,Ground Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        var updated = await _unitOfWork.Documents.GetByIdAsync(doc.Id);
        Assert.That(updated.RevisionId, Is.EqualTo(revision2.Id));
    }

    #endregion

    #region Integration Tests

    [Test]
    public async Task ImportDocumentsAsync_ComplexScenario_HandlesCorrectly()
    {
        // This test verifies a complex real-world scenario with:
        // - Mix of new and existing documents
        // - Custom properties
        // - Document updates
        
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        // Create one existing document
        var existingDoc = new Document("A-101", "Old Floor Plan", "A", 1);
        await _unitOfWork.Documents.InsertAsync(existingDoc);

        var csv = $@"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
{existingDoc.Id},A-101,Updated Floor Plan,A,1,Architecture,Ground Floor
new,A-102,New Ceiling Plan,A,1,Architecture,Ground Floor
new,S-201,Structural Layout,A,1,Structural,All Levels";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(3));
            Assert.That(result.DocumentsCreated, Is.EqualTo(2));
        });

        var allDocuments = await _unitOfWork.Documents.GetAllAsync();
        Assert.Multiple(() =>
        {
            Assert.That(allDocuments, Has.Count.EqualTo(3));
            
            var updated = allDocuments.First(d => d.Id == existingDoc.Id);
            Assert.That(updated.Name, Is.EqualTo("Updated Floor Plan"));
            
            Assert.That(allDocuments.Any(d => d.Number == "A-102"), Is.True);
            Assert.That(allDocuments.Any(d => d.Number == "S-201"), Is.True);
        });
    }

    [Test]
    public async Task ImportDocumentsAsync_WithPartialFailures_ContinuesProcessing()
    {
        // This test verifies that when some rows fail, processing continues for valid rows
        
        // Arrange
        await SetupTestRevision();
        await SetupTestCustomFields();

        var csv = @"Id,Document Number,Document Name,Revision Indicator,Revision Id,Discipline,Zone
new,A-101,Valid Document,A,1,Architecture,Ground Floor
999,A-102,Invalid ID,A,1,Architecture,Ground Floor
new,A-103,Another Valid,A,1,Architecture,First Floor";

        var filePath = await CreateTestCsvFile("import.csv", csv);

        // Act
        var result = await _service.ImportDocumentsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False); // Has errors
            Assert.That(result.DocumentsProcessed, Is.EqualTo(3));
            Assert.That(result.DocumentsCreated, Is.EqualTo(2)); // Two valid documents
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1)); // One invalid
            Assert.That(result.Errors, Has.Count.EqualTo(1));
        });

        var documents = await _unitOfWork.Documents.GetAllAsync();
        Assert.That(documents, Has.Count.EqualTo(2)); // Only valid documents created
    }

    #endregion
}
