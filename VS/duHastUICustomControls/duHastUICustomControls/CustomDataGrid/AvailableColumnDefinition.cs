using System;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public class AvailableColumnDefinition
    {
        public string PropertyName { get; set; }
        public string DisplayName { get; set; }
        public Type DataType { get; set; }
        public string Category { get; set; }
        public string Description { get; set; }

        public AvailableColumnDefinition(string propertyName, string displayName, Type dataType, string category = "General", string description = "")
        {
            PropertyName = propertyName;
            DisplayName = displayName;
            DataType = dataType;
            Category = category;
            Description = description;
        }

        public string TypeDisplayName
        {
            get
            {
                switch (DataType.Name)
                {
                    case "String":
                        return "Text";
                    case "Int32":
                        return "Number";
                    case "Double":
                        return "Decimal";
                    case "Boolean":
                        return "Yes/No";
                    case "DateTime":
                        return "Date";
                    default:
                        return DataType.Name;
                }
            }
        }
    }
}
