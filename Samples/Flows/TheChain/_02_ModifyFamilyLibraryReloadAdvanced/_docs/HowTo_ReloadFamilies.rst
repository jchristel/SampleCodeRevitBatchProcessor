#############################################
Reload Families
#############################################


Summary
=======

This flow reloads families which have been flagged as changed into their host families within a tree nesting structure.


Terminology used
----------------

Host family
~~~~~~~~~~~~~~~~~~~~~~~~

A family which contains other (nested) families. 
A host family can also be a nested family.

Nested family:
~~~~~~~~~~~~~~~~~~~~~~~~

A family which is loaded into another family.
A nested family can also be a host family.

Nesting tree
~~~~~~~~~~~~~~~~~~~~~~~~

A family and its nested families can be represented in a tree structure like shown below.

Note:

- A family always has the same child nodes, representing other nested families.
- A family may have different parent nodes: It can be nested into any number of host families.


Script flow diagram
--------------------------------


Outcomes
--------------------------------

All families have been re-laoded into their hosts all the way up the nesting tree and therefore any change to a nested family along this tree has been propagated all the way to the root (top) family.

Inputs
~~~~~~~~~~

: Input_ReloadFamilies.rst