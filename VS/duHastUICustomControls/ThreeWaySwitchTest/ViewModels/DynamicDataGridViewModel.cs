using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Linq;


namespace duHastNet.UI.ThreeWaySwitchTest.ViewModels
{
    public class DynamicDataGridViewModel : BaseDynamicGridViewModel<DynamicRowData>
    {
        public DynamicDataGridViewModel()
        {
            // Base class handles initialization
            // Add some sample data
            AddSampleData();
        }

        protected override void InitializeAvailableColumns()
        {
            AvailableColumns = new System.Collections.ObjectModel.ObservableCollection<AvailableColumnDefinition>
            {
                new AvailableColumnDefinition("Id", "ID", typeof(int), "Identity"),
                new AvailableColumnDefinition("Name", "Name", typeof(string), "Personal"),
                new AvailableColumnDefinition("Sure Name", "SureName", typeof(string), "Personal"),
                new AvailableColumnDefinition("Middle Name", "MiddleName", typeof(string), "Personal"),
                new AvailableColumnDefinition("Age", "Age", typeof(int), "Personal"),
                new AvailableColumnDefinition("Linked In", "LinkedIn", typeof(string), "Contact"),
                new AvailableColumnDefinition("Instagram", "Instagram", typeof(string), "Contact"),
                new AvailableColumnDefinition("Email", "Email", typeof(string), "Contact"),
                new AvailableColumnDefinition("IsActive", "Active", typeof(bool), "Status"),
                new AvailableColumnDefinition("PhoneNumber", "Phone", typeof(string), "Contact"),
                new AvailableColumnDefinition("Department", "Department", typeof(string), "Work"),
                new AvailableColumnDefinition("HireDate", "Hire Date", typeof(DateTime), "Work")
            };

            // Set up default columns
            ColumnDefinitions.Add(new DynamicColumnDefinition("Id", "ID", typeof(int)) { Width = 80, IsReadOnly = true });
            ColumnDefinitions.Add(new DynamicColumnDefinition("Name", "Name", typeof(string)) { Width = 150, IsReadOnly = true });
            ColumnDefinitions.Add(new DynamicColumnDefinition("Age", "Age", typeof(int)) { Width = 80, IsReadOnly = true });
            ColumnDefinitions.Add(new DynamicColumnDefinition("Email", "Email", typeof(string)) { Width = 200, IsReadOnly = true });
            ColumnDefinitions.Add(new DynamicColumnDefinition("IsActive", "Active", typeof(bool)) { Width = 80 });
        }

        /// <summary>
        /// overrides the default list of read only columns in the base view model. This is important!!
        /// </summary>
        /// <param name="propertyName"></param>
        /// <returns></returns>
        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            var readOnlyColumns = new[] { "Id", "Name", "Age", "Email" };
            return readOnlyColumns.Contains(propertyName, StringComparer.OrdinalIgnoreCase);
        }

        protected override DynamicRowData CreateNewRow()
        {
            var newRow = new DynamicRowData();
            newRow["Id"] = Data.Count + 1;
            newRow["Name"] = "New Person";
            newRow["SureName"] = "sure";
            newRow["MiddleName"] = "middle";
            newRow["Age"] = 0;
            newRow["Email"] = "new@example.com";
            newRow["Instagram"] = "insta";
            newRow["LinkedIn"] = "insta";
            newRow["IsActive"] = false;
            return newRow;
        }

        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {
            switch (columnDef.PropertyName)
            {
                case "Id":
                    return Data.Count + 1;
                case "Name":
                    return "New Person";
                case "SureName":
                    return "sure name";
                case "MiddleName":
                    return "middle";
                case "Age":
                    return 25;
                case "Email":
                    return "person@example.com";
                case "LinkedIn":
                    return "linked In";
                case "Instagram":
                    return "Instagram";
                case "IsActive":
                    return false;
                case "PhoneNumber":
                    return "555-0000";
                case "Department":
                    return "General";
                case "HireDate":
                    return DateTime.Now;
                default:
                    return GetDefaultValue(columnDef.DataType);
            }
        }

        private void AddSampleData()
        {
            var sampleData = new[]
            {
                new { Id = 1, Name = "John Doe", Age = 30, Email = "john@example.com", IsActive = true },
                new { Id = 2, Name = "Jane Smith", Age = 25, Email = "jane@example.com", IsActive = false },
                new { Id = 3, Name = "Jan Smith", Age = 25, Email = "jan@example.com", IsActive = true }
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
    }


}
