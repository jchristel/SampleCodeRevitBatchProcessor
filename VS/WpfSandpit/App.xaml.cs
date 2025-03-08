using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace WpfSandpit
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        private readonly duHast.Utils.WPF.Stores.NavigationStore _navigationStore;

        public App()
        {
            //set up the navigation store
            _navigationStore = new duHast.Utils.WPF.Stores.NavigationStore();
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            //set up the navigation store
            _navigationStore.CurrentViewModel = new ViewModels.testViewModel();

            //set up the main window and data context
            MainWindow = new MainWindow()
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

            //show the main window
            MainWindow.Show();
            //base.OnStartup(e);
           
        }

        private ViewModels.testViewModel CreateTestViewModel()
        {
            return new ViewModels.testViewModel();
        }

    }
}
