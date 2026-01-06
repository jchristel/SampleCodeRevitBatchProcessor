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

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CurrentFolder;

/// <summary>
/// Tests for CurrentFolderViewModel - Supported File Types functionality
/// Covers supported file types collection, commands, and helper methods
/// </summary>
[TestFixture]
public partial class CurrentFolderViewModelTests
{
    #region Supported File Types - Initialization Tests

    [Test]
    public void InitializeSupportedFileTypes_EnsuresPdfExists()
    {
        // Arrange & Act
        var viewModel = CreateViewModel();

        // Assert - PDF should always be present
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SupportedFileTypes, Is.Not.Null);
            Assert.That(viewModel.SupportedFileTypes.Count, Is.GreaterThanOrEqualTo(1));
            Assert.That(viewModel.SupportedFileTypes.Any(ft => ft.FileExtension.Equals(".pdf", StringComparison.OrdinalIgnoreCase)), 
                Is.True, "PDF file type should always exist");
        });
    }

    [Test]
    public void InitializeSupportedFileTypes_WithEmptySettings_CreatesPdf()
    {
        // Arrange - Empty file types
        _settings.SupportedFileTypes.Clear();

        // Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SupportedFileTypes.Count, Is.EqualTo(1));
            Assert.That(viewModel.SupportedFileTypes[0].FileExtension, Is.EqualTo(".pdf"));
            Assert.That(viewModel.SupportedFileTypes[0].Description, Is.EqualTo("PDF Document"));
            Assert.That(_settings.SupportedFileTypes.Count, Is.EqualTo(1), "Should add to settings");
        });
    }

    [Test]
    public void InitializeSupportedFileTypes_WithExistingPdf_DoesNotDuplicate()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "Existing PDF", null));

        // Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SupportedFileTypes.Count, Is.EqualTo(1), "Should not duplicate PDF");
            Assert.That(viewModel.SupportedFileTypes[0].Description, Is.EqualTo("Existing PDF"));
        });
    }

    [Test]
    public void InitializeSupportedFileTypes_LoadsMultipleTypes()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".dwg", "AutoCAD Drawing", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".xlsx", "Excel Spreadsheet", null));

        // Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SupportedFileTypes.Count, Is.EqualTo(3));
            Assert.That(viewModel.SupportedFileTypes[0].FileExtension, Is.EqualTo(".pdf"));
            Assert.That(viewModel.SupportedFileTypes[1].FileExtension, Is.EqualTo(".dwg"));
            Assert.That(viewModel.SupportedFileTypes[2].FileExtension, Is.EqualTo(".xlsx"));
        });
    }

    #endregion

    #region Supported File Types - Property Tests

    [Test]
    public void SelectedFileType_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.SelectedFileType))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.SelectedFileType = viewModel.SupportedFileTypes[0];

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void SelectedFileType_WhenSet_UpdatesCommandCanExecute()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".dwg", "AutoCAD Drawing", null));

        var viewModel = CreateViewModel();
        
        // Initially no selection
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.EditFileTypeCommand.CanExecute(null), Is.False);
            Assert.That(viewModel.RemoveFileTypeCommand.CanExecute(null), Is.False);
        });

        // Act - Select a non-PDF file type
        viewModel.SelectedFileType = viewModel.SupportedFileTypes[1]; // .dwg

        // Assert - Commands should now be enabled
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.EditFileTypeCommand.CanExecute(null), Is.True);
            Assert.That(viewModel.RemoveFileTypeCommand.CanExecute(null), Is.True, 
                "Remove should be enabled for non-PDF file types");
        });
    }

    #endregion

    #region Supported File Types - Command Tests

    [Test]
    public void EditFileTypeCommand_WithNoSelection_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFileType = null;

        // Act
        var canExecute = viewModel.EditFileTypeCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void EditFileTypeCommand_WithSelection_CanExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFileType = viewModel.SupportedFileTypes[0];

        // Act
        var canExecute = viewModel.EditFileTypeCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void RemoveFileTypeCommand_WithNoSelection_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFileType = null;

        // Act
        var canExecute = viewModel.RemoveFileTypeCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void RemoveFileTypeCommand_WithNonPdfSelection_CanExecute()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".dwg", "AutoCAD Drawing", null));

        var viewModel = CreateViewModel();
        viewModel.SelectedFileType = viewModel.SupportedFileTypes[1]; // .dwg (non-PDF)

        // Act
        var canExecute = viewModel.RemoveFileTypeCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True, "Remove should be enabled for non-PDF file types");
    }

    [Test]
    public void RemoveFileTypeCommand_WithPdfSelected_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFileType = viewModel.SupportedFileTypes[0]; // PDF (first in list)

        // Act
        var canExecute = viewModel.RemoveFileTypeCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False, "Cannot remove PDF file type");
    }

    #endregion

    #region Supported File Types - Helper Method Tests

    [Test]
    public void IsDuplicateFileExtension_WithExistingExtension_ReturnsTrue()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".dwg", "AutoCAD Drawing", null));

        var viewModel = CreateViewModel();

        // Act
        var isDuplicate = viewModel.IsDuplicateFileExtension(".dwg");

        // Assert
        Assert.That(isDuplicate, Is.True);
    }

    [Test]
    public void IsDuplicateFileExtension_WithNonExistingExtension_ReturnsFalse()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));

        var viewModel = CreateViewModel();

        // Act
        var isDuplicate = viewModel.IsDuplicateFileExtension(".xlsx");

        // Assert
        Assert.That(isDuplicate, Is.False);
    }

    [Test]
    public void IsDuplicateFileExtension_CaseInsensitive_ReturnsTrue()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".PDF", "PDF Document", null));

        var viewModel = CreateViewModel();

        // Act
        var isDuplicate = viewModel.IsDuplicateFileExtension(".pdf");

        // Assert
        Assert.That(isDuplicate, Is.True, "Extension comparison should be case-insensitive");
    }

    [Test]
    public void IsDuplicateFileExtension_ExcludingSelf_ReturnsFalse()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".dwg", "AutoCAD Drawing", null));

        var viewModel = CreateViewModel();

        // Act - Check for duplicate but exclude index 1 (self)
        var isDuplicate = viewModel.IsDuplicateFileExtension(".dwg", excludeIndex: 1);

        // Assert
        Assert.That(isDuplicate, Is.False, "Should not consider self as duplicate");
    }

    [Test]
    public void IsPdfFileType_WithPdfAtIndex_ReturnsTrue()
    {
        // Arrange
        var viewModel = CreateViewModel();
        // PDF is always first due to EnsurePdfFileTypeExists

        // Act
        var isPdf = viewModel.IsPdfFileType(0);

        // Assert
        Assert.That(isPdf, Is.True);
    }

    [Test]
    public void IsPdfFileType_WithNonPdfAtIndex_ReturnsFalse()
    {
        // Arrange
        _settings.SupportedFileTypes.Clear();
        _settings.SupportedFileTypes.Add(new SupportedFileType(".pdf", "PDF Document", null));
        _settings.SupportedFileTypes.Add(new SupportedFileType(".dwg", "AutoCAD Drawing", null));

        var viewModel = CreateViewModel();

        // Act
        var isPdf = viewModel.IsPdfFileType(1);

        // Assert
        Assert.That(isPdf, Is.False);
    }

    [Test]
    public void IsPdfFileType_WithInvalidIndex_ReturnsFalse()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act & Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsPdfFileType(-1), Is.False, "Negative index should return false");
            Assert.That(viewModel.IsPdfFileType(999), Is.False, "Out of range index should return false");
        });
    }

    #endregion
}
