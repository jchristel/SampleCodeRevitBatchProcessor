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
        duHast.Utils.WPF.Stores.NavigationStore _navigationStore;
        

        public App()
        {
            _navigationStore = new duHast.Utils.WPF.Stores.NavigationStore();
            

            //set up the navigation store
            _navigationStore.CurrentViewModel = CreateTestViewModel();

            MainWindow = new MainWindow()
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

        }

        private ViewModels.testViewModel CreateTestViewModel()
        {
            return new ViewModels.testViewModel();
        }

    }
}
