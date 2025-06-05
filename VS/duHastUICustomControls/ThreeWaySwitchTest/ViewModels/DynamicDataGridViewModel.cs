using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.Utils.WPF.Commands;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace duHastNet.UI.ThreeWaySwitchTest.ViewModels
{
    public class DynamicDataGridViewModel : INotifyPropertyChanged
    {
        private ObservableCollection<DynamicColumnDefinition> _columnDefinitions;
        private ObservableCollection<DynamicRowData> _data;

        public ObservableCollection<DynamicColumnDefinition> ColumnDefinitions
        {
            get => _columnDefinitions;
            set
            {
                _columnDefinitions = value;
                OnPropertyChanged();
            }
        }

        public ObservableCollection<DynamicRowData> Data
        {
            get => _data;
            set
            {
                _data = value;
                OnPropertyChanged();
            }
        }

        public ICommand InitializeGridCommand { get; }
        public ICommand AddRowCommand { get; }

        public DynamicDataGridViewModel()
        {
            InitializeGridCommand = new RelayCommand(_ => InitializeGrid());
            AddRowCommand = new RelayCommand(_ => AddRow());


            // Initialize with sample data
            InitializeGrid();
        }

        private void InitializeGrid()
        {
            // Define columns
            ColumnDefinitions = new ObservableCollection<DynamicColumnDefinition>
        {
            new DynamicColumnDefinition("Id", "ID", typeof(int)) { Width = 80, IsReadOnly = true },
            new DynamicColumnDefinition("Name", "Name", typeof(string)) { Width = 150 },
            new DynamicColumnDefinition("Age", "Age", typeof(int)) { Width = 80 },
            new DynamicColumnDefinition("Email", "Email", typeof(string)) { Width = 200 },
            new DynamicColumnDefinition("IsActive", "Active", typeof(bool)) { Width = 80 }
        };

            // Initialize data collection
            Data = new ObservableCollection<DynamicRowData>();

            // Add sample data
            AddSampleData();
        }

        private void AddSampleData()
        {
            var sampleData = new[]
            {
            new { Id = 1, Name = "John Doe", Age = 30, Email = "john@example.com", IsActive = true },
            new { Id = 2, Name = "Jane Smith", Age = 25, Email = "jane@example.com", IsActive = false },
            new { Id = 3, Name = "Bob Johnson", Age = 35, Email = "bob@example.com", IsActive = true }
        };

            foreach (var item in sampleData)
            {
                var row = new DynamicRowData();
                row["Id"] = item.Id;
                row["Name"] = item.Name;
                row["Age"] = item.Age;
                row["Email"] = item.Email;
                row["IsActive"] = item.IsActive;

                Data.Add(row);
            }
        }

        private void AddRow()
        {
            var newRow = new DynamicRowData();
            newRow["Id"] = Data.Count + 1;
            newRow["Name"] = "New Person";
            newRow["Age"] = 0;
            newRow["Email"] = "new@example.com";
            newRow["IsActive"] = false;

            Data.Add(newRow);
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    
}
