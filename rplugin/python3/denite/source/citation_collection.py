from os.path import dirname
from .citation import Source as Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'citation_collection'
        self.description = "search citation collection"
        self.kind = 'command'

    def gather_candidates(self, context):
        """
        Returns an array of collections.
        """
        candidates = {}
        collections = {}
        for item in self._get_items(context):
            for col in item.collections:
                if not col in collections:
                    collections[col] = col

                    candidates.append({
                        "word": col,
                        "action__command": self._set_col(col),
                        # "action__type": ": ",
                        "action__text": col,
                        "action__path": col,
                        "action__directory": dirname(col),
                    })
        return candidates

    def _set_collection(self, collection):
        return "call denite#custom#var('citation', 'collection', '{}')".format(collection)
