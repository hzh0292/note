import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import functools
import xmlrpc.client
from tornado.options import define, options

HOST = '13.231.137.58'
PORT = 8069
DB = 'demo'
USER = 'admin'
PASS = 'admin'
ROOT = 'http://%s:%d/xmlrpc/' % (HOST, PORT)
uid = xmlrpc.client.ServerProxy(ROOT + 'common').login(DB, USER, PASS)
call = functools.partial(xmlrpc.client.ServerProxy(ROOT + 'object').execute, DB, uid, PASS)

define("port", type=int, default=9000)


def trans_timezone(lst, key):
    # 此函数转化一个列表中的各元素(字典)的时间字符串字段为北京时间不含时分秒日期字符串
    from datetime import datetime, timedelta
    for item in lst:
        item[key] = (
                datetime.strptime(item[key], '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime(
            '%Y-%m-%d')
    return None


class SerialApiHandler(tornado.web.RequestHandler):
    def get(self):
        serial = self.get_argument('serial', None)
        args = [('name', '=', serial)]
        fields = ['product_id',  # 产品
                  'purchase_order_ids',  # 采购单
                  'sale_order_ids'  # 销售单
                  ]
        item = call('stock.production.lot', 'search_read', args, fields)
        if item:
            item = item[0]
            product = call('product.product', 'search_read', [('id', '=', item['product_id'][0])],
                           ['categ_id',  # 类别
                            'list_price',  # 价格
                            'qty_available',  # 可用数量
                            'stock_move_ids',  # 库存移动
                            'uom_id',  # 单位
                            'image'  # 图片
                            ])[0]
            location = call('stock.move', 'search_read', [('id', '=', max(product['stock_move_ids']))],
                            ['date',  # 时间
                             'location_id',  # 源位置
                             'location_dest_id',  # 目的位置
                             'partner_id'  # 客户
                             ])[0]
            self.write(dict(
                name=item['product_id'][1],
                categ=product['categ_id'][1],
                price=product['list_price'],
                uom=product['uom_id'][1],
                src_location=location['location_id'][1],
                dest_location=location['location_dest_id'][1],
                partner=location['partner_id'][1] if location['partner_id'] else None,
                image=product['image']
            ))
        else:
            self.write({'name': '未查找到此序列号对应的产品！'})


class SaleApiHandler(tornado.web.RequestHandler):
    def get(self):
        sale_order = self.get_argument('order', None)
        order = call('sale.order', 'search_read', [('name', '=', sale_order)],
                     ['state',  # 状态(draft, sale, ...)
                      'partner_id',  # 客户
                      'amount_total',  # 总价
                      'order_line',  # 明细行
                      'team_id',  # 销售团队
                      'picking_ids'  # 出货单
                      ])
        if order:
            order = order[0]
            order['picking_ids'] = call('stock.picking', 'read', order['picking_ids'],
                                        ['name',  # 出货单号
                                         'location_id',  # 源位置
                                         'location_dest_id',  # 目的位置
                                         'move_lines',  # 库存移动明细行
                                         ])

            for move in order['picking_ids']:
                move['move_lines'] = call('stock.move', 'read', move['move_lines'],
                                          ['product_id',  # 产品
                                           'product_uom_qty',  # 数量
                                           'product_uom',  # 单位
                                           'quantity_done',  # 完成数量
                                           'state',  # 状态(assigned, done, ...)
                                           ])
            order['order_line'] = call('sale.order.line', 'read', order['order_line'],
                                       ['name',  # 名称(产品)
                                        'price_unit',  # 单价
                                        'product_uom_qty',  # 数量
                                        'product_uom',  # 单位
                                        'price_subtotal',  # 总价
                                        'product_image',  # 图片
                                        ])
            self.write(order)
        else:
            self.write({'state': '未查找到此订单号，请检查！'})


class PickingOrderHandler(tornado.web.RequestHandler):
    def get(self):
        pickingOrder = self.get_argument('order', None)
        item = call('stock.picking', 'search_read', [('name', '=', pickingOrder)],
                    ['backorder_id',  # 欠谁的单
                     'backorder_ids',  # 有哪些欠单
                     'location_id',  # 源位置[1]
                     'location_dest_id',  # 目的位置[1]
                     'move_lines',  # 明细行
                     'name',  # 单号
                     'origin',  # 源单据
                     'partner_id',  # 合作伙伴[1]
                     'product_id',  # 产品[1]
                     'sale_id',  # 销售订单[1]
                     'status',  # 状态
                     'purchase_id'  # 采购订单[1]
                     ])
        if item:
            item = item[0]
            if item['backorder_id']:
                item['backorder_id'] = call('stock.picking', 'read', item['backorder_id'][0],
                                            ['location_id',  # 源位置
                                             'location_dest_id',  # 目的位置
                                             'move_lines',  # 明细行
                                             'name',  # 单号
                                             ])[0]

                item['backorder_id']['move_lines'] = call('stock.move', 'read', item['backorder_id']['move_lines'],
                                                          ['product_id',  # 产品
                                                           'product_uom_qty',  # 数量
                                                           'product_uom',  # 单位
                                                           'quantity_done',  # 完成数量
                                                           'state',  # 状态(assigned, done, ...)
                                                           ])
            item['backorder_ids'] = call('stock.picking', 'read', item['backorder_ids'],
                                         ['location_id',  # 源位置[1]
                                          'location_dest_id',  # 目的位置[1]
                                          'move_lines',  # 明细行
                                          'name',  # 单号
                                          'product_id'  # 产品[1]
                                          ])
            for k in item['backorder_ids']:
                k['move_lines'] = call('stock.move', 'read', k['move_lines'],
                                       ['product_id',  # 产品
                                        'product_uom_qty',  # 数量
                                        'product_uom',  # 单位
                                        'quantity_done',  # 完成数量
                                        'state',  # 状态(assigned, done, ...)
                                        ])

            if item['sale_id']:
                item['sale_id'] = call('sale.order', 'read', item['sale_id'][0],
                                       ['state',  # 状态(draft, sale, ...)
                                        'amount_total',  # 总价
                                        'order_line',  # 明细行
                                        'team_id',  # 销售团队
                                        ])[0]
                item['sale_id']['order_line'] = call('sale.order.line', 'read', item['sale_id']['order_line'],
                                                     ['name',  # 名称(产品)
                                                      'price_unit',  # 单价
                                                      'product_uom_qty',  # 数量
                                                      'product_uom',  # 单位
                                                      'price_subtotal',  # 总价
                                                      'product_image',  # 图片
                                                      ])
            if item['purchase_id']:
                item['purchase_id'] = call('purchase.order', 'read', item['purchase_id'][0],
                                           ['state',  # 状态
                                            'order_line',  # 明细行
                                            ])[0]
                item['purchase_id']['order_line'] = call('purchase.order.line', 'read',
                                                         item['purchase_id']['order_line'],
                                                         ['name',  # 名称(产品)
                                                          'product_uom_qty',  # 数量
                                                          'product_uom',  # 单位
                                                          'price_subtotal',  # 总价
                                                          'product_image',  # 图片
                                                          ])
            self.write(item)
        else:
            self.write({'origin': '未查找到此单号，请检查！'})


class PurchaseOrderHandler(tornado.web.RequestHandler):
    def get(self):
        purchase_order = self.get_argument('order', None)
        args = [('name', '=', purchase_order)]
        fields = ['name',  # 单号
                  'amount_total',  # 采购总额
                  'order_line',  # 订单明细
                  'origin',  # 源单据
                  'partner_id',  # 供应商
                  'state'  # 状态
                  ]
        item = call('purchase.order', 'search_read', args, fields)
        if item:
            item = item[0]
            line_fields = ['name',  # 名称(产品)
                           'product_image',  # 产品图片
                           'product_uom',  # 单位
                           'product_uom_qty',  # 数量
                           'date_planned'  # 计划日期
                           ]
            item['order_line'] = call('purchase.order.line', 'read', item['order_line'], line_fields)
            trans_timezone(item['order_line'], 'date_planned')
            self.write(item)
        else:
            self.write({'status': '未查找到此单号，请检查！'})


class StockInHandler(tornado.web.RequestHandler):
    def get(self):
        pickings = call('stock.picking', 'search_read', [('picking_type_code', '=', 'incoming')],
                        ['name',  # 单号
                         'origin',  # 源单据
                         'state',  # 状态
                         'scheduled_date',  # 计划日期
                         'move_lines',  # 明细行
                         'partner_id',  # 供应商
                         ])
        trans_timezone(pickings, 'scheduled_date')
        for item in pickings:
            item['move_lines'] = call('stock.move', 'read', item['move_lines'],
                                      ['product_id',  # 产品
                                       'product_uom_qty',  # 数量
                                       'product_uom',  # 单位
                                       'quantity_done',  # 完成数量
                                       'state',  # 状态(assigned, done, ...)
                                       ])
        self.write(dict(
            type='倉庫收貨單匯總',
            detail=pickings
        ))

    def post(self):
        move_id = self.get_body_argument('move', None)
        product_id = self.get_body_argument('product', None)
        move_count = self.get_body_argument('count', None)
        self.write(dict(
            move_id=move_id,
            product_id=product_id,
            move_count=move_count
        ))


urls = [
    (r"/", SerialApiHandler),
    (r"/sale", SaleApiHandler),
    (r"/picking", PickingOrderHandler),
    (r"/purchase", PurchaseOrderHandler),
    (r"/in", StockInHandler)
]

configs = dict(
    debug=True
)


class CustomApplication(tornado.web.Application):
    def __init__(self, urls, configs):
        handlers = urls
        settings = configs
        super(CustomApplication, self).__init__(handlers=handlers, **settings)


def create_app():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(CustomApplication(urls, configs))
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


app = create_app()

if __name__ == "__main__":
    app()
