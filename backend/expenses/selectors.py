from finance.models import Expense


def expenses_for_business(business):
    return Expense.objects.filter(business=business, status=Expense.STATUS_APPROVED)


def expense_for_business(*, business, pk):
    return Expense.objects.filter(business=business, pk=pk).first()
