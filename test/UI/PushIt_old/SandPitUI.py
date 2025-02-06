import clr
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')
clr.AddReference('System.Data')
clr.AddReference('System.Xaml')

from System.IO import MemoryStream
from System.Text import Encoding
from System.Windows.Markup import XamlReader
from System.Windows import Application

from System.Data import DataTable
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs

class MainViewModel(INotifyPropertyChanged):
    def __init__(self):
        self.property_changed_handlers = []
        
        self._data_table = self.create_data_table()
        
        # selected row content
        self._selected_row_content = ""
        
        self._selected_item = None
        # add a handler for the PropertyChanged event
        #self.add_PropertyChanged(self.on_selection_changed)
        self._selected_index = -1
        
        # filter data
        self.update_data()

    @property
    def DataView(self):
        """
        The collection view of the data collection. to which the xaml view is bound to.
        """
        return self._data_table.DefaultView

    @property
    def SelectedRowContent(self):
        return self._selected_row_content
    
    @property
    def SelectedIndex(self):
        return self._selected_index
    
    @SelectedIndex.setter
    def SelectedIndex(self, value):
        # this returns the row index of the filtered default view not the actual data table.
        self._selected_index = value
        try:
            # get the row view from the data table view
            row_view = self._data_table.DefaultView[value]
            # get the original row from the data table
            row = row_view.Row
            # update the selected row content
            self._selected_row_content = ""
            for i in range(row.Table.Columns.Count):
                self._selected_row_content = self._selected_row_content + " Column:[{}] Value:[{}] ".format(row.Table.Columns[i].ColumnName, row[i])
            
            self.OnPropertyChanged("SelectedRowContent")
        except Exception as e:
            print("Error: ", e)

    def create_data_table(self):
        data_table = DataTable()
        data_table.Columns.Add("Col1")
        data_table.Columns.Add("Col2")
        data_table.Columns.Add("Col3")

        data_table.Rows.Add("Row1Col1", "Row1Col2", 0)
        data_table.Rows.Add("Row2Col1", "Row2Col2", 1)
        data_table.Rows.Add("Row3Col1", "Row3Col2", 1)
        data_table.Rows.Add("Row4Col1", "Row4Col2", 3)
        data_table.Rows.Add("Row5Col1", "Row5Col2", 2)

        return data_table

    def update_data(self):
        
        # set up collection view based on the observable collection of families
        # this is what the xaml view is binding to
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        self._data_table_view = self._data_table.DefaultView
        
        # Apply the filter to the DataView
        self._data_table_view.RowFilter = "Col1 <> 'Row2Col1'"

    def add_PropertyChanged(self, handler):
        self.property_changed_handlers.append(handler)

    def remove_PropertyChanged(self, handler):
        self.property_changed_handlers.remove(handler)

    def OnPropertyChanged(self, propertyName):
        #print("OnPropertyChanged: ", propertyName)
        args = PropertyChangedEventArgs(propertyName)
        for handler in self.property_changed_handlers:
            handler(self, args)

    PropertyChanged = None

# Define the XAML with a DataGrid, ScrollViewer, and TextBox
xaml = '''
<Window
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MainWindow" Height="350" Width="525">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="*" />
            <RowDefinition Height="Auto" />
        </Grid.RowDefinitions>
        <ScrollViewer Grid.Row="0" HorizontalScrollBarVisibility="Auto">
            <Grid x:Name="grid" MinWidth="400" Width="{Binding Path=ActualWidth, RelativeSource={RelativeSource FindAncestor, AncestorType={x:Type ScrollContentPresenter}}}">
                <DataGrid x:Name="dataGrid" 
                ItemsSource="{Binding DataView}" 
                AutoGenerateColumns="True" 
                IsReadOnly="True" 
                SelectionMode="Single" 
                SelectedIndex="{Binding SelectedIndex}"
                ColumnWidth="*"
                HorizontalAlignment="Stretch">
                    <DataGrid.RowStyle>
                        <Style TargetType="DataGridRow">
                            <Setter Property="Background" Value="Red" />
                            <Style.Triggers>
                                <DataTrigger Binding="{Binding Col3}" Value="1">
                                    <Setter Property="Background" Value="LightGray"></Setter>
                                </DataTrigger>
                                <DataTrigger Binding="{Binding Col3}" Value="0">
                                    <Setter Property="Background" Value="White"></Setter>
                                </DataTrigger>
                            </Style.Triggers>
                        </Style>
                    </DataGrid.RowStyle>
                </DataGrid>
            </Grid>
        </ScrollViewer>
        <TextBox Grid.Row="1" Text="{Binding SelectedRowContent}" IsReadOnly="True" Margin="5" />
    </Grid>
</Window>
'''

# Convert the XAML string to a .NET MemoryStream
xaml_bytes = Encoding.UTF8.GetBytes(xaml)
xaml_stream = MemoryStream(xaml_bytes)

# Parse the XAML
window = XamlReader.Load(xaml_stream)

# Set the DataContext in code
viewModel = MainViewModel()
window.DataContext = viewModel

# Run the application
app = Application()
app.Run(window)