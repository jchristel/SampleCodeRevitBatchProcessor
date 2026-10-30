"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around data storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data storage can be used to project wide settings not associated with a specific element. 

Obsolete in Revit 2025 ... 
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

"""
Read and write ONE text field kept in a project's extensible storage.

A small, common need: a tool keeps a block of text (usually JSON) in the model itself so it travels
with the file. The schema has a single string field and lives on one DataStorage element.

Built on :mod:`duHast.Revit.ExtensibleSchemas.extensible_schemas_create`,
:mod:`duHast.Revit.ExtensibleSchemas.data_storage` and
:mod:`duHast.Revit.ExtensibleSchemas.data_storage_create`; nothing here parses the text.
"""

import clr

import duHast.Utilities.Objects.result as res

from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.ExtensibleSchemas.data_storage import find_data_storage
from duHast.Revit.ExtensibleSchemas.extensible_schemas import get_schema
from duHast.Revit.ExtensibleSchemas.extensible_schemas_create import create_schema

from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.DB.ExtensibleStorage import DataStorage, Entity


def read_project_text(doc, schema_guid, field_name):
    """
    Reads the text field of the project's data storage that holds the schema.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param schema_guid: The guid of the schema.
    :type schema_guid: str
    :param field_name: The name of the string field.
    :type field_name: str

    :return:
        Result class instance.

        - result.status. True if the read worked (also when the model holds nothing yet), otherwise False.
        - result.result will hold the text as its only member, or be empty when the model has none (no schema, no storage element).

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        schema = get_schema(schema_guid)
        if schema is None:
            return_value.append_message("No schema with guid {} in this session.".format(schema_guid))
            return return_value
        storage = find_data_storage(doc, schema_guid)
        if storage is None:
            return_value.append_message("No data storage element holds the schema.")
            return return_value
        return_value.result.append(storage.GetEntity(schema).Get[str](field_name))
    except Exception as e:
        return_value.update_sep(False, "Failed to read project text: {}".format(e))
    return return_value


def write_project_text_without_transaction_wrapper(
    doc, schema_guid, schema_name, schema_documentation, field_name, text
):
    """
    Writes the text into the project's data storage, creating the schema and the storage element on first use.

    Needs to be called within an open transaction. Refuses a family document and a read only document.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param schema_guid: The guid of the schema.
    :type schema_guid: str
    :param schema_name: The schema name (no spaces); used only when the schema has to be created.
    :type schema_name: str
    :param schema_documentation: Short description of the schema; used only when it has to be created.
    :type schema_documentation: str
    :param field_name: The name of the string field.
    :type field_name: str
    :param text: The text to store.
    :type text: str

    :return:
        Result class instance.

        - result.status. True if the text was stored, otherwise False.
        - result.message will contain the reason when it was not.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        if doc.IsFamilyDocument:
            return_value.update_sep(False, "A family document cannot hold project text.")
            return return_value
        if doc.IsReadOnly:
            return_value.update_sep(False, "The model is read only.")
            return return_value

        def add_text_field(builder):
            builder.AddSimpleField(field_name, clr.GetClrType(str))

        schema = create_schema(
            schema_name=schema_name,
            schema_documentation=schema_documentation,
            string_guid=schema_guid,
            field_builder=add_text_field,
        )
        storage = find_data_storage(doc, schema_guid)
        if storage is None:
            storage = DataStorage.Create(doc)
        entity = Entity(schema)
        entity.Set[str](field_name, text)
        storage.SetEntity(entity)
        return_value.append_message("Project text stored.")
    except Exception as e:
        return_value.update_sep(False, "Failed to store project text: {}".format(e))
    return return_value


def write_project_text(doc, schema_guid, schema_name, schema_documentation, field_name, text):
    """
    Writes the text into the project's data storage within its own transaction.

    See :func:`write_project_text_without_transaction_wrapper` for the arguments and the result.

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    def action():
        return write_project_text_without_transaction_wrapper(
            doc, schema_guid, schema_name, schema_documentation, field_name, text
        )

    return in_transaction(Transaction(doc, "Storing project text"), action)
