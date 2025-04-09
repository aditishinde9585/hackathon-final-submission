# m1_model.py
def suggest_category(description):
    description = description.lower()
    if "food" in description or "restaurant" in description:
        return "Food"
    elif "uber" in description or "ola" in description:
        return "Transport"
    elif "rent" in description:
        return "Housing"
    elif "electricity" in description or "bill" in description:
        return "Utilities"
    else:
        return "Other"