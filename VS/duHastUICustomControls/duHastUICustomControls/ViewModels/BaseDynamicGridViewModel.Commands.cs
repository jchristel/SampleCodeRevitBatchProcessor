using System.Windows.Input;
using duHastNet.UI.CustomControls.CustomDataGrid;


namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract partial class BaseDynamicGridViewModel<TData>
    where TData : DynamicRowData, new()
    {
        #region Commands

        public ICommand AddRowCommand { get; }
        public ICommand RemoveRowCommand { get; }
        public ICommand AddSelectedColumnCommand { get; }
        public ICommand RemoveColumnCommand { get; }
        public ICommand ToggleColumnLockCommand { get; }
        public ICommand ClearDataCommand { get; }

        #endregion
    }
}