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
using duHastNet.DocManager.Core.Models;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    /// <summary>
    /// ViewModel wrapper for custom field definitions to display in ListView
    /// </summary>
    public partial class CustomFieldViewModel : ObservableObject
    {
        /// <summary>
        /// The ID of the custom field definition (0 for new fields not yet saved)
        /// </summary>
        [ObservableProperty]
        private int _id;

        /// <summary>
        /// The name of the custom property field
        /// </summary>
        [ObservableProperty]
        private string _propertyName = string.Empty;

        /// <summary>
        /// Whether this custom field is active or inactive
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(StatusDisplay))]
        private bool _isActive = true;

        /// <summary>
        /// Display text for the Status column
        /// </summary>
        public string StatusDisplay => IsActive ? "Active" : "Inactive";

        /// <summary>
        /// Creates a new CustomFieldViewModel from a CustomFieldDefinition model
        /// </summary>
        /// <param name="definition">The custom field definition</param>
        public CustomFieldViewModel(CustomFieldDefinition definition)
        {
            Id = definition.Id;
            PropertyName = definition.PropertyName;
            IsActive = definition.IsActive;
        }

        /// <summary>
        /// Creates a new CustomFieldViewModel with the specified property name (for new fields)
        /// </summary>
        /// <param name="propertyName">The custom property name</param>
        public CustomFieldViewModel(string propertyName)
        {
            Id = 0; // Not yet saved to database
            PropertyName = propertyName;
            IsActive = true;
        }

        /// <summary>
        /// Parameterless constructor for design-time support
        /// </summary>
        public CustomFieldViewModel()
        {
        }

        /// <summary>
        /// Creates a clone of this custom field view model
        /// Used for tracking original state
        /// </summary>
        public CustomFieldViewModel Clone()
        {
            return new CustomFieldViewModel
            {
                Id = this.Id,
                PropertyName = this.PropertyName,
                IsActive = this.IsActive
            };
        }

        public override string ToString()
        {
            return $"{PropertyName} ({StatusDisplay})";
        }
    }
}