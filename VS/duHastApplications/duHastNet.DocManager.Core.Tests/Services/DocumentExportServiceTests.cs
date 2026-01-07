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
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Tests.Services;

/// <summary>
/// Tests for DocumentExportService
/// This test class covers CSV export functionality including:
/// - Basic document export with fixed columns
/// - Custom field handling and ordering
/// - Revision history in sparse and full modes
/// - Dynamic column generation
/// - Error handling
/// </summary>
[TestFixture]
public class DocumentExportServiceTests
{
    private DocumentExportService _service;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _service = new DocumentExportService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "DocumentExportServiceTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region Basic Export Tests

    [Test]
    public void ExportDocuments_WithSingleDocument_CreatesValidCsv()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        
        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);
        Assert.That(File.Exists(filePath), Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(2)); // Header + 1 data row
            Assert.That(lines[0], Does.Contain("Document Number"));
            Assert.That(lines[0], Does.Contain("Document Name"));
            Assert.That(lines[0], Does.Contain("Revision Indicator"));
            Assert.That(lines[1], Does.Contain("A-101"));
            Assert.That(lines[1], Does.Contain("Floor Plan"));
        });
    }

    [Test]
    public void ExportDocuments_WithMultipleDocuments_CreatesAllRows()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        
        var documents = new List<Document>
        {
            new Document("A-101", "Floor Plan", "A", 1) { Id = 1 },
            new Document("A-102", "Ceiling Plan", "A", 1) { Id = 2 },
            new Document("S-201", "Structural Layout", "A", 1) { Id = 3 }
        };
        
        var revisions = new List<Revision> { revision };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(4)); // Header + 3 data rows
            Assert.That(lines[1], Does.Contain("A-101"));
            Assert.That(lines[2], Does.Contain("A-102"));
            Assert.That(lines[3], Does.Contain("S-201"));
        });
    }

    [Test]
    public void ExportDocuments_WithEmptyDocuments_CreatesHeaderOnly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var documents = new List<Document>();
        var revisions = new List<Revision>();
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.That(lines, Has.Length.EqualTo(1)); // Header only
    }

    #endregion

    #region Custom Field Tests

    [Test]
    public void ExportDocuments_WithSingleCustomField_AddsColumnAndValue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        
        var customProperty = new CustomProperty 
        { 
            DocumentId = 1,
            CustomFieldDefinitionId = 1,
            PropertyName = "Discipline", 
            PropertyValue = "Architecture" 
        };
        document.CustomProperties.Add(customProperty);

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        var customFields = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Discipline", true)
        };

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines[0], Does.Contain("Discipline"));
            Assert.That(lines[1], Does.Contain("Architecture"));
        });
    }

    [Test]
    public void ExportDocuments_WithMultipleCustomFields_OrdersByPropertyName()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        
        document.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 1, 
            PropertyName = "Zone", 
            PropertyValue = "Zone A" 
        });
        document.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 2, 
            PropertyName = "Discipline", 
            PropertyValue = "Architecture" 
        });
        document.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 3, 
            PropertyName = "Package", 
            PropertyValue = "Package 1" 
        });

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        
        // Custom fields in non-alphabetical order
        var customFields = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Zone", true),
            new CustomFieldDefinition("Discipline", true),
            new CustomFieldDefinition("Package", true)
        };

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        var disciplineIndex = headerLine.IndexOf("Discipline");
        var packageIndex = headerLine.IndexOf("Package");
        var zoneIndex = headerLine.IndexOf("Zone");

        // Verify alphabetical order: Discipline < Package < Zone
        Assert.Multiple(() =>
        {
            Assert.That(disciplineIndex, Is.LessThan(packageIndex));
            Assert.That(packageIndex, Is.LessThan(zoneIndex));
        });
    }

    [Test]
    public void ExportDocuments_WithMissingCustomProperty_WritesEmptyValue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        
        // Document has no custom properties

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        var customFields = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Discipline", true)
        };

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        var fields = lines[1].Split(',');
        
        // The discipline field should be present but empty
        Assert.That(lines[0], Does.Contain("Discipline"));
        // Data row should have the column count matching header
        Assert.That(fields.Length, Is.EqualTo(lines[0].Split(',').Length));
    }

    [Test]
    public void ExportDocuments_WithPartialCustomProperties_FillsMissingWithEmpty()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        
        var doc1 = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        doc1.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 1, 
            PropertyName = "Discipline", 
            PropertyValue = "Architecture" 
        });
        doc1.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 2, 
            PropertyName = "Zone", 
            PropertyValue = "Zone A" 
        });

        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1) { Id = 2 };
        doc2.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 2, 
            CustomFieldDefinitionId = 1, 
            PropertyName = "Discipline", 
            PropertyValue = "Architecture" 
        });
        // Zone is missing

        var documents = new List<Document> { doc1, doc2 };
        var revisions = new List<Revision> { revision };
        var customFields = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Discipline", true),
            new CustomFieldDefinition("Zone", true)
        };

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        var doc1Fields = lines[1].Split(',');
        var doc2Fields = lines[2].Split(',');

        Assert.Multiple(() =>
        {
            Assert.That(doc1Fields.Length, Is.EqualTo(doc2Fields.Length));
            Assert.That(lines[1], Does.Contain("Zone A"));
        });
    }

    #endregion

    #region Revision History Tests - Sparse Mode

    [Test]
    public void ExportDocuments_SparseMode_WithOnlyCurrentRevision_HasOneHistoryColumn()
    {
        // When a document is created, its current revision is automatically added to RevisionIndicatorHistory
        // So even a "new" document will have 1 item in its history (the current revision)
        
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision = new Revision(DateTime.Now, "Initial Issue") { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        // RevisionIndicatorHistory will contain {1: "A"} from constructor

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: false);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        Assert.Multiple(() =>
        {
            // Fixed columns should be present
            Assert.That(headerLine, Does.Contain("Revision Indicator"));
            Assert.That(headerLine, Does.Contain("Revision Id"));
            
            // One history column pair (for the current revision)
            Assert.That(headerLine, Does.Contain("Revision Indicator 1"));
            Assert.That(headerLine, Does.Contain("Revision Id 1"));
            
            // But not two history columns
            Assert.That(headerLine, Does.Not.Contain("Revision Indicator 2"));
        });
    }

    [Test]
    public void ExportDocuments_SparseMode_WithSingleRevisionHistory_AddsHistoryColumns()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        
        var document = new Document("A-101", "Floor Plan", "B", 2) { Id = 1 };
        document.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" }
        };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision1, revision2 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: false);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines[0], Does.Contain("Revision Indicator 1"));
            Assert.That(lines[0], Does.Contain("Revision Id 1"));
            Assert.That(lines[1], Does.Contain("A"));
            Assert.That(lines[1], Does.Contain("1")); // Revision Id 1
        });
    }

    [Test]
    public void ExportDocuments_SparseMode_WithMultipleRevisionHistory_CreatesCorrectColumns()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        var revision3 = new Revision(new DateTime(2024, 3, 1), "Final") { Id = 3 };
        
        var document = new Document("A-101", "Floor Plan", "C", 3) { Id = 1 };
        document.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" },
            { 2, "B" }
        };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision1, revision2, revision3 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: false);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        Assert.Multiple(() =>
        {
            Assert.That(headerLine, Does.Contain("Revision Indicator 1"));
            Assert.That(headerLine, Does.Contain("Revision Id 1"));
            Assert.That(headerLine, Does.Contain("Revision Indicator 2"));
            Assert.That(headerLine, Does.Contain("Revision Id 2"));
        });
    }

    [Test]
    public void ExportDocuments_SparseMode_WithDifferentHistoryLengths_PadsWithEmpty()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        
        var doc1 = new Document("A-101", "Floor Plan", "B", 2) { Id = 1 };
        doc1.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" }
        };

        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1) { Id = 2 };
        // No revision history

        var documents = new List<Document> { doc1, doc2 };
        var revisions = new List<Revision> { revision1, revision2 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: false);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        var doc1Fields = lines[1].Split(',');
        var doc2Fields = lines[2].Split(',');

        // Both documents should have same number of fields
        Assert.That(doc1Fields.Length, Is.EqualTo(doc2Fields.Length));
    }

    #endregion

    #region Revision History Tests - Full Mode

    [Test]
    public void ExportDocuments_FullMode_WithNoRevisions_NoHistoryColumns()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>(); // No revisions
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: true);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        Assert.Multiple(() =>
        {
            // Fixed columns should be present
            Assert.That(headerLine, Does.Contain("Revision Indicator"));
            Assert.That(headerLine, Does.Contain("Revision Id"));
            
            // But no numbered history columns
            Assert.That(headerLine, Does.Not.Contain("Revision Indicator 1"));
            Assert.That(headerLine, Does.Not.Contain("Revision Id 1"));
        });
    }

    [Test]
    public void ExportDocuments_FullMode_CreatesColumnForEveryRevision()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        var revision3 = new Revision(new DateTime(2024, 3, 1), "Final") { Id = 3 };
        
        var document = new Document("A-101", "Floor Plan", "B", 2) { Id = 1 };
        document.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" }
        };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision1, revision2, revision3 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: true);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        Assert.Multiple(() =>
        {
            Assert.That(headerLine, Does.Contain("Revision Indicator 1"));
            Assert.That(headerLine, Does.Contain("Revision Indicator 2"));
            Assert.That(headerLine, Does.Contain("Revision Indicator 3"));
        });
    }

    [Test]
    public void ExportDocuments_FullMode_UsesRevisionIdAsColumnIdentifier()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 5 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 10 };
        
        var document = new Document("A-101", "Floor Plan", "A", 5) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision1, revision2 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: true);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        Assert.Multiple(() =>
        {
            Assert.That(headerLine, Does.Contain("Revision Indicator 5"));
            Assert.That(headerLine, Does.Contain("Revision Indicator 10"));
        });
    }

    [Test]
    public void ExportDocuments_FullMode_DocumentNotInRevision_WritesBlank()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };
        document.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" }
            // Not in revision 2
        };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision1, revision2 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: true);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        var dataFields = lines[1].Split(',');
        
        // Document should have data for revision 1 but blank for revision 2
        Assert.Multiple(() =>
        {
            Assert.That(lines[1], Does.Contain("A"));
            Assert.That(lines[1], Does.Contain("1")); // Revision 1 ID
            // The fields for revision 2 should be empty (consecutive commas)
        });
    }

    [Test]
    public void ExportDocuments_FullMode_RevisionsOrderedByDate()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        
        // Create revisions in non-chronological order
        var revision3 = new Revision(new DateTime(2024, 3, 1), "Final") { Id = 3 };
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Review") { Id = 2 };
        
        var document = new Document("A-101", "Floor Plan", "C", 3) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision3, revision1, revision2 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: true);

        // Assert
        Assert.That(result, Is.True);

        var headerLine = File.ReadAllLines(filePath)[0];
        var revision1Index = headerLine.IndexOf("Revision Indicator 1");
        var revision2Index = headerLine.IndexOf("Revision Indicator 2");
        var revision3Index = headerLine.IndexOf("Revision Indicator 3");

        // Verify chronological order
        Assert.Multiple(() =>
        {
            Assert.That(revision1Index, Is.LessThan(revision2Index));
            Assert.That(revision2Index, Is.LessThan(revision3Index));
        });
    }

    #endregion

    #region Error Handling Tests

    [Test]
    public void ExportDocuments_WithInvalidPath_ReturnsFalse()
    {
        // Arrange
        var invalidPath = Path.Combine("Z:\\NonExistentDrive\\InvalidPath\\", "documents.csv");
        var documents = new List<Document> { new Document("A-101", "Floor Plan", "A", 1) };
        var revisions = new List<Revision> { new Revision(DateTime.Now, "Test") { Id = 1 } };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(invalidPath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void ExportDocuments_WithNullDocuments_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        List<Document> documents = null;
        var revisions = new List<Revision>();
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void ExportDocuments_WithNullRevisions_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var documents = new List<Document> { new Document("A-101", "Floor Plan", "A", 1) };
        List<Revision> revisions = null;
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void ExportDocuments_WithNullCustomFields_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        var documents = new List<Document> { new Document("A-101", "Floor Plan", "A", 1) };
        var revisions = new List<Revision> { new Revision(DateTime.Now, "Test") { Id = 1 } };
        List<CustomFieldDefinition> customFields = null;

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions);

        // Assert
        Assert.That(result, Is.False);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void ExportDocuments_ComplexScenario_SparseMode_ExportsCorrectly()
    {
        // This test verifies a complex real-world scenario with:
        // - Multiple documents with different revision histories
        // - Multiple custom fields
        // - Sparse mode (only columns for used revisions)
        
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        var revision3 = new Revision(new DateTime(2024, 3, 1), "Final") { Id = 3 };

        var doc1 = new Document("A-101", "Floor Plan", "C", 3) { Id = 1 };
        doc1.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 1, 
            PropertyName = "Discipline", 
            PropertyValue = "Architecture" 
        });
        doc1.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 1, 
            CustomFieldDefinitionId = 2, 
            PropertyName = "Zone", 
            PropertyValue = "Ground Floor" 
        });
        doc1.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" },
            { 2, "B" }
        };

        var doc2 = new Document("S-201", "Structural Layout", "B", 2) { Id = 2 };
        doc2.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 2, 
            CustomFieldDefinitionId = 1, 
            PropertyName = "Discipline", 
            PropertyValue = "Structural" 
        });
        doc2.CustomProperties.Add(new CustomProperty 
        { 
            DocumentId = 2, 
            CustomFieldDefinitionId = 2, 
            PropertyName = "Zone", 
            PropertyValue = "All Levels" 
        });
        doc2.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" }
        };

        var documents = new List<Document> { doc1, doc2 };
        var revisions = new List<Revision> { revision1, revision2, revision3 };
        var customFields = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Zone", true),
            new CustomFieldDefinition("Discipline", true)
        };

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: false);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(3)); // Header + 2 data rows
            
            // Verify header contains all expected columns
            Assert.That(lines[0], Does.Contain("Document Number"));
            Assert.That(lines[0], Does.Contain("Discipline"));
            Assert.That(lines[0], Does.Contain("Zone"));
            Assert.That(lines[0], Does.Contain("Revision Indicator 1"));
            Assert.That(lines[0], Does.Contain("Revision Indicator 2"));
            
            // Verify doc1 data
            Assert.That(lines[1], Does.Contain("A-101"));
            Assert.That(lines[1], Does.Contain("Architecture"));
            Assert.That(lines[1], Does.Contain("Ground Floor"));
            
            // Verify doc2 data
            Assert.That(lines[2], Does.Contain("S-201"));
            Assert.That(lines[2], Does.Contain("Structural"));
            Assert.That(lines[2], Does.Contain("All Levels"));
        });
    }

    [Test]
    public void ExportDocuments_ComplexScenario_FullMode_ExportsCorrectly()
    {
        // This test verifies full revision history mode with:
        // - Multiple documents
        // - Some documents missing from certain revisions
        // - All revision columns present even if document not in revision
        
        // Arrange
        var filePath = Path.Combine(_testDirectory, "documents.csv");
        
        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review") { Id = 2 };
        var revision3 = new Revision(new DateTime(2024, 3, 1), "Final") { Id = 3 };

        var doc1 = new Document("A-101", "Floor Plan", "C", 3) { Id = 1 };
        doc1.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" },
            { 2, "B" }
            // Not in revision 3
        };

        var doc2 = new Document("S-201", "Structural Layout", "C", 3) { Id = 2 };
        doc2.RevisionIndicatorHistory = new Dictionary<int, string>
        {
            { 1, "A" },
            { 3, "C" }
            // Not in revision 2
        };

        var documents = new List<Document> { doc1, doc2 };
        var revisions = new List<Revision> { revision1, revision2, revision3 };
        var customFields = new List<CustomFieldDefinition>();

        // Act
        var result = _service.ExportDocuments(filePath, documents, customFields, revisions, useFullRevisionHistory: true);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        var headerLine = lines[0];
        
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(3)); // Header + 2 data rows
            
            // All three revision columns should be present
            Assert.That(headerLine, Does.Contain("Revision Indicator 1"));
            Assert.That(headerLine, Does.Contain("Revision Indicator 2"));
            Assert.That(headerLine, Does.Contain("Revision Indicator 3"));
            
            // All data rows should have same field count
            var headerFieldCount = headerLine.Split(',').Length;
            Assert.That(lines[1].Split(',').Length, Is.EqualTo(headerFieldCount));
            Assert.That(lines[2].Split(',').Length, Is.EqualTo(headerFieldCount));
        });
    }

    #endregion
}
