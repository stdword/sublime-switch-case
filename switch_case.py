# coding: utf-8

import re
from functools import wraps

import sublime
import sublime_plugin


class UnknownCase(Exception):
    pass


def ignore_enclosed_underscores(f):
    @wraps
    def wrapper(text):
        m = re.match(r'^(_*)(.*?)(_*)$', text)
        return m.group(1) + f(m.group(2)) + m.group(3)
    return wrapper


@ignore_enclosed_underscores
def detect_case(text):
    """
    Detects the case of `text`.
    Consequent underscores treats as single.
    Saves case (low or up) of characters in non important places.

    @param text: str
    @returns one of ['camel', 'title', 'underscore', 'other']
    """

    splitted = filter(bool, text.split('_'))

    if not splitted:
        # text is collection of underscores
        return 'other'

    if not all(part.isalnum() for part in splitted):
        # one or more text part contains not alpha-numeric characters
        return 'other'

    if len(splitted) != 1:
        return 'underscore'

    if splitted[0][0].isupper():  # check first character
        return 'title'
    return 'camel'  # first character lower or not letter


def translate_to_underscore_case(text):
    underscored = ''
    for ch in text:
        if ch.isupper():
            underscored += '_'
        underscored += ch
    return underscored.lower().strip('_')


def translate_to_camel_case(text, titled=False):
    words = map(lambda x: x.capitalize(), text.split('_'))
    if not titled:
        words[0] = words[0].lower()
    return ''.join(words)


def switch_case(text):
    case = detect_case(text)
    if case == 'camel':
        text = translate_to_underscore_case(text)
    elif case == 'underscore':
        text = translate_to_camel_case(text)
    else:
        raise UnknownCase()

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
                sublime.status_message('Unknown case type')
                continue
