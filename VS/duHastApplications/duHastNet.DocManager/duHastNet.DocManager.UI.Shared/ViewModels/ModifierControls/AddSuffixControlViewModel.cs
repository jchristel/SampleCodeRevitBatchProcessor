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
    /// ViewModel for AddSuffix modifier control
    /// Handles a single parameter: the suffix text to add to the end of document numbers
    /// Example: "ABC-123" + suffix "-DWG" → "ABC-123-DWG"
    /// </summary>
    public partial class AddSuffixControlViewModel : ObservableValidator
    {
        #region Properties

        /// <summary>
        /// The suffix text to add to the end of the document number
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Suffix is required")]
        private string _suffix = string.Empty;

        #endregion Properties

        #region Property Changed Handlers

        /// <summary>
        /// Called when Suffix property changes
        /// Triggers validation to provide immediate feedback
        /// </summary>
        partial void OnSuffixChanged(string value)
        {
            ValidateProperty(value, nameof(Suffix));
        }

        #endregion Property Changed Handlers

        #region Constructor

        /// <summary>
        /// Default constructor for new modifier
        /// Validates all properties on creation to show initial validation state
        /// </summary>
        public AddSuffixControlViewModel()
        {
            // Validate immediately so user sees required field errors
            ValidateAllProperties();
        }

        /// <summary>
        /// Constructor for loading existing modifier
        /// </summary>
        /// <param name="modifier">Existing AddToEnd modifier to load</param>
        public AddSuffixControlViewModel(AddToEnd modifier)
        {
            LoadFrom(modifier);
        }

        #endregion Constructor

        #region Methods

        /// <summary>
        /// Creates an IDocumentNumberModifier from the current settings
        /// </summary>
        /// <returns>AddToEnd modifier instance</returns>
        public IDocumentNumberModifier CreateModifier()
        {
            // Validate before creating
            ValidateAllProperties();

            return new AddToEnd(Suffix);
        }

        /// <summary>
        /// Loads values from an existing AddToEnd modifier
        /// Used in edit mode
        /// </summary>
        /// <param name="modifier">The modifier to load from</param>
        public void LoadFrom(AddToEnd modifier)
        {
            if (modifier == null)
                throw new ArgumentNullException(nameof(modifier));

            // Access the suffix using reflection (private field)
            var suffixField = typeof(AddToEnd).GetField(
                "_suffix",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (suffixField != null)
            {
                Suffix = suffixField.GetValue(modifier) as string ?? string.Empty;
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