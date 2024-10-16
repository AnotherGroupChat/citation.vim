# -*- coding: utf-8 -*-
import sys
import re
from pybtex.database.input import bibtex
from citation_vim.item import Item
from citation_vim.utils import check_path, raiseError


class BibtexParser(object):
    def __init__(self, context):
        self.context = context
        if not check_path(self.context["bibtex_file"]):
            raiseError("{} does not exist".format(self.context["bibtex_file"]))
            return []

    def load(self):
        """
        Returns: A bibtex file as an array of standardised Items.
        """
        bib_data = self._read_file(self.context["bibtex_file"])
        return self.build_items(bib_data)

    def build_items(self, bib_data):
        items = []
        for key in bib_data.entries:
            item = Item()
            item.collections = []
            bib_entry = bib_data.entries[key]
            authors = self.parse_authors(bib_entry)
            item.author = self.format_author(authors)
            item.type = bib_entry.type
            item.abstract = self.get_field(bib_entry, "abstract")
            item.doi = self.get_field(bib_entry, "doi")
            item.isbn = self.get_field(bib_entry, "isbn")
            item.publication = self.get_field(bib_entry, "journal")
            item.language = self.get_field_from(bib_entry, ["language", "langid"])
            item.issue = self.get_field(bib_entry, "number")
            item.notes = self.get_field_from(bib_entry, ["annotation", "annote"])
            item.pages = self.get_field(bib_entry, "pages")
            item.publisher = self.get_field_from(
                bib_entry, ["publisher", "school", "institution"]
            )
            item.tags = self.get_field_from(bib_entry, ["keyword", "keywords"])
            item.title = self.get_field(bib_entry, "title")
            item.volume = self.get_field(bib_entry, "volume")
            item.date = self.format_date(bib_entry)
            item.url = self.format_url(bib_entry)
            item.file = self.format_file(bib_entry)
            item.nick = self.get_field(bib_entry, "key")
            item.key = key
            item.combine()
            items.append(item)
        return items

    def _read_file(self, filename):
        """
        Returns: A bibtex file from the pybtex parser
        """
        parser = bibtex.Parser()
        return parser.parse_file(filename)

    def strip_braces(self, string):
        """
        Returns: string stripped of {} braces.
        """
        return string.replace("{", "").replace("}", "")

    def get_field(self, bib_entry, field):
        """
        Returns cleaned field value for any bibtex field.
        """
        output = bib_entry.fields[field] if field in bib_entry.fields else ""
        return self.strip_braces(output)

    def get_field_from(self, bib_entry, fields):
        output = ""
        for field in fields:
            if field in bib_entry.fields:
                output = bib_entry.fields[field]
                break
        return self.strip_braces(output)

    def parse_authors(self, bib_entry):
        """
        Returns: Array of authors
        """
        try:
            persons = bib_entry.persons["author"]
            if sys.version_info[0] == 2:
                authors = [str(au).split(",") for au in persons]
            elif sys.version_info[0] == 3:
                authors = [str(au).split(",") for au in persons]
        except KeyError:
            authors = []
        return authors

    def format_author(self, authors):
        """
        Returns: Authors - format depending on et_al_limit.
        """
        if authors == []:
            return ""
        if len(authors) > self.context["et_al_limit"]:
            return "%s et al." % authors[0][0]
        if len(authors) > 2:
            auth_string = ""
            for author in authors[:-1]:
                auth_string += author[0] + ", "
            return auth_string + "& " + authors[-1][0]
        if len(authors) == 2:
            return authors[0][0] + " & " + authors[1][0]
        return ", ".join(authors[0])

    def format_file(self, bib_entry):
        """
        Returns: Attachment file path
        """
        attachment = ""
        if "file" in bib_entry.fields:
            for file in bib_entry.fields["file"].split(";"):
                details = file.split(":")
                if 2 < len(details) and details[2] == "application/pdf":
                    attachment = details[1]
                    break
        return attachment

    def format_url(self, bib_entry):
        """
        Returns: Url string
        """
        url = ""
        if "url" in bib_entry.fields:
            url = bib_entry.fields["url"]
        elif "file" in bib_entry.fields:
            for file in bib_entry.fields["file"].split(";"):
                details = file.split(":")
                if 2 < len(details) and details[2] != "application/pdf":
                    url = details[1]
                    break
        return url

    def format_tags(bib_entry):
        """
        Returns: Tags/keywords string
        """
        tags = ""
        if "keywords" in bib_entry.fields:
            tags = ", ".join(bib_entry.fields["keywords"])
        return tags

    def format_date(self, bib_entry):
        output = ""
        if "year" in bib_entry.fields:
            output = self.strip_braces(bib_entry.fields["year"])
        elif "date" in bib_entry.fields:
            date = self.strip_braces(bib_entry.fields["date"])
            for split in re.split(" |-|/", date):
                if len(split) == 4 and split.isdigit():
                    output = split
                    break
        return output
