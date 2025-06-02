using duHastNet.UI.CustomControls;
using System.Collections.ObjectModel;
using System.Windows;


namespace ThreeWaySwitchTest
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public ObservableCollection<TestData> SampleItems { get; set; } = new ObservableCollection<TestData>
        {
            new TestData { Name = "Alice", Age = 25, IsActive = true },
            new TestData { Name = "Bob", Age = 30, IsActive = false },
            new TestData { Name = "Charlie", Age = 22, IsActive = true }
        };

        public MainWindow()
        {
            InitializeComponent();

           

            // Replace the existing XAML grid with this instance
            //Content = testGrid;

            TestDataGrid.ItemsSource = new ObservableCollection<TestData>
            {
                new TestData { Name = "Alice", Age = 25, IsActive = true },
                new TestData { Name = "Bob", Age = 30, IsActive = false },
                new TestData { Name = "Charlie", Age = 22, IsActive = true }
            };
        }
    }

    public class TestData
    {
        public string Name { get; set; }
        public int Age { get; set; }
        public bool IsActive { get; set; }
    }


}
