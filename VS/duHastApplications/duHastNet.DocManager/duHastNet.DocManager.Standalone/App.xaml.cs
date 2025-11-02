using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.MetaData;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Stores;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Services;
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
        private SettingsService? _settingsService;
        private NavigationStore? _navigationStore;
        private IDialogService? _dialogService;

        duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManager? _currentFolderManager;
        CloudDocumentManager _cloudDocumentManager;

        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Initialize the settings service (singleton for application lifetime)
            _settingsService = new SettingsService();

            // Initialize the API service (singleton for application lifetime)
            _docManagerApi = new DocManagerApi();

            // Initialize MessageStore (singleton for application lifetime)
            _messageStore = new MessageStore();

            // Initialize NavigationStore (singleton for application lifetime)
            _navigationStore = new NavigationStore();
            
            // Initialize DialogService (singleton for application lifetime)
            _dialogService = new DialogService();

            // Load settings from JSON files
            var (currentFolderManagerSettings, cloudDocumentManager) = await LoadSettingsAsync();

            _cloudDocumentManager = cloudDocumentManager;

            // Initialize Manager(singleton for application lifetime)
            // Manager starts empty - will be populated after database connection
            // Pass loaded CloudDocumentManager
            _manager = new Manager(_cloudDocumentManager);

            // Create CurrentFolderManager with loaded settings
            _currentFolderManager
                = new(currentFolderManagerSettings);

            // Create the main window with ViewModel
            // Pass both API and Manager to the ViewModel
            MainWindow = new DocManagerWindow()
            {
                DataContext = new NavigationHostViewModel(
                    docManagerApi: _docManagerApi,
                    manager: _manager,
                    currentFolderManager: _currentFolderManager,
                    messageStore: _messageStore,
                    navigationStore: _navigationStore,
                    dialogService: _dialogService)
            };

            MainWindow.Show();
        }

        /// <summary>
        /// Loads settings from JSON files, creating default instances if files don't exist
        /// </summary>
        /// <returns>Tuple containing CurrentFolderManagerSettings and MetaDataMapperAconex</returns>
        private async Task<(duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings, CloudDocumentManager)> LoadSettingsAsync()
        {
            duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings? currentFolderManagerSettings = null;
            CloudDocumentManager? cloudDocumentManager = null;

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
                // Load CloudDocumentManager
                cloudDocumentManager = await _settingsService!.LoadAsync<CloudDocumentManager>(
                    "CloudDocumentManager.json");

                if (cloudDocumentManager == null)
                {
                    // First run - create default empty mapper
                    cloudDocumentManager = new CloudDocumentManager();

                    // Log to message store that default mapper was created
                    _messageStore?.SetCurrentMessage(
                        "CloudDocumentManager.json not found. Created default empty mapper.",
                        MessageTypes.Information);
                }
                else
                {
                    // Settings loaded successfully
                    _messageStore?.SetCurrentMessage(
                        "CloudDocumentManager loaded successfully.",
                        MessageTypes.Information);
                }
            }
            catch (Exception ex)
            {
                // Error loading settings - create defaults and log error
                cloudDocumentManager = new CloudDocumentManager();

                _messageStore?.SetCurrentMessage(
                    $"Error loading CloudDocumentManager: {ex.Message}. Using default mapper.",
                    MessageTypes.Error);
            }

            return (currentFolderManagerSettings, cloudDocumentManager);
        }

        protected override void OnExit(ExitEventArgs e)
        {
            // Clean up resources
            _docManagerApi?.Dispose();

            base.OnExit(e);
        }
    }
}