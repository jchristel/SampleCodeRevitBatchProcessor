using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities
{
    // Custom TextWriter to capture redirected output
    class RedirectedOutput : Stream
    {
        private readonly System.Text.StringBuilder outputBuffer = new();

        // Define an event to notify subscribers when output is received
        public event EventHandler<OutputReceivedEventArgs>? OutputReceived;

        public override bool CanRead => true;
        public override bool CanSeek => false;
        public override bool CanWrite => true;
        public override long Length => 0;

        public override long Position
        {
            get => 0;
            set { }
        }

        public RedirectedOutput()
        {
            OutputReceived = null; // Initialize the event
        }
        public override void Flush() { }

        public override int Read(byte[] buffer, int offset, int count)
        {
            throw new NotSupportedException();
        }

        public override long Seek(long offset, SeekOrigin origin)
        {
            throw new NotSupportedException();
        }

        public override void SetLength(long value) { }

        public override void Write(byte[] buffer, int offset, int count)
        {
            string text = System.Text.Encoding.UTF8.GetString(buffer, offset, count);
            outputBuffer.Append(text);

            // Notify subscribers of the new output
            OnOutputReceived(new OutputReceivedEventArgs(text));
        }

        public string GetOutput()
        {
            return outputBuffer.ToString();
        }

        // Helper method to raise the OutputReceived event
        protected virtual void OnOutputReceived(OutputReceivedEventArgs e)
        {
            OutputReceived?.Invoke(this, e);
        }
    }

}
