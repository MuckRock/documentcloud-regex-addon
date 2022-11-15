"""
This is an add-on to search a document for a regex and output all of the matches
"""

import csv
import re

from documentcloud.addon import AddOn


class Regex(AddOn):
    def main(self):
        if not self.documents:
            self.set_message("Please select at least one document")
            return

        regex = self.data["regex"]
        pattern = re.compile(regex)

        with open("matches.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(["match", "url"])

            for document in self.client.documents.list(id__in=self.documents):

                if self.data.get("annotate"):
                    # Example code: I am only looking at the first page
                    # This should loop through all pages
                    url = (
                        document.asset_url + f"documents/{document.id}/pages/"
                        f"{document.slug}-p1.position.json"
                    )
                    # Should error check this
                    resp = self.client.get(url, full_url=True)
                    positions = resp.json()
                    print(positions[:3])
                    for info in positions:
                        # This will only match the regular expression against
                        # one word at a time - this can be altered as needed
                        if pattern.search(info["text"]):
                            document.annotations.create(
                                f"{regex} Match",
                                0,
                                x1=info["x1"],
                                y1=info["y1"],
                                x2=info["x2"],
                                y2=info["y2"],
                            )

                writer.writerows(
                    [m, document.canonical_url]
                    for m in pattern.findall(document.full_text)
                )

            self.upload_file(file_)


if __name__ == "__main__":
    Regex().main()
