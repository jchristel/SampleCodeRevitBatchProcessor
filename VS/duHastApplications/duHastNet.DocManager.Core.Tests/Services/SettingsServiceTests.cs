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
public class SettingsServiceTests
{
    private string _testDirectory;
    private SettingsService _service;

    [SetUp]
    public void Setup()
    {
        _testDirectory = Path.Combine(Path.GetTempPath(), "SettingsServiceTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
        _service = new SettingsService(_testDirectory);
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
    public void Constructor_WithDefaultConstructor_CreatesDefaultDirectory()
    {
        // Arrange & Act
        var service = new SettingsService();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(service, Is.Not.Null);
            Assert.That(service.SettingsDirectory, Is.Not.Null);
            Assert.That(service.SettingsDirectory, Does.Contain("duHast"));
            Assert.That(Directory.Exists(service.SettingsDirectory), Is.True);
        });

        // Cleanup
        try
        {
            Directory.Delete(service.SettingsDirectory, true);
        }
        catch
        {
            // Ignore cleanup errors
        }
    }

    [Test]
    public void Constructor_WithCustomPath_UsesCustomDirectory()
    {
        // Arrange
        var customPath = Path.Combine(Path.GetTempPath(), "CustomSettings", Guid.NewGuid().ToString());

        // Act
        var service = new SettingsService(customPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(service.SettingsDirectory, Is.EqualTo(customPath));
            Assert.That(Directory.Exists(customPath), Is.True);
        });

        // Cleanup
        if (Directory.Exists(customPath))
        {
            Directory.Delete(customPath, true);
        }
    }

    [Test]
    public void Constructor_WithNullCustomPath_ThrowsArgumentException()
    {
        // Arrange, Act & Assert
        var exception = Assert.Throws<ArgumentException>(() => new SettingsService(null));

        Assert.Multiple(() =>
        {
            Assert.That(exception.ParamName, Is.EqualTo("customSettingsPath"));
            Assert.That(exception.Message, Does.Contain("cannot be null or empty"));
        });
    }

    [Test]
    public void Constructor_WithEmptyCustomPath_ThrowsArgumentException()
    {
        // Arrange, Act & Assert
        var exception = Assert.Throws<ArgumentException>(() => new SettingsService(string.Empty));

        Assert.That(exception.ParamName, Is.EqualTo("customSettingsPath"));
    }

    [Test]
    public void Constructor_WithWhitespaceCustomPath_ThrowsArgumentException()
    {
        // Arrange, Act & Assert
        var exception = Assert.Throws<ArgumentException>(() => new SettingsService("   "));

        Assert.That(exception.ParamName, Is.EqualTo("customSettingsPath"));
    }

    #endregion

    #region SaveAsync Tests - Basic Operations

    [Test]
    public async Task SaveAsync_WithValidObject_SavesSuccessfully()
    {
        // Arrange
        var testObject = new TestSettings { Name = "Test", Value = 42 };
        var filename = "test.json";

        // Act
        var result = await _service.SaveAsync(testObject, filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.InstanceOf<SaveResult>());
            var saveResult = result as SaveResult;
            Assert.That(saveResult.IsSaveSuccessful, Is.True);
            Assert.That(saveResult.Success, Is.True);
            Assert.That(saveResult.FilePath, Does.Contain(filename));
            Assert.That(saveResult.HasErrors, Is.False);
            Assert.That(File.Exists(saveResult.FilePath), Is.True);
        });
    }

    [Test]
    public async Task SaveAsync_WithNullObject_ReturnsFailure()
    {
        // Arrange
        TestSettings testObject = null;
        var filename = "test.json";

        // Act
        var result = await _service.SaveAsync(testObject, filename);

        // Assert
        Assert.Multiple(() =>
        {
            var saveResult = result as SaveResult;
            Assert.That(saveResult.IsSaveSuccessful, Is.False);
            Assert.That(saveResult.Success, Is.False);
            Assert.That(saveResult.HasErrors, Is.True);
            Assert.That(saveResult.Errors[0], Does.Contain("Cannot save null object"));
        });
    }

    [Test]
    public async Task SaveAsync_WithNullFilename_ReturnsFailure()
    {
        // Arrange
        var testObject = new TestSettings { Name = "Test", Value = 42 };
        string filename = null;

        // Act
        var result = await _service.SaveAsync(testObject, filename);

        // Assert
        Assert.Multiple(() =>
        {
            var saveResult = result as SaveResult;
            Assert.That(saveResult.IsSaveSuccessful, Is.False);
            Assert.That(saveResult.HasErrors, Is.True);
            Assert.That(saveResult.Errors[0], Does.Contain("Filename cannot be null or empty"));
        });
    }

    [Test]
    public async Task SaveAsync_WithEmptyFilename_ReturnsFailure()
    {
        // Arrange
        var testObject = new TestSettings { Name = "Test", Value = 42 };
        var filename = string.Empty;

        // Act
        var result = await _service.SaveAsync(testObject, filename);

        // Assert
        Assert.Multiple(() =>
        {
            var saveResult = result as SaveResult;
            Assert.That(saveResult.IsSaveSuccessful, Is.False);
            Assert.That(saveResult.HasErrors, Is.True);
        });
    }

    [Test]
    public async Task SaveAsync_WithWhitespaceFilename_ReturnsFailure()
    {
        // Arrange
        var testObject = new TestSettings { Name = "Test", Value = 42 };
        var filename = "   ";

        // Act
        var result = await _service.SaveAsync(testObject, filename);

        // Assert
        Assert.Multiple(() =>
        {
            var saveResult = result as SaveResult;
            Assert.That(saveResult.IsSaveSuccessful, Is.False);
            Assert.That(saveResult.HasErrors, Is.True);
        });
    }

    [Test]
    public async Task SaveAsync_OverwritesExistingFile_SavesSuccessfully()
    {
        // Arrange
        var testObject1 = new TestSettings { Name = "First", Value = 1 };
        var testObject2 = new TestSettings { Name = "Second", Value = 2 };
        var filename = "overwrite.json";

        await _service.SaveAsync(testObject1, filename);

        // Act
        var result = await _service.SaveAsync(testObject2, filename);

        // Assert
        Assert.Multiple(() =>
        {
            var saveResult = result as SaveResult;
            Assert.That(saveResult.IsSaveSuccessful, Is.True);
        });

        var loaded = await _service.LoadAsync<TestSettings>(filename);
        Assert.Multiple(() =>
        {
            Assert.That(loaded, Is.Not.Null);
            Assert.That(loaded.Name, Is.EqualTo("Second"));
            Assert.That(loaded.Value, Is.EqualTo(2));
        });
    }

    [Test]
    public async Task SaveAsync_CreatesBackupOfExistingFile_BackupExists()
    {
        // Arrange
        var testObject1 = new TestSettings { Name = "Original", Value = 100 };
        var testObject2 = new TestSettings { Name = "Updated", Value = 200 };
        var filename = "backup_test.json";

        await _service.SaveAsync(testObject1, filename);

        // Act
        var result = await _service.SaveAsync(testObject2, filename);

        // Assert
        var saveResult = result as SaveResult;
        Assert.That(saveResult.IsSaveSuccessful, Is.True);

        var backupPath = saveResult.FilePath + ".bak";
        Assert.That(File.Exists(backupPath), Is.True);
    }

    [Test]
    public async Task SaveAsync_WithComplexObject_SavesAllProperties()
    {
        // Arrange
        var complexObject = new ComplexSettings
        {
            Name = "Complex",
            NestedObject = new TestSettings { Name = "Nested", Value = 99 },
            StringList = new List<string> { "item1", "item2", "item3" },
            Dictionary = new Dictionary<string, int> { { "one", 1 }, { "two", 2 } }
        };
        var filename = "complex.json";

        // Act
        var result = await _service.SaveAsync(complexObject, filename);

        // Assert
        var saveResult = result as SaveResult;
        Assert.That(saveResult.IsSaveSuccessful, Is.True);

        var loaded = await _service.LoadAsync<ComplexSettings>(filename);
        Assert.Multiple(() =>
        {
            Assert.That(loaded, Is.Not.Null);
            Assert.That(loaded.Name, Is.EqualTo("Complex"));
            Assert.That(loaded.NestedObject.Name, Is.EqualTo("Nested"));
            Assert.That(loaded.StringList, Has.Count.EqualTo(3));
            Assert.That(loaded.Dictionary["two"], Is.EqualTo(2));
        });
    }

    #endregion

    #region LoadAsync Tests - Basic Operations

    [Test]
    public async Task LoadAsync_WithExistingFile_LoadsSuccessfully()
    {
        // Arrange
        var testObject = new TestSettings { Name = "LoadTest", Value = 123 };
        var filename = "load_test.json";
        await _service.SaveAsync(testObject, filename);

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(loaded, Is.Not.Null);
            Assert.That(loaded.Name, Is.EqualTo("LoadTest"));
            Assert.That(loaded.Value, Is.EqualTo(123));
        });
    }

    [Test]
    public async Task LoadAsync_WithNonExistentFile_ReturnsNull()
    {
        // Arrange
        var filename = "nonexistent.json";

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.That(loaded, Is.Null);
    }

    [Test]
    public async Task LoadAsync_WithNullFilename_ReturnsNull()
    {
        // Arrange
        string filename = null;

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.That(loaded, Is.Null);
    }

    [Test]
    public async Task LoadAsync_WithEmptyFilename_ReturnsNull()
    {
        // Arrange
        var filename = string.Empty;

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.That(loaded, Is.Null);
    }

    [Test]
    public async Task LoadAsync_WithWhitespaceFilename_ReturnsNull()
    {
        // Arrange
        var filename = "   ";

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.That(loaded, Is.Null);
    }

    [Test]
    public async Task LoadAsync_WithCorruptedFile_FallsBackToBackup()
    {
        // Arrange
        var testObject = new TestSettings { Name = "Backup", Value = 999 };
        var filename = "corrupted.json";

        // First save creates the file
        await _service.SaveAsync(testObject, filename);
        
        // Second save creates a backup of the first save
        await _service.SaveAsync(testObject, filename);

        var filePath = _service.GetSettingsPath(filename);
        var backupPath = filePath + ".bak";

        // Verify backup was created
        Assert.That(File.Exists(backupPath), Is.True, "Backup file should exist after second save");

        // Corrupt the main file
        await File.WriteAllTextAsync(filePath, "{ corrupted json }");

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(loaded, Is.Not.Null);
            Assert.That(loaded.Name, Is.EqualTo("Backup"));
            Assert.That(loaded.Value, Is.EqualTo(999));
        });
    }

    [Test]
    public async Task LoadAsync_WithBothFilesCorrupted_ReturnsNull()
    {
        // Arrange
        var filename = "both_corrupted.json";
        var filePath = _service.GetSettingsPath(filename);
        var backupPath = filePath + ".bak";

        await File.WriteAllTextAsync(filePath, "{ corrupted json }");
        await File.WriteAllTextAsync(backupPath, "{ also corrupted }");

        // Act
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.That(loaded, Is.Null);
    }

    #endregion

    #region GetSettingsPath Tests

    [Test]
    public void GetSettingsPath_WithFilename_ReturnsFullPath()
    {
        // Arrange
        var filename = "settings.json";

        // Act
        var path = _service.GetSettingsPath(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(path, Does.Contain(_testDirectory));
            Assert.That(path, Does.EndWith(filename));
            Assert.That(Path.IsPathRooted(path), Is.True);
        });
    }

    [Test]
    public void GetSettingsPath_WithSubdirectoryFilename_CombinesProperly()
    {
        // Arrange
        var filename = Path.Combine("subfolder", "settings.json");

        // Act
        var path = _service.GetSettingsPath(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(path, Does.Contain(_testDirectory));
            Assert.That(path, Does.Contain("subfolder"));
            Assert.That(path, Does.EndWith("settings.json"));
        });
    }

    #endregion

    #region SettingsFileExists Tests

    [Test]
    public async Task SettingsFileExists_WithExistingFile_ReturnsTrue()
    {
        // Arrange
        var testObject = new TestSettings { Name = "Exists", Value = 1 };
        var filename = "exists.json";
        await _service.SaveAsync(testObject, filename);

        // Act
        var exists = _service.SettingsFileExists(filename);

        // Assert
        Assert.That(exists, Is.True);
    }

    [Test]
    public void SettingsFileExists_WithNonExistentFile_ReturnsFalse()
    {
        // Arrange
        var filename = "does_not_exist.json";

        // Act
        var exists = _service.SettingsFileExists(filename);

        // Assert
        Assert.That(exists, Is.False);
    }

    [Test]
    public void SettingsFileExists_WithNullFilename_ReturnsFalse()
    {
        // Arrange
        string filename = null;

        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => _service.SettingsFileExists(filename));
    }

    #endregion

    #region SettingsDirectory Tests

    [Test]
    public void SettingsDirectory_ReturnsConfiguredDirectory()
    {
        // Arrange & Act
        var directory = _service.SettingsDirectory;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(directory, Is.EqualTo(_testDirectory));
            Assert.That(Directory.Exists(directory), Is.True);
        });
    }

    #endregion

    #region Integration Tests

    [Test]
    public async Task IntegrationTest_SaveAndLoadCycle_PreservesData()
    {
        // This test verifies a complete save/load cycle
        
        // Arrange
        var original = new TestSettings { Name = "Integration", Value = 12345 };
        var filename = "integration.json";

        // Act - Save
        var saveResult = await _service.SaveAsync(original, filename) as SaveResult;
        Assert.That(saveResult.IsSaveSuccessful, Is.True);

        // Act - Load
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(loaded, Is.Not.Null);
            Assert.That(loaded.Name, Is.EqualTo(original.Name));
            Assert.That(loaded.Value, Is.EqualTo(original.Value));
        });
    }

    [Test]
    public async Task IntegrationTest_MultipleFiles_IndependentOfEachOther()
    {
        // This test verifies that multiple settings files work independently
        
        // Arrange
        var settings1 = new TestSettings { Name = "File1", Value = 100 };
        var settings2 = new TestSettings { Name = "File2", Value = 200 };
        var settings3 = new TestSettings { Name = "File3", Value = 300 };

        // Act
        await _service.SaveAsync(settings1, "file1.json");
        await _service.SaveAsync(settings2, "file2.json");
        await _service.SaveAsync(settings3, "file3.json");

        var loaded1 = await _service.LoadAsync<TestSettings>("file1.json");
        var loaded2 = await _service.LoadAsync<TestSettings>("file2.json");
        var loaded3 = await _service.LoadAsync<TestSettings>("file3.json");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(loaded1.Name, Is.EqualTo("File1"));
            Assert.That(loaded1.Value, Is.EqualTo(100));
            Assert.That(loaded2.Name, Is.EqualTo("File2"));
            Assert.That(loaded2.Value, Is.EqualTo(200));
            Assert.That(loaded3.Name, Is.EqualTo("File3"));
            Assert.That(loaded3.Value, Is.EqualTo(300));
        });
    }

    [Test]
    public async Task IntegrationTest_SaveOverwriteLoad_UsesLatestData()
    {
        // This test verifies that overwriting works correctly
        
        // Arrange
        var original = new TestSettings { Name = "Original", Value = 1 };
        var updated = new TestSettings { Name = "Updated", Value = 2 };
        var filename = "overwrite_cycle.json";

        // Act
        await _service.SaveAsync(original, filename);
        await _service.SaveAsync(updated, filename);
        var loaded = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(loaded.Name, Is.EqualTo("Updated"));
            Assert.That(loaded.Value, Is.EqualTo(2));
        });
    }

    [Test]
    public async Task IntegrationTest_SaveWithBackupRecovery_RecoversPreviousVersion()
    {
        // This test verifies backup recovery mechanism
        
        // Arrange
        var version1 = new TestSettings { Name = "Version1", Value = 100 };
        var version2 = new TestSettings { Name = "Version2", Value = 200 };
        var filename = "backup_recovery.json";

        await _service.SaveAsync(version1, filename);
        await _service.SaveAsync(version2, filename);

        var filePath = _service.GetSettingsPath(filename);
        await File.WriteAllTextAsync(filePath, "{ corrupted }");

        // Act
        var recovered = await _service.LoadAsync<TestSettings>(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(recovered, Is.Not.Null);
            Assert.That(recovered.Name, Is.EqualTo("Version1"));
            Assert.That(recovered.Value, Is.EqualTo(100));
        });
    }

    [Test]
    public async Task IntegrationTest_ComplexObjectRoundTrip_PreservesStructure()
    {
        // This test verifies complex nested objects are preserved
        
        // Arrange
        var complex = new ComplexSettings
        {
            Name = "ComplexTest",
            NestedObject = new TestSettings { Name = "Nested", Value = 777 },
            StringList = new List<string> { "alpha", "beta", "gamma" },
            Dictionary = new Dictionary<string, int> 
            { 
                { "first", 1 }, 
                { "second", 2 }, 
                { "third", 3 } 
            }
        };
        var filename = "complex_roundtrip.json";

        // Act
        await _service.SaveAsync(complex, filename);
        var loaded = await _service.LoadAsync<ComplexSettings>(filename);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(loaded, Is.Not.Null);
            Assert.That(loaded.Name, Is.EqualTo("ComplexTest"));
            Assert.That(loaded.NestedObject.Name, Is.EqualTo("Nested"));
            Assert.That(loaded.NestedObject.Value, Is.EqualTo(777));
            Assert.That(loaded.StringList, Has.Count.EqualTo(3));
            Assert.That(loaded.StringList[1], Is.EqualTo("beta"));
            Assert.That(loaded.Dictionary, Has.Count.EqualTo(3));
            Assert.That(loaded.Dictionary["second"], Is.EqualTo(2));
        });
    }

    #endregion

    #region Helper Classes

    private class TestSettings
    {
        public string Name { get; set; }
        public int Value { get; set; }
    }

    private class ComplexSettings
    {
        public string Name { get; set; }
        public TestSettings NestedObject { get; set; }
        public List<string> StringList { get; set; }
        public Dictionary<string, int> Dictionary { get; set; }
    }

    #endregion
}
}
