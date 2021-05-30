import os
import re
from shutil import copyfile
from denite.kind.file import Kind as File
from denite.kind.word import Kind as Word
from denite.kind.openable import Kind as Openable

import sys


def eprint(*args, **kwargs):
  raise Exception(*args)
  print(*args, file=sys.stderr, **kwargs)


class Kind(Word, File, Openable):

  def __init__(self, vim):
    super().__init__(vim)

    self.name = 'citation_collection'
    self.default_action = 'append'
    self.vim = vim

  def action_append(self, context):
    if context['targets'][0]['nick']:
      Word.action_append(self, context)

  def action_preview(self, context):
    for target in context['targets']:
      path = target['action__path']
      if not os.path.exists(path):
        with open("/home/dylan/phd/notes/reviews/review.template") as f:
          template = f.read().replace("Paper", target["title"])
        with open(path, "w") as f:
          f.write(template)
    super().action_preview(context)
