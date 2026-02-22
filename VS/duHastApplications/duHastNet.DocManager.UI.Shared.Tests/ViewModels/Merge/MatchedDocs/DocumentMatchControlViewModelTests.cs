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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Merge.MatchedDocs;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Merge.MatchedDocs;

/// <summary>
/// Tests for DocumentMatchControlViewModel
/// Covers matched document display, counts, and document matching operations
/// </summary>
[TestFixture]
public class DocumentMatchControlViewModelTests
{
    private Mock<CurrentFolderManager> _mockCurrentFolderManager;
    private Manager _manager;
    private MessageStore _messageStore;
    private Mock<IDialogService> _mockDialogService;
    private Mock<DocManagerApi> _mockDocManagerApi;
    private duHastNet.DocManager.Core.Models.CloudDocManager.CloudDocumentManager _cloudDocumentManager;

    [SetUp]
    public void Setup()
    {
        _mockCurrentFolderManager = new Mock<CurrentFolderManager>();
        _messageStore = new MessageStore();
        _mockDialogService = new Mock<IDialogService>();
        _mockDocManagerApi = new Mock<DocManagerApi>();
        
        // Use real instances for Manager and CloudDocumentManager
        _cloudDocumentManager = new duHastNet.DocManager.Core.Models.CloudDocManager.CloudDocumentManager();
        _manager = new Manager(_cloudDocumentManager);
    }

    [TearDown]
    public void TearDown()
    {
        _messageStore?.Dispose();
    }

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidDependencies_InitializesSuccessfully()
    {
        // Arrange & Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.MatchedDocuments, Is.Not.Null);
            Assert.That(viewModel.MatchedDocuments, Is.Empty);
            Assert.That(viewModel.IsBusy, Is.False);
        });
    }

    [Test]
    public void Constructor_WithNullParameters_ThrowsException()
    {
        // Arrange & Act & Assert
        Assert.Multiple(() =>
        {
            Assert.Throws<ArgumentNullException>(() => new DocumentMatchControlViewModel(
                null,
                _manager,
                _messageStore,
                _mockDialogService.Object,
                _mockDocManagerApi.Object));

            Assert.Throws<ArgumentNullException>(() => new DocumentMatchControlViewModel(
                _mockCurrentFolderManager.Object,
                null,
                _messageStore,
                _mockDialogService.Object,
                _mockDocManagerApi.Object));

            Assert.Throws<ArgumentNullException>(() => new DocumentMatchControlViewModel(
                _mockCurrentFolderManager.Object,
                _manager,
                null,
                _mockDialogService.Object,
                _mockDocManagerApi.Object));

            Assert.Throws<ArgumentNullException>(() => new DocumentMatchControlViewModel(
                _mockCurrentFolderManager.Object,
                _manager,
                _messageStore,
                null,
                _mockDocManagerApi.Object));

            Assert.Throws<ArgumentNullException>(() => new DocumentMatchControlViewModel(
                _mockCurrentFolderManager.Object,
                _manager,
                _messageStore,
                _mockDialogService.Object,
                null));
        });
    }

    #endregion

    #region Computed Properties Tests

    [Test]
    public void MatchedCount_WithOkDocuments_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 1),
            CreateStatus(DocumentMatchStatus.Ok, 2),
            CreateStatus(DocumentMatchStatus.NoMatch, null)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.MatchedCount, Is.EqualTo(2));
    }

    [Test]
    public void WarningCount_WithWarningDocuments_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.WarningRevisionNotSequential, 1),
            CreateStatus(DocumentMatchStatus.Ok, 2)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.WarningCount, Is.EqualTo(1));
    }

    [Test]
    public void RevisionNotSequentialCount_WithNonSequentialRevisions_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.WarningRevisionNotSequential, 1),
            CreateStatus(DocumentMatchStatus.WarningRevisionNotSequential, 2),
            CreateStatus(DocumentMatchStatus.Ok, 3)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2"),
            CreateDocument(3, "DOC-003", "Document 3")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.RevisionNotSequentialCount, Is.EqualTo(2));
    }

    [Test]
    public void MissingRevisionCount_WithMissingRevisions_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.ErrorMissingRevision, 1),
            CreateStatus(DocumentMatchStatus.Ok, 2)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.MissingRevisionCount, Is.EqualTo(1));
    }

    [Test]
    public void DuplicateDocumentCount_WithDuplicates_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.ErrorDuplicateDocument, 1),
            CreateStatus(DocumentMatchStatus.ErrorDuplicateDocument, 2),
            CreateStatus(DocumentMatchStatus.Ok, 3)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2"),
            CreateDocument(3, "DOC-003", "Document 3")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.DuplicateDocumentCount, Is.EqualTo(2));
    }

    [Test]
    public void NoMatchCount_WithNoMatches_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.NoMatch, null),
            CreateStatus(DocumentMatchStatus.NoMatch, null),
            CreateStatus(DocumentMatchStatus.Ok, 1)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.NoMatchCount, Is.EqualTo(2));
    }

    [Test]
    public void ErrorCount_WithVariousErrors_ReturnsCorrectTotal()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.ErrorMissingRevision, 1),
            CreateStatus(DocumentMatchStatus.ErrorDuplicateDocument, 2),
            CreateStatus(DocumentMatchStatus.NoMatch, null),
            CreateStatus(DocumentMatchStatus.Ok, 3)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2"),
            CreateDocument(3, "DOC-003", "Document 3")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.ErrorCount, Is.EqualTo(3)); // 1 missing + 1 duplicate + 1 no match
    }

    [Test]
    public void CanMergeCount_WithMergeableDocuments_ReturnsCorrectCount()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 1),
            CreateStatus(DocumentMatchStatus.WarningRevisionNotSequential, 2),
            CreateStatus(DocumentMatchStatus.ErrorMissingRevision, 3)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2"),
            CreateDocument(3, "DOC-003", "Document 3")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        // Ok and Warning statuses can be merged, but Error cannot
        Assert.That(viewModel.CanMergeCount, Is.EqualTo(2));
    }

    #endregion

    #region LoadMatchedDocuments Tests

    [Test]
    public void LoadMatchedDocuments_WithEmptyLists_ClearsCollection()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>();
        var currentDocuments = new List<Document>();

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.MatchedDocuments, Is.Empty);
    }

    [Test]
    public void LoadMatchedDocuments_WithValidData_PopulatesCollection()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 1),
            CreateStatus(DocumentMatchStatus.Ok, 2)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(viewModel.MatchedDocuments, Has.Count.EqualTo(2));
    }

    [Test]
    public void LoadMatchedDocuments_ClearsExistingDocuments()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var initialStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 1)
        };
        var initialDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1")
        };
        viewModel.LoadMatchedDocuments(initialStatuses, initialDocuments);

        var newStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 2),
            CreateStatus(DocumentMatchStatus.Ok, 3)
        };
        var newDocuments = new List<Document>
        {
            CreateDocument(2, "DOC-002", "Document 2"),
            CreateDocument(3, "DOC-003", "Document 3")
        };

        // Act
        viewModel.LoadMatchedDocuments(newStatuses, newDocuments);

        // Assert
        Assert.That(viewModel.MatchedDocuments, Has.Count.EqualTo(2));
        Assert.That(viewModel.MatchedDocuments.Any(m => m.MatchedDocumentNumber == "DOC-001"), Is.False);
    }

    [Test]
    public void LoadMatchedDocuments_UpdatesCounts()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 1),
            CreateStatus(DocumentMatchStatus.WarningRevisionNotSequential, 2),
            CreateStatus(DocumentMatchStatus.ErrorMissingRevision, 3)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1"),
            CreateDocument(2, "DOC-002", "Document 2"),
            CreateDocument(3, "DOC-003", "Document 3")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.MatchedCount, Is.EqualTo(1));
            Assert.That(viewModel.WarningCount, Is.EqualTo(1));
            Assert.That(viewModel.MissingRevisionCount, Is.EqualTo(1));
        });
    }

    [Test]
    public void LoadMatchedDocuments_RaisesMatchedDocumentsChangedEvent()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var eventRaised = false;
        viewModel.MatchedDocumentsChanged += (sender, args) => eventRaised = true;

        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.Ok, 1)
        };
        var currentDocuments = new List<Document>
        {
            CreateDocument(1, "DOC-001", "Document 1")
        };

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    [Test]
    public void LoadMatchedDocuments_WithNoMatchedDocument_HandlesNullDocument()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var matchedStatuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatus(DocumentMatchStatus.NoMatch, null)
        };
        var currentDocuments = new List<Document>();

        // Act
        viewModel.LoadMatchedDocuments(matchedStatuses, currentDocuments);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.MatchedDocuments, Has.Count.EqualTo(1));
            Assert.That(viewModel.MatchedDocuments[0].MatchedDocumentNumber, Is.Null);
        });
    }

    #endregion

    #region IsBusy Property Tests

    [Test]
    public void IsBusy_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.IsBusy))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.IsBusy = true;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    #endregion

    #region Helper Methods

    private DocumentMatchControlViewModel CreateViewModel()
    {
        return new DocumentMatchControlViewModel(
            _mockCurrentFolderManager.Object,
            _manager,
            _messageStore,
            _mockDialogService.Object,
            _mockDocManagerApi.Object);
    }

    private IncomingDocumentProcessingStatus CreateStatus(DocumentMatchStatus desiredStatus, int? matchedDocId)
    {
        var filePath = $"C:\\Incoming\\test_{matchedDocId ?? 0}.pdf";
        var status = new IncomingDocumentProcessingStatus(filePath)
        {
            MatchedDocumentId = matchedDocId,
            IncomingDocumentRevision = "A"
        };

        // Add appropriate error messages based on desired status
        switch (desiredStatus)
        {
            case DocumentMatchStatus.ErrorMissingRevision:
                status.AddProcessMessage(new duHastNet.DocManager.Core.Exceptions.InvalidRevisionFormatException("Missing revision"));
                break;
            case DocumentMatchStatus.ErrorDuplicateDocument:
                status.AddProcessMessage(new duHastNet.DocManager.Core.Exceptions.IncomingFileDuplicateException(
                    incomingFilePath: filePath,
                    matchedDocumentId: matchedDocId ?? 1,
                    duplicateFilePaths: new List<string> { "dup1.pdf", "dup2.pdf" },
                    fileExtension: ".pdf"));
                break;
            case DocumentMatchStatus.NoMatch:
                status.AddProcessMessage(new duHastNet.DocManager.Core.Exceptions.DocumentNotFoundException("No match found"));
                status.MatchedDocumentId = null;
                break;
            case DocumentMatchStatus.WarningRevisionNotSequential:
                // Will be determined by MatchedDocumentViewModel based on revision comparison
                status.IncomingDocumentRevision = "C"; // Not sequential if current is "A"
                break;
            case DocumentMatchStatus.Ok:
                // No errors, has a match
                status.IncomingDocumentRevision = "B"; // Sequential if current is "A"
                break;
        }

        return status;
    }

    private Document CreateDocument(int id, string number, string name)
    {
        return new Document(number, name, "A", 1)
        {
            Id = id
        };
    }

    #endregion
}
