using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class DynamicRowData : INotifyPropertyChanged
    {
        private Dictionary<string, object> _values = new Dictionary<string, object>();

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

        public Dictionary<string, object> Values => _values;

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
