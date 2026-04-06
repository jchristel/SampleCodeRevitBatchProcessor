//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//


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

namespace duHastNet.UI.DocManagerSettingsUI.Views
{
    /// <summary>
    /// Interaction logic for SettingsView.xaml
    /// </summary>
    public partial class SettingsView : UserControl
    {
        public SettingsView()
        {
            InitializeComponent();
        }

        /// <summary>
        /// used when browsing database file.
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void PickFile_OnClick(object sender, EventArgs e)
        {
            var dialog = new Microsoft.Win32.OpenFileDialog();
            dialog.Filter = "db Files (*.db)|*.db|All Files (*.*)|*.*";
            var dialogResult = dialog.ShowDialog();
            if (dialogResult == true)
            {
                DatabaseFilePathTextBox.Text = dialog.FileName;

                // Since setting the property explicitly bypasses the data binding, 
                // we must explicitly update it by calling BindingExpression.UpdateSource()
                this.DatabaseFilePathTextBox
                  .GetBindingExpression(TextBox.TextProperty)
                  .UpdateSource();
            }
        }
        private void Export_OnClick(object sender, EventArgs e)
        {
            var dialog = new Microsoft.Win32.SaveFileDialog();
            dialog.Filter = "json Files (*.json)|*.json";
            if (dialog.ShowDialog() == true)
            {
                ExportFilePathTextBox.Text = dialog.FileName;

                // Since setting the property explicitly bypasses the data binding, 
                // we must explicitly update it by calling BindingExpression.UpdateSource()
                this.ExportFilePathTextBox
                  .GetBindingExpression(TextBox.TextProperty)
                  .UpdateSource();
            }
        }

        private void Import_OnClick(object sender, EventArgs e)
        {
            var dialog = new Microsoft.Win32.OpenFileDialog();
            dialog.Filter = "json Files (*.json)|*.json|All Files (*.*)|*.*";
            if (dialog.ShowDialog() == true)
            {
                ImportFilePathTextBox.Text = dialog.FileName;

                // Since setting the property explicitly bypasses the data binding, 
                // we must explicitly update it by calling BindingExpression.UpdateSource()
                this.ImportFilePathTextBox
                  .GetBindingExpression(TextBox.TextProperty)
                  .UpdateSource();
            }
        }
    }
}
