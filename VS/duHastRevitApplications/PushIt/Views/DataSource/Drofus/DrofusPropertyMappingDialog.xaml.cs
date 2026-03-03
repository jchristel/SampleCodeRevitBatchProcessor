// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.ViewModels.DataSource.Drofus;
using System.Windows;

namespace duHastNet.PushIt.Views.DataSource.Drofus
{
    /// <summary>
    /// Code-behind for the Add / Edit drofus property mapping dialog.
    /// <para>
    /// The only responsibility of this file is to subscribe to the ViewModel's
    /// <see cref="DrofusPropertyMappingDialogViewModel.RequestClose"/> event and
    /// call <see cref="Window.Close"/> in the handler.  All logic lives in
    /// <see cref="DrofusPropertyMappingDialogViewModel"/>.
    /// </para>
    /// </summary>
    public partial class DrofusPropertyMappingDialog : Window
    {
        public DrofusPropertyMappingDialog()
        {
            InitializeComponent();

            // Subscribe once the DataContext is set.  DataContext is assigned by
            // ShowMappingDialog in DrofusDataSourceControlViewModel before
            // ShowDialog() is called, so it is already present when the
            // constructor runs via that path.  We use DataContextChanged as a
            // safety net in case the window is ever constructed differently.
            DataContextChanged += OnDataContextChanged;
        }

        private void OnDataContextChanged(
            object sender,
            DependencyPropertyChangedEventArgs e)
        {
            // Unsubscribe from the old ViewModel to prevent memory leaks if the
            // DataContext is ever replaced (uncommon for a dialog, but defensive).
            if (e.OldValue is DrofusPropertyMappingDialogViewModel oldVm)
                oldVm.RequestClose -= OnRequestClose;

            if (e.NewValue is DrofusPropertyMappingDialogViewModel newVm)
                newVm.RequestClose += OnRequestClose;
        }

        private void OnRequestClose(object? sender, System.EventArgs e)
        {
            Close();
        }
    }
}
