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
    /// ViewModel for AddAtIndex modifier control
    /// Handles two parameters: text to insert and the position (index) to insert it at
    /// Example: "ABC-123" + text "-DRAFT" at index 7 â†’ "ABC-123-DRAFT"
    /// Note: Index 0 is handled by AddPrefixControl, so this is for index > 0
    /// </summary>
    public partial class AddAtIndexControlViewModel : ObservableValidator
    {
        #region Properties

        /// <summary>
        /// The text to insert at the specified index
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Text to insert is required")]
        private string _text = string.Empty;

        /// <summary>
        /// The zero-based index position where text will be inserted
        /// Must be greater than 0 (use AddPrefix for index 0)
        /// </summary>
        [ObservableProperty]
        [Range(1, int.MaxValue, ErrorMessage = "Index must be 1 or greater (use Add Prefix for index 0)")]
        private int _index = 1;

        #endregion Properties

        #region Property Changed Handlers

        /// <summary>
        /// Called when Text property changes
        /// Triggers validation to provide immediate feedback
        /// </summary>
        partial void OnTextChanged(string value)
        {
            ValidateProperty(value, nameof(Text));
        }

        /// <summary>
        /// Called when Index property changes
        /// Triggers validation to provide immediate feedback
        /// </summary>
        partial void OnIndexChanged(int value)
        {
            ValidateProperty(value, nameof(Index));
        }

        #endregion Property Changed Handlers

        #region Constructor

        /// <summary>
        /// Default constructor for new modifier
        /// Validates all properties on creation to show initial validation state
        /// </summary>
        public AddAtIndexControlViewModel()
        {
            // Validate immediately so user sees required field errors
            ValidateAllProperties();
        }

        /// <summary>
        /// Constructor for loading existing modifier
        /// </summary>
        /// <param name="modifier">Existing AddAtIndex modifier (index must be > 0)</param>
        public AddAtIndexControlViewModel(AddAtIndex modifier)
        {
            LoadFrom(modifier);
        }

        #endregion Constructor

        #region Methods

        /// <summary>
        /// Creates an IDocumentNumberModifier from the current settings
        /// </summary>
        /// <returns>AddAtIndex modifier instance</returns>
        public IDocumentNumberModifier CreateModifier()
        {
            // Validate before creating
            ValidateAllProperties();

            return new AddAtIndex(Text, Index);
        }

        /// <summary>
        /// Loads values from an existing AddAtIndex modifier
        /// Used in edit mode (only if index > 0, since index 0 is prefix)
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
                var loadedIndex = (int)(indexField.GetValue(modifier) ?? 1);

                // Only load if index > 0 (index 0 is prefix, handled by AddPrefixControl)
                if (loadedIndex > 0)
                {
                    Text = valueField.GetValue(modifier) as string ?? string.Empty;
                    Index = loadedIndex;
                }
                else
                {
                    // This shouldn't happen, but handle gracefully
                    throw new ArgumentException("AddAtIndex with index 0 should use AddPrefixControl instead");
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