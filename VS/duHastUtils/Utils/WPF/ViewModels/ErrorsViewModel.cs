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

using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;

namespace duHastNet.Utils.WPF.ViewModels
{
    public class ErrorsViewModel : INotifyDataErrorInfo
    {
        //data validation
        public bool HasErrors => _errors.Count != 0;
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;
        private readonly Dictionary<string, List<string>> _errors = [];

        /// <summary>
        /// Data validation
        /// </summary>
        /// <param name="propertyName"></param>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errors.TryGetValue(propertyName, out var errors) ? errors : null;
        }

        /// <summary>
        /// Data validation - Add error
        /// </summary>
        /// <param name="propertyName"></param>
        /// <param name="errorMessage"></param>
        public void AddError(string propertyName, string errorMessage)
        {
            // make sure the property name is in the dictionary
            if (!_errors.TryGetValue(propertyName, out List<string> value))
            {
                value = [];
                _errors.Add(propertyName, value);
            }

            value.Add(errorMessage);
            // notify ui of error change
            OnErrorsChanged(propertyName);
        }

        /// <summary>
        /// Data validation - Clear errors for a property
        /// </summary>
        /// <param name="propertyName"></param>
        public void ClearErrors(string propertyName)
        {
            //only call OnErrorsChanged if there are errors to remove
            if (_errors.Remove(propertyName)) { OnErrorsChanged(propertyName); }
        }

        private void OnErrorsChanged(string propertyName)
        {
            ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
        }

    }
}
