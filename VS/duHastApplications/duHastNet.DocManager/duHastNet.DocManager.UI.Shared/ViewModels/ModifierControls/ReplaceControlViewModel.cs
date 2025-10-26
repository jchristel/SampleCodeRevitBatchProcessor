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
using duHastNet.DocManager.Core.Models.DocumentNumberModifiers;
using System.ComponentModel.DataAnnotations;

namespace duHastNet.DocManager.UI.Shared.ViewModels.ModifierControls
{
    /// <summary>
    /// ViewModel for Replace modifier control
    /// Handles two parameters: old value to find and new value to replace it with
    /// Example: "ABC-123" + replace "ABC" with "XYZ" → "XYZ-123"
    /// </summary>
    public partial class ReplaceControlViewModel : ObservableValidator
    {
        #region Properties

        /// <summary>
        /// The old value (text to find) in the document number
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Old value (find) is required")]
        private string _oldValue = string.Empty;

        /// <summary>
        /// The new value (replacement text) to replace the old value with
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "New value (replace with) is required")]
        private string _newValue = string.Empty;

        #endregion Properties

        #region Constructor

        /// <summary>
        /// Default constructor for new modifier
        /// </summary>
        public ReplaceControlViewModel()
        {
        }

        /// <summary>
        /// Constructor for loading existing modifier
        /// </summary>
        /// <param name="modifier">Existing Replace modifier</param>
        public ReplaceControlViewModel(Replace modifier)
        {
            LoadFrom(modifier);
        }

        #endregion Constructor

        #region Methods

        /// <summary>
        /// Creates an IDocumentNumberModifier from the current settings
        /// </summary>
        /// <returns>Replace modifier instance</returns>
        public IDocumentNumberModifier CreateModifier()
        {
            // Validate before creating
            ValidateAllProperties();

            return new Replace(OldValue, NewValue);
        }

        /// <summary>
        /// Loads values from an existing Replace modifier
        /// Used in edit mode
        /// </summary>
        /// <param name="modifier">The modifier to load from</param>
        public void LoadFrom(Replace modifier)
        {
            if (modifier == null)
                throw new ArgumentNullException(nameof(modifier));

            // Access the old and new values using reflection (private fields)
            var oldValueField = typeof(Replace).GetField(
                "_oldValue",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var newValueField = typeof(Replace).GetField(
                "_newValue",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (oldValueField != null && newValueField != null)
            {
                OldValue = oldValueField.GetValue(modifier) as string ?? string.Empty;
                NewValue = newValueField.GetValue(modifier) as string ?? string.Empty;
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
