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

using NUnit.Framework;
using Moq;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Interfaces;

namespace duHastNet.DocManager.Core.Tests.Services
{

[TestFixture]
public class RevisionImportServiceTests
{
    private Mock<IUnitOfWork> _mockUnitOfWork;
    private Mock<IRevisionRepository> _mockRevisionRepository;
    private RevisionImportService _service;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _mockUnitOfWork = new Mock<IUnitOfWork>();
        _mockRevisionRepository = new Mock<IRevisionRepository>();
        _mockUnitOfWork.Setup(x => x.Revisions).Returns(_mockRevisionRepository.Object);

        _service = new RevisionImportService(_mockUnitOfWork.Object);
        _testDirectory = Path.Combine(Path.GetTempPath(), "RevisionImportServiceTests", Guid.NewGuid().ToString());
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

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidUnitOfWork_InitializesSuccessfully()
    {
        // Arrange & Act
        var service = new RevisionImportService(_mockUnitOfWork.Object);

        // Assert
        Assert.That(service, Is.Not.Null);
    }

    [Test]
    public void Constructor_WithNullUnitOfWork_ThrowsArgumentNullException()
    {
        // Arrange, Act & Assert
        Assert.Throws<ArgumentNullException>(() => new RevisionImportService(null));
    }

    #endregion

    #region ImportRevisionsAsync - New Revisions Tests

    [Test]
    public async Task ImportRevisionsAsync_WithSingleNewRevision_CreatesSuccessfully()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "new_revision.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,Initial Release,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(1));
            Assert.That(result.DocumentsCreated, Is.EqualTo(1));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(0));
            Assert.That(result.HasErrors, Is.False);
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(
            It.Is<Revision>(r => r.Description == "Initial Release")), Times.Once);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithMultipleNewRevisions_CreatesAll()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "multiple_new.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-01-15,First Release,0\r\n" +
                        "new,2024-02-20,Second Release,0\r\n" +
                        "new,2024-03-25,Third Release,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(3));
            Assert.That(result.DocumentsCreated, Is.EqualTo(3));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(0));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(It.IsAny<Revision>()), Times.Exactly(3));
    }

    [Test]
    public async Task ImportRevisionsAsync_WithNewRevisionInvalidDate_ReportsError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "invalid_date.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,not-a-date,Invalid Date,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(1));
            Assert.That(result.DocumentsCreated, Is.EqualTo(0));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Row 2"));
            Assert.That(result.Errors[0], Does.Contain("Invalid Revision Date"));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(It.IsAny<Revision>()), Times.Never);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithConflictingRevision_ReportsError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "conflicting.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,Duplicate Release,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 15), "Duplicate Release");
        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision> { existingRevision });

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsCreated, Is.EqualTo(0));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("already exists"));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(It.IsAny<Revision>()), Times.Never);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithNewRevisionCaseInsensitive_CreatesSuccessfully()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "case_insensitive.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "NEW,2024-03-15,Release,0\r\n" +
                        "New,2024-03-16,Release,0\r\n" +
                        "NeW,2024-03-17,Release,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsCreated, Is.EqualTo(3));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(It.IsAny<Revision>()), Times.Exactly(3));
    }

    #endregion

    #region ImportRevisionsAsync - Update Existing Revisions Tests

    [Test]
    public async Task ImportRevisionsAsync_WithExistingRevisionUpdate_UpdatesSuccessfully()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "update_revision.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "1,2024-03-15,Updated Description,5\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 15), "Original Description") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        _mockRevisionRepository.Setup(x => x.UpdateAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(1));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(0));
            Assert.That(existingRevision.Description, Is.EqualTo("Updated Description"));
        });

        _mockRevisionRepository.Verify(x => x.UpdateAsync(existingRevision), Times.Once);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithInvalidRevisionId_ReportsError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "invalid_id.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "abc,2024-03-15,Description,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Invalid revision Id"));
            Assert.That(result.Errors[0], Does.Contain("abc"));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithNonExistentRevisionId_ReportsError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "nonexistent_id.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "999,2024-03-15,Description,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 999)))
            .ReturnsAsync((Revision)null);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Revision with Id 999 not found"));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithRevisionDateUpdate_UpdatesDate()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "update_date.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "1,2024-04-20,Description,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 15), "Description") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        _mockRevisionRepository.Setup(x => x.UpdateAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(existingRevision.RevisionDate.Date, Is.EqualTo(new DateTime(2024, 4, 20).Date));
        });

        _mockRevisionRepository.Verify(x => x.UpdateAsync(existingRevision), Times.Once);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithNoChanges_DoesNotUpdate()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "no_changes.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "1,2024-03-15,Same Description,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 15), "Same Description") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        _mockRevisionRepository.Verify(x => x.UpdateAsync(It.IsAny<Revision>()), Times.Never);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithDescriptionClearedToEmpty_UpdatesToNull()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "clear_description.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "1,2024-03-15,,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 15), "Original Description") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        _mockRevisionRepository.Setup(x => x.UpdateAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(existingRevision.Description, Is.Null);
        });

        _mockRevisionRepository.Verify(x => x.UpdateAsync(existingRevision), Times.Once);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithInvalidDateOnUpdate_ReportsError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "invalid_update_date.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "1,invalid-date,Description,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 15), "Description") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Invalid Revision Date"));
        });

        _mockRevisionRepository.Verify(x => x.UpdateAsync(It.IsAny<Revision>()), Times.Never);
    }

    #endregion

    #region ImportRevisionsAsync - Mixed Operations Tests

    [Test]
    public async Task ImportRevisionsAsync_WithMixedNewAndUpdates_ProcessesBoth()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "mixed_operations.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-01-15,New Release,0\r\n" +
                        "1,2024-02-20,Updated Release,0\r\n" +
                        "new,2024-03-25,Another New,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 2, 20), "Old Description") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        _mockRevisionRepository.Setup(x => x.UpdateAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(3));
            Assert.That(result.DocumentsCreated, Is.EqualTo(2));
            Assert.That(result.Message, Does.Contain("2 revisions created"));
            Assert.That(result.Message, Does.Contain("1 updated"));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(It.IsAny<Revision>()), Times.Exactly(2));
        _mockRevisionRepository.Verify(x => x.UpdateAsync(existingRevision), Times.Once);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithPartialErrors_ProcessesValid()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "partial_errors.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-01-15,Valid New,0\r\n" +
                        "new,invalid-date,Invalid Date,0\r\n" +
                        "999,2024-03-15,Nonexistent ID,0\r\n" +
                        "1,2024-02-20,Valid Update,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 2, 20), "Old") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 999)))
            .ReturnsAsync((Revision)null);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        _mockRevisionRepository.Setup(x => x.UpdateAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(4));
            Assert.That(result.DocumentsCreated, Is.EqualTo(1));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(2));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors, Has.Count.EqualTo(2));
        });
    }

    #endregion

    #region ImportRevisionsAsync - Empty and Edge Cases Tests

    [Test]
    public async Task ImportRevisionsAsync_WithEmptyFile_ReturnsSuccess()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "empty.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(0));
            Assert.That(result.DocumentsCreated, Is.EqualTo(0));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(0));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithNonExistentFile_ReturnsFailure()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "nonexistent.csv");

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Import failed"));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithMalformedCsv_ReturnsFailure()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "malformed.csv");
        var csvContent = "This is not a valid CSV file";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithSpecialCharactersInDescription_HandlesCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "special_chars.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,\"Release with commas, quotes \"\"quoted\"\", and newlines\",0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.That(result.IsImportSuccessful, Is.True);

        _mockRevisionRepository.Verify(x => x.InsertAsync(
            It.Is<Revision>(r => r.Description.Contains("commas") && r.Description.Contains("quoted"))), 
            Times.Once);
    }

    [Test]
    public async Task ImportRevisionsAsync_WithManyRevisions_ProcessesAll()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "many_revisions.csv");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("Id,Revision Date,Description,Document Count");
        for (int i = 1; i <= 100; i++)
        {
            sb.AppendLine($"new,2024-01-{i:D2},Release {i},0");
        }
        await File.WriteAllTextAsync(filePath, sb.ToString());

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(100));
            Assert.That(result.DocumentsCreated, Is.EqualTo(100));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(It.IsAny<Revision>()), Times.Exactly(100));
    }

    [Test]
    public async Task ImportRevisionsAsync_WithDifferentDateFormats_ParsesCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "date_formats.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,ISO Format,0\r\n" +
                        "new,3/15/2024,US Format,0\r\n" +
                        "new,15-03-2024,EU Format,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.DocumentsProcessed, Is.EqualTo(3));
            Assert.That(result.DocumentsCreated, Is.GreaterThan(0));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithRowException_CapturesError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "exception_row.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,Valid,0\r\n" +
                        "1,2024-03-16,Throws,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ThrowsAsync(new Exception("Database error"));

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.DocumentsProcessed, Is.EqualTo(2));
            Assert.That(result.DocumentsCreated, Is.EqualTo(1));
            Assert.That(result.DocumentsSkipped, Is.EqualTo(1));
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Row 3"));
            Assert.That(result.Errors[0], Does.Contain("Database error"));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithEmptyDescription_AcceptsEmptyString()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "empty_description.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.DocumentsCreated, Is.EqualTo(1));
        });

        _mockRevisionRepository.Verify(x => x.InsertAsync(
            It.Is<Revision>(r => r.Description == string.Empty)), Times.Once);
    }

    #endregion

    #region ImportRevisionsAsync - Result Message Tests

    [Test]
    public async Task ImportRevisionsAsync_WithSuccessfulImport_ContainsSuccessMessage()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "success_message.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,2024-03-15,New,0\r\n" +
                        "1,2024-03-16,Update,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        var existingRevision = new Revision(new DateTime(2024, 3, 16), "Old") { Id = 1 };
        _mockRevisionRepository.Setup(x => x.GetByIdAsync(It.Is<int>(id => id == 1)))
            .ReturnsAsync(existingRevision);

        _mockRevisionRepository.Setup(x => x.GetRevisionsByDateAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(new List<Revision>());

        _mockRevisionRepository.Setup(x => x.InsertAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        _mockRevisionRepository.Setup(x => x.UpdateAsync(It.IsAny<Revision>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.True);
            Assert.That(result.Message, Does.Contain("Import completed"));
            Assert.That(result.Message, Does.Contain("1 revisions created"));
            Assert.That(result.Message, Does.Contain("1 updated"));
        });
    }

    [Test]
    public async Task ImportRevisionsAsync_WithErrors_ContainsErrorMessage()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "error_message.csv");
        var csvContent = "Id,Revision Date,Description,Document Count\r\n" +
                        "new,invalid-date,Bad Date,0\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ImportRevisionsAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsImportSuccessful, Is.False);
            Assert.That(result.Message, Does.Contain("Import completed with errors"));
            Assert.That(result.Message, Does.Contain("1 skipped"));
        });
    }

    #endregion
}
}
