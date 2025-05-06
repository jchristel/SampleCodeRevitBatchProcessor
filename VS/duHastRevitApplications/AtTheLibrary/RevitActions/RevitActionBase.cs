using System.Collections.Generic;
using System.Linq;

namespace duHastNet.AtTheLibrary.RevitActions
{
    public class RevitActionBase
    {
        public Models.RevitFamiliesDataModel RevitModel { get; set; }

        private List<(string, Utils.WPF.Stores.MessageTypes)> Messages { get; }

        public List<string> GetErrorMessages()
        {
            return Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Error).Select(m => m.Item1).ToList();
        }

        public List<string> GetInformationMessages()
        {
            return Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Information).Select(m => m.Item1).ToList();
        }

        public List<string> GetLogMessages()
        {
            return Messages.Where(m => m.Item2 == Utils.WPF.Stores.MessageTypes.Log).Select(m => m.Item1).ToList();
        }


        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {
            Messages.Add((message, messageType));
        }

        public void ClearMessages()
        {
            Messages.Clear();
        }

        public RevitActionBase()
        {
            Messages = new List<(string, Utils.WPF.Stores.MessageTypes)>();
        }
    }
}
