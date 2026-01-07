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

using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.UI.Shared.Interfaces;

/// <summary>
/// Interface for MessageStore - manages application messages and notifications
/// </summary>
public interface IMessageStore
{
    /// <summary>
    /// Gets the current message being displayed
    /// </summary>
    string CurrentMessage { get; }

    /// <summary>
    /// Gets the type of the current message
    /// </summary>
    MessageTypes CurrentMessageType { get; }

    /// <summary>
    /// Gets the progress percentage for auto-dismiss timer (100 = full time remaining, 0 = expired)
    /// </summary>
    double ProgressPercentage { get; }

    /// <summary>
    /// Gets whether the auto-dismiss timer is currently active
    /// </summary>
    bool IsTimerActive { get; }

    /// <summary>
    /// Gets the number of messages waiting in the queue
    /// </summary>
    int PendingMessageCount { get; }

    /// <summary>
    /// Gets whether there is currently a message being displayed
    /// </summary>
    bool HasCurrentMessage { get; }

    /// <summary>
    /// Gets whether there are messages pending in the queue
    /// </summary>
    bool HasPendingMessages { get; }

    /// <summary>
    /// Enqueues a message to be displayed to the user
    /// </summary>
    /// <param name="message">Message text to display</param>
    /// <param name="messageType">Type of message (Information, Warning, Error)</param>
    /// <param name="dismissAfterSeconds">Optional auto-dismiss time in seconds</param>
    void EnqueueMessage(string message, MessageTypes messageType, int? dismissAfterSeconds = null);

    /// <summary>
    /// Clears the current message and optionally processes the next queued message
    /// </summary>
    /// <param name="autoAdvance">Whether to automatically show the next queued message</param>
    void ClearCurrentMessage(bool autoAdvance = true);

    /// <summary>
    /// Pauses the auto-dismiss timer for the current message
    /// </summary>
    void PauseDismissTimer();

    /// <summary>
    /// Resumes the auto-dismiss timer for the current message
    /// </summary>
    /// <param name="seconds">Number of seconds until auto-dismiss</param>
    void ResumeDismissTimer(int seconds);
}
