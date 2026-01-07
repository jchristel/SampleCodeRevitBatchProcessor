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

namespace duHastNet.DocManager.Core.Tests.Services;

/// <summary>
/// Tests for FilePropertyProvider
/// This test class covers file property extraction and validation including:
/// - Getting available file properties
/// - Extracting property values from file paths
/// - Property name validation
/// - Property descriptions
/// - Case-insensitive property name handling
/// - Alias support for property names
/// </summary>
[TestFixture]
public class FilePropertyProviderTests
{
    #region GetAvailableFileProperties Tests

    [Test]
    public void GetAvailableFileProperties_ReturnsExpectedProperties()
    {
        // Arrange & Act
        var properties = FilePropertyProvider.GetAvailableFileProperties();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(properties, Is.Not.Null);
            Assert.That(properties, Has.Count.EqualTo(5));
            Assert.That(properties, Contains.Item(FilePropertyProvider.PropertyFileName));
            Assert.That(properties, Contains.Item(FilePropertyProvider.PropertyFileNameWithoutExtension));
            Assert.That(properties, Contains.Item(FilePropertyProvider.PropertyExtension));
            Assert.That(properties, Contains.Item(FilePropertyProvider.PropertyFullPath));
            Assert.That(properties, Contains.Item(FilePropertyProvider.PropertyDirectoryName));
        });
    }

    [Test]
    public void GetAvailableFileProperties_ReturnsPropertiesInExpectedOrder()
    {
        // Arrange & Act
        var properties = FilePropertyProvider.GetAvailableFileProperties();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(properties[0], Is.EqualTo(FilePropertyProvider.PropertyFileName));
            Assert.That(properties[1], Is.EqualTo(FilePropertyProvider.PropertyFileNameWithoutExtension));
            Assert.That(properties[2], Is.EqualTo(FilePropertyProvider.PropertyExtension));
            Assert.That(properties[3], Is.EqualTo(FilePropertyProvider.PropertyFullPath));
            Assert.That(properties[4], Is.EqualTo(FilePropertyProvider.PropertyDirectoryName));
        });
    }

    [Test]
    public void GetAvailableFileProperties_CalledMultipleTimes_ReturnsConsistentResults()
    {
        // Arrange & Act
        var properties1 = FilePropertyProvider.GetAvailableFileProperties();
        var properties2 = FilePropertyProvider.GetAvailableFileProperties();

        // Assert
        Assert.That(properties2, Is.EqualTo(properties1));
    }

    #endregion

    #region GetFilePropertyValue Tests - FileName

    [Test]
    public void GetFilePropertyValue_FileName_ReturnsFileNameWithExtension()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");

        // Assert
        Assert.That(result, Is.EqualTo("MyDocument.pdf"));
    }

    [Test]
    public void GetFilePropertyValue_FileName_WithAlias_ReturnsFileNameWithExtension()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var resultWithName = FilePropertyProvider.GetFilePropertyValue(filePath, "Name");

        // Assert
        Assert.That(resultWithName, Is.EqualTo("MyDocument.pdf"));
    }

    [Test]
    public void GetFilePropertyValue_FileName_CaseInsensitive_ReturnsFileNameWithExtension()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "filename"), Is.EqualTo("MyDocument.pdf"));
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "FILENAME"), Is.EqualTo("MyDocument.pdf"));
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "FileName"), Is.EqualTo("MyDocument.pdf"));
        });
    }

    #endregion

    #region GetFilePropertyValue Tests - FileNameWithoutExtension

    [Test]
    public void GetFilePropertyValue_FileNameWithoutExtension_ReturnsNameOnly()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FileNameWithoutExtension");

        // Assert
        Assert.That(result, Is.EqualTo("MyDocument"));
    }

    [Test]
    public void GetFilePropertyValue_FileNameWithoutExtension_WithAlias_ReturnsNameOnly()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "NameWithoutExtension");

        // Assert
        Assert.That(result, Is.EqualTo("MyDocument"));
    }

    [Test]
    public void GetFilePropertyValue_FileNameWithoutExtension_WithMultipleDots_HandlesCorrectly()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\My.Document.Rev.A.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FileNameWithoutExtension");

        // Assert
        Assert.That(result, Is.EqualTo("My.Document.Rev.A"));
    }

    #endregion

    #region GetFilePropertyValue Tests - Extension

    [Test]
    public void GetFilePropertyValue_Extension_ReturnsExtensionWithoutDot()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "Extension");

        // Assert
        Assert.That(result, Is.EqualTo("pdf"));
    }

    [Test]
    public void GetFilePropertyValue_Extension_WithAliases_ReturnsExtensionWithoutDot()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "FileExtension"), Is.EqualTo("pdf"));
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "Ext"), Is.EqualTo("pdf"));
        });
    }

    [Test]
    public void GetFilePropertyValue_Extension_WithNoExtension_ReturnsEmpty()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "Extension");

        // Assert
        Assert.That(result, Is.Empty);
    }

    [Test]
    public void GetFilePropertyValue_Extension_WithUpperCaseExtension_ReturnsOriginalCase()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.PDF";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "Extension");

        // Assert
        Assert.That(result, Is.EqualTo("PDF"));
    }

    #endregion

    #region GetFilePropertyValue Tests - FullPath

    [Test]
    public void GetFilePropertyValue_FullPath_ReturnsCompletePath()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FullPath");

        // Assert
        Assert.That(result, Is.EqualTo(filePath));
    }

    [Test]
    public void GetFilePropertyValue_FullPath_WithAliases_ReturnsCompletePath()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "FilePath"), Is.EqualTo(filePath));
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "Path"), Is.EqualTo(filePath));
        });
    }

    #endregion

    #region GetFilePropertyValue Tests - DirectoryName

    [Test]
    public void GetFilePropertyValue_DirectoryName_ReturnsDirectoryPath()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "DirectoryName");

        // Assert
        Assert.That(result, Is.EqualTo(@"C:\Projects\Documents"));
    }

    [Test]
    public void GetFilePropertyValue_DirectoryName_WithAliases_ReturnsDirectoryPath()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "Directory"), Is.EqualTo(@"C:\Projects\Documents"));
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "Folder"), Is.EqualTo(@"C:\Projects\Documents"));
            Assert.That(FilePropertyProvider.GetFilePropertyValue(filePath, "FolderName"), Is.EqualTo(@"C:\Projects\Documents"));
        });
    }

    [Test]
    public void GetFilePropertyValue_DirectoryName_WithRootPath_ReturnsRoot()
    {
        // Arrange
        var filePath = @"C:\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "DirectoryName");

        // Assert
        Assert.That(result, Is.EqualTo(@"C:\"));
    }

    #endregion

    #region GetFilePropertyValue Tests - Edge Cases

    [Test]
    public void GetFilePropertyValue_WithNullPath_ReturnsEmpty()
    {
        // Arrange
        string? filePath = null;

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");

        // Assert
        Assert.That(result, Is.Empty);
    }

    [Test]
    public void GetFilePropertyValue_WithEmptyPath_ReturnsEmpty()
    {
        // Arrange
        var filePath = string.Empty;

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");

        // Assert
        Assert.That(result, Is.Empty);
    }

    [Test]
    public void GetFilePropertyValue_WithWhitespacePath_ReturnsEmpty()
    {
        // Arrange
        var filePath = "   ";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");

        // Assert
        Assert.That(result, Is.Empty);
    }

    [Test]
    public void GetFilePropertyValue_WithInvalidPropertyName_ReturnsEmpty()
    {
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "InvalidProperty");

        // Assert
        Assert.That(result, Is.Empty);
    }

    [Test]
    public void GetFilePropertyValue_WithPropertyNameContainingSpaces_HandlesCorrectly()
    {
        // Property names with spaces should be normalized (spaces removed)
        // Arrange
        var filePath = @"C:\Projects\Documents\MyDocument.pdf";

        // Act
        var result = FilePropertyProvider.GetFilePropertyValue(filePath, "File Name");

        // Assert
        Assert.That(result, Is.EqualTo("MyDocument.pdf"));
    }

    #endregion

    #region GetFilePropertyValue Tests - Different Path Formats

    [Test]
    public void GetFilePropertyValue_WithForwardSlashes_HandlesCorrectly()
    {
        // Arrange
        var filePath = "C:/Projects/Documents/MyDocument.pdf";

        // Act
        var fileName = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");
        var directory = FilePropertyProvider.GetFilePropertyValue(filePath, "DirectoryName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(fileName, Is.EqualTo("MyDocument.pdf"));
            Assert.That(directory, Is.Not.Empty);
        });
    }

    [Test]
    public void GetFilePropertyValue_WithUNCPath_HandlesCorrectly()
    {
        // Arrange
        var filePath = @"\\Server\Share\Documents\MyDocument.pdf";

        // Act
        var fileName = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");
        var directory = FilePropertyProvider.GetFilePropertyValue(filePath, "DirectoryName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(fileName, Is.EqualTo("MyDocument.pdf"));
            Assert.That(directory, Is.EqualTo(@"\\Server\Share\Documents"));
        });
    }

    [Test]
    public void GetFilePropertyValue_WithRelativePath_HandlesCorrectly()
    {
        // Arrange
        var filePath = @"Documents\MyDocument.pdf";

        // Act
        var fileName = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");
        var fileNameWithoutExt = FilePropertyProvider.GetFilePropertyValue(filePath, "FileNameWithoutExtension");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(fileName, Is.EqualTo("MyDocument.pdf"));
            Assert.That(fileNameWithoutExt, Is.EqualTo("MyDocument"));
        });
    }

    #endregion

    #region IsValidFileProperty Tests

    [Test]
    public void IsValidFileProperty_WithValidProperty_ReturnsTrue()
    {
        // Arrange & Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(FilePropertyProvider.IsValidFileProperty("FileName"), Is.True);
            Assert.That(FilePropertyProvider.IsValidFileProperty("FileNameWithoutExtension"), Is.True);
            Assert.That(FilePropertyProvider.IsValidFileProperty("Extension"), Is.True);
            Assert.That(FilePropertyProvider.IsValidFileProperty("FullPath"), Is.True);
            Assert.That(FilePropertyProvider.IsValidFileProperty("DirectoryName"), Is.True);
        });
    }

    [Test]
    public void IsValidFileProperty_CaseInsensitive_ReturnsTrue()
    {
        // Arrange & Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(FilePropertyProvider.IsValidFileProperty("filename"), Is.True);
            Assert.That(FilePropertyProvider.IsValidFileProperty("FILENAME"), Is.True);
            Assert.That(FilePropertyProvider.IsValidFileProperty("FileName"), Is.True);
        });
    }

    [Test]
    public void IsValidFileProperty_WithInvalidProperty_ReturnsFalse()
    {
        // Arrange & Act
        var result = FilePropertyProvider.IsValidFileProperty("InvalidProperty");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidFileProperty_WithNull_ReturnsFalse()
    {
        // Arrange & Act
        var result = FilePropertyProvider.IsValidFileProperty(null);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidFileProperty_WithEmptyString_ReturnsFalse()
    {
        // Arrange & Act
        var result = FilePropertyProvider.IsValidFileProperty(string.Empty);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidFileProperty_WithWhitespace_ReturnsFalse()
    {
        // Arrange & Act
        var result = FilePropertyProvider.IsValidFileProperty("   ");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void IsValidFileProperty_WithAlias_ReturnsFalse()
    {
        // Aliases are not in the canonical list returned by GetAvailableFileProperties
        // Arrange & Act
        var result = FilePropertyProvider.IsValidFileProperty("Name");

        // Assert
        Assert.That(result, Is.False, "Aliases should not be considered valid in the canonical list");
    }

    #endregion

    #region GetFilePropertyDescription Tests

    [Test]
    public void GetFilePropertyDescription_FileName_ReturnsExpectedDescription()
    {
        // Arrange & Act
        var description = FilePropertyProvider.GetFilePropertyDescription("FileName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(description, Is.Not.Empty);
            Assert.That(description, Does.Contain("file name"));
            Assert.That(description, Does.Contain("extension"));
        });
    }

    [Test]
    public void GetFilePropertyDescription_FileNameWithoutExtension_ReturnsExpectedDescription()
    {
        // Arrange & Act
        var description = FilePropertyProvider.GetFilePropertyDescription("FileNameWithoutExtension");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(description, Is.Not.Empty);
            Assert.That(description, Does.Contain("without extension"));
        });
    }

    [Test]
    public void GetFilePropertyDescription_Extension_ReturnsExpectedDescription()
    {
        // Arrange & Act
        var description = FilePropertyProvider.GetFilePropertyDescription("Extension");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(description, Is.Not.Empty);
            Assert.That(description, Does.Contain("extension"));
            Assert.That(description, Does.Contain("without the dot"));
        });
    }

    [Test]
    public void GetFilePropertyDescription_FullPath_ReturnsExpectedDescription()
    {
        // Arrange & Act
        var description = FilePropertyProvider.GetFilePropertyDescription("FullPath");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(description, Is.Not.Empty);
            Assert.That(description, Does.Contain("complete"));
            Assert.That(description, Does.Contain("path"));
        });
    }

    [Test]
    public void GetFilePropertyDescription_DirectoryName_ReturnsExpectedDescription()
    {
        // Arrange & Act
        var description = FilePropertyProvider.GetFilePropertyDescription("DirectoryName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(description, Is.Not.Empty);
            Assert.That(description, Does.Contain("directory"));
        });
    }

    [Test]
    public void GetFilePropertyDescription_CaseInsensitive_ReturnsDescription()
    {
        // Arrange & Act
        var descriptionLower = FilePropertyProvider.GetFilePropertyDescription("filename");
        var descriptionUpper = FilePropertyProvider.GetFilePropertyDescription("FILENAME");
        var descriptionMixed = FilePropertyProvider.GetFilePropertyDescription("FileName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(descriptionLower, Is.Not.Empty);
            Assert.That(descriptionUpper, Is.Not.Empty);
            Assert.That(descriptionMixed, Is.Not.Empty);
            Assert.That(descriptionLower, Is.EqualTo(descriptionMixed));
        });
    }

    [Test]
    public void GetFilePropertyDescription_WithInvalidProperty_ReturnsDefaultDescription()
    {
        // Arrange & Act
        var description = FilePropertyProvider.GetFilePropertyDescription("InvalidProperty");

        // Assert
        Assert.That(description, Is.EqualTo("File property"));
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_AllAvailableProperties_CanExtractValues()
    {
        // This test verifies that all properties returned by GetAvailableFileProperties
        // can actually extract values from a file path
        
        // Arrange
        var filePath = @"C:\Projects\Documents\TestFile.pdf";
        var properties = FilePropertyProvider.GetAvailableFileProperties();

        // Act & Assert
        foreach (var property in properties)
        {
            var value = FilePropertyProvider.GetFilePropertyValue(filePath, property);
            Assert.That(value, Is.Not.Null, $"Property {property} should return a non-null value");
            Assert.That(value, Is.Not.Empty, $"Property {property} should return a non-empty value for valid file path");
        }
    }

    [Test]
    public void IntegrationTest_CompleteWorkflow_ExtractAllPropertiesFromRealPath()
    {
        // This test simulates extracting all properties from a realistic file path
        
        // Arrange
        var filePath = @"C:\Users\John\Documents\Projects\DocManager\Drawings\A-101-Floor-Plan-Rev-B.pdf";

        // Act
        var fileName = FilePropertyProvider.GetFilePropertyValue(filePath, "FileName");
        var fileNameWithoutExt = FilePropertyProvider.GetFilePropertyValue(filePath, "FileNameWithoutExtension");
        var extension = FilePropertyProvider.GetFilePropertyValue(filePath, "Extension");
        var fullPath = FilePropertyProvider.GetFilePropertyValue(filePath, "FullPath");
        var directory = FilePropertyProvider.GetFilePropertyValue(filePath, "DirectoryName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(fileName, Is.EqualTo("A-101-Floor-Plan-Rev-B.pdf"));
            Assert.That(fileNameWithoutExt, Is.EqualTo("A-101-Floor-Plan-Rev-B"));
            Assert.That(extension, Is.EqualTo("pdf"));
            Assert.That(fullPath, Is.EqualTo(filePath));
            Assert.That(directory, Is.EqualTo(@"C:\Users\John\Documents\Projects\DocManager\Drawings"));
        });
    }

    #endregion
}
