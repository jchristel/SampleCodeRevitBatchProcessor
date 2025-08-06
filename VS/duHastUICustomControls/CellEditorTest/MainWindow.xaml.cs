using System.ComponentModel;
using System.Data;
using System.Text;
using System.Windows;


using System.Runtime.CompilerServices;


namespace duHastNet.UI.CustomControls.CellEditorTest
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window, INotifyPropertyChanged
    {
        private List<string> _headerRow;
        private List<List<object>> _dataRows;
        private List<string> _readOnlyColumns;

        #region Properties

        public List<string> HeaderRow
        {
            get => _headerRow;
            set
            {
                _headerRow = value;
                OnPropertyChanged();
            }
        }

        public List<List<object>> DataRows
        {
            get => _dataRows;
            set
            {
                _dataRows = value;
                OnPropertyChanged();
            }
        }

        public List<string> ReadOnlyColumns
        {
            get => _readOnlyColumns;
            set
            {
                _readOnlyColumns = value;
                OnPropertyChanged();
            }
        }
        #endregion


        public MainWindow()
        {
            InitializeComponent();

            DataContext = this;

            // Initialize with empty data
            HeaderRow = new List<string>();
            DataRows = new List<List<object>>();
            ReadOnlyColumns = new List<string>();

        }
        #region Event Handlers

        private void LoadSampleData_Click(object sender, RoutedEventArgs e)
        {
            // Create sample data
            HeaderRow = new List<string> { "Name", "Age", "Department", "Salary", "Active", "Start Date" };

            DataRows = new List<List<object>>
            {
                new List<object> { "John Doe", 30, "Engineering", 75000.0, true, DateTime.Now.AddYears(-2) },
                new List<object> { "Jane Smith", 28, "Marketing", 65000.0, true, DateTime.Now.AddYears(-1) },
                new List<object> { "Bob Johnson", 35, "Engineering", 82000.0, false, DateTime.Now.AddYears(-3) },
                new List<object> { "Alice Brown", 32, "HR", 55000.0, true, DateTime.Now.AddMonths(-8) },
                new List<object> { "Charlie Wilson", 29, "Sales", 60000.0, true, DateTime.Now.AddMonths(-6) }
            };

            // Make some columns read-only
            ReadOnlyColumns = new List<string> { "Start Date" };

            OutputTextBox.Text = "Sample data loaded successfully!";
        }

        private void GetCurrentData_Click(object sender, RoutedEventArgs e)
        {
            var (headers, data) = CellEditorControl.GetCurrentData();
            DisplayData("Current Data (as displayed in grid)", headers, data);
        }

        private void GetOriginalData_Click(object sender, RoutedEventArgs e)
        {
            var (headers, data) = CellEditorControl.GetOriginalData();
            DisplayData("Original Data (original column order)", headers, data);
        }

        private void ClearData_Click(object sender, RoutedEventArgs e)
        {
            HeaderRow = new List<string>();
            DataRows = new List<List<object>>();
            OutputTextBox.Text = "Data cleared!";
        }

        private void CellEditorControl_DataChanged(object sender, RoutedEventArgs e)
        {
            OutputTextBox.Text += $"\n[{DateTime.Now:HH:mm:ss}] Data changed event fired!";
        }

        private void ShowAvailableColumns_Click(object sender, RoutedEventArgs e)
        {
            var availableColumns = CellEditorControl.GetAvailableColumns();
            var currentColumns = CellEditorControl.GetCurrentColumns();
            var columnsToAdd = CellEditorControl.GetColumnsAvailableToAdd();

            var sb = new StringBuilder();
            sb.AppendLine("=== Column Information ===");
            sb.AppendLine($"All Available Columns: {string.Join(", ", availableColumns)}");
            sb.AppendLine($"Currently Displayed: {string.Join(", ", currentColumns)}");
            sb.AppendLine($"Available to Add: {string.Join(", ", columnsToAdd)}");

            OutputTextBox.Text = sb.ToString();
        }

        private void RemoveDepartmentColumn_Click(object sender, RoutedEventArgs e)
        {
            CellEditorControl.RemoveColumn("Department");
            OutputTextBox.Text = "Department column removed (data preserved)";
        }

        private void AddDepartmentColumn_Click(object sender, RoutedEventArgs e)
        {
            CellEditorControl.AddColumn("Department");
            OutputTextBox.Text = "Department column added back";
        }

        #endregion

        #region Helper Methods

        private void DisplayData(string title, List<string> headers, List<List<object>> data)
        {
            var sb = new StringBuilder();
            sb.AppendLine($"=== {title} ===");
            sb.AppendLine($"Generated at: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            sb.AppendLine();

            if (headers?.Count > 0)
            {
                sb.AppendLine("Headers:");
                sb.AppendLine(string.Join(" | ", headers));
                sb.AppendLine(new string('-', headers.Sum(h => h.Length + 3)));

                if (data?.Count > 0)
                {
                    sb.AppendLine("Data Rows:");
                    for (int i = 0; i < data.Count; i++)
                    {
                        var row = data[i];
                        var formattedRow = new List<string>();

                        for (int j = 0; j < headers.Count; j++)
                        {
                            if (j < row.Count)
                            {
                                var value = row[j];
                                string formattedValue;

                                if (value is DateTime dt)
                                {
                                    formattedValue = dt.ToString("yyyy-MM-dd HH:mm");
                                }
                                else if (value is double d)
                                {
                                    formattedValue = d.ToString("F2");
                                }
                                else if (value is bool b)
                                {
                                    formattedValue = b.ToString();
                                }
                                else if (value == null)
                                {
                                    formattedValue = "NULL";
                                }
                                else
                                {
                                    formattedValue = value.ToString();
                                }

                                formattedRow.Add(formattedValue);
                            }
                            else
                            {
                                formattedRow.Add("NULL");
                            }
                        }

                        sb.AppendLine($"Row {i + 1}: {string.Join(" | ", formattedRow)}");
                    }
                }
                else
                {
                    sb.AppendLine("No data rows found.");
                }
            }
            else
            {
                sb.AppendLine("No headers found.");
            }

            sb.AppendLine();
            sb.AppendLine("Raw Data Structure:");
            sb.AppendLine($"Headers Count: {headers?.Count ?? 0}");
            sb.AppendLine($"Data Rows Count: {data?.Count ?? 0}");

            if (data?.Count > 0)
            {
                sb.AppendLine($"Columns per row: {string.Join(", ", data.Select((row, index) => $"Row{index + 1}:{row.Count}"))}");
            }

            OutputTextBox.Text = sb.ToString();
        }

        #endregion

        #region INotifyPropertyChanged

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        #endregion
    }
}