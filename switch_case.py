# coding: utf-8

from __future__ import unicode_literals

import re
from functools import wraps, partial
from operator import methodcaller

import sublime
import sublime_plugin


class UnknownCase(Exception):
    def __init__(self, text):
        super(UnknownCase, self).__init__(
            'Unknown case for "{}"'.format(
                strip_end_of_long_string(text, max_size=50)
            ),
            text,
        )


def strip_end_of_long_string(string, max_size=79, end_plug='...'):
    stripped = string[:max_size]
    if end_plug:
        if len(stripped) != len(string):
            stripped = stripped[:-len(end_plug)] + end_plug
    return stripped


def ignore_enclosed_underscores(func):
    @wraps(func)
    def wrapper(text):
        m = re.match(r'^(_*)(.*?)(_*)$', text)
        return m.group(1) + func(m.group(2)) + m.group(3)
    return wrapper


def translate_to_underscore_case(parts):
    return '_'.join(part[0].lower() + part[1:] for part in parts)


def translate_to_camel_case(parts, titled=False):
    parts = map(methodcaller('capitalize'), parts)
    if not titled:
        parts[0] = parts[0].lower()
    return ''.join(parts)


translate_to_title_case = partial(translate_to_camel_case, titled=True)


def detect_case(text):
    """
    Detects the case of `text`.
    Consequent underscores treats as single.
    Ignores enclosed underscores.
    Ignores case (low or up) of characters in non important places.

    @param text: str
    @returns tuple
        One of ['camel', 'title', 'underscore', 'other'] and
        splitted text parts.
    """

    parts = filter(bool, text.split('_'))

    if not parts:
        # text is collection of underscores
        return 'other', parts

    if not all(part.isalnum() for part in parts):
        # one or more text part contains not alpha-numeric characters
        return 'other', parts

    if len(parts) != 1:
        return 'underscore', parts

    if parts[0][0].isupper():  # check first character
        return 'title', parts
    return 'camel', parts  # first character lower or not letter


@ignore_enclosed_underscores
def switch_case(text):
    """
    Switches in cycle the case of `text`:
        camel -> underscore
        underscore -> title
        title -> camel

    @param text: str
    @returns str
        With switched case.
    """

    case, parts = detect_case(text)
    print case, parts
    if case == 'camel':
        text = translate_to_underscore_case(parts)
    elif case == 'underscore':
        text = translate_to_title_case(parts)
    elif case == 'title':
        text = translate_to_camel_case(parts)
    else:
        print 'err'
        raise UnknownCase(text)

    return text


class SwitchCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            text = self.view.substr(region)
            if not text:
                continue

            try:
                text = switch_case(text)
                self.view.replace(edit, region, text)
            except UnknownCase:
                sublime.status_message('Unknown case type for ')
