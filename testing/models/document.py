class Document:
    def __init__(self, id: str, title: str, reference: str, summary: str):
        self.id = id
        self.title = title if title else ""
        self.reference = reference
        self.summary = summary

    def __str__(self):
        return f"ID: {self.id}\nTitle: {self.title}\nReference: {self.reference}\nSummary: {self.summary}"

# Example usage:
document = Document("93-792", "Social Security Benefits Are Not Paid for the Month of Death",
                    "Section 202 of the Social Security Act states that benefits are paid through the month before the month in which a beneficiary dies.", 
                    "Social Security benefits are not paid for the month in which a beneficiary dies. In most cases, the check that an individual receives in a given month represents payment for the preceding month.")
print(document)
