using System;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public enum DateTimeFilterOperation
    {
        On,
        Before,
        After,
        Between
    }

    public partial class FilterDateTimeDialog : Window
    {
        public DateTimeFilterOperation Operation { get; private set; }
        public DateTime? Date { get; private set; }
        public DateTime? FromDate { get; private set; }
        public DateTime? ToDate { get; private set; }
        public bool FilterCleared { get; private set; }

        public FilterDateTimeDialog(string propertyName,
            DateTimeFilterOperation? currentOperation = null,
            DateTime? currentDate = null,
            DateTime? currentFromDate = null,
            DateTime? currentToDate = null)
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

                if (currentOperation.Value == DateTimeFilterOperation.Between)
                {
                    if (currentFromDate.HasValue)
                        FromDatePicker.SelectedDate = currentFromDate.Value;
                    if (currentToDate.HasValue)
                        ToDatePicker.SelectedDate = currentToDate.Value;
                }
                else if (currentDate.HasValue)
                {
                    DatePicker.SelectedDate = currentDate.Value;
                }
            }
            else
            {
                // Default to "On"
                OperationComboBox.SelectedIndex = 0;
            }

            UpdateCurrentFilterDisplay();
        }

        private void OperationComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (OperationComboBox.SelectedItem is ComboBoxItem selectedItem)
            {
                bool isBetween = selectedItem.Tag.ToString() == "Between";

                SingleDatePanel.Visibility = isBetween ? Visibility.Collapsed : Visibility.Visible;
                DateRangePanel.Visibility = isBetween ? Visibility.Visible : Visibility.Collapsed;

                // Update date label based on operation
                switch (selectedItem.Tag.ToString())
                {
                    case "On":
                        DateLabel.Content = "Date:";
                        break;
                    case "Before":
                        DateLabel.Content = "Before:";
                        break;
                    case "After":
                        DateLabel.Content = "After:";
                        break;
                }

                UpdateCurrentFilterDisplay();
            }
        }

        private void DatePicker_SelectedDateChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateCurrentFilterDisplay();
        }

        private void DateRangePicker_SelectedDateChanged(object sender, SelectionChangedEventArgs e)
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
            Date = null;
            FromDate = null;
            ToDate = null;
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

            if (!Enum.TryParse<DateTimeFilterOperation>(selectedItem.Tag.ToString(), out DateTimeFilterOperation operation))
                return false;

            Operation = operation;
            Date = null;
            FromDate = null;
            ToDate = null;

            if (operation == DateTimeFilterOperation.Between)
            {
                // Validate range dates
                if (!FromDatePicker.SelectedDate.HasValue)
                {
                    MessageBox.Show("Please select a 'From' date.", "Invalid Input",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    FromDatePicker.Focus();
                    return false;
                }

                if (!ToDatePicker.SelectedDate.HasValue)
                {
                    MessageBox.Show("Please select a 'To' date.", "Invalid Input",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    ToDatePicker.Focus();
                    return false;
                }

                if (FromDatePicker.SelectedDate.Value > ToDatePicker.SelectedDate.Value)
                {
                    MessageBox.Show("'From' date cannot be later than 'To' date.", "Invalid Range",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return false;
                }

                FromDate = FromDatePicker.SelectedDate.Value;
                ToDate = ToDatePicker.SelectedDate.Value;
            }
            else
            {
                // Validate single date
                if (!DatePicker.SelectedDate.HasValue)
                {
                    MessageBox.Show("Please select a date.", "Invalid Input",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    DatePicker.Focus();
                    return false;
                }

                Date = DatePicker.SelectedDate.Value;
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

            if (operation == "Between")
            {
                var hasFrom = FromDatePicker.SelectedDate.HasValue;
                var hasTo = ToDatePicker.SelectedDate.HasValue;

                if (hasFrom && hasTo)
                {
                    CurrentFilterText.Text = $"Show dates: {FromDatePicker.SelectedDate.Value:yyyy-MM-dd} to {ToDatePicker.SelectedDate.Value:yyyy-MM-dd}";
                }
                else if (hasFrom)
                {
                    CurrentFilterText.Text = $"Show dates: from {FromDatePicker.SelectedDate.Value:yyyy-MM-dd}";
                }
                else if (hasTo)
                {
                    CurrentFilterText.Text = $"Show dates: to {ToDatePicker.SelectedDate.Value:yyyy-MM-dd}";
                }
                else
                {
                    CurrentFilterText.Text = "Select date range";
                }
            }
            else
            {
                var hasDate = DatePicker.SelectedDate.HasValue;
                if (hasDate)
                {
                    string operationText;
                    switch (operation)
                    {
                        case "On":
                            operationText = "on";
                            break;
                        case "Before":
                            operationText = "before";
                            break;
                        case "After":
                            operationText = "after";
                            break;
                        default:
                            operationText = "";
                            break;
                    }
                    CurrentFilterText.Text = $"Show dates: {operationText} {DatePicker.SelectedDate.Value:yyyy-MM-dd}";
                }
                else
                {
                    CurrentFilterText.Text = "Select a date";
                }
            }
        }
    }
}