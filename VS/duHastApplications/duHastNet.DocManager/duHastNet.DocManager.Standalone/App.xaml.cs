using System.Configuration;
using System.Data;
using System.Windows;

namespace DocManager.Standalone
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            // Initialize the API service
            duHastNet.DocManager.Core.Services.Api.DocManagerApi docManagerApi = new duHastNet.DocManager.Core.Services.Api.DocManagerApi();

            MainWindow = new MainWindow()
            {
                DataContext = new duHastNet.DocManager.UI.Shared.ViewModels.SettingsViewModel(docManagerApi)
            };

            MainWindow.Show();

            base.OnStartup(e);
            // TODO: Set up dependency injection here later
            // For now, just let the MainWindow start normally
        }
    }
}