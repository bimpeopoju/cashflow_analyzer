from finance.models import CashEntry


def cash_entries_for_business(business):
    return CashEntry.objects.filter(business=business)
