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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules;
using duHastNet.DocManager.Core.Interfaces;

namespace duHastNet.DocManager.Core.Tests.Models.CurrentFolder;

/// <summary>
/// Tests for CurrentFolderManager - Core functionality
/// This test class covers constructor, initialization, properties, and delegation methods
/// Additional functionality tested in:
/// - CurrentFolderManagerTests_FileOperations: File move and supersede operations
/// - CurrentFolderManagerTests_DocumentMatching: Document matching logic
/// </summary>
[TestFixture]
public class CurrentFolderManagerTests
{
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _testDirectory = Path.Combine(Path.GetTempPath(), "CurrentFolderManagerTests", Guid.NewGuid().ToString());
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
    public void Constructor_WithValidSettings_InitializesSuccessfully()
    {
        // Arrange
        var settings = new CurrentFolderManagerSettings
        {
            IncomingFolderPath = Path.Combine(_testDirectory, "Incoming"),
            CurrentFolderPath = Path.Combine(_testDirectory, "Current"),
            SupersededFolderPath = Path.Combine(_testDirectory, "Superseded")
        };

        // Act
        var manager = new CurrentFolderManager(settings);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager, Is.Not.Null);
            Assert.That(manager.Settings, Is.EqualTo(settings));
            Assert.That(manager.MatchedDocuments, Is.Not.Null);
            Assert.That(manager.MatchedDocuments, Is.Empty);
            Assert.That(manager.Errors, Is.Not.Null);
            Assert.That(manager.Errors, Is.Empty);
        });
    }

    [Test]
    public void Constructor_WithNullSettings_ThrowsArgumentNullException()
    {
        // Arrange
        CurrentFolderManagerSettings settings = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => new CurrentFolderManager(settings));
        Assert.That(exception.ParamName, Is.EqualTo("settings"));
    }

    [Test]
    public void Constructor_WithDefaultConstructor_InitializesWithDefaultSettings()
    {
        // Arrange & Act
        var manager = new CurrentFolderManager();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager, Is.Not.Null);
            Assert.That(manager.Settings, Is.Not.Null);
            Assert.That(manager.Settings.FilingRules, Is.Not.Null);
            Assert.That(manager.Settings.FilingRules, Is.Empty);
            Assert.That(manager.Settings.SupportedFileTypes, Is.Not.Null);
            Assert.That(manager.Settings.SupportedFileTypes, Is.Empty);
            Assert.That(manager.MatchedDocuments, Is.Empty);
            Assert.That(manager.Errors, Is.Empty);
        });
    }

    #endregion

    #region Settings Property Tests

    [Test]
    public void Settings_ReturnsConfiguredSettings()
    {
        // Arrange
        var incomingPath = Path.Combine(_testDirectory, "Incoming");
        var currentPath = Path.Combine(_testDirectory, "Current");
        var supersededPath = Path.Combine(_testDirectory, "Superseded");

        var settings = new CurrentFolderManagerSettings
        {
            IncomingFolderPath = incomingPath,
            CurrentFolderPath = currentPath,
            SupersededFolderPath = supersededPath,
            RevisionPrefix = "[",
            RevisionSuffix = "]"
        };

        var manager = new CurrentFolderManager(settings);

        // Act
        var retrievedSettings = manager.Settings;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(retrievedSettings, Is.SameAs(settings));
            Assert.That(retrievedSettings.IncomingFolderPath, Is.EqualTo(incomingPath));
            Assert.That(retrievedSettings.CurrentFolderPath, Is.EqualTo(currentPath));
            Assert.That(retrievedSettings.SupersededFolderPath, Is.EqualTo(supersededPath));
            Assert.That(retrievedSettings.RevisionPrefix, Is.EqualTo("["));
            Assert.That(retrievedSettings.RevisionSuffix, Is.EqualTo("]"));
        });
    }

    #endregion

    #region MatchedDocuments Property Tests

    [Test]
    public void MatchedDocuments_InitiallyEmpty()
    {
        // Arrange
        var manager = new CurrentFolderManager();

        // Act
        var matchedDocuments = manager.MatchedDocuments;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(matchedDocuments, Is.Not.Null);
            Assert.That(matchedDocuments, Is.Empty);
        });
    }

    [Test]
    public void GetMatchedDocuments_InitiallyReturnsEmptyList()
    {
        // Arrange
        var manager = new CurrentFolderManager();

        // Act
        var matchedDocuments = manager.GetMatchedDocuments();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(matchedDocuments, Is.Not.Null);
            Assert.That(matchedDocuments, Is.Empty);
        });
    }

    #endregion

    #region Errors Property Tests

    [Test]
    public void Errors_InitiallyEmpty()
    {
        // Arrange
        var manager = new CurrentFolderManager();

        // Act
        var errors = manager.Errors;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(errors, Is.Not.Null);
            Assert.That(errors, Is.Empty);
        });
    }

    #endregion

    #region Filing Rule Management Tests

    [Test]
    public void AddFilingRule_WithValidRule_AddsToSettings()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var targetDirectory = Path.Combine(_testDirectory, "Architecture");
        var filingRule = new BeginsWith("A-", targetDirectory);

        // Act
        manager.AddFilingRule(filingRule);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(1));
            Assert.That(manager.Settings.FilingRules[0], Is.SameAs(filingRule));
            Assert.That(manager.Settings.FilingRules[0].TargetDirectory, Is.EqualTo(targetDirectory));
        });
    }

    [Test]
    public void AddFilingRule_WithMultipleRules_AddsAllToSettings()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var architectureDir = Path.Combine(_testDirectory, "Architecture");
        var structuralDir = Path.Combine(_testDirectory, "Structural");
        var mechanicalDir = Path.Combine(_testDirectory, "Mechanical");

        var rule1 = new BeginsWith("A-", architectureDir);
        var rule2 = new BeginsWith("S-", structuralDir);
        var rule3 = new BeginsWith("M-", mechanicalDir);

        // Act
        manager.AddFilingRule(rule1);
        manager.AddFilingRule(rule2);
        manager.AddFilingRule(rule3);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(3));
            Assert.That(manager.Settings.FilingRules[0], Is.SameAs(rule1));
            Assert.That(manager.Settings.FilingRules[1], Is.SameAs(rule2));
            Assert.That(manager.Settings.FilingRules[2], Is.SameAs(rule3));
        });
    }

    [Test]
    public void AddFilingRule_WithNullRule_ThrowsArgumentNullException()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        IFilingRule filingRule = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => manager.AddFilingRule(filingRule));
        Assert.That(exception.ParamName, Is.EqualTo("filingRule"));
    }

    [Test]
    public void RemoveFilingRule_WithExistingRule_RemovesFromSettings()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var targetDirectory = Path.Combine(_testDirectory, "Architecture");
        var filingRule = new BeginsWith("A-", targetDirectory);
        manager.AddFilingRule(filingRule);

        // Act
        manager.RemoveFilingRule(filingRule);

        // Assert
        Assert.That(manager.Settings.FilingRules, Is.Empty);
    }

    [Test]
    public void RemoveFilingRule_WithNonExistentRule_DoesNotThrow()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var targetDirectory = Path.Combine(_testDirectory, "Architecture");
        var filingRule = new BeginsWith("A-", targetDirectory);

        // Act & Assert
        Assert.DoesNotThrow(() => manager.RemoveFilingRule(filingRule));
        Assert.That(manager.Settings.FilingRules, Is.Empty);
    }

    [Test]
    public void RemoveFilingRule_WithNullRule_ThrowsArgumentNullException()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        IFilingRule filingRule = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => manager.RemoveFilingRule(filingRule));
        Assert.That(exception.ParamName, Is.EqualTo("filingRule"));
    }

    [Test]
    public void ClearFilingRules_WithMultipleRules_RemovesAll()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var rule1 = new BeginsWith("A-", Path.Combine(_testDirectory, "Architecture"));
        var rule2 = new BeginsWith("S-", Path.Combine(_testDirectory, "Structural"));
        var rule3 = new BeginsWith("M-", Path.Combine(_testDirectory, "Mechanical"));

        manager.AddFilingRule(rule1);
        manager.AddFilingRule(rule2);
        manager.AddFilingRule(rule3);

        // Act
        manager.ClearFilingRules();

        // Assert
        Assert.That(manager.Settings.FilingRules, Is.Empty);
    }

    [Test]
    public void ClearFilingRules_WithEmptyRules_DoesNotThrow()
    {
        // Arrange
        var manager = new CurrentFolderManager();

        // Act & Assert
        Assert.DoesNotThrow(() => manager.ClearFilingRules());
        Assert.That(manager.Settings.FilingRules, Is.Empty);
    }

    #endregion

    #region Supported File Type Management Tests

    [Test]
    public void AddSupportedFileType_WithValidFileType_AddsToSettings()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var fileType = new SupportedFileType(".pdf", "PDF Document", null);

        // Act
        manager.AddSupportedFileType(fileType);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(1));
            Assert.That(manager.Settings.SupportedFileTypes[0], Is.SameAs(fileType));
            Assert.That(manager.Settings.SupportedFileTypes[0].FileExtension, Is.EqualTo(".pdf"));
            Assert.That(manager.Settings.SupportedFileTypes[0].Description, Is.EqualTo("PDF Document"));
        });
    }

    [Test]
    public void AddSupportedFileType_WithMultipleFileTypes_AddsAllToSettings()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var pdfType = new SupportedFileType(".pdf", "PDF Document", null);
        var dwgType = new SupportedFileType(".dwg", "AutoCAD Drawing", null);
        var rvtType = new SupportedFileType(".rvt", "Revit Model", null);

        // Act
        manager.AddSupportedFileType(pdfType);
        manager.AddSupportedFileType(dwgType);
        manager.AddSupportedFileType(rvtType);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(3));
            Assert.That(manager.Settings.SupportedFileTypes[0].FileExtension, Is.EqualTo(".pdf"));
            Assert.That(manager.Settings.SupportedFileTypes[1].FileExtension, Is.EqualTo(".dwg"));
            Assert.That(manager.Settings.SupportedFileTypes[2].FileExtension, Is.EqualTo(".rvt"));
        });
    }

    [Test]
    public void AddSupportedFileType_WithNullFileType_ThrowsArgumentNullException()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        SupportedFileType fileType = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => manager.AddSupportedFileType(fileType));
        Assert.That(exception.ParamName, Is.EqualTo("supportedFileType"));
    }

    [Test]
    public void RemoveSupportedFileType_WithExistingFileType_RemovesFromSettings()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var fileType = new SupportedFileType(".pdf", "PDF Document", null);
        manager.AddSupportedFileType(fileType);

        // Act
        manager.RemoveSupportedFileType(fileType);

        // Assert
        Assert.That(manager.Settings.SupportedFileTypes, Is.Empty);
    }

    [Test]
    public void RemoveSupportedFileType_WithNonExistentFileType_DoesNotThrow()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var fileType = new SupportedFileType(".pdf", "PDF Document", null);

        // Act & Assert
        Assert.DoesNotThrow(() => manager.RemoveSupportedFileType(fileType));
        Assert.That(manager.Settings.SupportedFileTypes, Is.Empty);
    }

    [Test]
    public void RemoveSupportedFileType_WithNullFileType_ThrowsArgumentNullException()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        SupportedFileType fileType = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => manager.RemoveSupportedFileType(fileType));
        Assert.That(exception.ParamName, Is.EqualTo("supportedFileType"));
    }

    [Test]
    public void ClearSupportedFileTypes_WithMultipleFileTypes_RemovesAll()
    {
        // Arrange
        var manager = new CurrentFolderManager();
        var pdfType = new SupportedFileType(".pdf", "PDF Document", null);
        var dwgType = new SupportedFileType(".dwg", "AutoCAD Drawing", null);
        var rvtType = new SupportedFileType(".rvt", "Revit Model", null);

        manager.AddSupportedFileType(pdfType);
        manager.AddSupportedFileType(dwgType);
        manager.AddSupportedFileType(rvtType);

        // Act
        manager.ClearSupportedFileTypes();

        // Assert
        Assert.That(manager.Settings.SupportedFileTypes, Is.Empty);
    }

    [Test]
    public void ClearSupportedFileTypes_WithEmptyFileTypes_DoesNotThrow()
    {
        // Arrange
        var manager = new CurrentFolderManager();

        // Act & Assert
        Assert.DoesNotThrow(() => manager.ClearSupportedFileTypes());
        Assert.That(manager.Settings.SupportedFileTypes, Is.Empty);
    }

    #endregion

    #region Settings Integration Tests

    [Test]
    public void Manager_WithComplexSettings_MaintainsAllConfiguration()
    {
        // This test verifies that a manager initialized with complex settings
        // maintains all configuration correctly including paths, filing rules, and file types
        
        // Arrange
        var incomingPath = Path.Combine(_testDirectory, "Incoming");
        var currentPath = Path.Combine(_testDirectory, "Current");
        var supersededPath = Path.Combine(_testDirectory, "Superseded");

        var settings = new CurrentFolderManagerSettings
        {
            IncomingFolderPath = incomingPath,
            CurrentFolderPath = currentPath,
            SupersededFolderPath = supersededPath,
            RevisionPrefix = "[",
            RevisionSuffix = "]"
        };

        // Add filing rules
        var archRule = new BeginsWith("A-", Path.Combine(_testDirectory, "Architecture"));
        var structRule = new BeginsWith("S-", Path.Combine(_testDirectory, "Structural"));
        settings.AddFilingRule(archRule);
        settings.AddFilingRule(structRule);

        // Add supported file types
        var pdfType = new SupportedFileType(".pdf", "PDF Document", null);
        var dwgType = new SupportedFileType(".dwg", "AutoCAD Drawing", null);
        settings.AddSupportedFileType(pdfType);
        settings.AddSupportedFileType(dwgType);

        // Act
        var manager = new CurrentFolderManager(settings);

        // Assert
        Assert.Multiple(() =>
        {
            // Verify paths
            Assert.That(manager.Settings.IncomingFolderPath, Is.EqualTo(incomingPath));
            Assert.That(manager.Settings.CurrentFolderPath, Is.EqualTo(currentPath));
            Assert.That(manager.Settings.SupersededFolderPath, Is.EqualTo(supersededPath));
            Assert.That(manager.Settings.RevisionPrefix, Is.EqualTo("["));
            Assert.That(manager.Settings.RevisionSuffix, Is.EqualTo("]"));

            // Verify filing rules
            Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(2));
            Assert.That(manager.Settings.FilingRules[0].ComparisonValue, Is.EqualTo("A-"));
            Assert.That(manager.Settings.FilingRules[1].ComparisonValue, Is.EqualTo("S-"));

            // Verify supported file types
            Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(2));
            Assert.That(manager.Settings.SupportedFileTypes[0].FileExtension, Is.EqualTo(".pdf"));
            Assert.That(manager.Settings.SupportedFileTypes[1].FileExtension, Is.EqualTo(".dwg"));

            // Verify initial state
            Assert.That(manager.MatchedDocuments, Is.Empty);
            Assert.That(manager.Errors, Is.Empty);
        });
    }

    [Test]
    public void Manager_ModifyingSettingsAfterConstruction_ReflectsChanges()
    {
        // Arrange
        var settings = new CurrentFolderManagerSettings();
        var manager = new CurrentFolderManager(settings);

        var filingRule = new BeginsWith("A-", Path.Combine(_testDirectory, "Architecture"));
        var fileType = new SupportedFileType(".pdf", "PDF Document", null);

        // Act
        manager.AddFilingRule(filingRule);
        manager.AddSupportedFileType(fileType);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(1));
            Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(1));
            Assert.That(settings.FilingRules, Has.Count.EqualTo(1)); // Original settings object updated
            Assert.That(settings.SupportedFileTypes, Has.Count.EqualTo(1)); // Original settings object updated
        });
    }

    #endregion

    #region Filing Rule Delegation Tests

    [Test]
    public void FilingRuleDelegation_AllMethodsCallSettingsMethods()
    {
        // This test verifies that the manager correctly delegates filing rule operations
        // to the settings object without adding additional logic
        
        // Arrange
        var manager = new CurrentFolderManager();
        var rule1 = new BeginsWith("A-", Path.Combine(_testDirectory, "Dir1"));
        var rule2 = new BeginsWith("B-", Path.Combine(_testDirectory, "Dir2"));

        // Act & Assert - Add
        manager.AddFilingRule(rule1);
        Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(1));

        manager.AddFilingRule(rule2);
        Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(2));

        // Act & Assert - Remove
        manager.RemoveFilingRule(rule1);
        Assert.That(manager.Settings.FilingRules, Has.Count.EqualTo(1));
        Assert.That(manager.Settings.FilingRules[0], Is.SameAs(rule2));

        // Act & Assert - Clear
        manager.ClearFilingRules();
        Assert.That(manager.Settings.FilingRules, Is.Empty);
    }

    #endregion

    #region Supported File Type Delegation Tests

    [Test]
    public void SupportedFileTypeDelegation_AllMethodsCallSettingsMethods()
    {
        // This test verifies that the manager correctly delegates supported file type operations
        // to the settings object without adding additional logic
        
        // Arrange
        var manager = new CurrentFolderManager();
        var type1 = new SupportedFileType(".pdf", "PDF", null);
        var type2 = new SupportedFileType(".dwg", "DWG", null);

        // Act & Assert - Add
        manager.AddSupportedFileType(type1);
        Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(1));

        manager.AddSupportedFileType(type2);
        Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(2));

        // Act & Assert - Remove
        manager.RemoveSupportedFileType(type1);
        Assert.That(manager.Settings.SupportedFileTypes, Has.Count.EqualTo(1));
        Assert.That(manager.Settings.SupportedFileTypes[0], Is.SameAs(type2));

        // Act & Assert - Clear
        manager.ClearSupportedFileTypes();
        Assert.That(manager.Settings.SupportedFileTypes, Is.Empty);
    }

    #endregion
}
