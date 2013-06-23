# coding: utf-8

from __future__ import unicode_literals

import sublime_plugin

from switch_case import switch_case


class SwitchCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            text = self.view.substr(region)
            if not text:
                continue

            text = switch_case(text)
            self.view.replace(edit, region, text)
