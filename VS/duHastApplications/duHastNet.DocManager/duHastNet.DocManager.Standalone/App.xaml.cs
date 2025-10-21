using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.UI.Shared.ViewModels;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Stores;
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

        // Singleton instances for application lifetime
        private DocManagerApi? _docManagerApi;
        private Manager? _manager;
        private MessageStore? _messageStore;

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Initialize the API service (singleton for application lifetime)
            _docManagerApi = new DocManagerApi();

            // Initialize Manager (singleton for application lifetime)
            // Manager starts empty - will be populated after database connection
            _manager = new Manager();

            // Initialize MessageStore (singleton for application lifetime)
            _messageStore = new MessageStore();

            //initalize cloud metadata mapper (need to be checking settings later)
            MetaDataMapperAconex cloudMetaData = new MetaDataMapperAconex();

            // Create CurrentFolderManager
            duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager = new();

            // Create the main window with ViewModel
            // Pass both API and Manager to the ViewModel
            MainWindow = new DocManagerWindow()
            {
                DataContext = new NavigationHostViewModel(
                    docManagerApi: _docManagerApi,
                    manager: _manager,
                    currentFolderManager: currentFolderManager,
                    cloudMetaData: cloudMetaData,
                    messageStore: _messageStore)
            };

            MainWindow.Show();
        }

        protected override void OnExit(ExitEventArgs e)
        {
            // Clean up resources
            _docManagerApi?.Dispose();

            base.OnExit(e);
        }
    }
}