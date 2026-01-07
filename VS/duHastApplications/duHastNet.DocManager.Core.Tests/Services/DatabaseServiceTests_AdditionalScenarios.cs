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
/// Additional DatabaseService tests covering edge cases and integration scenarios
/// This complements the existing comprehensive test suites:
/// - DatabaseServiceTests_Initialization
/// - DatabaseServiceTests_ConnectionManagement
/// - DatabaseServiceTests_TablesAndIndexes
/// - DatabaseServiceTests_SqlOperations
/// - DatabaseServiceTests_MaintenanceOperations
/// - DatabaseServiceTests_Dispose
/// </summary>
[TestFixture]
public class DatabaseServiceTests_AdditionalScenarios
{
    private DatabaseService _databaseService;
    private string _testDatabasePath;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _databaseService = new DatabaseService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "DatabaseServiceTests_Additional", Guid.NewGuid().ToString());
        _testDatabasePath = Path.Combine(_testDirectory, "test.db");
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_databaseService != null)
        {
            await _databaseService.CloseAsync();
            _databaseService.Dispose();
        }

        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region CheckDatabaseIntegrityAsync Edge Cases

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithCorruptedDatabase_InitializationThrows()
    {
        // This test verifies that attempting to initialize a corrupted database file
        // throws an exception during the CreateTablesAsync call within InitializeAsync
        
        // Arrange
        Directory.CreateDirectory(_testDirectory);
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CloseAsync();

        // Corrupt the database by writing invalid data
        await File.WriteAllTextAsync(_testDatabasePath, "This is not a valid SQLite database");

        // Act & Assert
        // InitializeAsync should throw because CreateTablesAsync cannot execute on corrupted file
        var newService = new DatabaseService();
        
        try
        {
            Assert.ThrowsAsync<SQLite.SQLiteException>(
                async () => await newService.InitializeAsync(_testDatabasePath));
        }
        finally
        {
            newService.Dispose();
        }
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithEmptyDatabase_ReturnsTrue()
    {
        // Arrange
        Directory.CreateDirectory(_testDirectory);
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Don't create any tables - just an empty database

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_AfterDataOperations_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Insert test data
        var revision = new Revision(DateTime.Now, "Test");
        await _databaseService.Connection.InsertAsync(revision);

        var document = new Document("A-101", "Test Document", "A", revision.Id);
        await _databaseService.Connection.InsertAsync(document);

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    #endregion

    #region InitializeAsync with Whitespace Path

    [Test]
    public void InitializeAsync_WithWhitespacePath_ThrowsArgumentException()
    {
        // Arrange
        var whitespacePath = "   ";

        // Act & Assert
        var exception = Assert.ThrowsAsync<ArgumentException>(
            async () => await _databaseService.InitializeAsync(whitespacePath));

        Assert.That(exception.ParamName, Is.EqualTo("databasePath"));
        Assert.That(exception.Message, Does.Contain("whitespace"));
    }

    [Test]
    public void InitializeAsync_WithTabsPath_ThrowsArgumentException()
    {
        // Arrange
        var whitespacePath = "\t\t\t";

        // Act & Assert
        var exception = Assert.ThrowsAsync<ArgumentException>(
            async () => await _databaseService.InitializeAsync(whitespacePath));

        Assert.That(exception.ParamName, Is.EqualTo("databasePath"));
    }

    #endregion

    #region Database Path Edge Cases

    [Test]
    public async Task InitializeAsync_WithRelativePath_WorksCorrectly()
    {
        // Arrange
        var relativePath = Path.Combine(".", "temp", "test.db");
        var fullPath = Path.GetFullPath(relativePath);
        var directory = Path.GetDirectoryName(fullPath);

        try
        {
            // Act
            await _databaseService.InitializeAsync(relativePath);

            // Assert
            Assert.Multiple(() =>
            {
                Assert.That(_databaseService.IsInitialized, Is.True);
                Assert.That(File.Exists(fullPath), Is.True);
            });
        }
        finally
        {
            await _databaseService.CloseAsync();
            if (Directory.Exists(directory))
            {
                Directory.Delete(directory, true);
            }
        }
    }

    [Test]
    public async Task InitializeAsync_WithSpecialCharactersInPath_WorksCorrectly()
    {
        // Arrange
        var specialPath = Path.Combine(_testDirectory, "test-file_name (1).db");
        Directory.CreateDirectory(_testDirectory);

        // Act
        await _databaseService.InitializeAsync(specialPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.True);
            Assert.That(_databaseService.DatabasePath, Is.EqualTo(specialPath));
            Assert.That(File.Exists(specialPath), Is.True);
        });
    }

    #endregion

    #region CreateTablesAsync Integration Tests

    [Test]
    public async Task CreateTablesAsync_WithUnicodeData_StoresAndRetrievesCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        var chineseText = "中文测试";
        var arabicText = "اختبار عربي";
        var emojiText = "Test 🚀 Emoji 📝";

        var revision = new Revision(DateTime.Now, chineseText);
        await _databaseService.Connection.InsertAsync(revision);

        var document = new Document("A-101", arabicText, emojiText, revision.Id);
        await _databaseService.Connection.InsertAsync(document);

        // Act
        var retrievedRevision = await _databaseService.Connection.FindAsync<Revision>(revision.Id);
        var retrievedDocument = await _databaseService.Connection.FindAsync<Document>(document.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(retrievedRevision.Description, Is.EqualTo(chineseText));
            Assert.That(retrievedDocument.Name, Is.EqualTo(arabicText));
            Assert.That(retrievedDocument.Revision, Is.EqualTo(emojiText));
        });
    }

    [Test]
    public async Task CreateTablesAsync_WithLargeTextData_StoresCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        var largeDescription = new string('A', 10000); // 10,000 characters
        var revision = new Revision(DateTime.Now, largeDescription);

        // Act
        await _databaseService.Connection.InsertAsync(revision);
        var retrieved = await _databaseService.Connection.FindAsync<Revision>(revision.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(retrieved, Is.Not.Null);
            Assert.That(retrieved.Description, Is.EqualTo(largeDescription));
            Assert.That(retrieved.Description.Length, Is.EqualTo(10000));
        });
    }

    [Test]
    public async Task CreateTablesAsync_CustomFieldDefinitions_EnforcesUniqueConstraint()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        var field1 = new CustomFieldDefinition("ProjectPhase", true);
        await _databaseService.Connection.InsertAsync(field1);

        var field2 = new CustomFieldDefinition("ProjectPhase", false);

        // Act & Assert
        Assert.ThrowsAsync<SQLite.SQLiteException>(
            async () => await _databaseService.Connection.InsertAsync(field2));
    }

    #endregion

    #region Connection Property Edge Cases

    [Test]
    public async Task Connection_AfterReinitialization_CanAccessOldData()
    {
        // This test verifies that data persists across reinitializations
        // and the connection can access previously stored data
        
        // Arrange - First initialization
        await _databaseService.InitializeAsync(_testDatabasePath);
        var revision = new Revision(DateTime.Now, "Original Data");
        await _databaseService.Connection.InsertAsync(revision);
        var originalId = revision.Id;

        // Act - Reinitialize (closes old connection, opens new one)
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Assert - Data should still be accessible
        var retrieved = await _databaseService.Connection.FindAsync<Revision>(originalId);
        Assert.Multiple(() =>
        {
            Assert.That(retrieved, Is.Not.Null);
            Assert.That(retrieved.Description, Is.EqualTo("Original Data"));
        });
    }

    [Test]
    public async Task Connection_MultipleTablesInTransaction_MaintainsConsistency()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        var revision = new Revision(DateTime.Now, "Test Revision");
        var document = new Document("A-101", "Test Doc", "A", 1);

        // Act - Use transaction for multiple inserts
        await _databaseService.Connection.RunInTransactionAsync((connection) =>
        {
            connection.Insert(revision);
            document.RevisionId = revision.Id;
            connection.Insert(document);
        });

        // Assert
        var retrievedRevision = await _databaseService.Connection.FindAsync<Revision>(revision.Id);
        var retrievedDocument = await _databaseService.Connection.FindAsync<Document>(document.Id);

        Assert.Multiple(() =>
        {
            Assert.That(retrievedRevision, Is.Not.Null);
            Assert.That(retrievedDocument, Is.Not.Null);
            Assert.That(retrievedDocument.RevisionId, Is.EqualTo(revision.Id));
        });
    }

    #endregion

    #region DatabasePath Property Tests

    [Test]
    public void DatabasePath_BeforeInitialization_IsNull()
    {
        // Arrange & Act
        var path = _databaseService.DatabasePath;

        // Assert
        Assert.That(path, Is.Null);
    }

    [Test]
    public async Task DatabasePath_AfterInitialization_ReturnsCorrectPath()
    {
        // Arrange & Act
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Assert
        Assert.That(_databaseService.DatabasePath, Is.EqualTo(_testDatabasePath));
    }

    [Test]
    public async Task DatabasePath_AfterClose_IsNull()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        await _databaseService.CloseAsync();

        // Assert
        Assert.That(_databaseService.DatabasePath, Is.Null);
    }

    [Test]
    public async Task DatabasePath_AfterReinitialization_ReturnsNewPath()
    {
        // Arrange
        var firstPath = Path.Combine(_testDirectory, "first.db");
        var secondPath = Path.Combine(_testDirectory, "second.db");
        Directory.CreateDirectory(_testDirectory);

        await _databaseService.InitializeAsync(firstPath);

        // Act
        await _databaseService.InitializeAsync(secondPath);

        // Assert
        Assert.That(_databaseService.DatabasePath, Is.EqualTo(secondPath));
    }

    #endregion

    #region IsInitialized Property Tests

    [Test]
    public void IsInitialized_BeforeInitialization_IsFalse()
    {
        // Arrange & Act
        var isInitialized = _databaseService.IsInitialized;

        // Assert
        Assert.That(isInitialized, Is.False);
    }

    [Test]
    public async Task IsInitialized_AfterInitialization_IsTrue()
    {
        // Arrange & Act
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.True);
    }

    [Test]
    public async Task IsInitialized_AfterClose_IsFalse()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        await _databaseService.CloseAsync();

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    [Test]
    public async Task IsInitialized_AfterDispose_IsFalse()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        _databaseService.Dispose();

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    #endregion

    #region Full Lifecycle Integration Tests

    [Test]
    public async Task FullLifecycle_InitializeCreateTablesOperateCloseReinitialize_WorksCorrectly()
    {
        // This test verifies a complete realistic usage scenario
        
        // Phase 1: Initialize and create data
        await _databaseService.InitializeAsync(_testDatabasePath);

        var revision1 = new Revision(DateTime.Now, "Phase 1");
        await _databaseService.Connection.InsertAsync(revision1);

        var document1 = new Document("A-101", "Document 1", "A", revision1.Id);
        await _databaseService.Connection.InsertAsync(document1);

        var customField = new CustomFieldDefinition("ProjectPhase", true);
        await _databaseService.Connection.InsertAsync(customField);

        // Phase 2: Close
        await _databaseService.CloseAsync();
        Assert.That(_databaseService.IsInitialized, Is.False);

        // Phase 3: Reinitialize and verify data
        await _databaseService.InitializeAsync(_testDatabasePath);

        var revisions = await _databaseService.Connection.Table<Revision>().ToListAsync();
        var documents = await _databaseService.Connection.Table<Document>().ToListAsync();
        var customFields = await _databaseService.Connection.Table<CustomFieldDefinition>().ToListAsync();

        Assert.Multiple(() =>
        {
            Assert.That(revisions, Has.Count.EqualTo(1));
            Assert.That(documents, Has.Count.EqualTo(1));
            Assert.That(customFields, Has.Count.EqualTo(1));
            Assert.That(revisions[0].Description, Is.EqualTo("Phase 1"));
            Assert.That(documents[0].Number, Is.EqualTo("A-101"));
            Assert.That(customFields[0].PropertyName, Is.EqualTo("ProjectPhase"));
        });

        // Phase 4: Add more data
        var revision2 = new Revision(DateTime.Now, "Phase 2");
        await _databaseService.Connection.InsertAsync(revision2);

        // Phase 5: Final verification
        var finalRevisions = await _databaseService.Connection.Table<Revision>().ToListAsync();
        Assert.That(finalRevisions, Has.Count.EqualTo(2));
    }

    [Test]
    public async Task FullLifecycle_WithMultipleDocumentsAndRevisions_MaintainsRelationships()
    {
        // This test verifies complex relationships work correctly across the full lifecycle
        
        // Arrange & Act - Create complex data structure
        await _databaseService.InitializeAsync(_testDatabasePath);

        var revision1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue");
        var revision2 = new Revision(new DateTime(2024, 2, 1), "Client Review");
        await _databaseService.Connection.InsertAsync(revision1);
        await _databaseService.Connection.InsertAsync(revision2);

        var doc1 = new Document("A-101", "Floor Plan", "A", revision1.Id);
        var doc2 = new Document("A-102", "Ceiling Plan", "A", revision1.Id);
        var doc3 = new Document("A-101", "Floor Plan", "B", revision2.Id); // Same doc, new revision

        await _databaseService.Connection.InsertAsync(doc1);
        await _databaseService.Connection.InsertAsync(doc2);
        await _databaseService.Connection.InsertAsync(doc3);

        // Close and reopen
        await _databaseService.CloseAsync();
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Assert - Verify relationships
        var allDocuments = await _databaseService.Connection.Table<Document>().ToListAsync();
        var revision1Docs = await _databaseService.Connection.Table<Document>()
            .Where(d => d.RevisionId == revision1.Id)
            .ToListAsync();
        var revision2Docs = await _databaseService.Connection.Table<Document>()
            .Where(d => d.RevisionId == revision2.Id)
            .ToListAsync();

        Assert.Multiple(() =>
        {
            Assert.That(allDocuments, Has.Count.EqualTo(3));
            Assert.That(revision1Docs, Has.Count.EqualTo(2));
            Assert.That(revision2Docs, Has.Count.EqualTo(1));
            Assert.That(revision2Docs[0].Number, Is.EqualTo("A-101"));
            Assert.That(revision2Docs[0].Revision, Is.EqualTo("B"));
        });
    }

    #endregion
}
