# rpc远程调用查询，通过get提交产品序列号/订单号，查询产品/订单的详细信息
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


class SerialApiHandler(tornado.web.RequestHandler):
    def get(self):
        serial = self.get_argument('serial', None)
        item = call('stock.production.lot', 'search_read', [('name', '=', serial)],
                    ['product_id',  # 产品
                     'purchase_order_ids',  # 采购单
                     'sale_order_ids'  # 销售单
                     ])
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
        saleOrder = self.get_argument('order', None)
        order = call('sale.order', 'search_read', [('name', '=', saleOrder)],
                     ['state',  # 状态(draft, sale, ...)
                      'partner_id',  # 客户
                      'amount_total',  # 总价
                      'order_line',  # 明细行
                      'team_id',  # 销售团队
                      'picking_ids'  # 出货单
                      ])
        if order:
            order = order[0]
            pickings = []
            for picking_id in order['picking_ids']:
                picking = call('stock.picking', 'search_read', [('id', '=', picking_id)],
                               ['name',  # 出货单号
                                'location_id',  # 源位置
                                'location_dest_id',  # 目的位置
                                'move_line_ids',  # 库存移动明细行
                                ])[0]

                move_lines = []
                for move_line_id in picking['move_line_ids']:
                    move_line = call('stock.move.line', 'search_read', [('id', '=', move_line_id)],
                                     ['product_id',  # 产品
                                      'product_qty',  # 数量
                                      'product_uom_id',  # 单位
                                      'qty_done',  # 完成数量
                                      'lot_id',  # 批次/序列号
                                      'state',  # 状态(assigned, done, ...)
                                      ])[0]
                    move_lines.append(move_line)
                picking['move_line_ids'] = move_lines
                pickings.append(picking)
            order['picking_ids'] = pickings

            lines = []
            for order_line_id in order['order_line']:
                line = call('sale.order.line', 'search_read', [('id', '=', order_line_id)],
                            ['name',  # 名称(产品)
                             'price_unit',  # 单价
                             'product_uom_qty',  # 数量
                             'product_uom',  # 单位
                             'price_subtotal',  # 总价
                             'product_image',  # 图片
                             ])[0]
                lines.append(line)
            order['order_line'] = lines
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
                     'move_line_ids',  # 明细行
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
            backorder_id = call('stock.picking', 'search_read', [('id', '=', item['backorder_id'][0])],
                                ['location_id',  # 源位置[1]
                                 'location_dest_id',  # 目的位置[1]
                                 'move_line_ids',  # 明细行
                                 'name',  # 单号
                                 ])[0] if item['backorder_id'] else []
            if backorder_id:
                move_line_ids_backorder_id = []
                for i in backorder_id['move_line_ids']:
                    move_line_ids_backorder_id.append(call('stock.move.line', 'search_read', [('id', '=', i)],
                                                           ['product_id',  # 产品
                                                            'product_qty',  # 数量
                                                            'product_uom_id',  # 单位
                                                            'qty_done',  # 完成数量
                                                            'lot_id',  # 批次/序列号
                                                            'state',  # 状态(assigned, done, ...)
                                                            ])[0])
                backorder_id['move_line_ids'] = move_line_ids_backorder_id
            backorder_ids = []
            for j in item['backorder_ids']:
                backorder_ids.append(call('stock.picking', 'search_read', [('id', '=', j)],
                                          ['location_id',  # 源位置[1]
                                           'location_dest_id',  # 目的位置[1]
                                           'move_line_ids',  # 明细行
                                           'name',  # 单号
                                           'product_id'  # 产品[1]
                                           ])[0])
            move_line_ids = []
            for k in item['move_line_ids']:
                move_line_ids.append(call('stock.move.line', 'search_read', [('id', '=', k)],
                                          ['product_id',  # 产品
                                           'product_qty',  # 数量
                                           'product_uom_id',  # 单位
                                           'qty_done',  # 完成数量
                                           'lot_id',  # 批次/序列号
                                           'state',  # 状态(assigned, done, ...)
                                           ])[0])
            sale_id = call('sale.order', 'search_read', [('id', '=', item['sale_id'][0])],
                           ['state',  # 状态(draft, sale, ...)
                            'partner_id',  # 客户
                            'amount_total',  # 总价
                            'order_line',  # 明细行
                            'team_id',  # 销售团队
                            'picking_ids'  # 出货单
                            ]) if item['sale_id'] else []
            if sale_id:
                sale_id = sale_id[0]
                lines = []
                for order_line_id in sale_id['order_line']:
                    lines.append(call('sale.order.line', 'search_read', [('id', '=', order_line_id)],
                                      ['name',  # 名称(产品)
                                       'price_unit',  # 单价
                                       'product_uom_qty',  # 数量
                                       'product_uom',  # 单位
                                       'price_subtotal',  # 总价
                                       'product_image',  # 图片
                                       ])[0])
                sale_id['order_line'] = lines

            purchase_id = call('purchase.order', 'search_read', [('id', '=', item['purchase_id'][0])],
                               ['state',  # 状态
                                'partner_id',  # 供应商
                                'amount_total',  # 总价
                                'order_line',  # 明细行
                                ]) if item['purchase_id'] else []
            if purchase_id:
                purchase_id = purchase_id[0]
                purchase_lines = []
                for purchase_line in purchase_id['order_line']:
                    purchase_lines.append(call('purchase.order.line', 'search_read', [('id', '=', purchase_line)],
                                               ['name',  # 名称(产品)
                                                'price_unit',  # 单价
                                                'product_uom_qty',  # 数量
                                                'product_uom',  # 单位
                                                'price_subtotal',  # 总价
                                                'product_image',  # 图片
                                                ])[0])
                purchase_id['order_line'] = purchase_lines

            item['backorder_id'] = backorder_id
            item['backorder_ids'] = backorder_ids
            item['move_line_ids'] = move_line_ids
            item['sale_id'] = sale_id
            item['purchase_id'] = purchase_id
            self.write(item)
        else:
            self.write({'status': '未查找到此单号，请检查！'})


class PurchaseOrderHandler(tornado.web.RequestHandler):
    def get(self):
        purchaseOrder = self.get_argument('order', None)
        item = call('purchase.order', 'search_read', [('name', '=', purchaseOrder)],
                    ['name',  # 单号
                     'amount_total',  # 采购总额
                     'order_line',  # 订单明细
                     'origin',  # 源单据
                     'partner_id',  # 供应商
                     'state'  # 状态
                     ])
        if item:
            item = item[0]
            order_line = []
            for i in item['order_line']:
                order_line.append(call('purchase.order.line', 'search_read', [('id', '=', i)],
                                       ['name',  # 名称(产品)
                                        'price_subtotal',  # 总价
                                        'price_unit',  # 单价
                                        'product_image',  # 产品图片
                                        'product_qty',  # 数量
                                        'date_planned'  # 计划日期
                                        ])[0])
            item['order_line'] = order_line
            self.write(item)
        else:
            self.write({'status': '未查找到此单号，请检查！'})


urls = [
    (r"/", SerialApiHandler),
    (r"/sale", SaleApiHandler),
    (r"/picking", PickingOrderHandler),
    (r"/purchase", PurchaseOrderHandler)
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
