using System.Windows.Controls;
using System.Windows.Input;

namespace duHastNet.DocManager.UI.Shared.Views;

public partial class GlobalMessageView : UserControl
{
    public GlobalMessageView()
    {
        InitializeComponent();
    }

    private void MessageBorder_MouseEnter(object sender, MouseEventArgs e)
    {
        // Pause timer when hovering
        if (DataContext is ViewModels.GlobalMessageViewModel vm)
        {
            vm.PauseTimerCommand.Execute(null);
        }
    }

    private void MessageBorder_MouseLeave(object sender, MouseEventArgs e)
    {
        // Resume timer when mouse leaves
        if (DataContext is ViewModels.GlobalMessageViewModel vm)
        {
            vm.ResumeTimerCommand.Execute(null);
        }
    }
}