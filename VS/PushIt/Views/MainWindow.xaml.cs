using PushIt.Utilities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace PushIt.Views
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        Models.Settings _settings;
        public MainWindow(Models.Settings settings)
        {
            InitializeComponent();
            this.Closing += MainWindow_Closing;

            _settings = settings;

        }

        private void MainWindow_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            if (DataContext is ICloseable closeable)
            {
                closeable.OnClosing();
            }

            // store settings
            Utilities.SettingsUtils.SaveSettings(_settings);
        }
    }
}
