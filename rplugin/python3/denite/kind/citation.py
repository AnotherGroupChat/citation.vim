import os
import re
from .word import Kind as Word
from .command import Kind as Command
from .file import Kind as File
from .directory import Kind as Directory

import sys

def eprint(*args, **kwargs):
    raise Exception(*args)
    print(*args, file=sys.stderr, **kwargs)


class Kind(Word, Command, File, Directory):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'citation'
        self.default_action = 'default'
        # self.persist_actions = ['preview']

    def action_default(self, context):
        target = context['targets'][0]
        source_context = target['source_context']

        if source_context['__source'] is 'sub_sources':
            self.action_field(context)
        else:
            Word.action_append(self, context)

    def action_field(self, context):
        target = context['targets'][0]
        cmd = 'Denite citation:{}'.format(target['action__source_field'])
        self.vim.command(cmd)

    def action_open(self, context):
        for target in context['targets']:
            path = target['action__path']
            self.vim.call('denite#util#open', path)

    def action_directory(self, context):
        Directory.action_open(self, context)

    def action_preview(self, context):
        target = context['targets'][0]
        if 'action__command' in target:
            Command.action_execute(self, context)
