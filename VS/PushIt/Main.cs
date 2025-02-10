using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.DB.Architecture;
using PushIt.Views;
using PushIt.Utilities;
using Serilog;
using System.IO;


namespace PushIt
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class Main : IExternalCommand
    {
        Models.RevitDataModel _revitDataModel = new Models.RevitDataModel();
        Stores.NavigationStore _navigationStore = new Stores.NavigationStore();
        Stores.MessageStore _messageStore = new Stores.MessageStore();
        RevitExternalEventHandlerManager _eventManager = new RevitExternalEventHandlerManager();

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //set up the logger
            setupLogger();

            // Example log entry
            Log.Information("Starting PushIt.");

            //Get application and document objects
            UIApplication uiapp = commandData.Application;
            Document doc = uiapp.ActiveUIDocument.Document;

            // get room data from file
            string dataPath = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\PushIt\Testdata\20250205_CSB.csv";

            // add rooms to RevitDataModel
            List<Models.RoomsDataModel> rooms = GetRooms(dataPath);
            foreach (Models.RoomsDataModel room in rooms)
            {
                _revitDataModel.AddRoom(room);
            }

            Log.Information("Found rooms: {0}", rooms.Count);

            //RoomsSelection roomsSelection = new RoomsSelection();
            //roomsSelection.Show();

            //set up the navigation store
            _navigationStore.CurrentViewModel = CreateRoomsSelectionViewModel();

            //set up the external event manager
            _eventManager.RevitDataModel = _revitDataModel;


            //show the main window
            MainWindow mainWindow = new MainWindow()
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore, _eventManager)
            };

            mainWindow.Show();

            return Result.Succeeded;

        }

        private ViewModels.RoomsSelectionViewModel CreateRoomsSelectionViewModel()
        {
            return new ViewModels.RoomsSelectionViewModel(
                _revitDataModel, _navigationStore, _messageStore, _eventManager);
        }

        public List<Models.RoomsDataModel> GetRooms(string dataPath)
        {
            List<Models.RoomsDataModel> rooms = Utilities.ReadRoomsData.GetRoomsData(dataPath);
            return rooms;
        }

        private void setupLogger()
        {
            // Configure Serilog
            string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string logDirectory = Path.Combine(localAppDataPath, "duHast");
            Directory.CreateDirectory(logDirectory);
            Log.Logger = new LoggerConfiguration()
                .WriteTo.File(
                    path: Path.Combine(logDirectory, "log-pushit.txt"),
                    rollingInterval: RollingInterval.Day,
                    retainedFileCountLimit: 4) // Keep the last 4 weeks of logs
                .CreateLogger();
            {
    }
}
