{
    'name': 'OCA模块整合',
    'version': '12.0.1.0.0',
    'category': 'Inventory',
    'summary': "品牌管理、条码扫描出入库、退货单、销售订单定制",
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA',
    'license': 'AGPL-3',
    'depends': [
        'stock', 'sale_management', 'purchase', 'crm', 'mrp', 'account_accountant', 'stock_barcode'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/price_security.xml',
        'views/views.xml',
        'reports/sale_report_view.xml',
        'reports/account_invoice_report_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True
}

