import os
import re
from .word import Kind as Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'citation'
        self.default_action = 'append'
        self.persist_actions = ['preview']

    def action_execute(self, context):
        target = context['targets'][0]
        self.vim.call('denite#util#execute_command',
                      target['action__command'])

    def action_open(self, context):
        target = context['targets'][0]
        path = target['action__path']

        if (re.match('https?://', path)
            or os.path.splitext(path)[1] == ".pdf"):
            self.vim.call('denite#util#open', path)

    def action_directory(self, context):
        target = context['targets'][0]
        path = target['action__path']
        self.vim.call('denite#util#open', path)

    def action_preview(self, context):
        pass

