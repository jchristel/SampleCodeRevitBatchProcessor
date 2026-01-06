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
using duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CurrentFolder;

/// <summary>
/// Tests for CurrentFolderViewModel - Filing Rules functionality
/// Covers filing rules collection, commands, and helper methods
/// </summary>
[TestFixture]
public partial class CurrentFolderViewModelTests
{
    #region Filing Rules - Initialization Tests

    [Test]
    public void InitializeFilingRules_LoadsRulesFromSettings()
    {
        // Arrange & Act
        var viewModel = CreateViewModel();

        // Assert - Should have one CatchAll rule from setup
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FilingRules, Is.Not.Null);
            Assert.That(viewModel.FilingRules.Count, Is.EqualTo(1));
            Assert.That(viewModel.FilingRules[0].RuleTypeEnum, Is.EqualTo(FilingRuleType.Default));
        });
    }

    [Test]
    public void InitializeFilingRules_WithEmptySettings_CreatesDefaultCatchAll()
    {
        // Arrange
        _settings.FilingRules.Clear();

        // Act
        var viewModel = CreateViewModel();

        // Assert - Should have created a default CatchAll rule
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FilingRules.Count, Is.EqualTo(1));
            Assert.That(viewModel.FilingRules[0].RuleTypeEnum, Is.EqualTo(FilingRuleType.Default));
            Assert.That(_settings.FilingRules.Count, Is.EqualTo(1), "Should add to settings");
        });
    }

    [Test]
    public void InitializeFilingRules_WithMultipleRules_LoadsAll()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));
        _settings.FilingRules.Add(new Core.Models.CurrentFolder.FilingRules.Contains("Project", _testDirectory));
        _settings.FilingRules.Add(new CatchAll(string.Empty, _testDirectory));

        // Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FilingRules.Count, Is.EqualTo(3));
            Assert.That(viewModel.FilingRules[0].RuleTypeEnum, Is.EqualTo(FilingRuleType.BeginsWith));
            Assert.That(viewModel.FilingRules[1].RuleTypeEnum, Is.EqualTo(FilingRuleType.Contains));
            Assert.That(viewModel.FilingRules[2].RuleTypeEnum, Is.EqualTo(FilingRuleType.Default));
        });
    }

    #endregion

    #region Filing Rules - Property Tests

    [Test]
    public void SelectedFilingRule_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.SelectedFilingRule))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.SelectedFilingRule = viewModel.FilingRules[0];

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void SelectedFilingRule_WhenSet_UpdatesCommandCanExecute()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));
        _settings.FilingRules.Add(new CatchAll(string.Empty, _testDirectory));
        
        var viewModel = CreateViewModel();
        
        // Initially no selection
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.EditFilingRuleCommand.CanExecute(null), Is.False);
            Assert.That(viewModel.RemoveFilingRuleCommand.CanExecute(null), Is.False);
        });

        // Act - Select a non-CatchAll rule
        viewModel.SelectedFilingRule = viewModel.FilingRules[0]; // BeginsWith rule

        // Assert - Commands should now be enabled
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.EditFilingRuleCommand.CanExecute(null), Is.True);
            Assert.That(viewModel.RemoveFilingRuleCommand.CanExecute(null), Is.True, 
                "Remove should be enabled for non-CatchAll rules");
        });
    }

    #endregion

    #region Filing Rules - Command Tests

    [Test]
    public void EditFilingRuleCommand_WithNoSelection_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = null;

        // Act
        var canExecute = viewModel.EditFilingRuleCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void EditFilingRuleCommand_WithSelection_CanExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[0];

        // Act
        var canExecute = viewModel.EditFilingRuleCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void RemoveFilingRuleCommand_WithNoSelection_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = null;

        // Act
        var canExecute = viewModel.RemoveFilingRuleCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void RemoveFilingRuleCommand_WithSelection_CanExecute()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));
        _settings.FilingRules.Add(new CatchAll(string.Empty, _testDirectory));
        
        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[0]; // Select non-CatchAll rule

        // Act
        var canExecute = viewModel.RemoveFilingRuleCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True, "Remove should be enabled for non-CatchAll rules");
    }

    [Test]
    public void RemoveFilingRuleCommand_WithCatchAllSelected_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[0]; // Select CatchAll rule (only one in default setup)

        // Act
        var canExecute = viewModel.RemoveFilingRuleCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False, "Cannot remove CatchAll rule");
    }

    [Test]
    public void MoveRuleUpCommand_WithFirstRule_CannotExecute()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("First", _testDirectory));
        _settings.FilingRules.Add(new BeginsWith("Second", _testDirectory));

        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[0]; // First rule

        // Act
        var canExecute = viewModel.MoveRuleUpCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False, "Cannot move first rule up");
    }

    [Test]
    public void MoveRuleUpCommand_WithSecondRule_CanExecute()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("First", _testDirectory));
        _settings.FilingRules.Add(new BeginsWith("Second", _testDirectory));

        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[1]; // Second rule

        // Act
        var canExecute = viewModel.MoveRuleUpCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void MoveRuleDownCommand_WithLastRule_CannotExecute()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("First", _testDirectory));
        _settings.FilingRules.Add(new BeginsWith("Last", _testDirectory));

        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[1]; // Last rule

        // Act
        var canExecute = viewModel.MoveRuleDownCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False, "Cannot move last rule down");
    }

    [Test]
    public void MoveRuleDownCommand_WithFirstRule_CanExecute()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("First", _testDirectory));
        _settings.FilingRules.Add(new BeginsWith("Last", _testDirectory));

        var viewModel = CreateViewModel();
        viewModel.SelectedFilingRule = viewModel.FilingRules[0]; // First rule

        // Act
        var canExecute = viewModel.MoveRuleDownCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    #endregion

    #region Filing Rules - Helper Method Tests

    [Test]
    public void IsDuplicateRule_WithExistingRule_ReturnsTrue()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));

        var viewModel = CreateViewModel();

        // Act
        var isDuplicate = viewModel.IsDuplicateRule(FilingRuleType.BeginsWith, "DOC");

        // Assert
        Assert.That(isDuplicate, Is.True);
    }

    [Test]
    public void IsDuplicateRule_WithNonExistingRule_ReturnsFalse()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));

        var viewModel = CreateViewModel();

        // Act
        var isDuplicate = viewModel.IsDuplicateRule(FilingRuleType.BeginsWith, "XYZ");

        // Assert
        Assert.That(isDuplicate, Is.False);
    }

    [Test]
    public void IsDuplicateRule_ExcludingSelf_ReturnsFalse()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));

        var viewModel = CreateViewModel();

        // Act - Check for duplicate but exclude index 0 (self)
        var isDuplicate = viewModel.IsDuplicateRule(FilingRuleType.BeginsWith, "DOC", excludeIndex: 0);

        // Assert
        Assert.That(isDuplicate, Is.False, "Should not consider self as duplicate");
    }

    [Test]
    public void CatchAllRuleExists_WithCatchAll_ReturnsTrue()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new CatchAll(string.Empty, _testDirectory));

        var viewModel = CreateViewModel();

        // Act
        var exists = viewModel.CatchAllRuleExists();

        // Assert
        Assert.That(exists, Is.True);
    }

    [Test]
    public void CatchAllRuleExists_WithoutCatchAll_ReturnsFalse()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new BeginsWith("DOC", _testDirectory));

        var viewModel = CreateViewModel();

        // Act
        var exists = viewModel.CatchAllRuleExists();

        // Assert
        Assert.That(exists, Is.False);
    }

    [Test]
    public void CatchAllRuleExists_ExcludingSelf_ReturnsFalse()
    {
        // Arrange
        _settings.FilingRules.Clear();
        _settings.FilingRules.Add(new CatchAll(string.Empty, _testDirectory));

        var viewModel = CreateViewModel();

        // Act - Check if CatchAll exists but exclude index 0 (the only CatchAll)
        var exists = viewModel.CatchAllRuleExists(excludeIndex: 0);

        // Assert
        Assert.That(exists, Is.False, "Should not consider self when excluded");
    }

    #endregion
}
