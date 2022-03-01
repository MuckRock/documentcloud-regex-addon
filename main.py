"""
This is an add-on to search a document for a regex and output all of the matches
"""

import json
import re

from addon import AddOn


class Regex(AddOn):

    def main(self):
        regex = self.data["regex"]
        pattern = re.compile(regex)

        matches = {}

        for doc_id in self.documents:
            document = self.client.documents.get(doc_id)
            matches[doc_id] = pattern.findall(document.full_text)

        with open("matches.json", "w+") as file_:
            file_.write(json.dumps(matches, indent=4))
            self.upload_file(file_)

if __name__ == "__main__":
    Regex().main()
