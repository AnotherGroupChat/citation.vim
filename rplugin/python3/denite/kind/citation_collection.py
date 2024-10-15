import os
import subprocess
from denite.kind.file import Kind as File
from denite.kind.word import Kind as Word
from denite.kind.openable import Kind as Openable


def eprint(*args, **kwargs):
    message = " ".join(map(str, args))
    raise Exception(message)


class Kind(Word, File, Openable):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = "citation_collection"
        self.default_action = "append"
        self.vim = vim

    def action_append(self, context):
        count = 0
        targets = [target for target in context["targets"] if target["nick"]]
        for target in targets:
            count += 1
            if count == 1:
                target["action__text"] = "\cite{" + target["action__text"]
            if count == len(targets):
                target["action__text"] += "}"
            else:
                target["action__text"] += ", "
            Word.action_append(self, {"targets": [target]})

    def action_preview(self, context):
        for target in context["targets"]:
            path = target["action__path"].replace("-", "_")
            if not os.path.exists(path):
                with open(target["review_directory"] + "review.template") as f:
                    template = f.read().replace("Paper", target["title"])
                with open(path, "w") as f:
                    f.write(template)
        super().action_preview(context)

    def action_open(self, context):
        for target in context["targets"]:
            path = target["action__path"].replace("-", "_")
            path = path.replace(".md", ".pdf")
            path = path.replace("/reviews/", "/literature/")
            if os.path.exists(path):
                try:
                    subprocess.run(["xdg-open", path], check=True)
                except subprocess.CalledProcessError:
                    eprint(f"Failed to open {path}")
                return
        eprint(f"Could not find {path}")
