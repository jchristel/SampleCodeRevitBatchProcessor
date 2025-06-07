using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class DynamicColumnDefinition : INotifyPropertyChanged
    {
        private bool _isReadOnly = false;

        public string PropertyName { get; set; }
        public string DisplayName { get; set; }
        public Type DataType { get; set; }
        public double Width { get; set; } = 100;

        public bool IsReadOnly
        {
            get => _isReadOnly;
            set
            {
                if (_isReadOnly != value)
                {
                    _isReadOnly = value;
                    OnPropertyChanged();
                }
            }
        }

        public DynamicColumnDefinition(string propertyName, string displayName, Type dataType)
        {
            PropertyName = propertyName;
            DisplayName = displayName;
            DataType = dataType;
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
