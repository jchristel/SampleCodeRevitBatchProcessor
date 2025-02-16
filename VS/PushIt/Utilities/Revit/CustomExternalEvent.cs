using Autodesk.Revit.UI;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Utilities.Revit
{
    public class CustomExternalEvent : IExternalEventHandler
    {
        private readonly Action<UIApplication> _executeAtEventRaised;

        public void Execute(UIApplication uiapp)
        {
            try
            {
                _executeAtEventRaised(uiapp);
            }
            catch (InvalidOperationException e)
            {
                TaskDialog.Show("External Event Handler", $"An exception occurred within the external event handler: {e.Message}");
            }
        }

        public string GetName()
        {
            return $"Function executed {_executeAtEventRaised.Method.Name}";
        }

        public CustomExternalEvent(Action<UIApplication> executeAtEventRaised)
        {
            _executeAtEventRaised = executeAtEventRaised;
        }
    }
}
