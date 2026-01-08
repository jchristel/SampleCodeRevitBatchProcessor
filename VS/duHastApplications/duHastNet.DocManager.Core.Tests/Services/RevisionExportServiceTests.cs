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
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

namespace duHastNet.DocManager.Core.Tests.Services
{

[TestFixture]
public class RevisionExportServiceTests
{
    private RevisionExportService _service;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _service = new RevisionExportService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "RevisionExportServiceTests", Guid.NewGuid().ToString());
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

    #region ExportRevisions Tests

    [Test]
    public void ExportRevisions_WithSingleRevision_CreatesValidCsvFile()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "single_revision.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Initial Release") { Id = 1 };
        revision.DocumentIds.Add(101);
        revision.DocumentIds.Add(102);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);
        Assert.That(File.Exists(filePath), Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines.Length, Is.EqualTo(2));
            Assert.That(lines[0], Is.EqualTo("Id,Revision Date,Description,Document Count"));
            Assert.That(lines[1], Does.Contain("1"));
            Assert.That(lines[1], Does.Contain("2024-03-15"));
            Assert.That(lines[1], Does.Contain("Initial Release"));
            Assert.That(lines[1], Does.Contain("2"));
        });
    }

    [Test]
    public void ExportRevisions_WithMultipleRevisions_CreatesValidCsvFile()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "multiple_revisions.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 15), "First Release") { Id = 1 };
        revision1.DocumentIds.Add(101);

        var revision2 = new Revision(new DateTime(2024, 2, 20), "Second Release") { Id = 2 };
        revision2.DocumentIds.Add(201);
        revision2.DocumentIds.Add(202);

        var revision3 = new Revision(new DateTime(2024, 3, 25), "Third Release") { Id = 3 };
        revision3.DocumentIds.Add(301);
        revision3.DocumentIds.Add(302);
        revision3.DocumentIds.Add(303);

        var revisions = new List<Revision> { revision1, revision2, revision3 };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);
        Assert.That(File.Exists(filePath), Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines.Length, Is.EqualTo(4));
            Assert.That(lines[0], Is.EqualTo("Id,Revision Date,Description,Document Count"));
            Assert.That(lines[1], Does.Contain("1"));
            Assert.That(lines[2], Does.Contain("2"));
            Assert.That(lines[3], Does.Contain("3"));
        });
    }

    [Test]
    public void ExportRevisions_WithEmptyList_CreatesHeaderOnlyFile()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "empty_revisions.csv");
        var revisions = new List<Revision>();

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);
        Assert.That(File.Exists(filePath), Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines.Length, Is.EqualTo(1));
            Assert.That(lines[0], Is.EqualTo("Id,Revision Date,Description,Document Count"));
        });
    }

    [Test]
    public void ExportRevisions_WithRevisionWithoutDocuments_ExportsZeroCount()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "no_documents.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "No Documents") { Id = 1 };
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines.Length, Is.EqualTo(2));
            Assert.That(lines[1], Does.EndWith(",0"));
        });
    }

    [Test]
    public void ExportRevisions_WithNullDescription_ExportsEmptyString()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "null_description.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), null) { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var content = File.ReadAllText(filePath);
        Assert.That(content, Does.Contain("1,2024-03-15,,1"));
    }

    [Test]
    public void ExportRevisions_WithDescriptionContainingCommas_QuotesDescription()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "description_with_commas.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Release for Site A, B, and C") { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        using (var reader = new StreamReader(filePath))
        using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)))
        {
            csv.Read();
            csv.ReadHeader();
            csv.Read();

            var description = csv.GetField<string>("Description");
            Assert.That(description, Is.EqualTo("Release for Site A, B, and C"));
        }
    }

    [Test]
    public void ExportRevisions_WithDescriptionContainingQuotes_EscapesQuotes()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "description_with_quotes.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Release 'Alpha' version") { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        using (var reader = new StreamReader(filePath))
        using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)))
        {
            csv.Read();
            csv.ReadHeader();
            csv.Read();

            var description = csv.GetField<string>("Description");
            Assert.That(description, Is.EqualTo("Release \"Alpha\" version"));
        }
    }

    [Test]
    public void ExportRevisions_WithDescriptionContainingNewlines_EscapesNewlines()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "description_with_newlines.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Release\r\nfor\r\nSite A") { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        using (var reader = new StreamReader(filePath))
        using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)))
        {
            csv.Read();
            csv.ReadHeader();
            csv.Read();

            var description = csv.GetField<string>("Description");
            Assert.That(description, Is.EqualTo("Release\r\nfor\r\nSite A"));
        }
    }

    [Test]
    public void ExportRevisions_WithDifferentDateFormats_UsesConsistentFormat()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "date_formats.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 5), "January") { Id = 1 };
        var revision2 = new Revision(new DateTime(2024, 12, 25), "December") { Id = 2 };
        var revisions = new List<Revision> { revision1, revision2 };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines[1], Does.Contain("2024-01-05"));
            Assert.That(lines[2], Does.Contain("2024-12-25"));
        });
    }

    [Test]
    public void ExportRevisions_WithLargeDocumentCount_ExportsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "large_count.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Large Release") { Id = 1 };
        for (int i = 1; i <= 1000; i++)
        {
            revision.DocumentIds.Add(i);
        }
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.That(lines[1], Does.Contain("1000"));
    }

    [Test]
    public void ExportRevisions_WithInvalidFilePath_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine("Z:\\NonExistentDrive", "invalid.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Test") { Id = 1 };
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void ExportRevisions_WithReadOnlyDirectory_ReturnsFalse()
    {
        // Arrange
        var readOnlyDir = Path.Combine(_testDirectory, "readonly");
        Directory.CreateDirectory(readOnlyDir);
        var dirInfo = new DirectoryInfo(readOnlyDir);
        dirInfo.Attributes = FileAttributes.ReadOnly;

        var filePath = Path.Combine(readOnlyDir, "test.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Test") { Id = 1 };
        var revisions = new List<Revision> { revision };

        try
        {
            // Act
            var result = _service.ExportRevisions(filePath, revisions);

            // Assert
            Assert.That(result, Is.False);
        }
        finally
        {
            dirInfo.Attributes = FileAttributes.Normal;
        }
    }

    [Test]
    public void ExportRevisions_WithExistingFile_OverwritesFile()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "overwrite.csv");
        File.WriteAllText(filePath, "Old content");

        var revision = new Revision(new DateTime(2024, 3, 15), "New Release") { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var content = File.ReadAllText(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(content, Does.Not.Contain("Old content"));
            Assert.That(content, Does.Contain("Id,Revision Date,Description,Document Count"));
            Assert.That(content, Does.Contain("New Release"));
        });
    }

    [Test]
    public void ExportRevisions_WithSpecialCharactersInDescription_ExportsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "special_chars.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), "Release #1 - 100% complete & verified!") { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        using (var reader = new StreamReader(filePath))
        using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)))
        {
            csv.Read();
            csv.ReadHeader();
            csv.Read();

            var description = csv.GetField<string>("Description");
            Assert.That(description, Is.EqualTo("Release #1 - 100% complete & verified!"));
        }
    }

    [Test]
    public void ExportRevisions_WithManyRevisions_ExportsAllRows()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "many_revisions.csv");
        var revisions = new List<Revision>();
        for (int i = 1; i <= 100; i++)
        {
            var revision = new Revision(new DateTime(2024, 1, 1).AddDays(i), $"Release {i}") { Id = i };
            revision.DocumentIds.Add(i * 10);
            revisions.Add(revision);
        }

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines.Length, Is.EqualTo(101));
            Assert.That(lines[0], Is.EqualTo("Id,Revision Date,Description,Document Count"));
            Assert.That(lines[1], Does.Contain("Release 1"));
            Assert.That(lines[100], Does.Contain("Release 100"));
        });
    }

    [Test]
    public void ExportRevisions_VerifyHeaderFormat_MatchesExpectedColumns()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "header_format.csv");
        var revisions = new List<Revision>();

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        using (var reader = new StreamReader(filePath))
        using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)))
        {
            csv.Read();
            csv.ReadHeader();

            Assert.Multiple(() =>
            {
                Assert.That(csv.HeaderRecord, Has.Length.EqualTo(4));
                Assert.That(csv.HeaderRecord[0], Is.EqualTo("Id"));
                Assert.That(csv.HeaderRecord[1], Is.EqualTo("Revision Date"));
                Assert.That(csv.HeaderRecord[2], Is.EqualTo("Description"));
                Assert.That(csv.HeaderRecord[3], Is.EqualTo("Document Count"));
            });
        }
    }

    [Test]
    public void ExportRevisions_WithLongDescription_ExportsCompletely()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "long_description.csv");
        var longDescription = new string('A', 1000);
        var revision = new Revision(new DateTime(2024, 3, 15), longDescription) { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        using (var reader = new StreamReader(filePath))
        using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)))
        {
            csv.Read();
            csv.ReadHeader();
            csv.Read();

            var description = csv.GetField<string>("Description");
            Assert.Multiple(() =>
            {
                Assert.That(description, Has.Length.EqualTo(1000));
                Assert.That(description, Is.EqualTo(longDescription));
            });
        }
    }

    [Test]
    public void ExportRevisions_WithEmptyDescription_ExportsEmptyString()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "empty_description.csv");
        var revision = new Revision(new DateTime(2024, 3, 15), string.Empty) { Id = 1 };
        revision.DocumentIds.Add(101);
        var revisions = new List<Revision> { revision };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var content = File.ReadAllText(filePath);
        Assert.That(content, Does.Contain("1,2024-03-15,,1"));
    }

    [Test]
    public void ExportRevisions_WithMixedRevisionStates_ExportsAll()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "mixed_states.csv");
        var revision1 = new Revision(new DateTime(2024, 1, 15), "With Documents") { Id = 1 };
        revision1.DocumentIds.Add(101);
        revision1.DocumentIds.Add(102);

        var revision2 = new Revision(new DateTime(2024, 2, 15), null) { Id = 2 };

        var revision3 = new Revision(new DateTime(2024, 3, 15), string.Empty) { Id = 3 };
        revision3.DocumentIds.Add(301);

        var revisions = new List<Revision> { revision1, revision2, revision3 };

        // Act
        var result = _service.ExportRevisions(filePath, revisions);

        // Assert
        Assert.That(result, Is.True);

        var lines = File.ReadAllLines(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines.Length, Is.EqualTo(4));
            Assert.That(lines[1], Does.Contain("With Documents"));
            Assert.That(lines[1], Does.Contain(",2"));
            Assert.That(lines[2], Does.Contain(",0"));
            Assert.That(lines[3], Does.Contain(",1"));
        });
    }

    #endregion
}
}
