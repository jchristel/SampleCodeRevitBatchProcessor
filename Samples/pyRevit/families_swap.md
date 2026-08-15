# Swap Families

**Panel:** Families | **Menu:** SwapFamilies

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/SwapFamilies.pulldown/Icon.png" width="40" alt="button icon">

Tools to replace instances of one family type with another in the current project.

All three report, as tables in the output window, the instances they could **not** swap:

| Table | Meaning |
|---|---|
| Host Families containing instances not swapped | Instances nested inside another family |
| Host Groups containing instances not swapped | Instances inside a group |

Those need resolving by hand — swapping nested and grouped instances is not automated.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/SwapFamilies.pulldown/Swap%20By%20Directives.pushbutton/Icon.png" width="24" alt="Swap By Directives icon"> Swap By Directives

Swaps instances according to CSV instruction files.

**You select a folder, not a file.** The tool searches it for files whose names begin with
`SwapDirective` and end in `.csv`, and reads every directive it finds across all of them.

**Directive file columns:**

```
Source Family Name, Source Family Category Name, Source Family Type Name,
Target Family Name, Target Family Type Name
```

**Use when:** You have a predefined substitution list to apply across a project — for example
moving from concept families to construction-issue families.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/SwapFamilies.pulldown/Swap%20By%20User%20Selection%20List.pushbutton/Icon.png" width="24" alt="Swap By Selection icon"> Swap By Selection

Swaps instances through two selection dialogs:

1. Select the **source** family type to replace, from the types loaded in the project.
2. Select the **target** type to use instead. The list is filtered to the source type's
   category.
3. All eligible instances of the source type are swapped.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/SwapFamilies.pulldown/Swap%20By%20User%20Selection%20Pick.pushbutton/Icon.png" width="24" alt="Swap By Picking icon"> Swap By Picking

The same as **Swap By Selection**, except the source is identified by **picking an instance
in the model** rather than choosing from a list. You then select the target type as before.

Afterwards it offers to **save the swap you just performed as a `SwapDirective` CSV** through
a save dialog. That file can be fed straight back into **Swap By Directives**, so a one-off
pick can be recorded and replayed on other models.

---

## Notes

- Instances nested in families or inside groups cannot be swapped automatically; they are
  reported for manual attention.
- Instance parameter values are preserved where the target type carries a parameter of the
  same name. Type parameters come from the target type.
- Progress is shown in a cancellable progress bar.
