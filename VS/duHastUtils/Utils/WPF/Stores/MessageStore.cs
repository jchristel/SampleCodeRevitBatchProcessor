//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
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
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;

using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.Utils.WPF.Interfaces;

namespace duHastNet.Utils.WPF.Stores;

public partial class MessageStore : ObservableObject, IMessageStore, IDisposable
{
    private CancellationTokenSource? _dismissCancellation;
    private const int DefaultDismissSeconds = 5;
    private readonly Queue<QueuedMessage> _messageQueue = new();
    private readonly object _queueLock = new();
    private bool _isProcessingMessage = false;

    [ObservableProperty]
    private string _currentMessage = string.Empty;

    [ObservableProperty]
    private MessageTypes _currentMessageType = MessageTypes.Information;

    [ObservableProperty]
    private double _progressPercentage = 0;

    [ObservableProperty]
    private bool _isTimerActive = false;

    [ObservableProperty]
    private int _pendingMessageCount = 0;

    public bool HasCurrentMessage => !string.IsNullOrEmpty(CurrentMessage);
    public bool HasPendingMessages => PendingMessageCount > 0;

    public void EnqueueMessage(string message, MessageTypes messageType, int? dismissAfterSeconds = null)
    {
        lock (_queueLock)
        {
            var queuedMessage = new QueuedMessage(message, messageType, dismissAfterSeconds);
            _messageQueue.Enqueue(queuedMessage);
            PendingMessageCount = _messageQueue.Count;
        }

        // If no message is currently being displayed, process the next one immediately
        if (!_isProcessingMessage && !HasCurrentMessage)
        {
            ProcessNextMessage();
        }
    }

    public void ClearCurrentMessage(bool autoAdvance = true)
    {
        CancelDismissTimer();
        CurrentMessage = string.Empty;
        ProgressPercentage = 100;
        IsTimerActive = false;
        _isProcessingMessage = false;

        if (autoAdvance)
        {
            ProcessNextMessage();
        }
    }

    public void ClearQueue()
    {
        lock (_queueLock)
        {
            _messageQueue.Clear();
            PendingMessageCount = 0;
        }
    }

    public void ClearAll()
    {
        ClearQueue();
        ClearCurrentMessage(autoAdvance: false);
    }

    [Obsolete("Use EnqueueMessage instead. This method is deprecated and will be removed in a future version.")]
    public void SetCurrentMessage(string message, MessageTypes messageType, int? dismissAfterSeconds = null)
    {
        // For backward compatibility, directly set the message without queueing
        CancelDismissTimer();

        // Limit to 10 rows
        if (message.Contains('\n'))
        {
            string[] lines = message.Split(['\n'], StringSplitOptions.RemoveEmptyEntries);
            if (lines.Length > 10)
            {
                message = string.Join("\n", lines[..10]);
            }
        }

        CurrentMessage = message;
        CurrentMessageType = messageType;

        // Start auto-dismiss timer if specified
        if (dismissAfterSeconds.HasValue && dismissAfterSeconds.Value > 0)
        {
            StartDismissTimer(dismissAfterSeconds.Value);
        }
        else
        {
            ProgressPercentage = 0;
            IsTimerActive = false;
        }
    }

    private void ProcessNextMessage()
    {
        QueuedMessage? nextMessage = null;

        lock (_queueLock)
        {
            if (_messageQueue.Count > 0)
            {
                nextMessage = _messageQueue.Dequeue();
                PendingMessageCount = _messageQueue.Count;
            }
        }

        if (nextMessage != null)
        {
            _isProcessingMessage = true;
            DisplayMessage(nextMessage);
        }
        else
        {
            _isProcessingMessage = false;
        }
    }

    private void DisplayMessage(QueuedMessage queuedMessage)
    {
        // Limit to 10 rows
        string message = queuedMessage.Message;
        if (message.Contains('\n'))
        {
            string[] lines = message.Split(['\n'], StringSplitOptions.RemoveEmptyEntries);
            if (lines.Length > 10)
            {
                message = string.Join("\n", lines[..10]);
            }
        }

        CurrentMessage = message;
        CurrentMessageType = queuedMessage.MessageType;

        // Start auto-dismiss timer if specified
        if (queuedMessage.DismissAfterSeconds.HasValue && queuedMessage.DismissAfterSeconds.Value > 0)
        {
            StartDismissTimer(queuedMessage.DismissAfterSeconds.Value);
        }
        else
        {
            ProgressPercentage = 0;
            IsTimerActive = false;
        }
    }

    public void PauseDismissTimer()
    {
        CancelDismissTimer();
        IsTimerActive = false;
    }

    public void ResumeDismissTimer(int seconds)
    {
        if (HasCurrentMessage && !IsTimerActive)
        {
            // Calculate remaining time based on current progress (now counting down)
            int remainingSeconds = (int)(seconds * (ProgressPercentage / 100)); // Changed formula
            if (remainingSeconds > 0)
            {
                StartDismissTimer(remainingSeconds);
            }
        }
    }

    private void StartDismissTimer(int seconds)
    {
        _dismissCancellation = new CancellationTokenSource();
        IsTimerActive = true;
        ProgressPercentage = 100; // Start at 100 instead of 0

        Task.Run(async () =>
        {
            try
            {
                var startTime = DateTime.Now;
                var duration = TimeSpan.FromSeconds(seconds);
                var updateInterval = TimeSpan.FromMilliseconds(50); // Update 20 times per second

                while (!_dismissCancellation.Token.IsCancellationRequested)
                {
                    var elapsed = DateTime.Now - startTime;
                    // INVERT: Start at 100, count down to 0
                    var progress = 100 - ((elapsed.TotalSeconds / duration.TotalSeconds) * 100);

                    if (progress <= 0) // Changed from >= 100
                    {
                        // Time's up - dismiss message and show next
                        await Task.Delay(100); // Small delay for visual smoothness
                        ClearCurrentMessage(autoAdvance: true);
                        break;
                    }

                    ProgressPercentage = progress;
                    await Task.Delay(updateInterval, _dismissCancellation.Token);
                }
            }
            catch (TaskCanceledException)
            {
                // Timer was cancelled - this is expected
            }
        }, _dismissCancellation.Token);
    }

    private void CancelDismissTimer()
    {
        _dismissCancellation?.Cancel();
        _dismissCancellation?.Dispose();
        _dismissCancellation = null;
    }

    partial void OnCurrentMessageChanged(string value)
    {
        OnPropertyChanged(nameof(HasCurrentMessage));
    }

    partial void OnPendingMessageCountChanged(int value)
    {
        OnPropertyChanged(nameof(HasPendingMessages));
    }

    public void Dispose()
    {
        CancelDismissTimer();
        ClearQueue();
    }
}
