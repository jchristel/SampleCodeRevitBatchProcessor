using System.Linq;
using duHastNet.UI.CustomControls.CustomDataGrid;

namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract partial class BaseDynamicGridViewModel<TData>
    where TData : DynamicRowData, new()
    {
        #region Row Management

        public virtual void AddRow()
        {
            var newRow = CreateNewRow();

            // Set default values for all existing columns
            foreach (var columnDef in ColumnDefinitions)
            {
                if (!newRow.Values.ContainsKey(columnDef.PropertyName))
                {
                    var availableColumn = AvailableColumns.FirstOrDefault(ac => ac.PropertyName == columnDef.PropertyName);
                    newRow[columnDef.PropertyName] = availableColumn != null
                        ? GetDefaultValueForColumn(availableColumn)
                        : GetDefaultValue(columnDef.DataType);
                }
            }

            Data.Add(newRow);
        }

        public virtual void RemoveRow(object parameter)
        {
            if (parameter is TData row && Data.Contains(row))
            {
                Data.Remove(row);
            }
            else if (parameter is int index && index >= 0 && index < Data.Count)
            {
                Data.RemoveAt(index);
            }
            else if (Data.Count > 0)
            {
                Data.RemoveAt(Data.Count - 1); // Remove last row
            }
        }

        #endregion
    }
}