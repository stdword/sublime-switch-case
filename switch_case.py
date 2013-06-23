# coding: utf-8

import sublime
import sublime_plugin


def detect_case(text):
    '''
        Если текст состоит из букв, цифр и _, то это underscore.
        Если текст состоит из букв, цифр, то это camel.
    '''
    replaced = text.replace('_', '')
    if not replaced.isalnum():
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


class SwitchCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            text = self.view.substr(region)
            if not text:
                continue

            case = detect_case(text)
            if case == 'camel':
                text = translate_to_underscore_case(text)
            elif case == 'underscore':
                text = translate_to_camel_case(text)
            else:
                sublime.status_message('Unknown case type')
                continue

            self.view.replace(edit, region, text)
