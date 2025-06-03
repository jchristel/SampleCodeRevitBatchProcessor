using duHastNet.UI.CustomControls;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Windows;


namespace ThreeWaySwitchTest
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        

        public MainWindow()
        {
            InitializeComponent();



            duHastNet.UI.CustomControls.Data.Headers = new List<string> { "Name", "Age", "Salary", "IsActive" }; // Define headers at startup

            var testDataCollection = new ObservableCollection<duHastNet.UI.CustomControls.Data>
{
            new Data { Values = new Dictionary<string, object> { { "Name", "Alice" }, { "Age", 25 }, { "Salary", 50000 }, { "IsActive", true } } },
            new Data { Values = new Dictionary<string, object> { { "Name", "Bob" }, { "Age", 30 }, { "Salary", 60000 }, { "IsActive", false } } }
};

            TestDataGrid.ItemsSource= testDataCollection;


        }
    }

}
