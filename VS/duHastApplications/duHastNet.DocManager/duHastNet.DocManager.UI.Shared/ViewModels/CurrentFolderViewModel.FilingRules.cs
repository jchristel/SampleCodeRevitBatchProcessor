//
//License:
//
//
// Revit Batch Processor Sample Code
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


using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.FilingRules;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    /// <summary>
    /// Partial class for CurrentFolderViewModel containing all filing rules functionality
    /// </summary>
    public partial class CurrentFolderViewModel
    {
        #region Filing Rules - Observable Properties

        /// <summary>
        /// Observable collection of filing rules for display in ListView
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<FilingRuleViewModel> _filingRules = new();

        /// <summary>
        /// Currently selected filing rule in the ListView
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(EditFilingRuleCommand))]
        [NotifyCanExecuteChangedFor(nameof(RemoveFilingRuleCommand))]
        [NotifyCanExecuteChangedFor(nameof(MoveRuleUpCommand))]
        [NotifyCanExecuteChangedFor(nameof(MoveRuleDownCommand))]
        private FilingRuleViewModel? _selectedFilingRule;

        #endregion Filing Rules - Observable Properties

        #region Filing Rules - Initialization

        /// <summary>
        /// Initializes the filing rules collection from CurrentFolderManager settings
        /// Called during ViewModel construction
        /// </summary>
        private void InitializeFilingRules()
        {
            // If no rules exist, create default CatchAll rule
            if (_currentFolderManager.Settings.FilingRules.Count == 0)
            {
                CreateDefaultCatchAllRule();
            }

            // Load existing rules from settings into display collection
            LoadFilingRulesFromSettings();
        }

        /// <summary>
        /// Creates the default CatchAll rule pointing to user's Documents folder
        /// This ensures there's always at least one rule
        /// </summary>
        private void CreateDefaultCatchAllRule()
        {
            var documentsPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
            var defaultRule = new Core.Models.FilingRules.CatchAll(
                comparisonValue: string.Empty,
                targetDirectory: documentsPath
            );

            _currentFolderManager.Settings.FilingRules.Add(defaultRule);
        }

        /// <summary>
        /// Loads filing rules from CurrentFolderManager.Settings into the FilingRules observable collection
        /// </summary>
        private void LoadFilingRulesFromSettings()
        {
            FilingRules.Clear();

            foreach (var rule in _currentFolderManager.Settings.FilingRules)
            {
                var displayModel = new FilingRuleViewModel(rule);
                FilingRules.Add(displayModel);
            }
        }

        #endregion Filing Rules - Initialization

        #region Filing Rules - Commands

        /// <summary>
        /// Command to add a new filing rule
        /// Opens the Add Filing Rule dialog
        /// </summary>
        [RelayCommand]
        private void AddFilingRule()
        {
            try
            {
                // Create ViewModel for Add mode
                var dialogViewModel = new FilingRuleDialogViewModel(_dialogService, this);

                // Create and show dialog
                var dialog = new Views.FilingRuleDialog(dialogViewModel);
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && dialogViewModel.CreatedRule != null)
                {
                    // Add the new rule to both collections
                    AddRuleToCollections(dialogViewModel.CreatedRule);

                    _messageStore.SetCurrentMessage(
                        "Filing rule added successfully",
                        MessageTypes.Information);
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error adding filing rule: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a filing rule can be edited
        /// </summary>
        private bool CanEditFilingRule()
        {
            return SelectedFilingRule != null;
        }

        /// <summary>
        /// Command to edit the selected filing rule
        /// Opens the Edit Filing Rule dialog with existing values
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanEditFilingRule))]
        private void EditFilingRule()
        {
            if (SelectedFilingRule == null)
                return;

            try
            {
                var selectedIndex = FilingRules.IndexOf(SelectedFilingRule);

                // Create ViewModel for Edit mode
                var dialogViewModel = new FilingRuleDialogViewModel(
                    _dialogService,
                    this,
                    SelectedFilingRule.UnderlyingRule,
                    selectedIndex);

                // Create and show dialog
                var dialog = new Views.FilingRuleDialog(dialogViewModel);
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && dialogViewModel.CreatedRule != null)
                {
                    // Replace the rule at the same position
                    ReplaceRuleAtIndex(selectedIndex, dialogViewModel.CreatedRule);

                    _messageStore.SetCurrentMessage(
                        "Filing rule updated successfully",
                        MessageTypes.Information);
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error editing filing rule: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a filing rule can be removed
        /// CatchAll rules cannot be removed
        /// </summary>
        private bool CanRemoveFilingRule()
        {
            if (SelectedFilingRule == null)
                return false;

            // Cannot remove CatchAll rule
            return SelectedFilingRule.RuleTypeEnum != FilingRuleType.Default;
        }

        /// <summary>
        /// Command to remove the selected filing rule
        /// CatchAll rules cannot be removed
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanRemoveFilingRule))]
        private void RemoveFilingRule()
        {
            if (SelectedFilingRule == null)
                return;

            try
            {
                // Double-check: prevent removal of CatchAll
                if (SelectedFilingRule.RuleTypeEnum == FilingRuleType.Default)
                {
                    _messageStore.SetCurrentMessage(
                        "The Default (CatchAll) rule cannot be deleted. It can only be edited to change its target path.",
                        MessageTypes.Warning);
                    return;
                }

                // Remove from settings
                _currentFolderManager.Settings.FilingRules.Remove(SelectedFilingRule.UnderlyingRule);

                // Remove from display collection
                FilingRules.Remove(SelectedFilingRule);

                _messageStore.SetCurrentMessage(
                    "Filing rule removed successfully",
                    MessageTypes.Information);
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error removing filing rule: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if the selected rule can be moved up
        /// Cannot move if no selection or already at top
        /// </summary>
        private bool CanMoveRuleUp()
        {
            if (SelectedFilingRule == null)
                return false;

            var index = FilingRules.IndexOf(SelectedFilingRule);
            return index > 0;
        }

        /// <summary>
        /// Command to move the selected filing rule up (higher priority)
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanMoveRuleUp))]
        private void MoveRuleUp()
        {
            if (SelectedFilingRule == null)
                return;

            try
            {
                var index = FilingRules.IndexOf(SelectedFilingRule);
                if (index > 0)
                {
                    // Swap in display collection
                    FilingRules.Move(index, index - 1);

                    // Sync to settings
                    SyncRuleOrderToSettings();
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error moving filing rule: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if the selected rule can be moved down
        /// Cannot move if no selection or already at bottom
        /// </summary>
        private bool CanMoveRuleDown()
        {
            if (SelectedFilingRule == null)
                return false;

            var index = FilingRules.IndexOf(SelectedFilingRule);
            return index < FilingRules.Count - 1;
        }

        /// <summary>
        /// Command to move the selected filing rule down (lower priority)
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanMoveRuleDown))]
        private void MoveRuleDown()
        {
            if (SelectedFilingRule == null)
                return;

            try
            {
                var index = FilingRules.IndexOf(SelectedFilingRule);
                if (index < FilingRules.Count - 1)
                {
                    // Swap in display collection
                    FilingRules.Move(index, index + 1);

                    // Sync to settings
                    SyncRuleOrderToSettings();
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error moving filing rule: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        #endregion Filing Rules - Commands

        #region Filing Rules - Helper Methods

        /// <summary>
        /// Synchronizes the order of rules in the observable collection to the settings
        /// Called after Move Up/Down operations
        /// </summary>
        private void SyncRuleOrderToSettings()
        {
            _currentFolderManager.Settings.FilingRules.Clear();

            foreach (var displayModel in FilingRules)
            {
                _currentFolderManager.Settings.FilingRules.Add(displayModel.UnderlyingRule);
            }
        }

        /// <summary>
        /// Adds a newly created rule to both the settings and display collections
        /// </summary>
        /// <param name="rule">The rule to add</param>
        private void AddRuleToCollections(Core.Interfaces.IFilingRule rule)
        {
            // Add to settings
            _currentFolderManager.Settings.FilingRules.Add(rule);

            // Add to display collection
            var displayModel = new FilingRuleViewModel(rule);
            FilingRules.Add(displayModel);
        }

        /// <summary>
        /// Replaces a rule at a specific index with an edited version
        /// </summary>
        /// <param name="index">Index of the rule to replace</param>
        /// <param name="editedRule">The new rule to replace with</param>
        private void ReplaceRuleAtIndex(int index, Core.Interfaces.IFilingRule editedRule)
        {
            // Replace in settings
            _currentFolderManager.Settings.FilingRules[index] = editedRule;

            // Replace in display collection
            var displayModel = new FilingRuleViewModel(editedRule);
            FilingRules[index] = displayModel;
        }

        /// <summary>
        /// Checks if a rule with the given type and value already exists
        /// Used for duplicate prevention
        /// </summary>
        /// <param name="ruleType">The rule type to check</param>
        /// <param name="filterValue">The filter value to check</param>
        /// <param name="excludeIndex">Optional index to exclude from check (for edit mode)</param>
        /// <returns>True if a duplicate exists, false otherwise</returns>
        public bool IsDuplicateRule(FilingRuleType ruleType, string filterValue, int? excludeIndex = null)
        {
            for (int i = 0; i < FilingRules.Count; i++)
            {
                // Skip self when editing
                if (excludeIndex.HasValue && i == excludeIndex.Value)
                    continue;

                var rule = FilingRules[i];

                // Check type and value only (ignore target path)
                if (rule.RuleTypeEnum == ruleType &&
                    rule.FilterValue.Equals(filterValue, StringComparison.OrdinalIgnoreCase))
                {
                    return true; // Duplicate found
                }
            }
            return false;
        }

        /// <summary>
        /// Checks if a CatchAll rule already exists in the collection
        /// Used to enforce single CatchAll rule constraint
        /// </summary>
        /// <param name="excludeIndex">Optional index to exclude from check (for edit mode)</param>
        /// <returns>True if a CatchAll exists, false otherwise</returns>
        public bool CatchAllRuleExists(int? excludeIndex = null)
        {
            for (int i = 0; i < FilingRules.Count; i++)
            {
                // Skip self when editing
                if (excludeIndex.HasValue && i == excludeIndex.Value)
                    continue;

                if (FilingRules[i].RuleTypeEnum == FilingRuleType.Default)
                {
                    return true;
                }
            }
            return false;
        }

        #endregion Filing Rules - Helper Methods
    }
}