using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class DynamicRowData : INotifyPropertyChanged
    {
        private Dictionary<string, object> _values = [];
        public Dictionary<string, object> Values
        {
            get
            {
                return _values;
            }
        }

        public object this[string propertyName]
        {
            get => _values.TryGetValue(propertyName, out var value) ? value : null;
            set
            {
                if (!Equals(_values.TryGetValue(propertyName, out var currentValue) ? currentValue : null, value))
                {
                    _values[propertyName] = value;
                    OnPropertyChanged(propertyName);
                }
            }
        }

        
        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
