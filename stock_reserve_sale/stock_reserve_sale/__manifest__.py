{
    'name': 'Stock Reserve Sales',
    'version': '12.0.0.1',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'images': [],
    'website': "http://www.camptocamp.com",
    'depends': ['sale_stock',
                'stock_reserve',
                ],
    'demo': [],
    'data': ['wizard/sale_stock_reserve_view.xml',
             'view/sale.xml',
             'view/stock_reserve.xml',
             ],
    'auto_install': False,
}
