using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.ViewModels
{
    public class ErrorsViewModel : INotifyDataErrorInfo
    {
        //data validation
        public bool HasErrors => _errors.Any();
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;
        private readonly Dictionary<string, List<string>> _errors = new Dictionary<string, List<string>>();

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
            if (!_errors.ContainsKey(propertyName))
            {
                _errors.Add(propertyName, new List<string>());
            }

            // add error message to the property
            _errors[propertyName].Add(errorMessage);
            // notify ui of error change
            OnErrorsChanged(propertyName);
        }

        /// <summary>
        /// Data validation - Clear errors for a property
        /// </summary>
        /// <param name="propertyName"></param>
        public void ClearErrors(string propertyName)
        {
            // check if property has errors and remove them
            if (_errors.ContainsKey(propertyName))
                //only call OnErrorsChanged if there are errors to remove
                if (_errors.Remove(propertyName)) { OnErrorsChanged(propertyName); }
        }

        private void OnErrorsChanged(string propertyName)
        {
            ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
        }

    }
}
