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


namespace duHastNet.DocManager.Core.Models
{
    public class CustomFieldsContainer
    {
        private List<CustomFieldDefinition> _customFields;

        public int CustomFieldsCount
        {
            get { return _customFields.Count; }
        }

        #region get custom fields

        /// <summary>
        /// clear all custom field definitions
        /// </summary>
        public void ClearCustomFields()
        {
            _customFields.Clear();
        }

        /// <summary>
        /// returns all custom field definitions
        /// </summary>
        /// <returns></returns>
        public IEnumerable<CustomFieldDefinition> GetAllCustomFields()
        {
            return _customFields;
        }

        /// <summary>
        /// Returns only active custom field definitions
        /// </summary>
        /// <returns></returns>
        public IEnumerable<CustomFieldDefinition> GetActiveCustomFieldDefinitions()
        {
            return _customFields.Where(cfd => cfd.IsActive);
        }

        #endregion custom fields

        #region edit custom fields

        /// <summary>
        /// adds a custom field definition to the container
        /// </summary>
        /// <param name="customField"></param>
        public void AddCustomField(CustomFieldDefinition customField)
        {
            //null check
            if (customField == null)
            {
                throw new ArgumentNullException(nameof(customField), "Custom field cannot be null.");
            }

            //check if a custom field with the same name already exists
            foreach (var existingCustomField in _customFields)
            {
                if (existingCustomField.Conflicts(customField))
                {
                    throw new Exceptions.CustomFieldDuplicateException(existingCustomField, customField);
                }
            }

            //no conflict found - add custom field
            _customFields.Add(customField);
        }

        #endregion edit custom fields

        public CustomFieldsContainer()
        {
            _customFields = [];
        }

    }
}
