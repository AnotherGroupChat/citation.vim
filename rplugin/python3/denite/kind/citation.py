import os
import re
from .word import Kind as Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'citation'
        self.default_action = 'default'
        self.persist_actions = ['preview']

    def action_default(self, context):
        target = context['targets'][0]
        source_context = target['source_context']

        if source_context['__source'] is 'sub_sources':
            self.action_field(context)
        else:
            self.action_append(context)

    def action_field(self, context):
        target = context['targets'][0]
        cmd = 'Denite citation:{}'.format(target['action__source_field'])
        self.vim.command(cmd)

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

