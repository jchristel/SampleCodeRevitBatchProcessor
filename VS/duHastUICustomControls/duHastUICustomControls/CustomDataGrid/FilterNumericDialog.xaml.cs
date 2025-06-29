using System;
using System.Globalization;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public enum NumericFilterOperation
    {
        Equal,
        GreaterThan,
        GreaterThanOrEqual,
        LessThan,
        LessThanOrEqual,
        Range
    }

    public partial class FilterNumericDialog : Window
    {
        public NumericFilterOperation Operation { get; private set; }
        public double? Value { get; private set; }
        public double? FromValue { get; private set; }
        public double? ToValue { get; private set; }
        public bool FilterCleared { get; private set; }

        public FilterNumericDialog(string propertyName,
            NumericFilterOperation? currentOperation = null,
            double? currentValue = null,
            double? currentFromValue = null,
            double? currentToValue = null)
        {
            InitializeComponent();

            Title = $"Filter {propertyName}";

            // Set current filter state
            if (currentOperation.HasValue)
            {
                foreach (ComboBoxItem item in OperationComboBox.Items)
                {
                    if (item.Tag.ToString() == currentOperation.Value.ToString())
                    {
                        OperationComboBox.SelectedItem = item;
                        break;
                    }
                }

                if (currentOperation.Value == NumericFilterOperation.Range)
                {
                    if (currentFromValue.HasValue)
                        FromValueTextBox.Text = currentFromValue.Value.ToString(CultureInfo.CurrentCulture);
                    if (currentToValue.HasValue)
                        ToValueTextBox.Text = currentToValue.Value.ToString(CultureInfo.CurrentCulture);
                }
                else if (currentValue.HasValue)
                {
                    ValueTextBox.Text = currentValue.Value.ToString(CultureInfo.CurrentCulture);
                }
            }
            else
            {
                // Default to "Is equal to"
                OperationComboBox.SelectedIndex = 0;
            }

            UpdateCurrentFilterDisplay();
        }

        private void OperationComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (OperationComboBox.SelectedItem is ComboBoxItem selectedItem)
            {
                bool isRange = selectedItem.Tag.ToString() == "Range";

                SingleValuePanel.Visibility = isRange ? Visibility.Collapsed : Visibility.Visible;
                RangePanel.Visibility = isRange ? Visibility.Visible : Visibility.Collapsed;

                // Update value label based on operation
                switch (selectedItem.Tag.ToString())
                {
                    case "Equal":
                        ValueLabel.Text = "Value:";
                        break;
                    case "GreaterThan":
                    case "GreaterThanOrEqual":
                        ValueLabel.Text = "Minimum:";
                        break;
                    case "LessThan":
                    case "LessThanOrEqual":
                        ValueLabel.Text = "Maximum:";
                        break;
                }

                UpdateCurrentFilterDisplay();
            }
        }

        private void ValueTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateCurrentFilterDisplay();
        }

        private void RangeTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateCurrentFilterDisplay();
        }

        private void ApplyButton_Click(object sender, RoutedEventArgs e)
        {
            if (ValidateAndSetValues())
            {
                FilterCleared = false;
                DialogResult = true;
            }
        }

        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            Value = null;
            FromValue = null;
            ToValue = null;
            FilterCleared = true;
            DialogResult = true;
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
        }

        private bool ValidateAndSetValues()
        {
            if (!(OperationComboBox.SelectedItem is ComboBoxItem selectedItem))
                return false;

            if (!Enum.TryParse<NumericFilterOperation>(selectedItem.Tag.ToString(), out NumericFilterOperation operation))
                return false;

            Operation = operation;
            Value = null;
            FromValue = null;
            ToValue = null;

            if (operation == NumericFilterOperation.Range)
            {
                // Validate range values
                if (!double.TryParse(FromValueTextBox.Text, out double fromVal))
                {
                    MessageBox.Show("Please enter a valid 'From' value.", "Invalid Input",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    FromValueTextBox.Focus();
                    return false;
                }

                if (!double.TryParse(ToValueTextBox.Text, out double toVal))
                {
                    MessageBox.Show("Please enter a valid 'To' value.", "Invalid Input",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    ToValueTextBox.Focus();
                    return false;
                }

                if (fromVal > toVal)
                {
                    MessageBox.Show("'From' value cannot be greater than 'To' value.", "Invalid Range",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return false;
                }

                FromValue = fromVal;
                ToValue = toVal;
            }
            else
            {
                // Validate single value
                if (!double.TryParse(ValueTextBox.Text, out double val))
                {
                    MessageBox.Show("Please enter a valid value.", "Invalid Input",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    ValueTextBox.Focus();
                    return false;
                }

                Value = val;
            }

            return true;
        }

        private void UpdateCurrentFilterDisplay()
        {
            if (!(OperationComboBox.SelectedItem is ComboBoxItem selectedItem))
            {
                CurrentFilterText.Text = "";
                return;
            }

            var operation = selectedItem.Tag.ToString();

            if (operation == "Range")
            {
                var hasFrom = !string.IsNullOrWhiteSpace(FromValueTextBox.Text);
                var hasTo = !string.IsNullOrWhiteSpace(ToValueTextBox.Text);

                if (hasFrom && hasTo)
                {
                    CurrentFilterText.Text = $"Show values: {FromValueTextBox.Text} ≤ value ≤ {ToValueTextBox.Text}";
                }
                else if (hasFrom)
                {
                    CurrentFilterText.Text = $"Show values: ≥ {FromValueTextBox.Text}";
                }
                else if (hasTo)
                {
                    CurrentFilterText.Text = $"Show values: ≤ {ToValueTextBox.Text}";
                }
                else
                {
                    CurrentFilterText.Text = "Enter range values";
                }
            }
            else
            {
                var hasValue = !string.IsNullOrWhiteSpace(ValueTextBox.Text);
                if (hasValue)
                {
                    string symbol;
                    switch (operation)
                    {
                        case "Equal":
                            symbol = "=";
                            break;
                        case "GreaterThan":
                            symbol = ">";
                            break;
                        case "GreaterThanOrEqual":
                            symbol = "≥";
                            break;
                        case "LessThan":
                            symbol = "<";
                            break;
                        case "LessThanOrEqual":
                            symbol = "≤";
                            break;
                        default:
                            symbol = "";
                            break;
                    }
                    CurrentFilterText.Text = $"Show values: value {symbol} {ValueTextBox.Text}";
                }
                else
                {
                    CurrentFilterText.Text = "Enter a value";
                }
            }
        }
    }
}