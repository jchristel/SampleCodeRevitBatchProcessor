# About

**Panel:** About | **Menu:** About

<img src="Extensions/duHast-2025.extension/duHast.tab/About.panel/About.pulldown/Icon.png" width="40" alt="button icon">

Two reference links. Neither reads from nor modifies the Revit model — each opens a page in
your default web browser and nothing else.

The menu lists **License** first, then a separator, then **Icon8**.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/About.panel/About.pulldown/License.pushbutton/Icon.png" width="24" alt="License icon"> License

Opens the extension's licence on GitHub:

`https://github.com/jchristel/SampleCodeRevitBatchProcessor?tab=License-1-ov-file#readme`

The project is released under the **BSD licence**, © Jan Christel. The same licence text
appears at the top of every source file in the extension.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/About.panel/About.pulldown/Icon8.pushbutton/Icon.png" width="24" alt="Icon8 icon"> Icon8

Opens `https://icons8.com` — the source of the icons used throughout the extension.

This button exists to **carry the attribution** that the Icons8 free licence requires. The
attribution snippet itself is kept alongside the panel, in
`Extensions/duHast-2025.extension/duHast.tab/About.panel/LinkIcon8.txt`:

```html
<a target="_blank" href="https://icons8.com/icon/111452/edit">Edit</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>
```

If you redistribute the extension, or reuse its icons elsewhere, that attribution needs to
travel with them.

---

## Notes

- Both buttons need an internet connection and a configured default browser. They open a
  browser window outside Revit; Revit itself is unaffected.
- Neither button opens a document, reads a parameter, or starts a transaction — they are safe
  to run at any time, including with no document open.
