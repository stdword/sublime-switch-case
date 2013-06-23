# coding: utf-8

import sublime
import sublime_plugin


class UnknownCase(Exception):
    pass


def detect_case(text):
    if not text.replace('_', '').isalnum():
        return 'other'

    if text.find('_') != -1:
            return 'underscore'
    return 'camel'


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
