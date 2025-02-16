using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace PushIt.Views
{
    /// <summary>
    /// Interaction logic for UserControl1.xaml
    /// </summary>
    public partial class RoomsSelection : UserControl
    {
        public RoomsSelection()
        {
            InitializeComponent();
        }

        private void PickFile_OnClick(object sender, EventArgs e)
        {
            var dialog = new System.Windows.Forms.OpenFileDialog();
            dialog.Filter = "csv Files (*.csv)|*.csv|All Files (*.*)|*.*";
            var dialogResult = dialog.ShowDialog();
            if (dialogResult == System.Windows.Forms.DialogResult.OK)
            {
                FilePathTextBox.Text = dialog.FileName;

                // Since setting the property explicitly bypasses the data binding, 
                // we must explicitly update it by calling BindingExpression.UpdateSource()
                this.FilePathTextBox
                  .GetBindingExpression(TextBox.TextProperty)
                  .UpdateSource();
            }
        }
    }
}
