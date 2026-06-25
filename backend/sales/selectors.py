from sales.models import Sale, SaleLine


def sales_for_business(business):
    return Sale.objects.filter(business=business, status=Sale.STATUS_COMPLETED)


def sale_lines_for_business(business):
    return SaleLine.objects.filter(sale__business=business, sale__status=Sale.STATUS_COMPLETED).select_related('sale', 'inventory_item')


def sale_for_business(*, business, pk):
    return Sale.objects.filter(business=business, pk=pk).first()
