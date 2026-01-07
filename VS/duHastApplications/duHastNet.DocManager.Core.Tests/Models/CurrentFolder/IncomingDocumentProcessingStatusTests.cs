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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Stores;

namespace duHastNet.DocManager.Core.Tests.Models.CurrentFolder;

[TestFixture]
public class IncomingDocumentProcessingStatusTests
{
    private const string TestDocumentPath = @"C:\Test\Document.pdf";

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidPath_InitializesCorrectly()
    {
        // Arrange & Act
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(status, Is.Not.Null);
            Assert.That(status.NewDocumentPath, Is.EqualTo(TestDocumentPath));
            Assert.That(status.ProcessMessages, Is.Empty);
            Assert.That(status.IsDuplicate, Is.False);
            Assert.That(status.DuplicateFilePaths, Is.Empty);
            Assert.That(status.MatchedDocumentId, Is.Null);
            Assert.That(status.IncomingDocumentRevision, Is.Null);
        });
    }

    #endregion

    #region AddProcessMessage Tests

    [Test]
    public void AddProcessMessage_WithMessageAndType_AddsToCollection()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var message = "Document processed successfully";

        // Act
        status.AddProcessMessage(message, ProcessMessageTypes.Info);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(status.ProcessMessages, Has.Count.EqualTo(1));
            Assert.That(status.ProcessMessages[0].message, Is.EqualTo(message));
            Assert.That(status.ProcessMessages[0].messageType, Is.EqualTo(ProcessMessageTypes.Info));
            Assert.That(status.ProcessMessages[0].exceptionType, Is.Null);
        });
    }

    [Test]
    public void AddProcessMessage_WithException_AddsErrorMessage()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new InvalidOperationException("Test error");

        // Act
        status.AddProcessMessage(exception);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(status.ProcessMessages, Has.Count.EqualTo(1));
            Assert.That(status.ProcessMessages[0].message, Is.EqualTo("Test error"));
            Assert.That(status.ProcessMessages[0].messageType, Is.EqualTo(ProcessMessageTypes.Error));
            Assert.That(status.ProcessMessages[0].exceptionType, Is.EqualTo(typeof(InvalidOperationException)));
        });
    }

    [Test]
    public void AddProcessMessage_WithIncomingFileDuplicateException_UpdatesDuplicateFields()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var duplicatePaths = new List<string> { @"C:\Dup1.pdf", @"C:\Dup2.pdf" };
        var exception = new Exceptions.IncomingFileDuplicateException("Duplicate found", duplicatePaths);

        // Act
        status.AddProcessMessage(exception);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(status.IsDuplicate, Is.True);
            Assert.That(status.DuplicateFilePaths, Has.Count.EqualTo(2));
            Assert.That(status.DuplicateFilePaths, Contains.Item(@"C:\Dup1.pdf"));
            Assert.That(status.HasDuplicateError(), Is.True);
        });
    }

    [Test]
    public void AddProcessMessage_WithMultipleMessages_AddsAllToCollection()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act
        status.AddProcessMessage("Info message", ProcessMessageTypes.Info);
        status.AddProcessMessage("Warning message", ProcessMessageTypes.Warning);
        status.AddProcessMessage("Error message", ProcessMessageTypes.Error);

        // Assert
        Assert.That(status.ProcessMessages, Has.Count.EqualTo(3));
    }

    #endregion

    #region GetProcessStatus Tests

    [Test]
    public void GetProcessStatus_WithNoErrors_ReturnsTrue()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage("Info message", ProcessMessageTypes.Info);
        status.AddProcessMessage("Warning message", ProcessMessageTypes.Warning);

        // Act
        var result = status.GetProcessStatus();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void GetProcessStatus_WithErrors_ReturnsFalse()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage("Error message", ProcessMessageTypes.Error);

        // Act
        var result = status.GetProcessStatus();

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void GetProcessStatus_WithMixedMessages_ReturnsFalseIfAnyError()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage("Info message", ProcessMessageTypes.Info);
        status.AddProcessMessage("Error message", ProcessMessageTypes.Error);
        status.AddProcessMessage("Warning message", ProcessMessageTypes.Warning);

        // Act
        var result = status.GetProcessStatus();

        // Assert
        Assert.That(result, Is.False);
    }

    #endregion

    #region Error Detection Tests

    [Test]
    public void HasRevisionError_WithRevisionException_ReturnsTrue()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new Exceptions.InvalidRevisionFormatException("A-101.pdf", "Invalid format");

        // Act
        status.AddProcessMessage(exception);

        // Assert
        Assert.That(status.HasRevisionError(), Is.True);
    }

    [Test]
    public void HasRevisionError_WithoutRevisionException_ReturnsFalse()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage(new InvalidOperationException("Other error"));

        // Act & Assert
        Assert.That(status.HasRevisionError(), Is.False);
    }

    [Test]
    public void HasDuplicateError_WithDuplicateException_ReturnsTrue()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new Exceptions.IncomingFileDuplicateException("Duplicate", new List<string>());

        // Act
        status.AddProcessMessage(exception);

        // Assert
        Assert.That(status.HasDuplicateError(), Is.True);
    }

    [Test]
    public void HasDocumentNotFoundError_WithNotFoundException_ReturnsTrue()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new Exceptions.DocumentNotFoundException("A-101");

        // Act
        status.AddProcessMessage(exception);

        // Assert
        Assert.That(status.HasDocumentNotFoundError(), Is.True);
    }

    #endregion

    #region GetErrorMessage Tests

    [Test]
    public void GetRevisionErrorMessage_WithRevisionError_ReturnsMessage()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new Exceptions.InvalidRevisionFormatException("A-101.pdf", "Invalid format");

        status.AddProcessMessage(exception);

        // Act
        var message = status.GetRevisionErrorMessage();

        // Assert
        Assert.That(message, Is.Not.Null);
        Assert.That(message, Does.Contain("Invalid format"));
    }

    [Test]
    public void GetRevisionErrorMessage_WithoutRevisionError_ReturnsNull()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act
        var message = status.GetRevisionErrorMessage();

        // Assert
        Assert.That(message, Is.Null);
    }

    [Test]
    public void GetDuplicateErrorMessage_WithDuplicateError_ReturnsMessage()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new Exceptions.IncomingFileDuplicateException("Duplicate found", new List<string>());

        status.AddProcessMessage(exception);

        // Act
        var message = status.GetDuplicateErrorMessage();

        // Assert
        Assert.That(message, Is.EqualTo("Duplicate found"));
    }

    [Test]
    public void GetDocumentNotFoundErrorMessage_WithNotFoundError_ReturnsMessage()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        var exception = new Exceptions.DocumentNotFoundException("A-101");

        status.AddProcessMessage(exception);

        // Act
        var message = status.GetDocumentNotFoundErrorMessage();

        // Assert
        Assert.That(message, Is.Not.Null);
    }

    [Test]
    public void GetAllErrorMessages_WithMultipleErrors_ReturnsAllErrors()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage("Error 1", ProcessMessageTypes.Error);
        status.AddProcessMessage("Info", ProcessMessageTypes.Info);
        status.AddProcessMessage("Error 2", ProcessMessageTypes.Error);

        // Act
        var errors = status.GetAllErrorMessages();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(errors, Has.Count.EqualTo(2));
            Assert.That(errors[0], Is.EqualTo("Error 1"));
            Assert.That(errors[1], Is.EqualTo("Error 2"));
        });
    }

    #endregion

    #region GetHighestPriorityError Tests

    [Test]
    public void GetHighestPriorityError_WithNoErrors_ReturnsNone()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act
        var errorType = status.GetHighestPriorityError();

        // Assert
        Assert.That(errorType, Is.EqualTo(ProcessingErrorType.None));
    }

    [Test]
    public void GetHighestPriorityError_WithRevisionError_ReturnsRevisionError()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage(new Exceptions.InvalidRevisionFormatException("file.pdf", "error"));

        // Act
        var errorType = status.GetHighestPriorityError();

        // Assert
        Assert.That(errorType, Is.EqualTo(ProcessingErrorType.RevisionError));
    }

    [Test]
    public void GetHighestPriorityError_WithMultipleErrors_ReturnsHighestPriority()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage(new Exceptions.DocumentNotFoundException("A-101"));
        status.AddProcessMessage(new Exceptions.IncomingFileDuplicateException("Dup", new List<string>()));
        status.AddProcessMessage(new Exceptions.InvalidRevisionFormatException("file.pdf", "error"));

        // Act
        var errorType = status.GetHighestPriorityError();

        // Assert - Revision error has highest priority
        Assert.That(errorType, Is.EqualTo(ProcessingErrorType.RevisionError));
    }

    [Test]
    public void GetHighestPriorityError_WithDuplicateAndNotFound_ReturnsDuplicate()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);
        status.AddProcessMessage(new Exceptions.DocumentNotFoundException("A-101"));
        status.AddProcessMessage(new Exceptions.IncomingFileDuplicateException("Dup", new List<string>()));

        // Act
        var errorType = status.GetHighestPriorityError();

        // Assert - Duplicate has higher priority than NotFound
        Assert.That(errorType, Is.EqualTo(ProcessingErrorType.DuplicateError));
    }

    #endregion

    #region Property Tests

    [Test]
    public void MatchedDocumentId_CanBeSetAndRetrieved()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act
        status.MatchedDocumentId = 123;

        // Assert
        Assert.That(status.MatchedDocumentId, Is.EqualTo(123));
    }

    [Test]
    public void IncomingDocumentRevision_CanBeSetAndRetrieved()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act
        status.IncomingDocumentRevision = "Rev A";

        // Assert
        Assert.That(status.IncomingDocumentRevision, Is.EqualTo("Rev A"));
    }

    [Test]
    public void IsDuplicate_CanBeSetManually()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act
        status.IsDuplicate = true;

        // Assert
        Assert.That(status.IsDuplicate, Is.True);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_CompleteProcessingScenario_TracksAllInformation()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act - Simulate processing
        status.AddProcessMessage("Starting processing", ProcessMessageTypes.Info);
        status.MatchedDocumentId = 456;
        status.IncomingDocumentRevision = "Rev B";
        status.AddProcessMessage("Processing complete", ProcessMessageTypes.Info);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(status.GetProcessStatus(), Is.True);
            Assert.That(status.MatchedDocumentId, Is.EqualTo(456));
            Assert.That(status.IncomingDocumentRevision, Is.EqualTo("Rev B"));
            Assert.That(status.ProcessMessages, Has.Count.EqualTo(2));
        });
    }

    [Test]
    public void IntegrationTest_ErrorProcessingScenario_CapturesErrors()
    {
        // Arrange
        var status = new IncomingDocumentProcessingStatus(TestDocumentPath);

        // Act - Simulate error scenario
        status.AddProcessMessage("Starting processing", ProcessMessageTypes.Info);
        status.AddProcessMessage(new Exceptions.InvalidRevisionFormatException("file.pdf", "Bad format"));
        status.AddProcessMessage("Processing failed", ProcessMessageTypes.Error);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(status.GetProcessStatus(), Is.False);
            Assert.That(status.HasRevisionError(), Is.True);
            Assert.That(status.GetHighestPriorityError(), Is.EqualTo(ProcessingErrorType.RevisionError));
            Assert.That(status.GetAllErrorMessages(), Has.Count.EqualTo(2));
        });
    }

    #endregion
}
