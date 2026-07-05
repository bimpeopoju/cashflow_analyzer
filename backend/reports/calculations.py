from cashflow.calculations import capital_summary_for_business
from businesses.services import money
from inventory.serializers import inventory_payload
from taxes.summary import tax_summary_for_business


def dashboard_for_business(*, business, sales, expenses, inventory, sale_lines=None, cash_entries=None):
    dashboard = capital_summary_for_business(
        business=business,
        sales=sales,
        expenses=expenses,
        sale_lines=sale_lines,
        cash_entries=cash_entries,
        inventory=inventory,
    )

    recent = [
        {
            'id': f'sale-{sale.id}',
            'kind': 'sale',
            'label': sale.item_name,
            'amount': money(sale.amount),
            'createdAt': sale.sold_at.isoformat(),
        }
        for sale in sales[:5]
    ] + [
        {
            'id': f'expense-{expense.id}',
            'kind': 'expense',
            'label': expense.category,
            'amount': money(expense.amount),
            'createdAt': expense.spent_at.isoformat(),
        }
        for expense in expenses[:5]
    ]
    recent.sort(key=lambda item: item['createdAt'], reverse=True)

    low_stock = [
        inventory_payload(item)
        for item in inventory
        if item.quantity <= item.reorder_level
    ][:5]

    dashboard['recentActivity'] = [
        {
            'id': item['id'],
            'kind': item['kind'],
            'label': item['label'],
            'amount': item['amount'],
            'createdAt': item['createdAt'],
        }
        for item in recent[:6]
    ]
    dashboard['lowStock'] = low_stock
    dashboard['taxSummary'] = tax_summary_for_business(
        business=business,
        sales=sales,
        expenses=expenses,
        sale_lines=sale_lines,
    )
    return dashboard
