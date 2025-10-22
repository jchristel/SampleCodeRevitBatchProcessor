using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Stores;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels;
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
        private ISettingsService? _settingsService;

        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Initialize the settings service (singleton for application lifetime)
            _settingsService = new SettingsService();

            // Initialize the API service (singleton for application lifetime)
            _docManagerApi = new DocManagerApi();

            // Initialize Manager (singleton for application lifetime)
            // Manager starts empty - will be populated after database connection
            _manager = new Manager();

            // Initialize MessageStore (singleton for application lifetime)
            _messageStore = new MessageStore();

            // Load settings from JSON files
            var (currentFolderManagerSettings, metaDataMapperAconex) = await LoadSettingsAsync();

            // Create CurrentFolderManager with loaded settings
            duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager
                = new(currentFolderManagerSettings);

            // Create the main window with ViewModel
            // Pass both API and Manager to the ViewModel
            MainWindow = new DocManagerWindow()
            {
                DataContext = new NavigationHostViewModel(
                    docManagerApi: _docManagerApi,
                    manager: _manager,
                    currentFolderManager: currentFolderManager,
                    cloudMetaData: metaDataMapperAconex,
                    messageStore: _messageStore)
            };

            MainWindow.Show();
        }

        /// <summary>
        /// Loads settings from JSON files, creating default instances if files don't exist
        /// </summary>
        /// <returns>Tuple containing CurrentFolderManagerSettings and MetaDataMapperAconex</returns>
        private async Task<(duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings, MetaDataMapperAconex)> LoadSettingsAsync()
        {
            duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings? currentFolderManagerSettings = null;
            MetaDataMapperAconex? metaDataMapperAconex = null;

            try
            {
                // Load CurrentFolderManagerSettings
                currentFolderManagerSettings = await _settingsService!.LoadAsync<duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings>(
                    "CurrentFolderManagerSettings.json");

                if (currentFolderManagerSettings == null)
                {
                    // First run - create default empty settings
                    currentFolderManagerSettings = new duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings();

                    // Log to message store that default settings were created
                    _messageStore?.SetCurrentMessage(
                        "CurrentFolderManagerSettings.json not found. Created default empty settings.",
                        MessageTypes.Information);
                }
                else
                {
                    // Settings loaded successfully
                    _messageStore?.SetCurrentMessage(
                        "CurrentFolderManagerSettings loaded successfully.",
                        MessageTypes.Information);
                }
            }
            catch (Exception ex)
            {
                // Error loading settings - create defaults and log error
                currentFolderManagerSettings = new duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings();

                _messageStore?.SetCurrentMessage(
                    $"Error loading CurrentFolderManagerSettings: {ex.Message}. Using default settings.",
                    MessageTypes.Error);
            }

            try
            {
                // Load MetaDataMapperAconex
                metaDataMapperAconex = await _settingsService!.LoadAsync<MetaDataMapperAconex>(
                    "MetaDataMapperAconex.json");

                if (metaDataMapperAconex == null)
                {
                    // First run - create default empty mapper
                    metaDataMapperAconex = new MetaDataMapperAconex();

                    // Log to message store that default mapper was created
                    _messageStore?.SetCurrentMessage(
                        "MetaDataMapperAconex.json not found. Created default empty mapper.",
                        MessageTypes.Information);
                }
                else
                {
                    // Settings loaded successfully
                    _messageStore?.SetCurrentMessage(
                        "MetaDataMapperAconex loaded successfully.",
                        MessageTypes.Information);
                }
            }
            catch (Exception ex)
            {
                // Error loading settings - create defaults and log error
                metaDataMapperAconex = new MetaDataMapperAconex();

                _messageStore?.SetCurrentMessage(
                    $"Error loading MetaDataMapperAconex: {ex.Message}. Using default mapper.",
                    MessageTypes.Error);
            }

            return (currentFolderManagerSettings, metaDataMapperAconex);
        }

        protected override void OnExit(ExitEventArgs e)
        {
            // Clean up resources
            _docManagerApi?.Dispose();

            base.OnExit(e);
        }
    }
}