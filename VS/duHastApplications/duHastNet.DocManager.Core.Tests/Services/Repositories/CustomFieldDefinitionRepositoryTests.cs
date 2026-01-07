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
/// Tests for CustomFieldDefinitionRepository
/// This test class covers all repository operations including:
/// - CRUD operations (inherited from BaseRepository)
/// - Custom queries specific to CustomFieldDefinition
/// - Active/Inactive filtering
/// - Property name uniqueness checks
/// </summary>
[TestFixture]
public class CustomFieldDefinitionRepositoryTests
{
    private SQLiteAsyncConnection _connection;
    private CustomFieldDefinitionRepository _repository;
    private string _testDatabasePath;

    [SetUp]
    public async Task Setup()
    {
        _testDatabasePath = Path.Combine(Path.GetTempPath(), "CustomFieldDefinitionRepositoryTests", $"{Guid.NewGuid()}.db");
        var directory = Path.GetDirectoryName(_testDatabasePath);
        if (!Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        _connection = new SQLiteAsyncConnection(_testDatabasePath);
        await _connection.CreateTableAsync<CustomFieldDefinition>();
        _repository = new CustomFieldDefinitionRepository(_connection);
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_connection != null)
        {
            await _connection.CloseAsync();
        }

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
        var repository = new CustomFieldDefinitionRepository(_connection);

        // Assert
        Assert.That(repository, Is.Not.Null);
    }

    #endregion

    #region GetByPropertyNameAsync Tests

    [Test]
    public async Task GetByPropertyNameAsync_WithExistingPropertyName_ReturnsDefinition()
    {
        // Arrange
        var propertyName = "ProjectPhase";
        var definition = new CustomFieldDefinition(propertyName, true);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.GetByPropertyNameAsync(propertyName);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.PropertyName, Is.EqualTo(propertyName));
            Assert.That(result.IsActive, Is.True);
        });
    }

    [Test]
    public async Task GetByPropertyNameAsync_WithNonExistentPropertyName_ReturnsNull()
    {
        // Arrange
        var propertyName = "NonExistentProperty";

        // Act
        var result = await _repository.GetByPropertyNameAsync(propertyName);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task GetByPropertyNameAsync_WithMultipleDefinitions_ReturnsCorrectOne()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ProjectPhase", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);
        var definition3 = new CustomFieldDefinition("Zone", false);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var result = await _repository.GetByPropertyNameAsync("DisciplineCode");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.PropertyName, Is.EqualTo("DisciplineCode"));
            Assert.That(result.IsActive, Is.True);
        });
    }

    #endregion

    #region GetActiveAsync Tests

    [Test]
    public async Task GetActiveAsync_WithNoDefinitions_ReturnsEmptyList()
    {
        // Arrange & Act
        var result = await _repository.GetActiveAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.Empty);
        });
    }

    [Test]
    public async Task GetActiveAsync_WithOnlyActiveDefinitions_ReturnsAll()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ProjectPhase", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);
        var definition3 = new CustomFieldDefinition("Zone", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var result = await _repository.GetActiveAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(3));
            Assert.That(result.All(d => d.IsActive), Is.True);
        });
    }

    [Test]
    public async Task GetActiveAsync_WithMixedActiveInactive_ReturnsOnlyActive()
    {
        // Arrange
        var activeDefinition1 = new CustomFieldDefinition("ProjectPhase", true);
        var activeDefinition2 = new CustomFieldDefinition("DisciplineCode", true);
        var inactiveDefinition1 = new CustomFieldDefinition("OldField1", false);
        var inactiveDefinition2 = new CustomFieldDefinition("OldField2", false);

        await _repository.InsertAsync(activeDefinition1);
        await _repository.InsertAsync(activeDefinition2);
        await _repository.InsertAsync(inactiveDefinition1);
        await _repository.InsertAsync(inactiveDefinition2);

        // Act
        var result = await _repository.GetActiveAsync();

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
    public async Task GetActiveAsync_ResultsOrderedByPropertyName()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Zone", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);
        var definition3 = new CustomFieldDefinition("ProjectPhase", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var result = await _repository.GetActiveAsync();

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

    #region GetInactiveAsync Tests

    [Test]
    public async Task GetInactiveAsync_WithNoDefinitions_ReturnsEmptyList()
    {
        // Arrange & Act
        var result = await _repository.GetInactiveAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.Empty);
        });
    }

    [Test]
    public async Task GetInactiveAsync_WithOnlyInactiveDefinitions_ReturnsAll()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("OldField1", false);
        var definition2 = new CustomFieldDefinition("OldField2", false);
        var definition3 = new CustomFieldDefinition("OldField3", false);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var result = await _repository.GetInactiveAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(3));
            Assert.That(result.All(d => !d.IsActive), Is.True);
        });
    }

    [Test]
    public async Task GetInactiveAsync_WithMixedActiveInactive_ReturnsOnlyInactive()
    {
        // Arrange
        var activeDefinition1 = new CustomFieldDefinition("ProjectPhase", true);
        var activeDefinition2 = new CustomFieldDefinition("DisciplineCode", true);
        var inactiveDefinition1 = new CustomFieldDefinition("OldField1", false);
        var inactiveDefinition2 = new CustomFieldDefinition("OldField2", false);

        await _repository.InsertAsync(activeDefinition1);
        await _repository.InsertAsync(activeDefinition2);
        await _repository.InsertAsync(inactiveDefinition1);
        await _repository.InsertAsync(inactiveDefinition2);

        // Act
        var result = await _repository.GetInactiveAsync();

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
    public async Task GetInactiveAsync_ResultsOrderedByPropertyName()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ZOldField", false);
        var definition2 = new CustomFieldDefinition("BOldField", false);
        var definition3 = new CustomFieldDefinition("MOldField", false);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var result = await _repository.GetInactiveAsync();

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

    #region PropertyNameExistsAsync Tests

    [Test]
    public async Task PropertyNameExistsAsync_WithExistingPropertyName_ReturnsTrue()
    {
        // Arrange
        var propertyName = "ProjectPhase";
        var definition = new CustomFieldDefinition(propertyName, true);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.PropertyNameExistsAsync(propertyName);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task PropertyNameExistsAsync_WithNonExistentPropertyName_ReturnsFalse()
    {
        // Arrange
        var propertyName = "NonExistentProperty";

        // Act
        var result = await _repository.PropertyNameExistsAsync(propertyName);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task PropertyNameExistsAsync_IsCaseInsensitive_ReturnsTrue()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var resultLower = await _repository.PropertyNameExistsAsync("projectphase");
        var resultUpper = await _repository.PropertyNameExistsAsync("PROJECTPHASE");
        var resultMixed = await _repository.PropertyNameExistsAsync("PrOjEcTpHaSe");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(resultLower, Is.True);
            Assert.That(resultUpper, Is.True);
            Assert.That(resultMixed, Is.True);
        });
    }

    [Test]
    public async Task PropertyNameExistsAsync_WithInactiveDefinition_StillReturnsTrue()
    {
        // Arrange
        var propertyName = "OldField";
        var definition = new CustomFieldDefinition(propertyName, false);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.PropertyNameExistsAsync(propertyName);

        // Assert
        Assert.That(result, Is.True);
    }

    #endregion

    #region UpdateIsActiveAsync Tests

    [Test]
    public async Task UpdateIsActiveAsync_WithExistingDefinition_UpdatesStatus()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var rowsAffected = await _repository.UpdateIsActiveAsync(definition.Id, false);

        // Assert
        var updated = await _repository.GetByIdAsync(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(updated, Is.Not.Null);
            Assert.That(updated.IsActive, Is.False);
        });
    }

    [Test]
    public async Task UpdateIsActiveAsync_TogglingMultipleTimes_UpdatesCorrectly()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act - Toggle to inactive
        await _repository.UpdateIsActiveAsync(definition.Id, false);
        var afterFirstToggle = await _repository.GetByIdAsync(definition.Id);

        // Act - Toggle back to active
        await _repository.UpdateIsActiveAsync(definition.Id, true);
        var afterSecondToggle = await _repository.GetByIdAsync(definition.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(afterFirstToggle.IsActive, Is.False);
            Assert.That(afterSecondToggle.IsActive, Is.True);
        });
    }

    [Test]
    public async Task UpdateIsActiveAsync_WithNonExistentId_ReturnsZero()
    {
        // Arrange
        var nonExistentId = 99999;

        // Act
        var rowsAffected = await _repository.UpdateIsActiveAsync(nonExistentId, false);

        // Assert
        Assert.That(rowsAffected, Is.EqualTo(0));
    }

    [Test]
    public async Task UpdateIsActiveAsync_OnlyUpdatesSpecifiedDefinition()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", true);
        var definition3 = new CustomFieldDefinition("Field3", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        await _repository.UpdateIsActiveAsync(definition2.Id, false);

        // Assert
        var field1 = await _repository.GetByIdAsync(definition1.Id);
        var field2 = await _repository.GetByIdAsync(definition2.Id);
        var field3 = await _repository.GetByIdAsync(definition3.Id);

        Assert.Multiple(() =>
        {
            Assert.That(field1.IsActive, Is.True);
            Assert.That(field2.IsActive, Is.False);
            Assert.That(field3.IsActive, Is.True);
        });
    }

    #endregion

    #region Inherited BaseRepository Method Tests

    [Test]
    public async Task InsertAsync_WithValidDefinition_InsertsSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);

        // Act
        var rowsAffected = await _repository.InsertAsync(definition);

        // Assert
        var retrieved = await _repository.GetByIdAsync(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(definition.Id, Is.GreaterThan(0));
            Assert.That(retrieved, Is.Not.Null);
            Assert.That(retrieved.PropertyName, Is.EqualTo("ProjectPhase"));
        });
    }

    [Test]
    public async Task GetByIdAsync_WithExistingId_ReturnsDefinition()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.GetByIdAsync(definition.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.Id, Is.EqualTo(definition.Id));
            Assert.That(result.PropertyName, Is.EqualTo("ProjectPhase"));
        });
    }

    [Test]
    public async Task GetByIdAsync_WithNonExistentId_ReturnsNull()
    {
        // Arrange
        var nonExistentId = 99999;

        // Act
        var result = await _repository.GetByIdAsync(nonExistentId);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task GetAllAsync_WithMultipleDefinitions_ReturnsAll()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var result = await _repository.GetAllAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
    }

    [Test]
    public async Task GetAllAsync_WithEmptyTable_ReturnsEmptyList()
    {
        // Arrange & Act
        var result = await _repository.GetAllAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Is.Empty);
        });
    }

    [Test]
    public async Task UpdateAsync_WithModifiedDefinition_UpdatesSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Modify the definition
        definition.PropertyName = "ProjectStage";
        definition.IsActive = false;

        // Act
        var rowsAffected = await _repository.UpdateAsync(definition);

        // Assert
        var updated = await _repository.GetByIdAsync(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(updated.PropertyName, Is.EqualTo("ProjectStage"));
            Assert.That(updated.IsActive, Is.False);
        });
    }

    [Test]
    public async Task DeleteAsync_WithEntity_DeletesSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var rowsAffected = await _repository.DeleteAsync(definition);

        // Assert
        var deleted = await _repository.GetByIdAsync(definition.Id);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(deleted, Is.Null);
        });
    }

    [Test]
    public async Task DeleteAsync_WithId_DeletesSuccessfully()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);
        var idToDelete = definition.Id;

        // Act
        var rowsAffected = await _repository.DeleteAsync(idToDelete);

        // Assert
        var deleted = await _repository.GetByIdAsync(idToDelete);
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(1));
            Assert.That(deleted, Is.Null);
        });
    }

    [Test]
    public async Task CountAsync_WithMultipleDefinitions_ReturnsCorrectCount()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var count = await _repository.CountAsync();

        // Assert
        Assert.That(count, Is.EqualTo(3));
    }

    [Test]
    public async Task CountAsync_WithEmptyTable_ReturnsZero()
    {
        // Arrange & Act
        var count = await _repository.CountAsync();

        // Assert
        Assert.That(count, Is.EqualTo(0));
    }

    [Test]
    public async Task CountAsync_WithPredicate_ReturnsFilteredCount()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("Field1", true);
        var definition2 = new CustomFieldDefinition("Field2", false);
        var definition3 = new CustomFieldDefinition("Field3", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var activeCount = await _repository.CountAsync(d => d.IsActive);

        // Assert
        Assert.That(activeCount, Is.EqualTo(2));
    }

    [Test]
    public async Task FindAsync_WithPredicate_ReturnsMatchingDefinitions()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ProjectPhase", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", false);
        var definition3 = new CustomFieldDefinition("Zone", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);
        await _repository.InsertAsync(definition3);

        // Act
        var activeDefinitions = await _repository.FindAsync(d => d.IsActive);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(activeDefinitions, Has.Count.EqualTo(2));
            Assert.That(activeDefinitions.All(d => d.IsActive), Is.True);
        });
    }

    [Test]
    public async Task FirstOrDefaultAsync_WithMatchingPredicate_ReturnsFirstMatch()
    {
        // Arrange
        var definition1 = new CustomFieldDefinition("ProjectPhase", true);
        var definition2 = new CustomFieldDefinition("DisciplineCode", true);

        await _repository.InsertAsync(definition1);
        await _repository.InsertAsync(definition2);

        // Act
        var result = await _repository.FirstOrDefaultAsync(d => d.IsActive);

        // Assert
        Assert.That(result, Is.Not.Null);
    }

    [Test]
    public async Task FirstOrDefaultAsync_WithNoMatch_ReturnsNull()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.FirstOrDefaultAsync(d => !d.IsActive);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task ExistsAsync_WithMatchingPredicate_ReturnsTrue()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.ExistsAsync(d => d.PropertyName == "ProjectPhase");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task ExistsAsync_WithNoMatch_ReturnsFalse()
    {
        // Arrange
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);

        // Act
        var result = await _repository.ExistsAsync(d => d.PropertyName == "NonExistent");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task InsertAllAsync_WithMultipleDefinitions_InsertsAll()
    {
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Field1", true),
            new CustomFieldDefinition("Field2", false),
            new CustomFieldDefinition("Field3", true)
        };

        // Act
        var rowsAffected = await _repository.InsertAllAsync(definitions);

        // Assert
        var allDefinitions = await _repository.GetAllAsync();
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(3));
            Assert.That(allDefinitions, Has.Count.EqualTo(3));
        });
    }

    [Test]
    public async Task UpdateAllAsync_WithMultipleDefinitions_UpdatesAll()
    {
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Field1", true),
            new CustomFieldDefinition("Field2", true),
            new CustomFieldDefinition("Field3", true)
        };
        await _repository.InsertAllAsync(definitions);

        // Modify all definitions
        foreach (var def in definitions)
        {
            def.IsActive = false;
        }

        // Act
        var rowsAffected = await _repository.UpdateAllAsync(definitions);

        // Assert
        var allDefinitions = await _repository.GetAllAsync();
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(3));
            Assert.That(allDefinitions.All(d => !d.IsActive), Is.True);
        });
    }

    [Test]
    public async Task DeleteAllAsync_WithMultipleDefinitions_DeletesAll()
    {
        // Arrange
        var definitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition("Field1", true),
            new CustomFieldDefinition("Field2", false),
            new CustomFieldDefinition("Field3", true)
        };
        await _repository.InsertAllAsync(definitions);

        // Act
        var rowsAffected = await _repository.DeleteAllAsync(definitions);

        // Assert
        var remainingCount = await _repository.CountAsync();
        Assert.Multiple(() =>
        {
            Assert.That(rowsAffected, Is.EqualTo(3));
            Assert.That(remainingCount, Is.EqualTo(0));
        });
    }

    #endregion

    #region Integration Tests

    [Test]
    public async Task IntegrationTest_CompleteLifecycle_WorksCorrectly()
    {
        // This test verifies a complete lifecycle of a custom field definition:
        // Create -> Read -> Update -> Toggle Active Status -> Delete
        
        // Arrange - Create
        var definition = new CustomFieldDefinition("ProjectPhase", true);
        await _repository.InsertAsync(definition);
        
        // Act & Assert - Read
        var retrieved = await _repository.GetByPropertyNameAsync("ProjectPhase");
        Assert.Multiple(() =>
        {
            Assert.That(retrieved, Is.Not.Null);
            Assert.That(retrieved.PropertyName, Is.EqualTo("ProjectPhase"));
            Assert.That(retrieved.IsActive, Is.True);
        });

        // Act & Assert - Update
        retrieved.PropertyName = "ProjectStage";
        await _repository.UpdateAsync(retrieved);
        var afterUpdate = await _repository.GetByIdAsync(retrieved.Id);
        Assert.That(afterUpdate.PropertyName, Is.EqualTo("ProjectStage"));

        // Act & Assert - Toggle Active Status
        await _repository.UpdateIsActiveAsync(retrieved.Id, false);
        var afterToggle = await _repository.GetByIdAsync(retrieved.Id);
        Assert.That(afterToggle.IsActive, Is.False);

        // Act & Assert - Verify in inactive list
        var inactiveList = await _repository.GetInactiveAsync();
        Assert.That(inactiveList, Has.Count.EqualTo(1));

        // Act & Assert - Delete
        await _repository.DeleteAsync(retrieved.Id);
        var afterDelete = await _repository.GetByIdAsync(retrieved.Id);
        Assert.That(afterDelete, Is.Null);
    }

    [Test]
    public async Task IntegrationTest_MultipleDefinitions_FilteringAndSorting()
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
        await _repository.InsertAllAsync(definitions);

        // Act & Assert - Get Active (should be sorted)
        var activeList = await _repository.GetActiveAsync();
        Assert.Multiple(() =>
        {
            Assert.That(activeList, Has.Count.EqualTo(3));
            Assert.That(activeList[0].PropertyName, Is.EqualTo("DisciplineCode"));
            Assert.That(activeList[1].PropertyName, Is.EqualTo("ProjectPhase"));
            Assert.That(activeList[2].PropertyName, Is.EqualTo("Zone"));
        });

        // Act & Assert - Get Inactive (should be sorted)
        var inactiveList = await _repository.GetInactiveAsync();
        Assert.Multiple(() =>
        {
            Assert.That(inactiveList, Has.Count.EqualTo(2));
            Assert.That(inactiveList[0].PropertyName, Is.EqualTo("OldField1"));
            Assert.That(inactiveList[1].PropertyName, Is.EqualTo("OldField2"));
        });

        // Act & Assert - Property name exists check
        var exists = await _repository.PropertyNameExistsAsync("projectphase");
        Assert.That(exists, Is.True);

        // Act & Assert - Toggle one active to inactive
        var projectPhase = await _repository.GetByPropertyNameAsync("ProjectPhase");
        await _repository.UpdateIsActiveAsync(projectPhase.Id, false);

        var newActiveList = await _repository.GetActiveAsync();
        var newInactiveList = await _repository.GetInactiveAsync();

        Assert.Multiple(() =>
        {
            Assert.That(newActiveList, Has.Count.EqualTo(2));
            Assert.That(newInactiveList, Has.Count.EqualTo(3));
        });
    }

    #endregion
}
