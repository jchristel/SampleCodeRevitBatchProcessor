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
using duHastNet.DocManager.Core.Models;

namespace duHastNet.DocManager.Core.Tests.Models;

[TestFixture]
public class RevisionContainerTests
{
    private RevisionContainer _container;

    [SetUp]
    public void Setup()
    {
        _container = new RevisionContainer();
    }

    #region Constructor Tests

    [Test]
    public void Constructor_InitializesWithEmptyCollection()
    {
        // Arrange & Act
        var container = new RevisionContainer();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(container, Is.Not.Null);
            Assert.That(container.RevisionCount, Is.EqualTo(0));
            Assert.That(container.GetAllRevisions(), Is.Empty);
        });
    }

    #endregion

    #region AddRevision Tests

    [Test]
    public void AddRevision_WithValidRevision_IncreasesCount()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 1, 15), "Initial Release");

        // Act
        _container.AddRevision(revision);

        // Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(1));
    }

    [Test]
    public void AddRevision_WithNullRevision_ThrowsArgumentNullException()
    {
        // Arrange
        Revision revision = null;

        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(() => _container.AddRevision(revision));

        Assert.That(exception.ParamName, Is.EqualTo("rev"));
    }

    [Test]
    public void AddRevision_WithDuplicateRevision_ThrowsRevisionDuplicateException()
    {
        // Arrange
        var rev1 = new Revision(new DateTime(2024, 1, 15), "Initial Release");
        var rev2 = new Revision(new DateTime(2024, 1, 15), "Initial Release");

        _container.AddRevision(rev1);

        // Act & Assert
        Assert.Throws<Exceptions.RevisionDuplicateException>(() => _container.AddRevision(rev2));
    }

    [Test]
    public void AddRevision_WithMultipleUniqueRevisions_AddsAll()
    {
        // Arrange
        var rev1 = new Revision(new DateTime(2024, 1, 15), "Initial Release");
        var rev2 = new Revision(new DateTime(2024, 2, 20), "Second Release");
        var rev3 = new Revision(new DateTime(2024, 3, 25), "Third Release");

        // Act
        _container.AddRevision(rev1);
        _container.AddRevision(rev2);
        _container.AddRevision(rev3);

        // Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(3));
    }

    [Test]
    public void AddRevision_WithSameDateDifferentDescription_AddsSuccessfully()
    {
        // Arrange
        var rev1 = new Revision(new DateTime(2024, 1, 15), "First Description");
        var rev2 = new Revision(new DateTime(2024, 1, 15), "Second Description");

        // Act
        _container.AddRevision(rev1);
        _container.AddRevision(rev2);

        // Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(2));
    }

    #endregion

    #region GetAllRevisions Tests

    [Test]
    public void GetAllRevisions_WithNoRevisions_ReturnsEmptyCollection()
    {
        // Arrange & Act
        var revisions = _container.GetAllRevisions();

        // Assert
        Assert.That(revisions, Is.Empty);
    }

    [Test]
    public void GetAllRevisions_WithMultipleRevisions_ReturnsAllRevisions()
    {
        // Arrange
        var rev1 = new Revision(new DateTime(2024, 1, 15), "First");
        var rev2 = new Revision(new DateTime(2024, 2, 20), "Second");

        _container.AddRevision(rev1);
        _container.AddRevision(rev2);

        // Act
        var revisions = _container.GetAllRevisions().ToList();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(revisions, Has.Count.EqualTo(2));
            Assert.That(revisions, Contains.Item(rev1));
            Assert.That(revisions, Contains.Item(rev2));
        });
    }

    #endregion

    #region ClearRevisions Tests

    [Test]
    public void ClearRevisions_WithEmptyContainer_DoesNotThrow()
    {
        // Arrange & Act & Assert
        Assert.DoesNotThrow(() => _container.ClearRevisions());
        Assert.That(_container.RevisionCount, Is.EqualTo(0));
    }

    [Test]
    public void ClearRevisions_WithMultipleRevisions_RemovesAll()
    {
        // Arrange
        _container.AddRevision(new Revision(new DateTime(2024, 1, 15), "First"));
        _container.AddRevision(new Revision(new DateTime(2024, 2, 20), "Second"));

        // Act
        _container.ClearRevisions();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_container.RevisionCount, Is.EqualTo(0));
            Assert.That(_container.GetAllRevisions(), Is.Empty);
        });
    }

    [Test]
    public void ClearRevisions_AfterClear_CanAddNewRevisions()
    {
        // Arrange
        _container.AddRevision(new Revision(new DateTime(2024, 1, 15), "First"));
        _container.ClearRevisions();

        // Act
        _container.AddRevision(new Revision(new DateTime(2024, 1, 15), "First"));

        // Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(1));
    }

    #endregion

    #region RevisionCount Tests

    [Test]
    public void RevisionCount_WithEmptyContainer_ReturnsZero()
    {
        // Arrange & Act & Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(0));
    }

    [Test]
    public void RevisionCount_AfterAddingRevisions_ReturnsCorrectCount()
    {
        // Arrange
        _container.AddRevision(new Revision(new DateTime(2024, 1, 15), "First"));
        _container.AddRevision(new Revision(new DateTime(2024, 2, 20), "Second"));
        _container.AddRevision(new Revision(new DateTime(2024, 3, 25), "Third"));

        // Act & Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(3));
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_AddGetClearCycle_WorksCorrectly()
    {
        // Arrange
        var rev1 = new Revision(new DateTime(2024, 1, 15), "First");
        var rev2 = new Revision(new DateTime(2024, 2, 20), "Second");
        var rev3 = new Revision(new DateTime(2024, 3, 25), "Third");

        // Act - Add
        _container.AddRevision(rev1);
        _container.AddRevision(rev2);
        _container.AddRevision(rev3);

        Assert.That(_container.RevisionCount, Is.EqualTo(3));

        // Act - Get All
        var allRevisions = _container.GetAllRevisions().ToList();
        Assert.That(allRevisions, Has.Count.EqualTo(3));

        // Act - Clear
        _container.ClearRevisions();

        // Assert Final State
        Assert.Multiple(() =>
        {
            Assert.That(_container.RevisionCount, Is.EqualTo(0));
            Assert.That(_container.GetAllRevisions(), Is.Empty);
        });
    }

    [Test]
    public void IntegrationTest_DuplicateDetection_WorksCorrectly()
    {
        // Arrange
        var rev1 = new Revision(new DateTime(2024, 1, 15), "Test Release");
        var rev2 = new Revision(new DateTime(2024, 2, 20), "Other Release");
        var duplicateRev = new Revision(new DateTime(2024, 1, 15), "Test Release");

        // Act
        _container.AddRevision(rev1);
        _container.AddRevision(rev2);

        // Assert
        Assert.That(_container.RevisionCount, Is.EqualTo(2));
        Assert.Throws<Exceptions.RevisionDuplicateException>(() => _container.AddRevision(duplicateRev));
        Assert.That(_container.RevisionCount, Is.EqualTo(2));
    }

    #endregion
}
