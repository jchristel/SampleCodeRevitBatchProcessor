using Autodesk.Revit.DB;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RevitUtils
{
    public static class ParaUtils
    {
        public static bool SetParameterValueByName(Element el, string parameterName, string value)
        {
            // set the value
            IList<Parameter> parameters = el.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                if (parameter.Definition.Name == parameterName)
                {
                    bool setResult = RevitUtils.SharedParaUtils.SetParameterValue(parameter, value);
                    return setResult;
                }
            }

            return false;
        }

        public static string GetParameterValueByName(Element el, string parameterName)
        {
            // get the value
            IList<Parameter> parameters = el.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                if (parameter.Definition.Name == parameterName)
                {
                    string value = RevitUtils.SharedParaUtils.GetSharedParameterValueFromElementByElementId(el,parameter.Id);
                    return value;
                }
            }
            return null;
        }
    }
}
