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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers;
using System.ComponentModel.DataAnnotations;

namespace duHastNet.DocManager.UI.Shared.ViewModels.ModifierControls
{
    /// <summary>
    /// ViewModel for AddPrefix modifier control
    /// Handles a single parameter: the prefix text to add to the beginning of document numbers
    /// Uses AddAtIndex with index 0 under the hood
    /// Example: "ABC-123" + prefix "DWG-" â†’ "DWG-ABC-123"
    /// </summary>
    public partial class AddPrefixControlViewModel : ObservableValidator
    {
        #region Properties

        /// <summary>
        /// The prefix text to add to the beginning of the document number
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Prefix is required")]
        private string _prefix = string.Empty;

        #endregion Properties

        #region Property Changed Handlers

        /// <summary>
        /// Called when Prefix property changes
        /// Triggers validation to provide immediate feedback
        /// </summary>
        partial void OnPrefixChanged(string value)
        {
            ValidateProperty(value, nameof(Prefix));
        }

        #endregion Property Changed Handlers

        #region Constructor

        /// <summary>
        /// Default constructor for new modifier
        /// Validates all properties on creation to show initial validation state
        /// </summary>
        public AddPrefixControlViewModel()
        {
            // Validate immediately so user sees required field errors
            ValidateAllProperties();
        }

        /// <summary>
        /// Constructor for loading existing modifier
        /// </summary>
        /// <param name="modifier">Existing AddAtIndex modifier with index 0</param>
        public AddPrefixControlViewModel(AddAtIndex modifier)
        {
            LoadFrom(modifier);
        }

        #endregion Constructor

        #region Methods

        /// <summary>
        /// Creates an IDocumentNumberModifier from the current settings
        /// Returns AddAtIndex with index 0 (prefix behavior)
        /// </summary>
        /// <returns>AddAtIndex modifier instance with index 0</returns>
        public IDocumentNumberModifier CreateModifier()
        {
            // Validate before creating
            ValidateAllProperties();

            // Prefix is AddAtIndex with index 0
            return new AddAtIndex(Prefix, 0);
        }

        /// <summary>
        /// Loads values from an existing AddAtIndex modifier
        /// Used in edit mode (only if index is 0)
        /// </summary>
        /// <param name="modifier">The modifier to load from</param>
        public void LoadFrom(AddAtIndex modifier)
        {
            if (modifier == null)
                throw new ArgumentNullException(nameof(modifier));

            // Access the value and index using reflection (private fields)
            var valueField = typeof(AddAtIndex).GetField(
                "_value",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var indexField = typeof(AddAtIndex).GetField(
                "_index",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (valueField != null && indexField != null)
            {
                var index = (int)(indexField.GetValue(modifier) ?? 0);

                // Only load if this is actually a prefix (index 0)
                if (index == 0)
                {
                    Prefix = valueField.GetValue(modifier) as string ?? string.Empty;
                }
            }
        }

        /// <summary>
        /// Validates all properties
        /// Called before creating the modifier
        /// </summary>
        public bool IsValid()
        {
            ValidateAllProperties();
            return !HasErrors;
        }

        #endregion Methods
    }
}