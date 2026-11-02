# RoomMate Export

**Panel:** RoomMate | **Button:** Export

<img src="Extensions/duHast-2025.extension/duHast.tab/RoomMate.panel/RoomMateRooms.pushbutton/Icon.png" width="40" alt="button icon">

Exports room and door data from the selected models and pushes it to a **local RoomMate
server** over HTTP. Nothing is written to disk and nothing in the Revit model is modified.

## Where the data goes

The server is expected on **`http://127.0.0.1:5151`** — the local machine, not a remote
host. Three endpoints are used:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/settings/projects` | GET | Read the projects registered on the server |
| `/rooms/stream` | POST | Push rooms and levels |
| `/doors/stream` | POST | Push doors |

Each push is a **gzip-compressed NDJSON stream** — `Content-Type: application/x-ndjson`,
`Content-Encoding: gzip` — with the envelope as the first line and one line per room or door
after it. Large exports are streamed rather than buffered whole.

The RoomMate server must be running before you start; if it cannot be reached the run aborts
at the project step and nothing is exported.

## What it does

1. **Select the models.** A document picker offers the active document and every loaded
   Revit link, with multi-select. All selected models are pushed under the same project.
2. **Select the project.** The list is fetched from the server's registered projects, so it
   reflects what the server knows, not anything in the Revit file. There is no default and no
   skip — if the server is unreachable, has no registered projects, or you cancel, the run
   aborts.
3. **Select the phase.** Asked once for the whole run, offering only the phase names **common
   to every selected model**. Each model then resolves that name against its own phases, so
   the name is what carries across models, not the phase id.
4. **Per model**, in a cancellable progress bar:
   - build the envelope (below);
   - export the rooms and levels that exist in the chosen phase, and push them;
   - export the doors that exist in the chosen phase, and push them.

**Rooms are pushed before doors, and a failed rooms push stops that model there.** A door
carries only room *ids*, not room data, so doors pushed against rooms that never landed would
be meaningless — and a room id is only unique within one model.

## What is sent

**Envelope**, carried by both pushes:

| Field | Source |
|---|---|
| `project.id` / `project.name` | The project you picked from the server |
| `model.id` / `model.name` | The Revit document **Title** |
| `snapshot.taken_at` | UTC timestamp with microseconds |
| `phase` | The phase you picked — required; the server refuses a push without it |
| `model_to_shared` | The model's shared-coordinate transform, as a 2D affine matrix. Optional |
| `room_boundary` | The model's Area and Volume Computations boundary setting. Rooms push only, optional |

The two optional fields are advisory. If either cannot be read, a message is recorded and the
push still goes ahead — the server falls back to project-level defaults.

**Rooms push:** duHast room data and building level data for the model, filtered to the
chosen phase.

**Doors push:** duHast door data, plus per-door placement data read from the Revit API —
insertion point and the through-wall normal — with `from_room` / `to_room` given as room ids.

## Reading the result

| Outcome | Meaning |
|---|---|
| `server accepted` | The push landed and is live |
| `stored but NOT live` (HTTP 202) | **Rooms only.** The declared phase disagrees with the phase this model was first pushed under, so the payload is quarantined. Nothing reads it until someone activates it on the server |
| `push failed` | Rejected or unreachable; the message names which |

A 202 is easy to misread as success. If a model does not appear to have updated on the
server, check for this message first.

For doors there is no 202 — a phase disagreement is **refused outright**, because activating
it would re-phase the model while its rooms stayed behind.

## Notes on behaviour worth knowing

- **Model identity is the document Title.** Two different files sharing a Title collide into
  one record on the server, and renaming a file forks its history into a new record. This is
  a known stopgap — there is no stable GUID available for a plain local file.
- **One model failing does not abandon the rest.** Each model's export and push runs
  independently; the run continues and ends red, reporting which model failed and why.
- **A model with no doors at all is reported as a failure.** That is the server contract, not
  a bug in the export.
- Cancelling is honoured after the export and before the post, so a cancel during a long
  export does not then send the payload anyway.
- Every message is collected on the run result and printed to the pyRevit output window; read
  it rather than assuming a completed progress bar means everything landed.

## Requirements

- A RoomMate server running on `127.0.0.1:5151`.
- The project must already be **onboarded on the server** — the extension cannot create one.
- The selected models must share at least one phase name, and must have phases at all.

## Not on the ribbon

The library behind this button also provides **rooms-only** and **doors-only** entry points,
for re-pushing one half without paying for the other's export. Neither has a button in this
extension; they need wiring up in a `script.py` to be reachable.
