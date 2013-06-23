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
            'Unknown case for "{text}"'.format(
                text=strip_end_of_long_string(text, max_size=50)
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
    Ignores case (low or up) of characters in non important places.

    @param text: str
    @returns one of ['camel', 'title', 'underscore', 'other', 'mixed'].
        'mixed': both camel and underscore (ex: "handler")
    """

    parts = split_by_case(text, 'underscored')
    if not parts:
        # text is collection of underscores
        return 'other'

    if not all(part.isalnum() for part in parts):
        # one or more text part contains not alpha-numeric characters
        return 'other'

    if len(parts) != 1:
        return 'underscore'

    parts = split_by_case(parts[0], 'camel')
    if parts[0][0].isupper():  # check first character
        return 'title'

    # first character lower or not letter

    if len(parts) == 1:
        return 'mixed'

    return 'camel'


def split_by_case(text, case):
    """
    Split `text` into parts corresponding to `case`.
    In underscored mode:
        * consequent underscores treats as single
        * ignores enclosed underscores
        * ignores case (low or up) of characters
    In camel mode:
        * splits between low-case and up-case character
        * treats consequent upper characters as one part

    @param text: str
    @param case: one of ['underscore', 'camel']
    @returns list
        Splitted (corresponding to `case`) `text`.
    """

    if case == 'underscore':
        return filter(bool, text.split('_'))
    elif case == 'camel':
        text = text.replace('|', '||')
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1|\2', text.replace('|', '||'))
        return map(methodcaller('replace', '||', '|'), text.split('|'))
    return [text]


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

    case = detect_case(text)
    if case == 'camel':
        parts = split_by_case(text, 'camel')
        text = translate_to_underscore_case(parts)
    elif case == 'underscore':
        parts = split_by_case(text, 'underscore')
        text = translate_to_title_case(parts)
    elif case == 'title':
        parts = split_by_case(text, 'camel')
        text = translate_to_camel_case(parts)
    elif case == 'mixed':
        parts = split_by_case(text, 'camel')
        text = translate_to_title_case(parts)
    else:
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
