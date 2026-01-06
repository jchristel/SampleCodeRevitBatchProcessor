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
using duHastNet.DocManager.Core.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Merge.MergeLog;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Merge.MergeLog;

/// <summary>
/// Tests for MergeLogDialogViewModel
/// Covers log entry loading, computed properties, and dialog operations
/// </summary>
[TestFixture]
public class MergeLogDialogViewModelTests
{
    #region Constructor Tests

    [Test]
    public void Constructor_Default_InitializesSuccessfully()
    {
        // Arrange & Act
        var viewModel = new MergeLogDialogViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.LogEntries, Is.Not.Null);
            Assert.That(viewModel.LogEntries, Is.Empty);
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Merge Log"));
        });
    }

    [Test]
    public void Constructor_WithNullStatuses_InitializesWithEmptyEntries()
    {
        // Arrange & Act
        var viewModel = new MergeLogDialogViewModel(null);

        // Assert
        Assert.That(viewModel.LogEntries, Is.Empty);
    }

    [Test]
    public void Constructor_WithEmptyStatuses_InitializesWithEmptyEntries()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>();

        // Act
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Assert
        Assert.That(viewModel.LogEntries, Is.Empty);
    }

    [Test]
    public void Constructor_WithStatusesWithMessages_LoadsEntries()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Info message 1", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Error message", ProcessMessageTypes.Error)
        };

        // Act
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Assert
        Assert.That(viewModel.LogEntries, Has.Count.EqualTo(2));
    }

    [Test]
    public void Constructor_WithStatusesWithoutMessages_DoesNotLoadEntries()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithoutMessages("C:\\Docs\\Doc1.pdf"),
            CreateStatusWithoutMessages("C:\\Docs\\Doc2.pdf")
        };

        // Act
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Assert
        Assert.That(viewModel.LogEntries, Is.Empty);
    }

    [Test]
    public void Constructor_WithMixedStatuses_LoadsOnlyStatusesWithMessages()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Info message", ProcessMessageTypes.Information),
            CreateStatusWithoutMessages("C:\\Docs\\Doc2.pdf"),
            CreateStatusWithMessages("C:\\Docs\\Doc3.pdf", "Error message", ProcessMessageTypes.Error)
        };

        // Act
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Assert
        Assert.That(viewModel.LogEntries, Has.Count.EqualTo(2));
    }

    #endregion

    #region Computed Properties Tests

    [Test]
    public void TotalDocuments_WithNoEntries_ReturnsZero()
    {
        // Arrange
        var viewModel = new MergeLogDialogViewModel();

        // Act
        var count = viewModel.TotalDocuments;

        // Assert
        Assert.That(count, Is.EqualTo(0));
    }

    [Test]
    public void TotalDocuments_WithEntries_ReturnsCorrectCount()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Message 1", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Message 2", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc3.pdf", "Message 3", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var count = viewModel.TotalDocuments;

        // Assert
        Assert.That(count, Is.EqualTo(3));
    }

    [Test]
    public void DocumentsWithErrors_WithNoErrors_ReturnsZero()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Info message", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var count = viewModel.DocumentsWithErrors;

        // Assert
        Assert.That(count, Is.EqualTo(0));
    }

    [Test]
    public void DocumentsWithErrors_WithErrors_ReturnsCorrectCount()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Error message", ProcessMessageTypes.Error),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Info message", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc3.pdf", "Error message", ProcessMessageTypes.Error)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var count = viewModel.DocumentsWithErrors;

        // Assert
        Assert.That(count, Is.EqualTo(2));
    }

    [Test]
    public void DocumentsSuccessful_WithAllSuccessful_ReturnsCorrectCount()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Info message", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Info message", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var count = viewModel.DocumentsSuccessful;

        // Assert
        Assert.That(count, Is.EqualTo(2));
    }

    [Test]
    public void DocumentsSuccessful_WithSomeErrors_ReturnsCorrectCount()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Error message", ProcessMessageTypes.Error),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Info message", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc3.pdf", "Info message", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var count = viewModel.DocumentsSuccessful;

        // Assert
        Assert.That(count, Is.EqualTo(2));
    }

    [Test]
    public void HasAnyErrors_WithNoErrors_ReturnsFalse()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Info message", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var hasErrors = viewModel.HasAnyErrors;

        // Assert
        Assert.That(hasErrors, Is.False);
    }

    [Test]
    public void HasAnyErrors_WithErrors_ReturnsTrue()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Error message", ProcessMessageTypes.Error)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var hasErrors = viewModel.HasAnyErrors;

        // Assert
        Assert.That(hasErrors, Is.True);
    }

    [Test]
    public void SummaryMessage_WithNoDocuments_ReturnsNoDocumentsMessage()
    {
        // Arrange
        var viewModel = new MergeLogDialogViewModel();

        // Act
        var message = viewModel.SummaryMessage;

        // Assert
        Assert.That(message, Is.EqualTo("No documents were processed."));
    }

    [Test]
    public void SummaryMessage_WithAllSuccessful_ReturnsSuccessMessage()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Info message", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Info message", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var message = viewModel.SummaryMessage;

        // Assert
        Assert.That(message, Is.EqualTo("All 2 document(s) processed successfully."));
    }

    [Test]
    public void SummaryMessage_WithSomeErrors_ReturnsMixedMessage()
    {
        // Arrange
        var statuses = new List<IncomingDocumentProcessingStatus>
        {
            CreateStatusWithMessages("C:\\Docs\\Doc1.pdf", "Error message", ProcessMessageTypes.Error),
            CreateStatusWithMessages("C:\\Docs\\Doc2.pdf", "Info message", ProcessMessageTypes.Information),
            CreateStatusWithMessages("C:\\Docs\\Doc3.pdf", "Info message", ProcessMessageTypes.Information)
        };
        var viewModel = new MergeLogDialogViewModel(statuses);

        // Act
        var message = viewModel.SummaryMessage;

        // Assert
        Assert.That(message, Is.EqualTo("Processed 3 document(s): 2 successful, 1 with errors."));
    }

    #endregion

    #region OkCommand Tests

    [Test]
    public void OkCommand_WhenExecuted_RaisesRequestCloseEvent()
    {
        // Arrange
        var viewModel = new MergeLogDialogViewModel();
        var eventRaised = false;
        viewModel.RequestClose += (sender, args) => eventRaised = true;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    [Test]
    public void OkCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = new MergeLogDialogViewModel();

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    #endregion

    #region Helper Methods

    private IncomingDocumentProcessingStatus CreateStatusWithMessages(string filePath, string message, ProcessMessageTypes messageType)
    {
        var status = new IncomingDocumentProcessingStatus(filePath);
        status.AddProcessMessage(message, messageType);
        return status;
    }

    private IncomingDocumentProcessingStatus CreateStatusWithoutMessages(string filePath)
    {
        return new IncomingDocumentProcessingStatus(filePath);
    }

    #endregion
}
