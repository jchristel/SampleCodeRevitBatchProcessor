#############################################
RoomMate Tasks
#############################################

*******
Summary
*******

The 'RoomMate Tasks' flow runs the room tasks a RoomMate server holds for a chosen set of Revit models, with nobody
at the screen. It is the RoomMate **Tasks** button without its window: for each model every queued task is claimed,
checked, written (one task per transaction group) and reported back to the server.

- populate and update tasks place a room's items
- create RLS and create RLS set tasks make room layout sheets

The RoomMate code does the work (``room_m.room_mate.tasks_unattended``); the flow opens the models and saves them.

**Not yet run in Revit.**

Actions Overview
----------------

This flow is run through a PowerShell script (``_Script\startRoomMateTasks.ps1``) which executes:

#. A pre-processing script collecting the Revit files to process, in a window (``-UI yes``, the default) or every
   file in ``PATH_TO_FILES_TO_PROCESS`` (``-UI no``).
#. Main Process: a Revit Batch Processor session which, per model:

    #. Opens a new local copy of the model, all worksets open.
    #. Claims every queued RoomMate task of the model and runs it.
    #. Synchronises with central (or saves a non workshared model), only when a task was written.

#. A post process which checks the Revit Batch Processor log files for exceptions and removes the marker files.

What nobody is asked
--------------------

The Tasks button asks a person two things. The flow answers them from ``settings.py``:

- **Tasks with warnings** (a missing room tag, an elevation that could not be placed, ...) are reported aborted, with
  their warnings, unless ``PROCEED_WITH_WARNINGS`` is ``True``.
- **Incomplete RLS settings** in a model abort its create RLS tasks, with what is missing. The flow never edits them:
  open the model and use the RoomMate **RLS settings** button.

Every task the flow claims is reported to the server, whatever happens, so none is left "in progress". The RoomMate
tasks page (``/tasks/`` on the server) shows the outcome of each, and every step is written to ``RoomMate.log`` in the
RoomMate folder of the application data.

Setup
-----

- Install the RoomMate pyRevit extension on the machine that runs the flow (the RoomMate installer, or
  ``installer\build-extension.ps1 -Deploy``). ``settings.py`` loads ``room_m`` and the duHast RoomMate ships from
  ``%APPDATA%\pyRevit\Extensions\RoomMate.extension\lib``, ahead of any other duHast.
- The RoomMate server must be reachable from this machine.

In ``_Script\settings.py``:

- ``ROOMMATE_PROJECT_ID``: the RoomMate project the models belong to.
- ``ROOMMATE_SERVER``: empty to use the address kept in each model (the **Server** button), the ``ROOMMATE_SERVER``
  environment variable or ``%APPDATA%\RoomMate\server.json``; or an address used for every model.
- ``MODEL_ID_FROM_FILE_NAME``: tasks are kept per model id, the model's title when it was exported. The flow opens a
  new local copy, whose title can differ, so by default it asks for the central file's name. Set it to ``False`` to
  ask for the open document's title. The log says which id was asked for; "Nothing queued" for a model with tasks
  on the server usually means the id differs.
- ``PROCEED_WITH_WARNINGS``, ``SAVE_WHEN_CHANGED``: see above.
- ``PATH_TO_FILES_TO_PROCESS``, ``IS_CLOUD_PROJECT``: as in the other flows.

In ``_settings\BatchRvt.RoomMateTasksA.Settings.json``: the paths to this flow, and the Revit version.

More than one session
---------------------

The server hands a model's tasks to one session only, so models can be processed in parallel: add a settings file
per session (each with its own ``Tasklist_n.txt``), list them in ``startRoomMateTasks.ps1`` and set
``NO_OF_TASK_LIST_FILES`` to match.
