def ConDoesNotEqual (valueOne, valueTwo):
    '''
    Returns True if valueOne does not match valueTwo.
    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    :return: True if valueOne does not match valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne != valueTwo):
        return True
    else:
        return False


def ConDoesEqual (valueOne, valueTwo):
    '''
    Returns True if valueOne does match valueTwo.
    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    :return: True if valueOne does match valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne == valueTwo):
        return True
    else:
        return False


def ConOneStartWithTwo (valueOne, valueTwo):
    '''
    Returns True if valueOne starts with valueTwo.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueOne starts with valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne.startswith(valueTwo)):
        return True
    else:
        return False


def ConTwoStartWithOne (valueOne, valueTwo):
    '''
    Returns True if valueTwo starts with valueOne.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueTwo starts with valueOne, otherwise False
    :rtype: bool
    '''

    if (valueTwo.startswith(valueOne)):
        return True
    else:
        return False


def ConTwoDoesNotStartWithOne (valueOne, valueTwo):
    '''
    Returns True if valueTwo does not starts with valueOne.
    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    :return: True if valueTwo does not starts with valueOne, otherwise False
    :rtype: bool
    '''

    if (valueTwo.startswith(valueOne)):
        return False
    else:
        return True