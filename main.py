""" DocumentCloud Add-On that finds regex matches in documents """
import csv
import re

from documentcloud.addon import AddOn
from documentcloud.exceptions import DoesNotExistError

class Regex(AddOn):
    """Uses re to find all regular expression matches,
    outputs the results in a CSV, optionally annotates the document.
    """

    def main(self):
        """Main functionality"""
        if self.get_document_count() is None:
            self.set_message("Please select at least one document.")
            return

        regex = self.data["regex"]
        annotate = self.data["annotate"]
        access_level = self.data["annotation_access"]
        key = self.data.get("key").strip()

        try:
            pattern = re.compile(regex)
        except re.error:
            self.set_message(f"Invalid regular expression provided: {regex}")
            return

        with open("matches.csv", "w+", encoding="utf-8") as file_:
            writer = csv.writer(file_)
            writer.writerow(["match", "url", "page_number"])

            for document in self.get_documents():
                try:
                    json_text = document.json_text
                    pages = json_text.get("pages", [])
                except (AttributeError, DoesNotExistError):
                    self.set_message(
                        f"Could not retrieve text for document with id {document.id}. "
                        "Please ensure the document has been OCRed."
                    )
                    continue

                matches_found = []

                for page in pages:
                    page_number = page["page"] + 1  # Convert to 1-based indexing
                    content = page.get("contents", "")
                    matches = pattern.findall(content)

                    for match in matches:
                        writer.writerow([match, document.canonical_url, page_number])
                        matches_found.append(match)

                        if annotate:
                            document.annotations.create(
                                title=f"{match}",
                                page_number=page_number - 1,
                                access=access_level,
                            )

                if matches_found:
                    if key in document.data:
                        document.data[key].extend(matches_found)
                    else:
                        document.data[key] = matches_found
                    document.save()

            self.upload_file(file_)

if __name__ == "__main__":
    Regex().main()
