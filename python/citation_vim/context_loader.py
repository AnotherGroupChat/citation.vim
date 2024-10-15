# -*- coding: utf-8 -*-

import os.path
import pynvim as vim
import re
from citation_vim.utils import raiseError, decode_str


class ContextLoader(object):
    """
    Loads context from Vim
    """

    def __init__(self, vim):
        self.vim = vim
        context = {}
        context = self.get_mode(context)
        context = self.get_shared_context(context)
        self.context = context

    def get_mode(self, context):
        context["mode"] = self.vim.eval("g:citation_vim_mode")
        if context["mode"] == "bibtex":
            context = self.get_bibtex_context(context)
        else:
            raiseError("'g:citation_vim_mode' must be set to 'bibtex'")
        return context

    def get_bibtex_context(self, context):
        context["bibtex_file"] = self.get_bibtex_file()
        context["cache"] = True
        context["cache_path"] = self.get_cache_path()
        return context

    def get_shared_context(self, context):
        keys_to_check = {
            "key_clean_regex": "g:citation_vim_key_clean_regex",
            "key_title_banned_regex": "g:citation_vim_key_title_banned_regex",
            "collection": "g:citation_vim_collection",
            "key_format": "g:citation_vim_key_format",
            "reverse_order": "g:citation_vim_reverse_order",
            "wrap_chars": "g:citation_vim_source_wrap",
            "desc_format": "g:citation_vim_description_format",
            "et_al_limit": "g:citation_vim_et_al_limit",
            "desc_fields": "g:citation_vim_description_fields",
            "source": "a:source",
            "source_field": "a:field",
        }

        for key, vim_var in keys_to_check.items():
            try:
                value = self.vim.eval(vim_var)
                if key in ["reverse_order", "et_al_limit"]:
                    value = int(decode_str(value))
                elif key in ["key_clean_regex", "key_title_banned_regex"]:
                    value = re.compile(decode_str(value))
                else:
                    value = decode_str(value)
                context[key] = value
            except vim.api.common.NvimError:
                pass  # Key does not exist, do nothing

        # Defaults set in plugin
        context["bibtex_file"] = self.get_bibtex_file()
        context["cache_path"] = self.get_cache_path()
        context["review_directory"] = self.get_review_directory()
        return context

    def get_review_directory(self):
        file = self.vim.eval("g:citation_vim_review_directory")
        return os.path.expanduser(file)

    def get_bibtex_file(self):
        file = self.vim.eval("g:citation_vim_bibtex_file")
        return os.path.expanduser(file)

    def get_cache_path(self):
        return os.path.expanduser(self.vim.eval("g:citation_vim_cache_path"))

    def get_searchkeys(self):
        searchkeys = self.vim.eval("l:searchkeys")
        if len(searchkeys) > 0:
            return searchkeys.split()
        return []

    def can_cache(self, searchkeys):
        if searchkeys == []:
            return True
        return False
