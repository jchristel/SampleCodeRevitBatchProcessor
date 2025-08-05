# CellEditor Control

A custom WPF control that provides an easy-to-use interface for editing tabular data with built-in row management capabilities.

## Features

- ✅ Display data from simple header/data row collections
- ✅ Add, duplicate, and delete rows with toolbar buttons
- ✅ Get data exactly as displayed (respecting column reordering, sorting)
- ✅ Support for read-only columns
- ✅ Right-click context menu
- ✅ Data change events
- ✅ Column reordering and sorting
- ✅ Type inference (bool, int, double, DateTime, string)

## Quick Start

### 1. Add to XAML

```xml
<local:CellEditor x:Name="MyCellEditor"
                 HeaderRow="{Binding MyHeaders}"
                 DataRows="{Binding MyDataRows}"
                 ReadOnlyColumns="{Binding MyReadOnlyColumns}"
                 AllowAddRow="True"
                 AllowDuplicateRow="True"
                 AllowDeleteRow="True"
                 DataChanged="OnDataChanged"/>
```

### 2. Prepare Data in Code-Behind or ViewModel

```csharp
// Headers
var headers = new List<string> { "Name", "Age", "Active", "Salary" };

// Data rows
var dataRows = new List<List<object>>
{
    new List<object> { "John", 30, true, 50000.0 },
    new List<object> { "Jane", 25, false, 45000.0 }
};

// Optional: Read-only columns
var readOnlyColumns = new List<string> { "Age" };
```

### 3. Get Data Back

```csharp
// Get data as currently displayed (with any reordering/sorting)
var (currentHeaders, currentData) = cellEditor.GetCurrentData();

// Get data in original order
var (originalHeaders, originalData) = cellEditor.GetOriginalData();
```

## API Reference

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `HeaderRow` | `List<string>` | `null` | Column headers |
| `DataRows` | `List<List<object>>` | `null` | Data rows (each inner list is one row) |
| `ReadOnlyColumns` | `List<string>` | `null` | Headers of columns that should be read-only |
| `AllowAddRow` | `bool` | `true` | Show/hide Add Row button |
| `AllowDuplicateRow` | `bool` | `true` | Show/hide Duplicate Row button |
| `AllowDeleteRow` | `bool` | `true` | Show/hide Delete Row button |

### Events

| Event | Type | Description |
|-------|------|-------------|
| `DataChanged` | `RoutedEventHandler` | Fired when data is modified (add, delete, edit, sort) |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `GetCurrentData()` | `(List<string>, List<List<object>>)` | Returns headers and data as currently displayed |
| `GetOriginalData()` | `(List<string>, List<List<object>>)` | Returns headers and data in original order |
| `RefreshData(headers, dataRows)` | `void` | Updates the control with new data |

## Data Types

The control automatically infers data types from input values:

| Type | Display | Notes |
|------|---------|-------|
| `bool` | Checkbox | True/false values |
| `int` | Numeric input | Whole numbers |
| `double` | Decimal input | Floating point numbers |
| `DateTime` | Text | Formatted as "dd/MM/yyyy HH:mm:ss" |
| `string` | Text input | Default for all other types |

## User Interactions

### Toolbar Buttons
- **Add Row**: Adds a new empty row at the bottom
- **Duplicate Row**: Duplicates the currently selected row (requires row selection)
- **Delete Row**: Removes the currently selected row (requires row selection)

### Right-Click Context Menu
Same options as toolbar buttons, available via right-click anywhere on the grid.

### Column Operations
- **Reorder**: Drag column headers to change column order
- **Sort**: Click column headers to sort data (click again to reverse)
- **Resize**: Drag column borders to adjust width

## Usage Examples

### Basic Usage

```csharp
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        LoadSampleData();
    }

    private void LoadSampleData()
    {
        var headers = new List<string> { "Product", "Price", "InStock", "LastUpdated" };
        var data = new List<List<object>>
        {
            new List<object> { "Widget A", 19.99, true, DateTime.Now.AddDays(-5) },
            new List<object> { "Widget B", 29.99, false, DateTime.Now.AddDays(-2) },
            new List<object> { "Widget C", 39.99, true, DateTime.Now.AddDays(-1) }
        };

        MyCellEditor.HeaderRow = headers;
        MyCellEditor.DataRows = data;
        MyCellEditor.ReadOnlyColumns = new List<string> { "LastUpdated" };
    }

    private void OnDataChanged(object sender, RoutedEventArgs e)
    {
        // React to data changes
        var (headers, data) = MyCellEditor.GetCurrentData();
        Console.WriteLine($"Data changed: {data.Count} rows, {headers.Count} columns");
    }
}
```

### MVVM Pattern

```csharp
public class MainViewModel : INotifyPropertyChanged
{
    private List<string> _headerRow;
    private List<List<object>> _dataRows;
    private List<string> _readOnlyColumns;

    public List<string> HeaderRow
    {
        get => _headerRow;
        set { _headerRow = value; OnPropertyChanged(); }
    }

    public List<List<object>> DataRows
    {
        get => _dataRows;
        set { _dataRows = value; OnPropertyChanged(); }
    }

    public List<string> ReadOnlyColumns
    {
        get => _readOnlyColumns;
        set { _readOnlyColumns = value; OnPropertyChanged(); }
    }

    public ICommand LoadDataCommand { get; }
    public ICommand SaveDataCommand { get; }

    public MainViewModel()
    {
        LoadDataCommand = new RelayCommand(_ => LoadData());
        SaveDataCommand = new RelayCommand(_ => SaveData());
    }

    private void LoadData()
    {
        HeaderRow = new List<string> { "Name", "Email", "Active" };
        DataRows = new List<List<object>>
        {
            new List<object> { "John Doe", "john@example.com", true },
            new List<object> { "Jane Smith", "jane@example.com", false }
        };
        ReadOnlyColumns = new List<string> { "Email" };
    }

    private void SaveData()
    {
        // Access data from CellEditor control
        // Implementation depends on how you reference the control
    }

    public event PropertyChangedEventHandler PropertyChanged;
    protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

## Data Flow Example

**Input Data:**
```csharp
Headers: ["Name", "Age", "Department"]
Data: [
    ["John", 30, "IT"],
    ["Jane", 25, "HR"]
]
```

**After User Reorders Columns and Sorts by Department:**

`GetCurrentData()` returns:
```csharp
Headers: ["Department", "Name", "Age"]  // Reordered
Data: [
    ["HR", "Jane", 25],                 // Sorted
    ["IT", "John", 30]
]
```

`GetOriginalData()` returns:
```csharp
Headers: ["Name", "Age", "Department"]  // Original order
Data: [
    ["John", 30, "IT"],                 // Original order
    ["Jane", 25, "HR"]
]
```

## Installation

1. **Add References**: Ensure you have references to:
   - `duHastNet.UI.CustomControls.CustomDataGrid` (DynamicDataGrid)
   - `duHastNet.Utils.WPF.ViewModels` (BaseDynamicGridViewModel)
   - `duHastNet.Utils.WPF.Commands` (RelayCommand)

2. **Add Files**: Add the following files to your project:
   - `CellEditor.cs` - Main control
   - `ViewModels/CellEditorViewModel.cs` - ViewModel
   - `CellEditor/CellEditorStyle.xaml` - Control template
   - `Converters/BooleanToVisibilityConverter.cs` - Converter
   - `Converters/NullToBooleanConverter.cs` - Converter

3. **Update Generic.xaml**: Ensure your `Themes/Generic.xaml` includes:
   ```xml
   <ResourceDictionary Source="pack://application:,,,/YourAssemblyName;component/CellEditor/CellEditorStyle.xaml"/>
   ```

4. **Add Namespace**: In your XAML files:
   ```xml
   xmlns:local="clr-namespace:duHastNet.UI.CustomControls"
   ```

## Styling

The control can be styled using standard WPF techniques:

```xml
<Style TargetType="{x:Type local:CellEditor}">
    <Setter Property="Background" Value="White"/>
    <Setter Property="BorderBrush" Value="Gray"/>
    <Setter Property="BorderThickness" Value="1"/>
</Style>
```

Individual elements can be styled by targeting the template parts:
- `PART_DataGrid` - The main data grid
- `PART_AddRowButton` - Add row button
- `PART_DuplicateRowButton` - Duplicate row button  
- `PART_DeleteRowButton` - Delete row button

## Troubleshooting

### Common Issues

**Q: The control doesn't appear**
- Check that `CellEditorStyle.xaml` is included in your `Generic.xaml`
- Verify namespace declarations in XAML

**Q: Buttons are not working**
- Ensure `RelayCommand` is available in your project
- Check that DataContext is properly set

**Q: Data changes aren't reflected**
- Make sure you're using `INotifyPropertyChanged` for data-bound properties
- Verify that `HeaderRow` and `DataRows` are being set correctly

**Q: Converters not found**
- Check that converter classes are in the correct namespace
- Verify `xmlns:converters` declaration in XAML

### Performance Considerations

- For large datasets (1000+ rows), consider implementing virtualization
- Use appropriate data types to avoid unnecessary conversions
- Consider debouncing `DataChanged` events if you have expensive operations

## License

This control is part of the duHast.NET library and follows the same BSD license terms.