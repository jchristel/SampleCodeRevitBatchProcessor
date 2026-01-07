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
using Moq;
using CsvHelper;
using CsvHelper.Configuration;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Interfaces;
using System.Globalization;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class CloudMetadataExportServiceTests
{
    private CloudMetadataExportService _service;
    private string _testDirectory;
    private Mock<ICloudMetaData> _mockCloudMetaData;

    [SetUp]
    public void Setup()
    {
        _service = new CloudMetadataExportService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "CloudMetadataExportServiceTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
        _mockCloudMetaData = new Mock<ICloudMetaData>();
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region ExportMetadataAsync - Input Validation Tests

    [Test]
    public async Task ExportMetadataAsync_WithNullFilePath_ReturnsFalse()
    {
        // Arrange
        string filePath = null;
        var documents = new List<Document>();
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>();

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task ExportMetadataAsync_WithEmptyFilePath_ReturnsFalse()
    {
        // Arrange
        var filePath = string.Empty;
        var documents = new List<Document>();
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>();

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task ExportMetadataAsync_WithWhitespaceFilePath_ReturnsFalse()
    {
        // Arrange
        var filePath = "   ";
        var documents = new List<Document>();
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>();

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task ExportMetadataAsync_WithNullCloudMetaData_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var documents = new List<Document>();
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>();

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            null,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task ExportMetadataAsync_WithEmptyDocuments_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var documents = new List<Document>();
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>();

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap>
        {
            new MetaDataMap("Field1", "Value1", null, null, "Aconex")
        });

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task ExportMetadataAsync_WithEmptyMappings_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var documents = new List<Document>
        {
            new Document("A-101", "Floor Plan", "1", 1)
        };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>();

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    #endregion

    #region ExportMetadataAsync - Basic Export Tests

    [Test]
    public async Task ExportMetadataAsync_WithSingleDocumentFixedValue_CreatesValidCsv()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var documentNumber = "A-101";
        var documentName = "Ground Floor Plan";
        var revision = "3";
        var revisionId = 1;

        var document = new Document(documentNumber, documentName, revision, revisionId);
        document.Id = 1;

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("Project", "Test Project", null, null, "Aconex"),
            new MetaDataMap("Status", "Current", null, null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.True);
            Assert.That(File.Exists(filePath), Is.True);
        });

        // Verify CSV content
        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(2)); // Header + 1 data row
            Assert.That(lines[0], Is.EqualTo("Project,Status"));
            Assert.That(lines[1], Is.EqualTo("Test Project,Current"));
        });
    }

    [Test]
    public async Task ExportMetadataAsync_WithDocumentProperties_MapsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var documentNumber = "S-201";
        var documentName = "Structural Plan";
        var revision = "A";
        var revisionId = 1;

        var document = new Document(documentNumber, documentName, revision, revisionId);
        document.Id = 1;

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "S-201.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex"),
            new MetaDataMap("DocumentName", null, "Name", null, "Aconex"),
            new MetaDataMap("Revision", null, "Revision", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        // Verify CSV content
        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(2));
            Assert.That(lines[0], Is.EqualTo("DocumentNumber,DocumentName,Revision"));
            Assert.That(lines[1], Is.EqualTo($"{documentNumber},{documentName},{revision}"));
        });
    }

    [Test]
    public async Task ExportMetadataAsync_WithMultipleDocuments_CreatesMultipleRows()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");

        var document1 = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };
        var document2 = new Document("A-102", "Ceiling Plan", "2", 2) { Id = 2 };

        var documents = new List<Document> { document1, document2 };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } },
            { 2, new List<string> { Path.Combine(_testDirectory, "A-102.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(3)); // Header + 2 data rows
            Assert.That(lines[1], Is.EqualTo("A-101"));
            Assert.That(lines[2], Is.EqualTo("A-102"));
        });
    }

    #endregion

    #region ExportMetadataAsync - Multiple Files Per Document Tests

    [Test]
    public async Task ExportMetadataAsync_WithMultipleFilesPerDocument_CreatesRowPerFile()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            {
                1, new List<string>
                {
                    Path.Combine(_testDirectory, "A-101.pdf"),
                    Path.Combine(_testDirectory, "A-101.dwg"),
                    Path.Combine(_testDirectory, "A-101.rvt")
                }
            }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex"),
            new MetaDataMap("FileName", null, null, "FileName", "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(4)); // Header + 3 data rows (one per file)
            Assert.That(lines[1], Does.Contain("A-101.pdf"));
            Assert.That(lines[2], Does.Contain("A-101.dwg"));
            Assert.That(lines[3], Does.Contain("A-101.rvt"));
        });
    }

    #endregion

    #region ExportMetadataAsync - File Property Tests

    [Test]
    public async Task ExportMetadataAsync_WithFileNameProperty_ExtractsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };
        var incomingFilePath = Path.Combine(_testDirectory, "TestDocument.pdf");

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { incomingFilePath } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("FileName", null, null, "FileName", "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("TestDocument.pdf"));
    }

    [Test]
    public async Task ExportMetadataAsync_WithFileExtensionProperty_ExtractsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };
        var incomingFilePath = Path.Combine(_testDirectory, "TestDocument.dwg");

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { incomingFilePath } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("Extension", null, null, "Extension", "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("dwg"));
    }

    [Test]
    public async Task ExportMetadataAsync_WithFileNameWithoutExtension_ExtractsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };
        var incomingFilePath = Path.Combine(_testDirectory, "MyDocument.pdf");

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { incomingFilePath } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("NameWithoutExt", null, null, "FileNameWithoutExtension", "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("MyDocument"));
    }

    #endregion

    #region ExportMetadataAsync - Revision Property Tests

    [Test]
    public async Task ExportMetadataAsync_WithRevisionDate_FormatsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var revisionDate = new DateTime(2024, 6, 15);
        var revision = new Revision("Rev A", revisionDate, "First Issue") { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("RevisionDate", null, "RevisionDate", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("15/06/2024"));
    }

    [Test]
    public async Task ExportMetadataAsync_WithRevisionDescription_MapsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var revisionDescription = "Initial Submission";
        var revision = new Revision("Rev A", DateTime.Now, revisionDescription) { Id = 1 };
        var document = new Document("A-101", "Floor Plan", "A", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision> { revision };
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("RevisionDesc", null, "RevisionDescription", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo(revisionDescription));
    }

    #endregion

    #region ExportMetadataAsync - Custom Property Tests

    [Test]
    public async Task ExportMetadataAsync_WithCustomProperty_MapsCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var customProperty = new CustomProperty { PropertyName = "Discipline", PropertyValue = "Architecture" };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>
        {
            { 1, new List<CustomProperty> { customProperty } }
        };
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DisciplineField", null, "Discipline", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("Architecture"));
    }

    [Test]
    public async Task ExportMetadataAsync_WithMultipleCustomProperties_MapsAllCorrectly()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var customProperty1 = new CustomProperty { PropertyName = "Discipline", PropertyValue = "Architecture" };
        var customProperty2 = new CustomProperty { PropertyName = "Zone", PropertyValue = "Zone A" };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>
        {
            { 1, new List<CustomProperty> { customProperty1, customProperty2 } }
        };
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DisciplineField", null, "Discipline", null, "Aconex"),
            new MetaDataMap("ZoneField", null, "Zone", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("Architecture,Zone A"));
    }

    #endregion

    #region ExportMetadataAsync - Document Number Modifier Tests

    [Test]
    public async Task ExportMetadataAsync_WithDocumentNumberModifier_AppliesModifier()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };
        var incomingFilePath = Path.Combine(_testDirectory, "A-101.dwg");

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { incomingFilePath } }
        };

        var mockModifier = new Mock<IDocumentNumberModifier>();
        mockModifier.Setup(x => x.DocumentNumber(It.IsAny<string>()))
            .Returns((string num) => num + "-DWG");

        var supportedFileType = new SupportedFileType(".dwg", "AutoCAD Drawing", mockModifier.Object);

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType> { supportedFileType });

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("A-101-DWG"));
    }

    [Test]
    public async Task ExportMetadataAsync_WithoutMatchingFileType_ReturnsUnmodifiedNumber()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };
        var incomingFilePath = Path.Combine(_testDirectory, "A-101.pdf");

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { incomingFilePath } }
        };

        var mockModifier = new Mock<IDocumentNumberModifier>();
        mockModifier.Setup(x => x.DocumentNumber(It.IsAny<string>()))
            .Returns((string num) => num + "-DWG");

        var supportedFileType = new SupportedFileType(".dwg", "AutoCAD Drawing", mockModifier.Object);

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType> { supportedFileType });

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("A-101")); // No modifier applied for .pdf
    }

    #endregion

    #region ExportMetadataAsync - Template File Tests

    [Test]
    public async Task ExportMetadataAsync_WithTemplateFile_UsesTemplateHeaderOrder()
    {
        // Arrange
        var templatePath = Path.Combine(_testDirectory, "template.csv");
        var outputPath = Path.Combine(_testDirectory, "output.csv");

        // Create template file with specific column order
        await File.WriteAllTextAsync(templatePath, "Column3,Column1,Column2\n");

        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("Column1", "Value1", null, null, "Aconex"),
            new MetaDataMap("Column2", "Value2", null, null, "Aconex"),
            new MetaDataMap("Column3", "Value3", null, null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(templatePath);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            outputPath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(outputPath);
        Assert.Multiple(() =>
        {
            Assert.That(lines[0], Is.EqualTo("Column3,Column1,Column2")); // Template order preserved
            Assert.That(lines[1], Is.EqualTo("Value3,Value1,Value2")); // Values match template order
        });
    }

    [Test]
    public async Task ExportMetadataAsync_WithNonExistentTemplateFile_UsesMappingOrder()
    {
        // Arrange
        var templatePath = Path.Combine(_testDirectory, "nonexistent.csv");
        var outputPath = Path.Combine(_testDirectory, "output.csv");

        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("FieldA", "ValueA", null, null, "Aconex"),
            new MetaDataMap("FieldB", "ValueB", null, null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(templatePath);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            outputPath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(outputPath);
        Assert.That(lines[0], Is.EqualTo("FieldA,FieldB"));
    }

    #endregion

    #region ExportMetadataAsync - Empty/Null Mapping Tests

    [Test]
    public async Task ExportMetadataAsync_WithUnmappedColumn_WritesEmptyValue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var templatePath = Path.Combine(_testDirectory, "template.csv");

        // Create template with column that has no mapping
        await File.WriteAllTextAsync(templatePath, "MappedField,UnmappedField\n");

        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("MappedField", "SomeValue", null, null, "Aconex")
            // No mapping for UnmappedField
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(templatePath);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo("SomeValue,")); // Empty value for unmapped field
    }

    [Test]
    public async Task ExportMetadataAsync_WithMissingCustomProperty_WritesEmptyValue()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>(); // No custom properties
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { Path.Combine(_testDirectory, "A-101.pdf") } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("CustomField", null, "NonExistentProperty", null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines[1], Is.EqualTo(string.Empty));
    }

    #endregion

    #region ExportMetadataAsync - Error Handling Tests

    [Test]
    public async Task ExportMetadataAsync_WithInvalidPath_ReturnsFalse()
    {
        // Arrange
        var filePath = Path.Combine("Z:\\NonExistentDrive\\InvalidPath\\", "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            { 1, new List<string> { "test.pdf" } }
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("Field", "Value", null, null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task ExportMetadataAsync_WithDocumentWithoutFiles_SkipsDocument()
    {
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");
        var document = new Document("A-101", "Floor Plan", "1", 1) { Id = 1 };

        var documents = new List<Document> { document };
        var revisions = new List<Revision>();
        var customProperties = new Dictionary<int, List<CustomProperty>>();
        var filePathsByDocumentId = new Dictionary<int, List<string>>(); // No files for document

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("Field", "Value", null, null, "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(new List<SupportedFileType>());

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.That(lines, Has.Length.EqualTo(1)); // Only header, no data rows
    }

    #endregion

    #region ExportMetadataAsync - Integration Tests

    [Test]
    public async Task ExportMetadataAsync_WithComplexScenario_ExportsCorrectly()
    {
        // This test verifies a complex real-world scenario with multiple documents,
        // files, custom properties, revisions, and various mapping types
        
        // Arrange
        var filePath = Path.Combine(_testDirectory, "metadata.csv");

        var revision1 = new Revision("Rev A", new DateTime(2024, 1, 15), "Initial Issue") { Id = 1 };
        var revision2 = new Revision("Rev B", new DateTime(2024, 2, 20), "Client Comments") { Id = 2 };

        var document1 = new Document("A-101", "Ground Floor Plan", "A", 1) { Id = 1 };
        var document2 = new Document("S-201", "Structural Layout", "B", 2) { Id = 2 };

        var documents = new List<Document> { document1, document2 };
        var revisions = new List<Revision> { revision1, revision2 };

        var customProperties = new Dictionary<int, List<CustomProperty>>
        {
            {
                1, new List<CustomProperty>
                {
                    new CustomProperty { PropertyName = "Discipline", PropertyValue = "Architecture" },
                    new CustomProperty { PropertyName = "Zone", PropertyValue = "Ground Floor" }
                }
            },
            {
                2, new List<CustomProperty>
                {
                    new CustomProperty { PropertyName = "Discipline", PropertyValue = "Structural" },
                    new CustomProperty { PropertyName = "Zone", PropertyValue = "All Levels" }
                }
            }
        };

        var filePathsByDocumentId = new Dictionary<int, List<string>>
        {
            {
                1, new List<string>
                {
                    Path.Combine(_testDirectory, "A-101.pdf"),
                    Path.Combine(_testDirectory, "A-101.dwg")
                }
            },
            {
                2, new List<string>
                {
                    Path.Combine(_testDirectory, "S-201.pdf")
                }
            }
        };

        var mockModifier = new Mock<IDocumentNumberModifier>();
        mockModifier.Setup(x => x.DocumentNumber(It.IsAny<string>()))
            .Returns((string num) => num + "-DWG");

        var supportedFileTypes = new List<SupportedFileType>
        {
            new SupportedFileType(".dwg", "AutoCAD Drawing", mockModifier.Object)
        };

        var mappings = new List<MetaDataMap>
        {
            new MetaDataMap("Project", "Test Project", null, null, "Aconex"),
            new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex"),
            new MetaDataMap("DocumentName", null, "Name", null, "Aconex"),
            new MetaDataMap("Revision", null, "Revision", null, "Aconex"),
            new MetaDataMap("RevisionDate", null, "RevisionDate", null, "Aconex"),
            new MetaDataMap("Discipline", null, "Discipline", null, "Aconex"),
            new MetaDataMap("FileName", null, null, "FileName", "Aconex")
        };

        _mockCloudMetaData.Setup(x => x.MetaDataMap).Returns(mappings);
        _mockCloudMetaData.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockCloudMetaData.Setup(x => x.SupportedFileTypes).Returns(supportedFileTypes);

        // Act
        var result = await _service.ExportMetadataAsync(
            filePath,
            documents,
            revisions,
            _mockCloudMetaData.Object,
            customProperties,
            filePathsByDocumentId);

        // Assert
        Assert.That(result, Is.True);

        var lines = await File.ReadAllLinesAsync(filePath);
        Assert.Multiple(() =>
        {
            Assert.That(lines, Has.Length.EqualTo(4)); // Header + 3 file rows
            Assert.That(lines[0], Is.EqualTo("Project,DocumentNumber,DocumentName,Revision,RevisionDate,Discipline,FileName"));
            
            // First document, first file (PDF - no modifier)
            Assert.That(lines[1], Does.Contain("A-101"));
            Assert.That(lines[1], Does.Contain("Ground Floor Plan"));
            Assert.That(lines[1], Does.Contain("Architecture"));
            Assert.That(lines[1], Does.Contain("A-101.pdf"));
            
            // First document, second file (DWG - with modifier)
            Assert.That(lines[2], Does.Contain("A-101-DWG"));
            Assert.That(lines[2], Does.Contain("A-101.dwg"));
            
            // Second document
            Assert.That(lines[3], Does.Contain("S-201"));
            Assert.That(lines[3], Does.Contain("Structural"));
        });
    }

    #endregion
}
