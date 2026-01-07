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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CloudDocManager;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Tests.Models;

/// <summary>
/// Tests for Manager class
/// This test class covers the business logic manager including:
/// - Constructor validation
/// - Document management (add, get, count)
/// - Revision management (add, get, count)
/// - Custom field definition management
/// - Custom property name retrieval
/// - Data loading and clearing operations
/// - Cloud document manager integration
/// </summary>
[TestFixture]
public class ManagerTests
{
    private CloudDocumentManager _cloudDocManager;

    [SetUp]
    public void Setup()
    {
        _cloudDocManager = new CloudDocumentManager();
    }

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidCloudDocumentManager_InitializesSuccessfully()
    {
        // Arrange & Act
        var manager = new Manager(_cloudDocManager);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager, Is.Not.Null);
            Assert.That(manager.CloudDocumentManager, Is.EqualTo(_cloudDocManager));
            Assert.That(manager.IsDataLoaded, Is.False);
            Assert.That(manager.DocumentCount, Is.EqualTo(0));
            Assert.That(manager.RevisionCount, Is.EqualTo(0));
            Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(0));
        });
    }

    [Test]
    public void Constructor_WithNullCloudDocumentManager_ThrowsArgumentNullException()
    {
        // Arrange, Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(
            () => new Manager(null));

        Assert.That(exception.ParamName, Is.EqualTo("cloudDocumentManager"));
    }

    #endregion

    #region Document Management Tests

    [Test]
    public void AddDocument_WithValidDocument_IncreasesCount()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var document = new Document("A-101", "Floor Plan", "A", 1);

        // Act
        manager.AddDocument(document);

        // Assert
        Assert.That(manager.DocumentCount, Is.EqualTo(1));
    }

    [Test]
    public void AddDocument_MultipleDocuments_IncreasesCountCorrectly()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc1 = new Document("A-101", "Floor Plan", "A", 1);
        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1);
        var doc3 = new Document("S-201", "Structural", "A", 1);

        // Act
        manager.AddDocument(doc1);
        manager.AddDocument(doc2);
        manager.AddDocument(doc3);

        // Assert
        Assert.That(manager.DocumentCount, Is.EqualTo(3));
    }

    [Test]
    public void GetAllDocuments_WithNoDocuments_ReturnsEmptyCollection()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        var documents = manager.GetAllDocuments();

        // Assert
        Assert.That(documents, Is.Empty);
    }

    [Test]
    public void GetAllDocuments_WithMultipleDocuments_ReturnsAllDocuments()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc1 = new Document("A-101", "Floor Plan", "A", 1);
        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1);

        manager.AddDocument(doc1);
        manager.AddDocument(doc2);

        // Act
        var documents = manager.GetAllDocuments().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(documents, Has.Count.EqualTo(2));
            Assert.That(documents, Contains.Item(doc1));
            Assert.That(documents, Contains.Item(doc2));
        });
    }

    [Test]
    public void GetAllDocumentsOfRevisionId_WithMatchingDocuments_ReturnsFiltered()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc1 = new Document("A-101", "Floor Plan", "A", 1) { RevisionId = 1 };
        var doc2 = new Document("A-102", "Ceiling Plan", "B", 2) { RevisionId = 2 };
        var doc3 = new Document("A-103", "Elevation", "A", 1) { RevisionId = 1 };

        manager.AddDocument(doc1);
        manager.AddDocument(doc2);
        manager.AddDocument(doc3);

        // Act
        var documents = manager.GetAllDocumentsOfRevisionId(1).ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(documents, Has.Count.EqualTo(2));
            Assert.That(documents, Contains.Item(doc1));
            Assert.That(documents, Contains.Item(doc3));
            Assert.That(documents, Does.Not.Contain(doc2));
        });
    }

    [Test]
    public void GetAllDocumentsOfRevisionId_WithNoMatches_ReturnsEmpty()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc1 = new Document("A-101", "Floor Plan", "A", 1) { RevisionId = 1 };

        manager.AddDocument(doc1);

        // Act
        var documents = manager.GetAllDocumentsOfRevisionId(999);

        // Assert
        Assert.That(documents, Is.Empty);
    }

    [Test]
    public void DocumentCount_WithNoDocuments_ReturnsZero()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act & Assert
        Assert.That(manager.DocumentCount, Is.EqualTo(0));
    }

    #endregion

    #region Revision Management Tests

    [Test]
    public void AddRevision_WithValidRevision_IncreasesCount()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var revision = new Revision(new DateTime(2024, 1, 1), "Initial Issue");

        // Act
        manager.AddRevision(revision);

        // Assert
        Assert.That(manager.RevisionCount, Is.EqualTo(1));
    }

    [Test]
    public void AddRevision_MultipleRevisions_IncreasesCountCorrectly()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var rev1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue");
        var rev2 = new Revision(new DateTime(2024, 2, 1), "First Review");
        var rev3 = new Revision(new DateTime(2024, 3, 1), "Final");

        // Act
        manager.AddRevision(rev1);
        manager.AddRevision(rev2);
        manager.AddRevision(rev3);

        // Assert
        Assert.That(manager.RevisionCount, Is.EqualTo(3));
    }

    [Test]
    public void GetAllRevisions_WithNoRevisions_ReturnsEmptyCollection()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        var revisions = manager.GetAllRevisions();

        // Assert
        Assert.That(revisions, Is.Empty);
    }

    [Test]
    public void GetAllRevisions_WithMultipleRevisions_ReturnsAllRevisions()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var rev1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue");
        var rev2 = new Revision(new DateTime(2024, 2, 1), "First Review");

        manager.AddRevision(rev1);
        manager.AddRevision(rev2);

        // Act
        var revisions = manager.GetAllRevisions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(revisions, Has.Count.EqualTo(2));
            Assert.That(revisions, Contains.Item(rev1));
            Assert.That(revisions, Contains.Item(rev2));
        });
    }

    [Test]
    public void RevisionCount_WithNoRevisions_ReturnsZero()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act & Assert
        Assert.That(manager.RevisionCount, Is.EqualTo(0));
    }

    #endregion

    #region Custom Field Definition Management Tests

    [Test]
    public void AddCustomFieldDefinition_WithValidDefinition_IncreasesCount()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var definition = new CustomFieldDefinition("Discipline", true);

        // Act
        manager.AddCustomFieldDefinition(definition);

        // Assert
        Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(1));
    }

    [Test]
    public void AddCustomFieldDefinition_MultipleDefinitions_IncreasesCountCorrectly()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var def1 = new CustomFieldDefinition("Discipline", true);
        var def2 = new CustomFieldDefinition("Zone", true);
        var def3 = new CustomFieldDefinition("Status", true);

        // Act
        manager.AddCustomFieldDefinition(def1);
        manager.AddCustomFieldDefinition(def2);
        manager.AddCustomFieldDefinition(def3);

        // Assert
        Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(3));
    }

    [Test]
    public void GetAllCustomFieldDefinitions_WithNoDefinitions_ReturnsEmptyCollection()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        var definitions = manager.GetAllCustomFieldDefinitions();

        // Assert
        Assert.That(definitions, Is.Empty);
    }

    [Test]
    public void GetAllCustomFieldDefinitions_WithMultipleDefinitions_ReturnsAllDefinitions()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var def1 = new CustomFieldDefinition("Discipline", true);
        var def2 = new CustomFieldDefinition("Zone", false);

        manager.AddCustomFieldDefinition(def1);
        manager.AddCustomFieldDefinition(def2);

        // Act
        var definitions = manager.GetAllCustomFieldDefinitions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(definitions, Has.Count.EqualTo(2));
            Assert.That(definitions, Contains.Item(def1));
            Assert.That(definitions, Contains.Item(def2));
        });
    }

    [Test]
    public void GetActiveCustomFieldDefinitions_WithMixedActiveInactive_ReturnsOnlyActive()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var activeField1 = new CustomFieldDefinition("Discipline", true) { IsActive = true };
        var inactiveField = new CustomFieldDefinition("OldField", false) { IsActive = false };
        var activeField2 = new CustomFieldDefinition("Zone", true) { IsActive = true };

        manager.AddCustomFieldDefinition(activeField1);
        manager.AddCustomFieldDefinition(inactiveField);
        manager.AddCustomFieldDefinition(activeField2);

        // Act
        var activeDefinitions = manager.GetActiveCustomFieldDefinitions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(activeDefinitions, Has.Count.EqualTo(2));
            Assert.That(activeDefinitions, Contains.Item(activeField1));
            Assert.That(activeDefinitions, Contains.Item(activeField2));
            Assert.That(activeDefinitions, Does.Not.Contain(inactiveField));
        });
    }

    [Test]
    public void GetActiveCustomFieldDefinitions_WithNoActiveFields_ReturnsEmpty()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var inactiveField = new CustomFieldDefinition("OldField", false) { IsActive = false };

        manager.AddCustomFieldDefinition(inactiveField);

        // Act
        var activeDefinitions = manager.GetActiveCustomFieldDefinitions();

        // Assert
        Assert.That(activeDefinitions, Is.Empty);
    }

    [Test]
    public void CustomFieldDefinitionCount_WithNoDefinitions_ReturnsZero()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act & Assert
        Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(0));
    }

    #endregion

    #region Custom Property Names Tests

    [Test]
    public void GetAllCustomPropertyNames_WithNoDocuments_ReturnsEmptyCollection()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        var propertyNames = manager.GetAllCustomPropertyNames();

        // Assert
        Assert.That(propertyNames, Is.Empty);
    }

    [Test]
    public void GetAllCustomPropertyNames_WithDocumentsContainingProperties_ReturnsPropertyNames()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc = new Document("A-101", "Floor Plan", "A", 1);
        doc.CustomProperties.Add(new CustomProperty(1, 1, "Architecture") { PropertyName = "Discipline" });
        doc.CustomProperties.Add(new CustomProperty(1, 2, "Ground Floor") { PropertyName = "Zone" });

        manager.AddDocument(doc);

        // Act
        var propertyNames = manager.GetAllCustomPropertyNames().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(propertyNames, Has.Count.GreaterThanOrEqualTo(2));
            Assert.That(propertyNames, Does.Contain("Discipline"));
            Assert.That(propertyNames, Does.Contain("Zone"));
        });
    }

    #endregion

    #region Data Operations Tests

    [Test]
    public void IsDataLoaded_InitiallyFalse()
    {
        // Arrange & Act
        var manager = new Manager(_cloudDocManager);

        // Assert
        Assert.That(manager.IsDataLoaded, Is.False);
    }

    [Test]
    public void MarkDataAsLoaded_SetsIsDataLoadedToTrue()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        manager.MarkDataAsLoaded();

        // Assert
        Assert.That(manager.IsDataLoaded, Is.True);
    }

    [Test]
    public void MarkDataAsLoaded_CanBeCalledMultipleTimes()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        manager.MarkDataAsLoaded();
        manager.MarkDataAsLoaded();
        manager.MarkDataAsLoaded();

        // Assert
        Assert.That(manager.IsDataLoaded, Is.True);
    }

    [Test]
    public void ClearData_RemovesAllDocuments()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc1 = new Document("A-101", "Floor Plan", "A", 1);
        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1);

        manager.AddDocument(doc1);
        manager.AddDocument(doc2);

        // Act
        manager.ClearData();

        // Assert
        Assert.That(manager.DocumentCount, Is.EqualTo(0));
    }

    [Test]
    public void ClearData_RemovesAllRevisions()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var rev1 = new Revision(new DateTime(2024, 1, 1), "Initial");
        var rev2 = new Revision(new DateTime(2024, 2, 1), "Review");

        manager.AddRevision(rev1);
        manager.AddRevision(rev2);

        // Act
        manager.ClearData();

        // Assert
        Assert.That(manager.RevisionCount, Is.EqualTo(0));
    }

    [Test]
    public void ClearData_RemovesAllCustomFieldDefinitions()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var def1 = new CustomFieldDefinition("Discipline", true);
        var def2 = new CustomFieldDefinition("Zone", true);

        manager.AddCustomFieldDefinition(def1);
        manager.AddCustomFieldDefinition(def2);

        // Act
        manager.ClearData();

        // Assert
        Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(0));
    }

    [Test]
    public void ClearData_ClearsAllDataTypes()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var doc = new Document("A-101", "Floor Plan", "A", 1);
        var rev = new Revision(new DateTime(2024, 1, 1), "Initial");
        var def = new CustomFieldDefinition("Discipline", true);

        manager.AddDocument(doc);
        manager.AddRevision(rev);
        manager.AddCustomFieldDefinition(def);
        manager.MarkDataAsLoaded();

        // Act
        manager.ClearData();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.DocumentCount, Is.EqualTo(0));
            Assert.That(manager.RevisionCount, Is.EqualTo(0));
            Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(0));
            // Note: IsDataLoaded is NOT cleared by ClearData
            Assert.That(manager.IsDataLoaded, Is.True);
        });
    }

    [Test]
    public void ClearData_OnEmptyManager_DoesNotThrow()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act & Assert
        Assert.DoesNotThrow(() => manager.ClearData());
    }

    #endregion

    #region Cloud Document Manager Tests

    [Test]
    public void CloudDocumentManager_ReturnsInitializedInstance()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        var cloudDocManager = manager.CloudDocumentManager;

        // Assert
        Assert.That(cloudDocManager, Is.EqualTo(_cloudDocManager));
    }

    [Test]
    public void CloudDocManager_Property_CanBeSet()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);
        var newCloudDocManager = new CloudDocumentManager();

        // Act
        manager.CloudDocManager = newCloudDocManager;

        // Assert
        Assert.That(manager.CloudDocManager, Is.EqualTo(newCloudDocManager));
    }

    [Test]
    public void CloudDocManager_Property_CanBeSetToNull()
    {
        // Arrange
        var manager = new Manager(_cloudDocManager);

        // Act
        manager.CloudDocManager = null;

        // Assert
        Assert.That(manager.CloudDocManager, Is.Null);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_CompleteWorkflow_AddAndRetrieveAllDataTypes()
    {
        // This test verifies a complete workflow with all data types
        
        // Arrange
        var manager = new Manager(_cloudDocManager);

        var doc1 = new Document("A-101", "Floor Plan", "A", 1);
        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1);

        var rev1 = new Revision(new DateTime(2024, 1, 1), "Initial Issue");
        var rev2 = new Revision(new DateTime(2024, 2, 1), "First Review");

        var def1 = new CustomFieldDefinition("Discipline", true);
        var def2 = new CustomFieldDefinition("Zone", true);

        // Act
        manager.AddDocument(doc1);
        manager.AddDocument(doc2);
        manager.AddRevision(rev1);
        manager.AddRevision(rev2);
        manager.AddCustomFieldDefinition(def1);
        manager.AddCustomFieldDefinition(def2);
        manager.MarkDataAsLoaded();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.DocumentCount, Is.EqualTo(2));
            Assert.That(manager.RevisionCount, Is.EqualTo(2));
            Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(2));
            Assert.That(manager.IsDataLoaded, Is.True);

            var documents = manager.GetAllDocuments().ToList();
            Assert.That(documents, Has.Count.EqualTo(2));

            var revisions = manager.GetAllRevisions().ToList();
            Assert.That(revisions, Has.Count.EqualTo(2));

            var definitions = manager.GetAllCustomFieldDefinitions().ToList();
            Assert.That(definitions, Has.Count.EqualTo(2));
        });
    }

    [Test]
    public void IntegrationTest_AddThenClear_AllCountsResetToZero()
    {
        // This test verifies that ClearData properly resets all containers
        
        // Arrange
        var manager = new Manager(_cloudDocManager);

        manager.AddDocument(new Document("A-101", "Floor Plan", "A", 1));
        manager.AddRevision(new Revision(new DateTime(2024, 1, 1), "Initial"));
        manager.AddCustomFieldDefinition(new CustomFieldDefinition("Discipline", true));
        manager.MarkDataAsLoaded();

        // Act
        manager.ClearData();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.DocumentCount, Is.EqualTo(0));
            Assert.That(manager.RevisionCount, Is.EqualTo(0));
            Assert.That(manager.CustomFieldDefinitionCount, Is.EqualTo(0));
            Assert.That(manager.GetAllDocuments(), Is.Empty);
            Assert.That(manager.GetAllRevisions(), Is.Empty);
            Assert.That(manager.GetAllCustomFieldDefinitions(), Is.Empty);
        });
    }

    [Test]
    public void IntegrationTest_FilterDocumentsByRevisionId_ReturnsCorrectSubset()
    {
        // This test verifies filtering documents by revision ID works correctly
        
        // Arrange
        var manager = new Manager(_cloudDocManager);

        var rev1 = new Revision(new DateTime(2024, 1, 1), "Initial") { Id = 1 };
        var rev2 = new Revision(new DateTime(2024, 2, 1), "Review") { Id = 2 };

        manager.AddRevision(rev1);
        manager.AddRevision(rev2);

        var doc1 = new Document("A-101", "Floor Plan", "A", 1) { RevisionId = 1 };
        var doc2 = new Document("A-102", "Ceiling Plan", "A", 1) { RevisionId = 1 };
        var doc3 = new Document("A-103", "Elevation", "B", 2) { RevisionId = 2 };
        var doc4 = new Document("S-201", "Structural", "A", 1) { RevisionId = 1 };

        manager.AddDocument(doc1);
        manager.AddDocument(doc2);
        manager.AddDocument(doc3);
        manager.AddDocument(doc4);

        // Act
        var rev1Documents = manager.GetAllDocumentsOfRevisionId(1).ToList();
        var rev2Documents = manager.GetAllDocumentsOfRevisionId(2).ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(manager.DocumentCount, Is.EqualTo(4));
            Assert.That(rev1Documents, Has.Count.EqualTo(3));
            Assert.That(rev2Documents, Has.Count.EqualTo(1));
            Assert.That(rev1Documents, Contains.Item(doc1));
            Assert.That(rev1Documents, Contains.Item(doc2));
            Assert.That(rev1Documents, Contains.Item(doc4));
            Assert.That(rev2Documents, Contains.Item(doc3));
        });
    }

    #endregion
}
