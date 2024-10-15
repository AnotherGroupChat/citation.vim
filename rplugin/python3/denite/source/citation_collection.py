import sys
from os.path import abspath, join, pardir
from denite.base.source import Base


sys.path.append(
    abspath(join(__file__, pardir, pardir, pardir, pardir, pardir, "python"))
)
from citation_vim.utils import read_cache, write_cache, is_current
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
    "zotero_key",
]

key_title_banned_regex = r"\b(a|an|the|some|from|on|in|to|of|do|with|der|die|das|ein|eine|einer|eines|einem|einen|un|une|la|le|l|el|las|los|al|uno|una|unos|unas|de|des|del|d)\W"
key_clean_regex = "[^A-Za-z0-9\!\$\&\*\+\-\.\/\:\;\<\>\?\[\]\^\_\`\|]+"


class Source(Base):
    """Zotero/Bibtex source for Denite.nvim"""

    def __init__(self, vim):
        super().__init__(vim)

        self.name = "citation_collection"
        self.description = "search citation collection"
        self.kind = "citation_collection"

        self.matchers = ["matcher_fuzzy"]
        self.is_public_context = True

        self.sub_sources = sub_sources
        self.__cache = False
        self.__cache_file = None
        self._parser = None

        self.vars = {
            "cache_path": "",
            "mode": "bibtex",
            "collection": "",
            "bibtex_file": "bibtex.bib",
            "reverse_order": True,
            "et_al_limit": 5,
            "key_clean_regex": key_clean_regex,
            "key_title_banned_regex": key_title_banned_regex,
            "key_format": "",
            "key_outer_prefix": "[",
            "key_inner_prefix": "@",
            "key_suffix": "]",
            "desc_format": "{}∶ {} ‴{}‴ ₋{}₋ ₍{}₎",
            "desc_fields": ["type", "key", "title", "author", "date"],
            "wrap_chars": "||",
            "highlight_dash": "‾⁻−₋‐⋯┄–—―∼┈─▭▬┉━┅₌⁼‗",
            "highlight_bar": "‖│┃┆∥┇┊┋",
            "highlight_bracket": "⊂〔₍⁽⊃〕₎⁾",
            "highlight_arrow": "◀◁<‹▶▷>›",
            "highlight_colon": "∶∷→⇒≫",
            "highlight_blob": "♯♡◆◇◊○◎●◐◑∗∙⊙⊚⌂★☺☻▪■□▢▣▤▥▦▧▨▩",
            "highlight_tiny": "、。‸₊⁺∘♢☆☜☞♢☼",
            "highlight_text": "″‴‶‷",
            "searchkeys": [],
            "review_directory": "",
        }

    def on_init(self, context):
        if len(context["args"]) >= 1:
            context["__source"] = "source_field"
            context["__field"] = context["args"].pop(0)
            self._set_mode(context)
        else:
            context["__source"] = "sub_sources"

        from citation_vim.context_loader import ContextLoader

        self.vars.update(ContextLoader(self.vim).context)
        self.__cache_file = join(self.vars["cache_path"], "citation_vim_cache")

    def _set_mode(self, context):
        """Set up bibtex or zotero mode"""
        # Enable cache
        self._enable_cache()
        # Get parser
        from citation_vim.bibtex.parser import BibtexParser

        self._parser = BibtexParser(self.vars)

    def _enable_cache(self):
        self.__cache = True
        self.__cache_file = join(self.vars["cache_path"], "citation_vim_cache")

    def _get_searchkeys(self, context):
        if len(context["args"]) > 0:
            self.vars["searchkeys"] = context["args"].pop(0)
            self.__cache = False
        else:
            self.vars["searchkeys"] = []
            self._enable_cache()

    def _gather_sub_sources(self):
        # Generate candidates and return it
        candidates = []
        for sub_source in self.sub_sources:
            candidates.append(
                {
                    "word": sub_source,
                    "action__source_field": sub_source,
                }
            )
        return candidates

    def _gather_items(self, context):
        candidates = []

        if context["__field"] == "duplicate_keys":
            items = self._get_duplicate_key(context)
        else:
            items = self._get_items(context)

        if context["__field"] == "key":
            text = (
                self.vars["key_outer_prefix"]
                + self.vars["key_inner_prefix"]
                + "{}"
                + self.vars["key_suffix"]
            )
        elif context["__field"] == "key_inner":
            text = self.vars["key_inner_prefix"] + "{}"
        else:
            text = "{}"

        if context["__field"] == "url":
            file_url = "url"
        else:
            file_url = "file"

        # Update vars with source field
        self.vars["source_field"] = context["__field"]

        # Retirn items
        for item in items:
            if (
                not self.vars["collection"]
                or self.vars["collection"] in item.collections
            ):
                candidate = {
                    "word": item.describe(self.vars),
                    "action__text": text.format(getattr(item, context["__field"])),
                    "action__path": getattr(item, file_url).replace("-", "_"),
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
        self.vars["collection"] = ""
        context["__field"] = "key"
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
        if self._parser is None:
            self._set_mode(context)
        items = self._parser.load()
        if self.vars["reverse_order"]:
            items.reverse()
        if self.__cache:
            write_cache(self.__cache_file, items)
        return items

    def _is_cached(self):
        """
        Returns boolean based on cache and target file dates
        """
        file_path = self.vars["bibtex_file"]
        return is_current(file_path, self.__cache_file)

    def gather_candidates(self, context):
        """
        Returns an array of collections.
        """
        candidates = []
        for item in self._get_items(context):
            candidates.append(
                {
                    "word": f"[@{item.key}] | {item.nick} | {item.title}",
                    "title": f"{item.title}",
                    "nick": f"{item.nick}",
                    "action__text": item.key,
                    "action__path": self.vars["review_directory"]
                    + f"{item.nick or item.key}.md".replace("-", "_"),
                    "review_directory": self.vars["review_directory"],
                }
            )
        return candidates

    def _set_collection(self, collection):
        return "call denite#custom#var('citation', 'collection', '{}')".format(
            collection
        )


__all__ = ["Source"]
