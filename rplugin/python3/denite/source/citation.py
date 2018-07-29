import sys
from os.path import abspath, join, pardir
from .base import Base

sys.path.append(
    abspath(join(__file__, pardir, pardir, pardir, pardir, pardir, 'python')))
from citation_vim.utils import read_cache, write_cache, is_current, raiseError
from citation_vim.item import Item

sub_sources = [
    "abstract",
    "author",
    "collection",
    "combined",
    "date",
    "doi",
    "duplicate_keys",
    "file",
    "isbn",
    "publication",
    "key",
    "key_inner",
    "language",
    "issue",
    "notes",
    "pages",
    "publisher",
    "tags",
    "title",
    "type",
    "url",
    "volume",
    "zotero_key"
]

key_title_banned_regex = r"\b(a|an|the|some|from|on|in|to|of|do|with|der|die|das|ein|eine|einer|eines|einem|einen|un|une|la|le|l|el|las|los|al|uno|una|unos|unas|de|des|del|d)\W"
key_clean_regex = "[^A-Za-z0-9\!\$\&\*\+\-\.\/\:\;\<\>\?\[\]\^\_\`\|]+"


class Source(Base):
    """ Zotero/Bibtex source for Denite.nvim """

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'citation'
        self.kind = 'citation'
        self.matchers = ['matcher_fuzzy']
        self.is_public_context = True

        self.sub_sources = sub_sources
        self.__cache = False
        self.__cache_file = None

        self.vars = {
            'cache_path': "",
            'mode': 'zotero',
            'zotero_version': 5,
            'zotero_path': '~/Zotero',
            'zotero_attachment_path': '~/Zotero/library',
            'collection': "",
            'bibtex_file': "",
            'reverse_order': True,
            'et_al_limit': 5,
            'key_clean_regex': key_clean_regex,
            'key_title_banned_regex': key_title_banned_regex,
            'key_format': "",
            'key_outer_prefix': '[',
            'key_inner_prefix': '@',
            'key_suffix': ']',
            'desc_format': '{}∶ {} ‴{}‴ ₋{}₋ ₍{}₎',
            'desc_fields': ["type", "key", "title", "author", "date"],
            'wrap_chars': '||',
            'highlight_dash': "‾⁻−₋‐⋯┄–—―∼┈─▭▬┉━┅₌⁼‗",
            'highlight_bar': "‖│┃┆∥┇┊┋",
            'highlight_bracket': "⊂〔₍⁽⊃〕₎⁾",
            'highlight_arrow': "◀◁<‹▶▷>›",
            'highlight_colon': "∶∷→⇒≫",
            'highlight_blob': "♯♡◆◇◊○◎●◐◑∗∙⊙⊚⌂★☺☻▪■□▢▣▤▥▦▧▨▩",
            'highlight_tiny': "、。‸₊⁺∘♢☆☜☞♢☼",
            'highlight_text': "″‴‶‷",
        }

    def on_init(self, context):
        if len(context['args']) >= 1:
            context['__source'] = 'source_field'
            context['__field'] = context['args'].pop(0)

            # Set mode; zotero or bibtex
            self._set_mode(context)
        else:
            context['__source'] = 'sub_sources'

    def gather_candidates(self, context):
        if context['__source'] is 'sub_sources':
            return self._gather_sub_sources()
        else:
            return self._gather_items(context)

    def _set_mode(self, context):
        if self.vars['mode'] == "bibtex" and self.vars['bibtex_file']:
            self._enable_cache(context)
        elif self.vars['mode'] == "zotero" and self.vars['zotero_path']:
            if len(context['args']) > 0:
                context['__searchkeys'] = context['args'].pop(0)
                self.__cache = False
            else:
                context['__searchkeys'] = []
                self._enable_cache(context)
        else:
            raiseError("'mode' must be set to 'zotero' or 'bibtex'")

    def _enable_cache(self, context):
        self.__cache = True
        self.__cache_file = join(self.vars['cache_path'], "citation_vim_cache")

    def _gather_sub_sources(self):
        # Generate candidates and return it
        candidates = []
        for sub_source in self.sub_sources:
            candidates.append({
                "word": sub_source,
                "action__command": self._set_sub_source(sub_source),
            })
        return candidates

    def _set_sub_source(self, sub_source):
        return ':Denite citation:{}'.format(sub_source)

    def _gather_items(self, context):
        candidates = []

        if context['__field'] is 'duplicate_keys':
            items = self._get_duplicate_key(context)
        else:
            items = self._get_items(context)

        if context['__field'] is 'key':
            text = (self.vars['key_outer_prefix']
                    + self.vars['key_inner_prefix']
                    + '{}'
                    + self.vars['key_suffix'])
        elif context['__field'] is 'key_inner':
            text = self.vars['key_inner_prefix'] + '{}'
        else:
            text = '{}'

        if context['__field'] is 'url':
            file_url = 'url'
        else:
            file_url = 'file'

        # Update vars with source field
        self.vars['source_field'] = context['__field']

        # Retirn items
        for item in items:
            if (not self.vars['collection']
                    or self.vars['collection'] in item.collections):
                candidate = {
                    "word": item.describe(self.vars),
                    "action__text": text.format(getattr(item, context['__field'])),
                    "action__path": getattr(item, file_url),
                    "action__command": self._set_message(item.combined),
                }
                candidates.append(candidate)
        return candidates

    def _set_message(self, message):
        return "echo {}".format(message)

    def _get_duplicate_keys(self, context):
        """
        Returns an array of collections.
        """
        self.vars['collection'] = ""
        context['__field'] = 'key'
        self.__cache = False

        # Get items
        items = self._get_items(context)

        # Filter itesm for duplicate keys
        items.sort(key=lambda item: item.key)
        last_item = Item()
        last_item.key = ""
        filtered_items = []
        for item in items:
            if last_item.key == item.key:
                filtered_items.append(item)
            last_item = item
        return filtered_items

    def _get_items(self, context):
        """
        Returns items from cache or parser
        """
        if self.__cache and self._is_cached():
            return read_cache(self.__cache_file)
        parser = self._get_parser()
        items = parser.load()
        if context['__reverse_order']:
            items.reverse()
        if self.__cache:
            write_cache(self.__cache_file, items)
        return items

    def _get_parser(self):
        """
        Returns a bibtex or zotero parser.
        """
        if self.vars['mode'] == "bibtex":
            from citation_vim.bibtex.parser import BibtexParser
            parser = BibtexParser(self.vars)
        elif self.vars['mode'] == "zotero":
            from citation_vim.zotero.parser import ZoteroParser
            parser = ZoteroParser(self.vars)
        return parser

    def _is_cached(self):
        """
        Returns boolean based on cache and target file dates
        """
        if self.vars['mode'] == 'bibtex':
            file_path = self.vars['bibtex_file']
        elif self.vars['mode'] == 'zotero':
            zotero_database = join(self.vars['zotero_path'], "zotero.sqlite")
            file_path = zotero_database
        return is_current(file_path, self.__cache_file)
