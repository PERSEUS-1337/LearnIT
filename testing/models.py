import json


class Extracted:
    def __init__(self, title: str, content: str):
        self.title = (
            title if title else ""
        )  # Set title to empty string if None or empty
        self.content = content

    def to_dict(self):
        return {"title": self.title, "content": self.content}

    def __str__(self):
        return f"Title: {self.title}\nContent: {self.content}"


class ExtractedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Extracted):
            return obj.to_dict()
        return super().default(obj)


class Document:
    def __init__(self, id: str, title: str, reference: str = "", summary: str = ""):
        self.id = id
        self.title = title if title else ""
        self.reference = Extracted(title, reference) if reference else Extracted("", "")
        self.summary = Extracted(title, summary) if summary else Extracted("", "")

    def __str__(self):
        return f"ID: {self.id}\nTitle: {self.title}\nReference: {self.reference}\nSummary: {self.summary}"



# Example usage:
document = Document(
    "93-792",
    "",
    "Section 202 of the Social Security Act states that benefits are paid through the month before the month in which a beneficiary dies.",
    "Social Security benefits are not paid for the month in which a beneficiary dies. In most cases, the check that an individual receives in a given month represents payment for the preceding month.",
)
print(document)
