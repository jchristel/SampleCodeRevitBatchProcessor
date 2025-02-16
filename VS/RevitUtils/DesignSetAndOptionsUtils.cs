using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace RevitUtils
{
    public static class DesignSetAndOptionsUtils
    {
       
        public static FilteredElementCollector GetDesginOptions(Document doc)
        {
            return new FilteredElementCollector(doc).OfClass(typeof(DesignOption));
        }

        public static DesignOption GetActiveDesignOption(Document doc)
        {
            ElementId elementId = DesignOption.GetActiveDesignOptionId(doc);
            if (elementId == ElementId.InvalidElementId)
            {
                return null;
            }
            return doc.GetElement(elementId) as DesignOption;
        }

        public static Element GetDesignSetFromDesignOption(Document doc, DesignOption designOption)
        {
            Element designSet = doc.GetElement(designOption.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId());
            return designSet;
        }

        public static Element GetDesignSetOfActiveDesignOption(Document doc)
        {
            DesignOption activeDesignOption = GetActiveDesignOption(doc);
            if (activeDesignOption == null)
            {
                return null;
            }
            return GetDesignSetFromDesignOption(doc, activeDesignOption);
        }

        public static List<Element> GetDesignSets(Document doc)
        {
            List<Element> designSets = new List<Element>();
            FilteredElementCollector designOptions = GetDesginOptions(doc);
            foreach (DesignOption designOption in designOptions)
            {
                Element designSet = GetDesignSetFromDesignOption(doc, designOption);
                if (designSet != null)
                {
                    if (!designSets.Contains(designSet))
                    {
                        designSets.Add(designSet);
                    }
                }
            }
            return designSets;
        }

        public static Dictionary<string,List<DesignOption>> GetDesignOptionsByDesignSetName(Document doc)
        {
            Dictionary<string, List<DesignOption>> designOptionsByDesignSetName = new Dictionary<string, List<DesignOption>>();

            FilteredElementCollector designOptions = GetDesginOptions(doc);
            foreach (DesignOption designOption in designOptions)
            {
                Element designSet = GetDesignSetFromDesignOption(doc, designOption);
                if (designSet != null)
                {
                    string designSetName = designSet.Name;
                    if (!designOptionsByDesignSetName.ContainsKey(designSetName))
                    {
                        designOptionsByDesignSetName.Add(designSetName, new List<DesignOption>());
                    }
                    designOptionsByDesignSetName[designSetName].Add(designOption);
                }
            }
            return designOptionsByDesignSetName;
        }

        public static bool IsDesignOptionPrimary(Document doc, string designSetName, string designOptionName)
        {
            bool isPrimary = false;

            FilteredElementCollector designOptions = GetDesginOptions(doc);

            foreach (DesignOption designOption in designOptions)
            {
                Element designSet = GetDesignSetFromDesignOption(doc, designOption);
                if (designSet != null)
                {
                    // add chevrons to the name supplied by the user (not sure that is required, since it may already have chevrons)
                    if (designSet.Name == "<"+designSetName+">" && designOption.Name == designOptionName)
                    {
                        isPrimary = designOption.IsPrimary;
                        break;
                    }
                }
            }

            return isPrimary;
        }
        public static Dictionary<string, object> GetDesignSetOptionInfo(Document doc, Element element)
        {
            // keys match properties in DataDesignSetOption class!!
            var dic = new Dictionary<string, object>
            {
                { DesignSetAndOptionDefaultNames.DESIGN_SET_NAME, DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME },
                { DesignSetAndOptionDefaultNames.DESIGN_OPTION_NAME, DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME },
                { DesignSetAndOptionDefaultNames.DESIGN_OPTION_IS_PRIMARY, true }
            };

            try
            {
                // this only works for objects inheriting from Autodesk.Revit.DB.Element
                DesignOption designOption = element.DesignOption;
                if (designOption != null)
                {
                    dic[DesignSetAndOptionDefaultNames.DESIGN_OPTION_NAME] = designOption.Name;
                    dic[DesignSetAndOptionDefaultNames.DESIGN_OPTION_IS_PRIMARY] = designOption.IsPrimary;

                    Element designSet = doc.GetElement(designOption.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId());
                    if (designSet != null)
                    {
                        dic[DesignSetAndOptionDefaultNames.DESIGN_SET_NAME] = designSet.Name;
                    }
                }
            }
            catch (Exception)
            {
                // Ignore exceptions and return the default dictionary
            }

            return dic;
        }

        public static List<ElementId> GetDesignOptionIdsOfAllPrimaryOptions(Document doc)
        {
            List<ElementId> designOptionIds = new List<ElementId>();
            FilteredElementCollector designOptions = GetDesginOptions(doc);
            foreach (DesignOption designOption in designOptions)
            {
                if (designOption.IsPrimary)
                {
                    designOptionIds.Add(designOption.Id);
                }
            }
            return designOptionIds;
        }

        public static List<ElementId> GetDesignOptionIdsOfAllPrimaryOptionsButTheOneContainingFilterId(Document doc, ElementId filterId)
        {
            // setup return value
            List<ElementId> primaryOptionsIds = new List<ElementId>();

            // get a dictionary with design sets as key and design options as values
            Dictionary<string, List<DesignOption>> designOptionsByDesignSet = GetDesignOptionsByDesignSetName(doc);

            // loop over all design sets and check if the filter id is in the design options
            foreach (var kvp in designOptionsByDesignSet)
            {
                string designSet = kvp.Key;
                List<DesignOption> designOptions = kvp.Value;

                // set filter match flag
                bool match = false;
                // set default value for primary design option id
                ElementId primaryDesignOptionId = null;

                // loop over all design options in the design set
                foreach (DesignOption designOption in designOptions)
                {
                    // check if design option is primary
                    if (designOption.IsPrimary)
                    {
                        primaryDesignOptionId = designOption.Id;
                    }
                    // check if design option id is the filter id
                    if (designOption.Id == filterId)
                    {
                        match = true;
                        break;
                    }
                }

                // if no match was found, add the primary design option id to the list
                if (!match && primaryDesignOptionId != null)
                {
                    primaryOptionsIds.Add(primaryDesignOptionId);
                }
            }

            return primaryOptionsIds;
        }
    }
}
