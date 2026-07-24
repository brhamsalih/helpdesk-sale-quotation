from odoo import api, fields, models
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    customer_reference = fields.Char(
        string="Customer Reference Code"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
    )
    unit_price = fields.Float(
        string="Unit Price",
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Quotation",
        readonly=True,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.unit_price = self.product_id.lst_price

    def action_create_quotation(self):
        # Validation
        if self.sale_order_id:
            raise UserError("A quotation has already been created for this ticket.")
        if not self.partner_id:
            raise UserError("Please select a Customer.")
        if not self.product_id:
            raise UserError("Please select a Product.")
        if not self.uom_id:
            raise UserError("Please select a Unit of Measure.")
        if self.quantity <= 0:
            raise UserError("Quantity must be greater than zero.")
        if self.unit_price < 0:
            raise UserError("Unit Price cannot be negative.")
            
        # Create Sale Order
        sale_order = self.env["sale.order"].create({
            "partner_id": self.partner_id.id,
        })

        # Create Sale Order Line
        self.env["sale.order.line"].create({
            "order_id": sale_order.id,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity,
            "product_uom_id": self.uom_id.id,
            "price_unit": self.unit_price,
        })

        # Link Ticket
        self.sale_order_id = sale_order.id

        # Open Quotation
        return {
            "type": "ir.actions.act_window",
            "name": "Quotation",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": sale_order.id,
            "target": "current",
        }