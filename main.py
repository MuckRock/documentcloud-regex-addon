"""
This is an add-on to search a document for a regex and output all of the matches
"""

import csv
import re

from documentcloud.addon import AddOn


class Regex(AddOn):
    """ Uses re to find all regular expressions matches, 
        outputs the results in a CSV, optionally annotates the document. 
    """
    def main(self):
        """ Main functionality """
        if self.get_document_count() is None:
            self.set_message("Please select at least one document.")
            return
        regex = self.data["regex"]
        pattern = re.compile(regex)
        annotate = self.data['annotate']
        access_level = self.data['annotation_access']

        with open("matches.csv", "w+", encoding="utf-8") as file_:
            writer = csv.writer(file_)
            writer.writerow(["match", "url", "page_number"])

            for document in self.get_documents():
                for page_number in range(1, document.page_count + 1):
                    page_text = document.get_page_text(page_number)
                    matches = pattern.findall(page_text)
                    for match in matches:
                        writer.writerow([match, document.canonical_url, page_number])
                        if annotate:
                            document.annotations.create(
                                title=f"{match}", page_number=page_number-1, access=access_level
                            )

            self.upload_file(file_)


if __name__ == "__main__":
    Regex().main()
