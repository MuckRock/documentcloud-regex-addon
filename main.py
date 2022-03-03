"""
This is an add-on to search a document for a regex and output all of the matches
"""

import csv
import re

from documentcloud.addon import AddOn


class Regex(AddOn):
    def main(self):
        regex = self.data["regex"]
        pattern = re.compile(regex)

        with open("matches.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(["match", "url"])

            for doc_id in self.documents:
                document = self.client.documents.get(doc_id)
                writer.writerows(
                    [m, document.canonical_url]
                    for m in pattern.findall(document.full_text)
                )

            self.upload_file(file_)


if __name__ == "__main__":
    Regex().main()
