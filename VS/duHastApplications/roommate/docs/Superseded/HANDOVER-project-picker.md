# Handover — project picker for the pyRevit push

Add a required project-selection step to the pyRevit → Rust room push. The
user must choose a **server-registered** project before any export runs; the
old behaviour derived the project id from the Revit document, which the server
usually rejects.

Touches two IronPython/pyRevit files only — `post_rooms.py` and
`room_mate.py`. No Rust change: the server already exposes `GET /projects` and
already rejects unregistered projects, so this is purely the producer catching
up to a guarantee the server enforces.

---

## Why

`room_mate.py`'s `export_and_post_model` built the identity envelope's project
block from the Revit document:

```python
"project": {
    "id": project_info.Number or selected_doc.Title,
    "name": project_info.Name or selected_doc.Title,
},
```

That id is a *guess*. The server only accepts a push whose project id has a
registered settings bundle — `validate_ingest` in `handlers.rs` returns
`422 "no settings configured for project '<id>'"` otherwise — and the id
becomes a storage path component. A Revit `ProjectInformation.Number` (or a
`Title` fallback) will usually not match a registered id, so pushes either
fail with a 422 or, if it happens to match, risk landing data under the wrong
key. The fix is to let the user pick from the server's own list.

`build_envelope` in `post_rooms.py` already does the right thing on its side:
it reads `project`/`model`/`snapshot` off the export dict and **raises
`ValueError` if `project.id` is missing** rather than defaulting to
`"unknown"`. So the flaw was never in `build_envelope` — it was the
Revit-derived id feeding it. `build_envelope` needs **no change**; it just
receives the picked id and validates it as before.

---

## Source of truth: `GET /projects`

The server's `projects::list_projects` (`projects.rs`) returns every project
that has both stored data **and** a registered settings bundle, as
`[{ "id", "name" }]`, sorted by name. This is the authoritative list of ids a
push can target. An empty list (`200 []`) is a valid answer — it means no
project is onboarded yet, which is a hard stop for the producer (onboarding is
a server-side step), not an error to paper over.

Building selection (`GET /projects/{id}/buildings`) is **out of scope**: that's
a viewer-side read filter, not part of the push. The push carries no building.

---

## Changes

### 1. `post_rooms.py` — add `fetch_projects`

New helper near `_post_content`, reusing the existing `make_client` and
`unwrap_aggregate`. Returns the same `(ok, status, text)` tuple the post
functions use, so callers branch uniformly. `text` is the parsed list on
success, an error string otherwise. A 2xx with a non-list / unparseable body
is treated as a failure; an empty list is a success the caller interprets.

```python
SERVER_URL_PROJECTS = "http://127.0.0.1:5151/projects"


def fetch_projects(url=SERVER_URL_PROJECTS):
    client = make_client()
    try:
        response = client.GetAsync(url).Result
        status = int(response.StatusCode)
        text = response.Content.ReadAsStringAsync().Result
        if not (200 <= status < 300):
            return (False, status, "server returned {}: {}".format(status, text))
        try:
            projects = json.loads(text)
        except ValueError as e:
            return (False, status, "could not parse /projects response: {}".format(e))
        if not isinstance(projects, list):
            return (False, status, "unexpected /projects shape: {}".format(text))
        return (True, status, projects)
    except Exception as e:
        return (False, None, "could not reach {}: {}".format(url, unwrap_aggregate(e)))
    finally:
        client.Dispose()
```

### 2. `room_mate.py` — pick once, thread through

Import `fetch_projects` alongside `post_payload_stream`, and add a picker that
forces a choice. It returns `{"id", "name"}` or `None`, where `None` means
**abort the run** (server unreachable, no projects registered, or user
cancelled). No default/skip path by design.

```python
from post_rooms import post_payload_stream, fetch_projects


def choose_project(forms):
    ok, status, payload = fetch_projects()
    if not ok:
        forms.alert(
            "Could not load projects from the server.\n\n{}".format(payload),
            title="Roommate - push aborted", warn_icon=True)
        return None
    projects = payload
    if not projects:
        forms.alert(
            "The server has no registered projects.\n\n"
            "A project must be onboarded on the server before rooms can be "
            "pushed to it.",
            title="Roommate - no projects", warn_icon=True)
        return None
    options = [{"name": p.get("name") or p["id"], "id": p["id"]} for p in projects]
    selected = forms.SelectFromList.show(
        options, name_attr="name",
        title="Select a project to push to",
        button_name="Push to this project",
        multiselect=False)
    if not selected:
        return None
    return {"id": selected["id"], "name": selected["name"]}
```

Call it in `rooms_export_entry` **after** document selection, **before** the
export loop. `None` returns early — nothing is exported or pushed:

```python
        project = choose_project(forms)
        if project is None:
            return_value.update_sep(False, "Push aborted: no project selected.")
            return return_value
```

Pass `project` into the per-model call:

```python
                export_and_post_model(selected_doc, project, return_value, pb)
```

### 3. `room_mate.py` — `export_and_post_model` uses the picked project

New `project` parameter. Only the envelope's `project` block changes; `model`,
`snapshot`, and everything downstream are untouched.

```python
def export_and_post_model(selected_doc, project, return_value, pb):
    ...
    envelope = {
        "project": {
            "id": project["id"],
            "name": project["name"],
        },
        "model": {
            "id": selected_doc.Title,
            "name": selected_doc.Title,
        },
        "snapshot": {
            "taken_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    }
```

---

## Behaviour notes

- **One project per run.** Every model selected in a single run posts under the
  one picked project — matching "several models under one project" in
  STRATEGY-SERVER.md. If a run could ever legitimately span models belonging to
  *different* server projects, the picker would need to move per-model instead.
  Flag if that's a real case.
- **Linked vs active documents.** The old code read the linked/active doc's
  `ProjectInformation` for identity; that's now ignored entirely, so
  linked-vs-active no longer affects project identity. Correct for the
  one-project-per-run model.
- **Failure semantics unchanged.** `fetch_projects` and the picker run before
  the loop, so an abort here stops cleanly. Per-model push failures still flip
  `Result` red via `update_sep(False, ...)` without abandoning other models.

---

## Verify

1. **Happy path** — server up with ≥1 registered project: picker lists them by
   name, selection pushes under the chosen id, snapshot lands under
   `<root>/<project id>/...`.
2. **No projects** — server up, none registered: alert shown, run aborts, no
   export.
3. **Server down** — picker alert names the unreachable URL, run aborts.
4. **Cancel** — dismissing the picker aborts silently (no alert), `Result` ends
   red with "no project selected".
5. **Wrong id can't happen** — confirm the pushed id always equals a
   `/projects` id (no Revit-derived value reaches the envelope).

---

## Explicitly not done (separate fixes)

- **Model id is still `Title`, not a GUID.** Two files sharing a Title collide
  into one model record; renaming forks history. Switch to
  `Document.CreationGUID` / worksharing GUIDs if duHast ever exposes them.
- **Building selection** — viewer-side, not push-side. Untouched.
- **`taken_at` collisions** within one second — the microsecond stamp already
  mitigates; server-side dedup is its own item.
