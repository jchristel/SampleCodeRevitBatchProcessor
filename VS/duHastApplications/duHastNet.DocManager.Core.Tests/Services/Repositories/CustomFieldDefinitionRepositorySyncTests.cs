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
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

/// <summary>
/// Tests for CustomFieldDefinitionRepositorySync
/// This test class covers all repository operations including:
/// - CRUD operations (inherited from BaseRepositorySync)
/// - Custom queries specific to CustomFieldDefinition
/// - Active/Inactive filtering
/// - Property name uniqueness checks
/// </summary>
[TestFixture]
public class CustomFieldDefinitionRepositorySyncTests
{
    private SQLiteConnection _connection;
    private CustomFieldDefinitionRepositorySync _repository;
    private string _testDatabasePath;

    [SetUp]
    public void Setup()
    {
        _testDatabasePath = Path.Combine(Path.GetTempPath(), "CustomFieldDefinitionRepositorySyncTests", $"{Guid.NewGuid()}.db");
        var directory = Path.GetDirectoryName(_testDatabasePath);
        if (!Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        _connection = new SQLiteConnection(_testDatabasePath);
        _connection.CreateTable<CustomFieldDefinition>();
        _repository = new CustomFieldDefinitionRepositorySync(_connection);
    }

    [TearDown]
    public void TearDown()
    {
        _connection?.Close();

        if (File.Exists(_testDatabasePath))
        {
            File.Delete(_testDatabasePath);
        }
    }

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidConnection_InitializesSuccessfully()
    {
        // Arrange & Act
        var repository = new CustomFieldDefinitionRepositorySync(_connection);

        // Assert
        Assert.That(repository, Is.Not.Null);
    }

    #endregion

    #region GetByPropertyName Tests

    [Test]
    public void GetByPropertyName_WithExistingPropertyName_ReturnsDefinition()
    {
        // Arrange
        var propertyName = "ProjectPhase";
        var definition = new CustomFieldDefinition(propertyName, true);
        _repository.Insert(definition);

        // Act
        var result = _repository.GetByPropertyName(propertyName);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.PropertyName, Is.EqualTo(propertyName));
            Assert.That(result.IsActive, Is.True);
        });
    }

    [Test]
    public void GetByPropertyName_WithNonExistentPropertyName_ReturnsNull()
    {
        // Arrange
        var propertyName = "NonExistentProperty";

        // Act
        var result = _repository.GetByPropertyName(propertyName);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetByPropertyName_WithMultipleDefinitions_ReturnsCorrectOne()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ProjectPhase", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);
        var definition3 = new CustomFieldDefinition("Zone", false);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.GetByPropertyName("DisciplineCode");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.PropertyName, Is.EqualTo("DisciplineCode"));
            Assert.That(result.IsActive, Is.True);
        });
    }

    #endregion

    #region GetActive Tests

    [Test]
    public void GetActive_WithNoDefinitions_ReturnsEmptyList()
    {
        // Arrange & Act
        var result = _repository.GetActive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.Empty);
        });
    }

    [Test]
    public void GetActive_WithOnlyActiveDefinitions_ReturnsAll()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ProjectPhase", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);
        var definition3 = new CustomFieldDefinition("Zone", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.GetActive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(3));
            Assert.That(result.All(d => d.IsActive), Is.True);
        });
    }

    [Test]
    public void GetActive_WithMixedActiveInactive_ReturnsOnlyActive()
    {
        // Arrange
        var activeDefinition1 = new CustomFieldDefinition("ProjectPhase", true);
        var activeDefinition2 = new CustomFieldDefinition("DisciplineCode", true);
        var inactiveDefinition1 = new CustomFieldDefinition("OldField1", false);
        var inactiveDefinition2 = new CustomFieldDefinition("OldField2", false);

        _repository.Insert(activeDefinition1);
        _repository.Insert(activeDefinition2);
        _repository.Insert(inactiveDefinition1);
        _repository.Insert(inactiveDefinition2);

        // Act
        var result = _repository.GetActive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(2));
            Assert.That(result.All(d => d.IsActive), Is.True);
            Assert.That(result.Any(d => d.PropertyName == "ProjectPhase"), Is.True);
            Assert.That(result.Any(d => d.PropertyName == "DisciplineCode"), Is.True);
        });
    }

    [Test]
    public void GetActive_ResultsOrderedByPropertyName()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Zone", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);
        var definition3 = new CustomFieldDefinition("ProjectPhase", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.GetActive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(3));
            Assert.That(result[0].PropertyName, Is.EqualTo("DisciplineCode"));
            Assert.That(result[1].PropertyName, Is.EqualTo("ProjectPhase"));
            Assert.That(result[2].PropertyName, Is.EqualTo("Zone"));
        });
    }

    #endregion

    #region GetInactive Tests

    [Test]
    public void GetInactive_WithNoDefinitions_ReturnsEmptyList()
    {
        // Arrange & Act
        var result = _repository.GetInactive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.Empty);
        });
    }

    [Test]
    public void GetInactive_WithOnlyInactiveDefinitions_ReturnsAll()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("OldField1", false);
        var definition2 = new CustomFieldDefinition("OldField2", false);
        var definition3 = new CustomFieldDefinition("OldField3", false);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.GetInactive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(3));
            Assert.That(result.All(d => !d.IsActive), Is.True);
        });
    }

    [Test]
    public void GetInactive_WithMixedActiveInactive_ReturnsOnlyInactive()
    {
        // Arrange
        var activeDefinition1 = new CustomFieldDefinition("ProjectPhase", true);
        var activeDefinition2 = new CustomFieldDefinition("DisciplineCode", true);
        var inactiveDefinition1 = new CustomFieldDefinition("OldField1", false);
        var inactiveDefinition2 = new CustomFieldDefinition("OldField2", false);

        _repository.Insert(activeDefinition1);
        _repository.Insert(activeDefinition2);
        _repository.Insert(inactiveDefinition1);
        _repository.Insert(inactiveDefinition2);

        // Act
        var result = _repository.GetInactive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(2));
            Assert.That(result.All(d => !d.IsActive), Is.True);
            Assert.That(result.Any(d => d.PropertyName == "OldField1"), Is.True);
            Assert.That(result.Any(d => d.PropertyName == "OldField2"), Is.True);
        });
    }

    [Test]
    public void GetInactive_ResultsOrderedByPropertyName()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ZOldField", false);
        var definition2 = new CustomFieldDefinition("BOldField", false);
        var definition3 = new CustomFieldDefinition("MOldField", false);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.GetInactive();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(3));
            Assert.That(result[0].PropertyName, Is.EqualTo("BOldField"));
            Assert.That(result[1].PropertyName, Is.EqualTo("MOldField"));
            Assert.That(result[2].PropertyName, Is.EqualTo("ZOldField"));
        });
    }

    #endregion

    #region PropertyNameExists Tests

    [Test]
    public void PropertyNameExists_WithExistingPropertyName_ReturnsTrue()
    {
        // Arrange
        var propertyName = "ProjectPhase";
        var definition = new CustomFieldDefinition(propertyName, true);
        _repository.Insert(definition);

        // Act
        var result = _repository.PropertyNameExists(propertyName);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void PropertyNameExists_WithNonExistentPropertyName_ReturnsFalse()
    {
        // Arrange
        var propertyName = "NonExistentProperty";

        // Act
        var result = _repository.PropertyNameExists(propertyName);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void PropertyNameExists_IsCaseInsensitive_ReturnsTrue()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var resultLower = _repository.PropertyNameExists("projectphase");
        var resultUpper = _repository.PropertyNameExists("PROJECTPHASE");
        var resultMixed = _repository.PropertyNameExists("PrOjEcTpHaSe");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(resultLower, Is.True);
            Assert.That(resultUpper, Is.True);
            Assert.That(resultMixed, Is.True);
        });
    }

    [Test]
    public void PropertyNameExists_WithInactiveDefinition_StillReturnsTrue()
    {
        // Arrange
        var propertyName = "OldField";
        var definition = new CustomFieldDefinition(propertyName, false);
        _repository.Insert(definition);

        // Act
        var result = _repository.PropertyNameExists(propertyName);

        // Assert
        Assert.That(result, Is.True);
    }

    #endregion

    #region UpdateIsActive Tests

    [Test]
    public void UpdateIsActive_WithExistingDefinition_UpdatesStatus()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var rowsAffected = _repository.UpdateIsActive(definition.Id, false);

        // Assert
        var updated = _repository.GetById(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(updated, Is.Not.Null);
            Assert.That(updated.IsActive, Is.False);
        });
    }

    [Test]
    public void UpdateIsActive_TogglingMultipleTimes_UpdatesCorrectly()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act - Toggle to inactive
        _repository.UpdateIsActive(definition.Id, false);
        var afterFirstToggle = _repository.GetById(definition.Id);

        // Act - Toggle back to active
        _repository.UpdateIsActive(definition.Id, true);
        var afterSecondToggle = _repository.GetById(definition.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(afterFirstToggle.IsActive, Is.False);
            Assert.That(afterSecondToggle.IsActive, Is.True);
        });
    }

    [Test]
    public void UpdateIsActive_WithNonExistentId_ReturnsZero()
    {
        // Arrange
        var nonExistentId = 99999;

        // Act
        var rowsAffected = _repository.UpdateIsActive(nonExistentId, false);

        // Assert
        Assert.That(rowsAffected, Is.EqualTo(0));
    }

    [Test]
    public void UpdateIsActive_OnlyUpdatesSpecifiedDefinition()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", true);
        var definition3 = new CustomFieldDefinition("Field3", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        _repository.UpdateIsActive(definition2.Id, false);

        // Assert
        var field1 = _repository.GetById(definition1.Id);
        var field2 = _repository.GetById(definition2.Id);
        var field3 = _repository.GetById(definition3.Id);

        Assert.Multiple(() =>
        {
            Assert.That(field1.IsActive, Is.True);
            Assert.That(field2.IsActive, Is.False);
            Assert.That(field3.IsActive, Is.True);
        });
    }

    #endregion

    #region Inherited BaseRepositorySync Method Tests

    [Test]
    public void Insert_WithValidDefinition_InsertsSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);

        // Act
        var rowsAffected = _repository.Insert(definition);

        // Assert
        var retrieved = _repository.GetById(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(definition.Id, Is.GreaterThan(0));
            Assert.That(retrieved, Is.Not.Null);
            Assert.That(retrieved.PropertyName, Is.EqualTo("ProjectPhase"));
        });
    }

    [Test]
    public void GetById_WithExistingId_ReturnsDefinition()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var result = _repository.GetById(definition.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.Id, Is.EqualTo(definition.Id));
            Assert.That(result.PropertyName, Is.EqualTo("ProjectPhase"));
        });
    }

    [Test]
    public void GetById_WithNonExistentId_ReturnsNull()
    {
        // Arrange
        var nonExistentId = 99999;

        // Act
        var result = _repository.GetById(nonExistentId);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetAll_WithMultipleDefinitions_ReturnsAll()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.GetAll();

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
    }

    [Test]
    public void GetAll_WithNoDefinitions_ReturnsEmptyList()
    {
        // Arrange & Act
        var result = _repository.GetAll();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.Empty);
        });
    }

    [Test]
    public void Update_WithModifiedDefinition_UpdatesSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("OriginalName", true);
        _repository.Insert(definition);

        // Modify
        definition.PropertyName = "UpdatedName";
        definition.IsActive = false;

        // Act
        var rowsAffected = _repository.Update(definition);

        // Assert
        var updated = _repository.GetById(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(updated.PropertyName, Is.EqualTo("UpdatedName"));
            Assert.That(updated.IsActive, Is.False);
        });
    }

    [Test]
    public void Delete_WithExistingDefinition_DeletesSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var rowsAffected = _repository.Delete(definition);

        // Assert
        var deleted = _repository.GetById(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(deleted, Is.Null);
        });
    }

    [Test]
    public void Delete_ById_DeletesSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);
        var definitionId = definition.Id;

        // Act
        var rowsAffected = _repository.Delete(definitionId);

        // Assert
        var deleted = _repository.GetById(definitionId);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(deleted, Is.Null);
        });
    }

    [Test]
    public void Count_WithDefinitions_ReturnsCorrectCount()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.Count();

        // Assert
        Assert.That(result, Is.EqualTo(3));
    }

    [Test]
    public void Count_WithPredicate_ReturnsCorrectCount()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.Count(d => d.IsActive);

        // Assert
        Assert.That(result, Is.EqualTo(2));
    }

    [Test]
    public void Find_WithPredicate_ReturnsMatchingDefinitions()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);
        _repository.Insert(definition3);

        // Act
        var result = _repository.Find(d => d.IsActive);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(2));
            Assert.That(result.All(d => d.IsActive), Is.True);
        });
    }

    [Test]
    public void FirstOrDefault_WithMatchingPredicate_ReturnsFirstMatch()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", true);

        _repository.Insert(definition1);
        _repository.Insert(definition2);

        // Act
        var result = _repository.FirstOrDefault(d => d.IsActive);

        // Assert
        Assert.That(result, Is.Not.Null);
    }

    [Test]
    public void FirstOrDefault_WithNoMatch_ReturnsNull()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var result = _repository.FirstOrDefault(d => !d.IsActive);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void Exists_WithMatchingPredicate_ReturnsTrue()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var result = _repository.Exists(d => d.PropertyName == "ProjectPhase");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void Exists_WithNoMatch_ReturnsFalse()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);

        // Act
        var result = _repository.Exists(d => d.PropertyName == "NonExistent");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void InsertAll_WithMultipleDefinitions_InsertsAll()
    {
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Field1", true),
            new CustomFieldDefinition("Field2", false),
            new CustomFieldDefinition("Field3", true)
        };

        // Act
        var rowsAffected = _repository.InsertAll(definitions);

        // Assert
        var allDefinitions = _repository.GetAll();
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(3));
            Assert.That(allDefinitions, Has.Count.EqualTo(3));
        });
    }

    [Test]
    public void UpdateAll_WithMultipleDefinitions_UpdatesAll()
    {
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Field1", true),
            new CustomFieldDefinition("Field2", true),
            new CustomFieldDefinition("Field3", true)
        };
        _repository.InsertAll(definitions);

        // Modify all definitions
        foreach (var def in definitions)
        {
            def.IsActive = false;
        }

        // Act
        var rowsAffected = _repository.UpdateAll(definitions);

        // Assert
        var allDefinitions = _repository.GetAll();
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(3));
            Assert.That(allDefinitions.All(d => !d.IsActive), Is.True);
        });
    }

    [Test]
    public void DeleteAll_WithMultipleDefinitions_DeletesAll()
    {
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Field1", true),
            new CustomFieldDefinition("Field2", false),
            new CustomFieldDefinition("Field3", true)
        };
        _repository.InsertAll(definitions);

        // Act
        var rowsAffected = _repository.DeleteAll(definitions);

        // Assert
        var remainingCount = _repository.Count();
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(3));
            Assert.That(remainingCount, Is.EqualTo(0));
        });
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_CompleteLifecycle_WorksCorrectly()
    {
        // This test verifies a complete lifecycle of a custom field definition:
        // Create -> Read -> Update -> Toggle Active Status -> Delete
        
        // Arrange - Create
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        _repository.Insert(definition);
        
        // Act & Assert - Read
        var retrieved = _repository.GetByPropertyName("ProjectPhase");
        Assert.Multiple(() =>
        {
            Assert.That(retrieved, Is.Not.Null);
            Assert.That(retrieved.PropertyName, Is.EqualTo("ProjectPhase"));
            Assert.That(retrieved.IsActive, Is.True);
        });

        // Act & Assert - Update
        retrieved.PropertyName = "ProjectStage";
        _repository.Update(retrieved);
        var afterUpdate = _repository.GetById(retrieved.Id);
        Assert.That(afterUpdate.PropertyName, Is.EqualTo("ProjectStage"));

        // Act & Assert - Toggle Active Status
        _repository.UpdateIsActive(retrieved.Id, false);
        var afterToggle = _repository.GetById(retrieved.Id);
        Assert.That(afterToggle.IsActive, Is.False);

        // Act & Assert - Verify in inactive list
        var inactiveList = _repository.GetInactive();
        Assert.That(inactiveList, Has.Count.EqualTo(1));

        // Act & Assert - Delete
        _repository.Delete(retrieved.Id);
        var afterDelete = _repository.GetById(retrieved.Id);
        Assert.That(afterDelete, Is.Null);
    }

    [Test]
    public void IntegrationTest_MultipleDefinitions_FilteringAndSorting()
    {
        // This test verifies multiple definitions work correctly with filtering and sorting
        
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Zone", true),
            new CustomFieldDefinition("ProjectPhase", true),
            new CustomFieldDefinition("OldField1", false),
            new CustomFieldDefinition("DisciplineCode", true),
            new CustomFieldDefinition("OldField2", false)
        };
        _repository.InsertAll(definitions);

        // Act & Assert - Get Active (should be sorted)
        var activeList = _repository.GetActive();
        Assert.Multiple(() =>
        {
            Assert.That(activeList, Has.Count.EqualTo(3));
            Assert.That(activeList[0].PropertyName, Is.EqualTo("DisciplineCode"));
            Assert.That(activeList[1].PropertyName, Is.EqualTo("ProjectPhase"));
            Assert.That(activeList[2].PropertyName, Is.EqualTo("Zone"));
        });

        // Act & Assert - Get Inactive (should be sorted)
        var inactiveList = _repository.GetInactive();
        Assert.Multiple(() =>
        {
            Assert.That(inactiveList, Has.Count.EqualTo(2));
            Assert.That(inactiveList[0].PropertyName, Is.EqualTo("OldField1"));
            Assert.That(inactiveList[1].PropertyName, Is.EqualTo("OldField2"));
        });

        // Act & Assert - Property name exists check
        var exists = _repository.PropertyNameExists("projectphase");
        Assert.That(exists, Is.True);

        // Act & Assert - Toggle one active to inactive
        var projectPhase = _repository.GetByPropertyName("ProjectPhase");
        _repository.UpdateIsActive(projectPhase.Id, false);

        var newActiveList = _repository.GetActive();
        var newInactiveList = _repository.GetInactive();

        Assert.Multiple(() =>
        {
            Assert.That(newActiveList, Has.Count.EqualTo(2));
            Assert.That(newInactiveList, Has.Count.EqualTo(3));
        });
    }

    #endregion
}
