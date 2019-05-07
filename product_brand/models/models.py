from datetime import timedelta

from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "产品品牌"
    _order = 'name'

    name = fields.Char('品牌名称', required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='品牌商',
        help='选择此品牌的所有者',
        ondelete='restrict'
    )
    logo = fields.Binary('品牌图标')
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='品牌的产品数量',
        compute='_compute_products_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _compute_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='品牌',
        help='为这个产品选择一个品牌'
    )
    a2_name = fields.Char(string='A2 Name')
    last_purchase_date = fields.Date(string='Last Purchase Date')
    bill_of_materials = fields.Boolean(string='Bill of Materials')
    substitutes_exist = fields.Boolean(string='Substitutes Exist')
    cost_is_adjusted = fields.Boolean(string='Cost is Adjusted')
    series_name = fields.Char(string='Series Name')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    returned_ids = fields.Many2many(
        comodel_name="stock.picking", compute="_compute_returned_ids",
        string="退货单")
    barcode = fields.Char(string='条码')

    @api.onchange('barcode')
    def barcode_scanning(self):
        match = False
        product_obj = self.env['product.product']
        product_id = product_obj.search([('barcode', '=', self.barcode)])
        if self.barcode and not product_id:
            self.barcode = None
            return {
                'warning': {
                    'title': "没有这个条码的产品",
                    'message': "请确认是否输入正确或者先添加此条码的产品"
                }
            }
        if self.barcode and self.move_ids_without_package:
            for line in self.move_ids_without_package:
                if line.product_id.barcode == self.barcode:
                    line.quantity_done += 1
                    self.barcode = None
                    match = True
        if self.barcode and not match:
            self.barcode = None
            if product_id:
                return {
                    'warning': {
                        'title': "该产品不在订单中",
                        'message': "您可以通过点击「添加明细行」添加此产品然后再扫描"
                    }
                }

    @api.multi
    def _compute_returned_ids(self):
        for picking in self:
            picking.returned_ids = picking.mapped(
                'move_lines.returned_move_ids.picking_id')


class StockMove(models.Model):
    _inherit = 'stock.move'

    date_planned = fields.Date(string='交货日期', compute='_compute_date_planned')

    @api.multi
    def _compute_date_planned(self):
        for line in self:
            if line.sale_line_id:
                line.date_planned = line.sale_line_id.date_planned
            elif line.purchase_line_id:
                line.date_planned = line.purchase_line_id.date_planned.date()
            else:
                line.date_planned = line.picking_id.scheduled_date.date()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    buffer_store = fields.Float(string='太空倉', compute='_compute_buffer_store')
    date_planned = fields.Date(string="交貨日期")

    @api.depends('product_id')
    def _compute_buffer_store(self):
        for r in self:
            r.buffer_store = r.product_id.virtual_available

    @api.onchange('product_id')
    def _check_date_planned(self):
        for r in self:
            if r.order_id.commitment_date and not r.date_planned:
                r.date_planned = r.order_id.commitment_date.strftime('%Y-%m-%d')

    @api.onchange('date_planned')
    def _onchange_date_planned_gt_commitment_date(self):
        for r in self:
            if not r.date_planned or r.date_planned > r.order_id.commitment_date.date():
                r.date_planned = r.order_id.commitment_date.date()
                return {
                    'warning': {
                        'title': "當前產品交貨日期大於訂單交貨時間",
                        'message': ("您選擇的產品的交貨日期大於訂單最晚交貨時間。"
                                    "請確認您的訂單最晚交貨時間是否無誤。")
                    }
                }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commitment_date = fields.Datetime(required=True, string="交貨日期", default=fields.Datetime.now() + timedelta(days=3))
    overdue = fields.Boolean(compute='_compute_overdue', string="交貨>30天")
    need_downpayment = fields.Boolean(compute='_compute_need_downpayment', string="需要定金")

    @api.depends('commitment_date', 'create_date')
    def _compute_overdue(self):
        for order in self:
            start_time = fields.Datetime.now()
            if order.create_date:
                start_time = order.create_date
            if order.commitment_date:
                order.overdue = order.commitment_date > (start_time + timedelta(days=30))
            else:
                order.commitment_date = fields.Datetime.now() + timedelta(days=3)
            for line in order.order_line:
                if line.date_planned is False:
                    line.date_planned = order.commitment_date.date()
                if line.date_planned > (start_time + timedelta(days=30)).date():
                    order.overdue = True

    @api.depends('amount_total')
    def _compute_need_downpayment(self):
        limit = self.env['ir.config_parameter'].sudo().get_param('sale.order_need_downpayment')
        if not limit:
            self.env['ir.config_parameter'].sudo().set_param('sale.order_need_downpayment', 1000)
        for order in self:
            order.need_downpayment = False
            if order.amount_total > float(limit):
                order.need_downpayment = True

    @api.onchange('overdue')
    def _onchange_overdue(self):
        if self.overdue:
            return {
                'warning': {
                    'title': '訂單交貨日期較長',
                    'message': ("您選擇的訂單交貨日期超過30天。"
                                "請確認您的選擇，如果堅持此日期，此報價單需要得到上級審批。")
                }
            }

    @api.onchange('need_downpayment')
    def _onchange_need_downpayment(self):
        if self.need_downpayment:
            return {
                'warning': {
                    'title': '需預付定金',
                    'message': ("此訂單需要預付30%定金。"
                                "請在跟客戶確認好訂單後及時收取定金並創建發票。")
                }
            }
