using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities.Output
{
    public class WpfFormOutputObserver : RBP_Launcher.Interfaces.IOutputObserver
    { 
        // private readonly  form; // Replace Form1 with your actual WPF form class

        //public WpfFormOutputObserver(Form1 form)
        //{
        //    this.form = form;
        //}

        public void Update(string message)
        {
            // Update WPF form with the message
            // Example:
            // form.UpdateOutput(message);
        }
    }
}
