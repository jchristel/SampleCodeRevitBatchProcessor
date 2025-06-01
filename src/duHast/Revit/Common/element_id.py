def get_el_id(el):
    """
    Gets the ID of a Revit element.
    :param el: The Revit element.
    :return: The ID of the element.
    :rtype: int
    """

    if el:
        el_id = getattr(el, "Id", None)
        if el_id:
            return el_id
        else:
            raise ValueError("Element provided does not have an Id attribute.")
    else:
        raise ValueError("Element is None, cannot get ID.")


def get_el_id_int(el):
    """
    Gets the integer ID of a Revit element.
    :param el: The Revit element.
    :return: The integer ID of the element.
    :rtype: int

    """

    el_id = get_el_id(el)

    if getattr(el_id, "IntegerValue", None):
        return int(el_id.IntegerValue)
    elif getattr(el_id, "Value", None):
        return int(el_id.Value)
    else:
        raise ValueError("Element ID does not have an IntegerValue or Value attribute.")
