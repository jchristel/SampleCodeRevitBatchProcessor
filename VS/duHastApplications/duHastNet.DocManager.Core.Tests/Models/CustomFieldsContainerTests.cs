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
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Tests.Models.Database;

[TestFixture]
public class CustomFieldsContainerTests
{
    private CustomFieldsContainer _container;

    [SetUp]
    public void Setup()
    {
        _container = new CustomFieldsContainer();
    }

    #region Constructor Tests

    [Test]
    public void Constructor_InitializesWithEmptyCollection()
    {
        // Arrange & Act
        var container = new CustomFieldsContainer();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(container, Is.Not.Null);
            Assert.That(container.CustomFieldsCount, Is.EqualTo(0));
            Assert.That(container.GetAllCustomFields(), Is.Empty);
        });
    }

    #endregion

    #region AddCustomField Tests

    [Test]
    public void AddCustomField_WithValidField_IncreasesCount()
    {
        // Arrange
        var field = new CustomFieldDefinition("Discipline", true);

        // Act
        _container.AddCustomField(field);

        // Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(1));
    }

    [Test]
    public void AddCustomField_WithNullField_ThrowsArgumentNullException()
    {
        // Arrange
        CustomFieldDefinition field = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => _container.AddCustomField(field));

        Assert.That(exception.ParamName, Is.EqualTo("customField"));
    }

    [Test]
    public void AddCustomField_WithDuplicateName_ThrowsCustomFieldDuplicateException()
    {
        // Arrange
        var field1 = new CustomFieldDefinition("Discipline", true);
        var field2 = new CustomFieldDefinition("Discipline", false);

        _container.AddCustomField(field1);

        // Act & Assert
        Assert.Throws<Exceptions.CustomFieldDuplicateException>(() => _container.AddCustomField(field2));
    }

    [Test]
    public void AddCustomField_WithMultipleUniqueFields_AddsAll()
    {
        // Arrange
        var field1 = new CustomFieldDefinition("Discipline", true);
        var field2 = new CustomFieldDefinition("Zone", true);
        var field3 = new CustomFieldDefinition("Level", true);

        // Act
        _container.AddCustomField(field1);
        _container.AddCustomField(field2);
        _container.AddCustomField(field3);

        // Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(3));
    }

    [Test]
    public void AddCustomField_WithCaseSensitiveNames_AddsBoth()
    {
        // Arrange
        var field1 = new CustomFieldDefinition("discipline", true);
        var field2 = new CustomFieldDefinition("Discipline", true);

        // Act
        _container.AddCustomField(field1);
        _container.AddCustomField(field2);

        // Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(2));
    }

    #endregion

    #region GetAllCustomFields Tests

    [Test]
    public void GetAllCustomFields_WithNoFields_ReturnsEmptyCollection()
    {
        // Arrange & Act
        var fields = _container.GetAllCustomFields();

        // Assert
        Assert.That(fields, Is.Empty);
    }

    [Test]
    public void GetAllCustomFields_WithMultipleFields_ReturnsAllFields()
    {
        // Arrange
        var field1 = new CustomFieldDefinition("Discipline", true);
        var field2 = new CustomFieldDefinition("Zone", false);
        var field3 = new CustomFieldDefinition("Level", true);

        _container.AddCustomField(field1);
        _container.AddCustomField(field2);
        _container.AddCustomField(field3);

        // Act
        var fields = _container.GetAllCustomFields().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(fields, Has.Count.EqualTo(3));
            Assert.That(fields, Contains.Item(field1));
            Assert.That(fields, Contains.Item(field2));
            Assert.That(fields, Contains.Item(field3));
        });
    }

    #endregion

    #region GetActiveCustomFieldDefinitions Tests

    [Test]
    public void GetActiveCustomFieldDefinitions_WithNoFields_ReturnsEmptyCollection()
    {
        // Arrange & Act
        var activeFields = _container.GetActiveCustomFieldDefinitions();

        // Assert
        Assert.That(activeFields, Is.Empty);
    }

    [Test]
    public void GetActiveCustomFieldDefinitions_WithOnlyActiveFields_ReturnsAll()
    {
        // Arrange
        var field1 = new CustomFieldDefinition("Discipline", true);
        var field2 = new CustomFieldDefinition("Zone", true);

        _container.AddCustomField(field1);
        _container.AddCustomField(field2);

        // Act
        var activeFields = _container.GetActiveCustomFieldDefinitions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(activeFields, Has.Count.EqualTo(2));
            Assert.That(activeFields, Contains.Item(field1));
            Assert.That(activeFields, Contains.Item(field2));
        });
    }

    [Test]
    public void GetActiveCustomFieldDefinitions_WithOnlyInactiveFields_ReturnsEmpty()
    {
        // Arrange
        var field1 = new CustomFieldDefinition("Discipline", false);
        var field2 = new CustomFieldDefinition("Zone", false);

        _container.AddCustomField(field1);
        _container.AddCustomField(field2);

        // Act
        var activeFields = _container.GetActiveCustomFieldDefinitions();

        // Assert
        Assert.That(activeFields, Is.Empty);
    }

    [Test]
    public void GetActiveCustomFieldDefinitions_WithMixedActiveAndInactive_ReturnsOnlyActive()
    {
        // Arrange
        var activeField1 = new CustomFieldDefinition("Discipline", true);
        var inactiveField = new CustomFieldDefinition("Zone", false);
        var activeField2 = new CustomFieldDefinition("Level", true);

        _container.AddCustomField(activeField1);
        _container.AddCustomField(inactiveField);
        _container.AddCustomField(activeField2);

        // Act
        var activeFields = _container.GetActiveCustomFieldDefinitions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(activeFields, Has.Count.EqualTo(2));
            Assert.That(activeFields, Contains.Item(activeField1));
            Assert.That(activeFields, Contains.Item(activeField2));
            Assert.That(activeFields, Does.Not.Contain(inactiveField));
        });
    }

    #endregion

    #region ClearCustomFields Tests

    [Test]
    public void ClearCustomFields_WithEmptyContainer_DoesNotThrow()
    {
        // Arrange & Act & Assert
        Assert.DoesNotThrow(() => _container.ClearCustomFields());
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(0));
    }

    [Test]
    public void ClearCustomFields_WithMultipleFields_RemovesAll()
    {
        // Arrange
        _container.AddCustomField(new CustomFieldDefinition("Discipline", true));
        _container.AddCustomField(new CustomFieldDefinition("Zone", true));
        _container.AddCustomField(new CustomFieldDefinition("Level", true));

        // Act
        _container.ClearCustomFields();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_container.CustomFieldsCount, Is.EqualTo(0));
            Assert.That(_container.GetAllCustomFields(), Is.Empty);
        });
    }

    [Test]
    public void ClearCustomFields_AfterClear_CanAddNewFields()
    {
        // Arrange
        _container.AddCustomField(new CustomFieldDefinition("Discipline", true));
        _container.ClearCustomFields();

        // Act
        _container.AddCustomField(new CustomFieldDefinition("NewField", true));

        // Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(1));
    }

    #endregion

    #region CustomFieldsCount Tests

    [Test]
    public void CustomFieldsCount_WithEmptyContainer_ReturnsZero()
    {
        // Arrange & Act & Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(0));
    }

    [Test]
    public void CustomFieldsCount_AfterAddingFields_ReturnsCorrectCount()
    {
        // Arrange
        _container.AddCustomField(new CustomFieldDefinition("Field1", true));
        _container.AddCustomField(new CustomFieldDefinition("Field2", true));
        _container.AddCustomField(new CustomFieldDefinition("Field3", true));

        // Act & Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(3));
    }

    [Test]
    public void CustomFieldsCount_AfterClear_ReturnsZero()
    {
        // Arrange
        _container.AddCustomField(new CustomFieldDefinition("Field1", true));
        _container.AddCustomField(new CustomFieldDefinition("Field2", true));

        // Act
        _container.ClearCustomFields();

        // Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(0));
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_AddGetClearCycle_WorksCorrectly()
    {
        // This test verifies a complete add-get-clear cycle
        
        // Arrange
        var field1 = new CustomFieldDefinition("Discipline", true);
        var field2 = new CustomFieldDefinition("Zone", false);
        var field3 = new CustomFieldDefinition("Level", true);

        // Act - Add
        _container.AddCustomField(field1);
        _container.AddCustomField(field2);
        _container.AddCustomField(field3);

        Assert.That(_container.CustomFieldsCount, Is.EqualTo(3));

        // Act - Get All
        var allFields = _container.GetAllCustomFields().ToList();
        Assert.That(allFields, Has.Count.EqualTo(3));

        // Act - Get Active Only
        var activeFields = _container.GetActiveCustomFieldDefinitions().ToList();
        Assert.That(activeFields, Has.Count.EqualTo(2));

        // Act - Clear
        _container.ClearCustomFields();

        // Assert Final State
        Assert.Multiple(() =>
        {
            Assert.That(_container.CustomFieldsCount, Is.EqualTo(0));
            Assert.That(_container.GetAllCustomFields(), Is.Empty);
            Assert.That(_container.GetActiveCustomFieldDefinitions(), Is.Empty);
        });
    }

    [Test]
    public void IntegrationTest_AddMultipleThenFilter_ReturnsCorrectSubsets()
    {
        // This test verifies filtering works correctly with mixed active/inactive fields
        
        // Arrange
        var activeFields = new[]
        {
            new CustomFieldDefinition("Active1", true),
            new CustomFieldDefinition("Active2", true),
            new CustomFieldDefinition("Active3", true)
        };

        var inactiveFields = new[]
        {
            new CustomFieldDefinition("Inactive1", false),
            new CustomFieldDefinition("Inactive2", false)
        };

        // Act
        foreach (var field in activeFields)
        {
            _container.AddCustomField(field);
        }

        foreach (var field in inactiveFields)
        {
            _container.AddCustomField(field);
        }

        var all = _container.GetAllCustomFields().ToList();
        var active = _container.GetActiveCustomFieldDefinitions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_container.CustomFieldsCount, Is.EqualTo(5));
            Assert.That(all, Has.Count.EqualTo(5));
            Assert.That(active, Has.Count.EqualTo(3));
            
            foreach (var field in activeFields)
            {
                Assert.That(active, Contains.Item(field));
            }
            
            foreach (var field in inactiveFields)
            {
                Assert.That(active, Does.Not.Contain(field));
            }
        });
    }

    [Test]
    public void IntegrationTest_DuplicateDetection_WorksAcrossMultipleOperations()
    {
        // This test verifies duplicate detection works correctly
        
        // Arrange
        var field1 = new CustomFieldDefinition("TestField", true);
        var field2 = new CustomFieldDefinition("OtherField", false);
        var duplicateField = new CustomFieldDefinition("TestField", false);

        // Act
        _container.AddCustomField(field1);
        _container.AddCustomField(field2);

        // Assert
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(2));
        Assert.Throws<Exceptions.CustomFieldDuplicateException>(() => _container.AddCustomField(duplicateField));
        Assert.That(_container.CustomFieldsCount, Is.EqualTo(2));
    }

    #endregion
}
