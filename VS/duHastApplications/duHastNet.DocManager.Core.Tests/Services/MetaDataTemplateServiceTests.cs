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
using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Tests.Services
{

[TestFixture]
public class MetaDataTemplateServiceTests
{
    private MetaDataTemplateService _service;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _service = new MetaDataTemplateService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "MetaDataTemplateServiceTests", Guid.NewGuid().ToString());
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

    #region ReadColumnHeadersAsync Tests

    [Test]
    public async Task ReadColumnHeadersAsync_WithValidCsvFile_ReturnsSuccessWithHeaders()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "test.csv");
        var csvContent = "DocumentNumber,DocumentName,Revision,Status\r\n" +
                        "A-101,Floor Plan,3,Current\r\n" +
                        "A-102,Site Plan,2,Superseded\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.Success, Is.True);
            Assert.That(result.FilePath, Is.EqualTo(filePath));
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(4));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
            Assert.That(result.ColumnHeaders[1], Is.EqualTo("DocumentName"));
            Assert.That(result.ColumnHeaders[2], Is.EqualTo("Revision"));
            Assert.That(result.ColumnHeaders[3], Is.EqualTo("Status"));
            Assert.That(result.HasErrors, Is.False);
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithNullFilePath_ReturnsFailure()
    {
        // Arrange
        string filePath = null;

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("cannot be null or empty"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithEmptyFilePath_ReturnsFailure()
    {
        // Arrange
        var filePath = string.Empty;

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("cannot be null or empty"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithWhitespaceFilePath_ReturnsFailure()
    {
        // Arrange
        var filePath = "   ";

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("cannot be null or empty"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithNonExistentFile_ReturnsFailure()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "nonexistent.csv");

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Invalid file"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithNonCsvExtension_ReturnsFailure()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "test.txt");
        await File.WriteAllTextAsync(filePath, "Column1,Column2\r\nValue1,Value2\r\n");

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Invalid file"));
            Assert.That(result.Errors[0], Does.Contain("CSV file"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithEmptyCsvFile_ReturnsFailure()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "empty.csv");
        await File.WriteAllTextAsync(filePath, string.Empty);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("CSV parsing error"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithHeadersContainingWhitespace_TrimsHeaders()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "whitespace.csv");
        var csvContent = "  DocumentNumber  ,  DocumentName  ,  Revision  \r\n" +
                        "A-101,Floor Plan,3\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(3));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
            Assert.That(result.ColumnHeaders[1], Is.EqualTo("DocumentName"));
            Assert.That(result.ColumnHeaders[2], Is.EqualTo("Revision"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithOnlyWhitespaceHeaders_ReturnsFailure()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "whitespace_only.csv");
        var csvContent = "  ,  ,  \r\n" +
                        "A-101,Floor Plan,3\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.False);
            Assert.That(result.Success, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("empty or whitespace"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithDuplicateHeaders_ReturnsSuccessWithWarning()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "duplicates.csv");
        var csvContent = "DocumentNumber,DocumentName,DocumentNumber,Status\r\n" +
                        "A-101,Floor Plan,3,Current\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.Success, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(4));
            Assert.That(result.HasWarnings, Is.True);
            Assert.That(result.Warnings[0], Does.Contain("duplicate"));
            Assert.That(result.Warnings[0], Does.Contain("DocumentNumber"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithSemicolonDelimiter_ReadsHeaders()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "semicolon.csv");
        var csvContent = "DocumentNumber;DocumentName;Revision\r\n" +
                        "A-101;Floor Plan;3\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(3));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
            Assert.That(result.ColumnHeaders[1], Is.EqualTo("DocumentName"));
            Assert.That(result.ColumnHeaders[2], Is.EqualTo("Revision"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithTabDelimiter_ReadsHeaders()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "tab.csv");
        var csvContent = "DocumentNumber\tDocumentName\tRevision\r\n" +
                        "A-101\tFloor Plan\t3\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(3));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
            Assert.That(result.ColumnHeaders[1], Is.EqualTo("DocumentName"));
            Assert.That(result.ColumnHeaders[2], Is.EqualTo("Revision"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithComments_IgnoresCommentLines()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "comments.csv");
        var csvContent = "# This is a comment\r\n" +
                        "DocumentNumber,DocumentName,Revision\r\n" +
                        "A-101,Floor Plan,3\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(3));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithSingleColumn_ReturnsSuccessWithOneHeader()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "single_column.csv");
        var csvContent = "DocumentNumber\r\n" +
                        "A-101\r\n" +
                        "A-102\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(1));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithManyColumns_ReturnsAllHeaders()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "many_columns.csv");
        var headers = new List<string>();
        for (int i = 1; i <= 20; i++)
        {
            headers.Add($"Column{i}");
        }
        var csvContent = string.Join(",", headers) + "\r\n" +
                        string.Join(",", Enumerable.Repeat("Value", 20)) + "\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(20));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("Column1"));
            Assert.That(result.ColumnHeaders[19], Is.EqualTo("Column20"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithSpecialCharactersInHeaders_PreservesCharacters()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "special_chars.csv");
        var csvContent = "Document#,Name & Title,Revision (Rev),Status/Type\r\n" +
                        "A-101,Floor Plan,3,Current\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(4));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("Document#"));
            Assert.That(result.ColumnHeaders[1], Is.EqualTo("Name & Title"));
            Assert.That(result.ColumnHeaders[2], Is.EqualTo("Revision (Rev)"));
            Assert.That(result.ColumnHeaders[3], Is.EqualTo("Status/Type"));
        });
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithLockedFile_ReturnsFailureWithIoError()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "locked.csv");
        await File.WriteAllTextAsync(filePath, "Column1,Column2\r\n");

        // Act & Assert
        using (var stream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.None))
        {
            var result = await _service.ReadColumnHeadersAsync(filePath);

            Assert.Multiple(() =>
            {
                Assert.That(result.IsReadSuccessful, Is.False);
                Assert.That(result.Success, Is.False);
                Assert.That(result.HasErrors, Is.True);
                Assert.That(result.Errors[0], Does.Contain("File access error"));
            });
        }
    }

    [Test]
    public async Task ReadColumnHeadersAsync_WithMixedEmptyAndValidHeaders_FiltersEmptyHeaders()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "mixed_empty.csv");
        var csvContent = "DocumentNumber,,DocumentName,,Revision\r\n" +
                        "A-101,X,Floor Plan,Y,3\r\n";
        await File.WriteAllTextAsync(filePath, csvContent);

        // Act
        var result = await _service.ReadColumnHeadersAsync(filePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsReadSuccessful, Is.True);
            Assert.That(result.ColumnHeaders, Has.Count.EqualTo(3));
            Assert.That(result.ColumnHeaders[0], Is.EqualTo("DocumentNumber"));
            Assert.That(result.ColumnHeaders[1], Is.EqualTo("DocumentName"));
            Assert.That(result.ColumnHeaders[2], Is.EqualTo("Revision"));
        });
    }

    #endregion

    #region IsValidCsvFile Tests

    [Test]
    public void IsValidCsvFile_WithValidCsvFile_ReturnsTrue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "valid.csv");
        File.WriteAllText(filePath, "Column1,Column2\r\nValue1,Value2\r\n");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void IsValidCsvFile_WithNullPath_ReturnsFalse()
    {
        // Arrange
        string filePath = null;

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithEmptyPath_ReturnsFalse()
    {
        // Arrange
        var filePath = string.Empty;

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithWhitespacePath_ReturnsFalse()
    {
        // Arrange
        var filePath = "   ";

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithNonExistentFile_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "nonexistent.csv");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithTxtExtension_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "file.txt");
        File.WriteAllText(filePath, "Column1,Column2\r\n");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithXlsxExtension_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "file.xlsx");
        File.WriteAllText(filePath, "dummy content");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithUppercaseExtension_ReturnsTrue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "file.CSV");
        File.WriteAllText(filePath, "Column1,Column2\r\n");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void IsValidCsvFile_WithMixedCaseExtension_ReturnsTrue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "file.CsV");
        File.WriteAllText(filePath, "Column1,Column2\r\n");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void IsValidCsvFile_WithNoExtension_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "file_no_ext");
        File.WriteAllText(filePath, "Column1,Column2\r\n");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidCsvFile_WithDoubleExtension_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "file.txt.csv");
        File.WriteAllText(filePath, "Column1,Column2\r\n");

        // Act
        var result = _service.IsValidCsvFile(filePath);

        // Assert
        Assert.That(result, Is.True);
    }

    #endregion
}
}
