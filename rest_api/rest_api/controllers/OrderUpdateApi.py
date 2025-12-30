from odoo import http
from odoo.http import request, Response
import json
import pycountry
import datetime
import xmlrpc.client
from xmlrpc.client import MultiCall 
import jsonrpcclient
import json
import requests
from odoo import exceptions
import logging


class OrderUpdateApi(http.Controller):
    
    @http.route('/api/order_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def order_update(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
            base_url = 'https://furor.odoo.com'
            db = 'effjayapparel-furor-furor-prod-2368041'
            username = 'api@edenrobe.com'
            password = 'apieden123!@#'
            common_url = f"{base_url}/xmlrpc/2/common"
            object_url = f"{base_url}/xmlrpc/2/object"
            common = xmlrpc.client.ServerProxy(common_url)
            uid = common.authenticate(db, username, password, {})
            if uid:
                request_json = request.httprequest.data.decode('utf-8')
                data = json.loads(request_json)
                if 'updateOrder' in data:
                    account_move_update = request.env['account.move'].sudo().search([('invoice_origin', '=', data['updateOrder']['orderId'])])
                    if not account_move_update:
                        stock_warehouse_check = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', data['updateOrder']['shopId'])])
                        if not stock_warehouse_check:
                            response_data = {
                                'data': {
                                    'status': 200,
                                    'error': 'Invaild Warehouse',
                                }
                            }
                            # order_posting_json = json.dumps(response_data, indent=4)
                            return response_data
                        sale_order_update_check = request.env['sale.order'].sudo().search([('name', '=', data['updateOrder']['orderId'])])
                        if sale_order_update_check.state == 'done':
                            sale_order_update_check.write({
                                    'state': 'draft'
                            })
                        if sale_order_update_check.state == 'sale':
                            sale_order_update_check.write({
                                'state': 'draft'
                            })
                            sale_order_line_update_check = request.env['sale.order.line'].sudo().search([('order_id', '=', sale_order_update_check.id)])
                            for line in sale_order_line_update_check:
                                line.write({
                                        'state': 'draft'
                                })
                        order_status_update_cancel = request.env['sale.order'].sudo().search([('state', '=', 'draft'), ('name', '=', data['updateOrder']['orderId'])])
                        stock_picking_update_cancel = request.env['stock.picking'].sudo().search([('origin', '=', data['updateOrder']['orderId'])])
                        if order_status_update_cancel:
                            order_status_update_cancel.write({
                                'state': 'cancel',
                            })
                            if stock_picking_update_cancel:
                                stock_picking_update_cancel.write({
                                    'state': 'cancel',
                                })
                                stock_move_update_cancel = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_update_cancel.id)])
                                if stock_move_update_cancel:
                                    for move in stock_move_update_cancel:
                                        move.write({
                                            'state': 'cancel'
                                        })
                            order_id = data['updateOrder']['orderId']
                            shop_id = data['updateOrder']['shopId']
                            tele_phone = data['updateOrder']['customer']['Telephone']
                            email = data['updateOrder']['customer']['CustomerEmail']
                            first_name = data['updateOrder']['customer']['FirstName']
                            last_name = data['updateOrder']['customer']['LastName']
                            address1 = data['updateOrder']['customer']['Address1']
                            address2 = data['updateOrder']['customer']['Address2']
                            city = data['updateOrder']['customer']['City']
                            stock_warehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', shop_id)])
                            if stock_warehouse:
                                location_id = stock_warehouse[0].id
                            else:
                                location_id = 4623
                            res_partner_update = request.env['res.partner'].sudo().search([('email', '=', email)])
                            if res_partner_update:
                                res_partner_update.write({
                                    'display_name': f"{first_name} {last_name}",
                                    'name': f"{first_name} {last_name}",
                                    'street': address1,
                                    'street2': address2,
                                    'city': city,
                                    'phone': tele_phone,
                                    'mobile': tele_phone,
                                })
                            order_status_update_data = request.env['sale.order'].sudo().search([('state', '=', 'cancel'), ('name', '=', data['updateOrder']['orderId'])])
                            models = xmlrpc.client.ServerProxy(object_url)
                            records_list_update = []
                            for item in data['updateOrder']['items']:
                                sku = item['SKU']
                                qty = item['Quantity']
                                unit_price = float(item['UnitPrice'])
                                discount_amount = float(item['DiscountAmount'])
                                product_template = request.env['product.template'].sudo().search([('barcode', '=', sku)])
                                product_template_id = product_template[0].id
                                product_product = request.env['product.product'].sudo().search([('barcode', '=', sku)])
                                product_product_id = product_product[0].id
                                taxes_ids = product_product[0].taxes_id.ids
                                taxes_array = ','.join(map(str, taxes_ids))
                                account_tax = request.env['account.tax'].sudo().search([('id', 'in', taxes_ids)])
                                total_tax_percentage = sum(account_tax.mapped('amount'))
                                total_tax_div = (total_tax_percentage/100)
                                discount_value = (unit_price-product_product[0].list_price)
                                taxes_discount = (product_product[0].list_price*total_tax_div)
                                taxes_value = (total_tax_div+1)
                                total_discount_value = ((discount_value-taxes_discount)/taxes_value)
                                total_discount_percentage = ((total_discount_value/product_product[0].list_price*100)*-1)
                                if product_product_id:
                                    record_update = [
                                        0,
                                        0,
                                        {
                                            'product_id': product_product_id,
                                            'product_template_id': product_template_id,
                                            'product_uom_qty': qty,
                                            'product_uom': qty,
                                            'price_unit': product_product[0].list_price,
                                            'discount': total_discount_percentage,
                                            'company_id': 1,
                                            'currency_id': 157,
                                            'order_partner_id': order_status_update_data.partner_id.id,
                                            'state': 'sale',
                                            'qty_delivered_method': 'manual',
                                            'customer_lead': 0.0,
                                            'invoice_status': 'no',
                                        }
                                    ]
                                    records_list_update.append(record_update)
                            sale_order_data = {
                                'name': order_id,
                                'partner_id': order_status_update_data.partner_id.id,
                                'partner_invoice_id': order_status_update_data.partner_id.id,
                                'partner_shipping_id': order_status_update_data.partner_id.id,
                                'date_order': order_status_update_data.date_order,
                                'company_id': 1,
                                'warehouse_id': location_id,
                                'state': 'sale',
                                'pricelist_id': 1,
                                'currency_id': 157,
                                'source_id': order_status_update_data.source_id.id,
                                'order_line': records_list_update,
                                'note': "",
                                'user_id': uid,
                                'team_id': 1
                            }
                            sale_order_id = models.execute_kw(
                                db, uid, password,
                                'sale.order', 'create',
                                [sale_order_data]
                            )
                            if sale_order_id:
                                if order_status_update_data:
                                    stock_picking_delete_data = request.env['stock.picking'].sudo().search([('state', '=', 'cancel'), ('sale_id', '=', order_status_update_data.id)])
                                    if stock_picking_delete_data:
                                        stock_move_status_delete_data = request.env['stock.move'].sudo().search([('state', '=', 'cancel'), ('picking_id', '=', stock_picking_delete_data.id)])
                                        if stock_move_status_delete_data:
                                            stock_move_line_status_delete_data = request.env['stock.move.line'].sudo().search([('state', '=', 'cancel'), ('picking_id', '=', stock_picking_delete_data.id)])
                                            for move_line in stock_move_line_status_delete_data:
                                                move_line.unlink()
                                            for line in stock_move_status_delete_data:
                                                line.unlink()
                                        stock_picking_delete_data.unlink()
                                    order_status_update_data.unlink()
                                response_data = {
                                    'data': {
                                        'status': 200,
                                        'success': True,
                                        'message': 'Record Update Successfully',
                                        'sale_order_id': sale_order_id
                                    }
                                }
                                # order_posting_json = json.dumps(response_data, indent=4)
                                return response_data
                        else:
                            response_data = {
                                'data': {
                                    'status': 200,
                                    'error': 'No Order Record',
                                }
                            }
                            # order_posting_json = json.dumps(response_data, indent=4)
                            return response_data
                    else:
                        response_data = {
                            'data': {
                                'status': 200,
                                'error': 'Sorry Invoice Create Already',
                            }
                        }
                        # order_posting_json = json.dumps(response_data, indent=4)
                        return response_data     
                else:
                    response_data = {
                        'data': {
                            'status': 200,
                            'error': 'Json Format Issues {salesOrder}',
                        }
                    }
                    # order_posting_json = json.dumps(response_data, indent=4)
                    return response_data
            else:
                response_data = {
                    'data': {
                        'status': 200,
                        'error': 'Authentication failed.',
                    }
                }
                # order_posting_json = json.dumps(response_data, indent=4)
                return response_data
        except Exception as e:
            response_data = {
                'data': {
                    'status': 500,
                    'error': str(e)
                }
            }
            # order_update_json = json.dumps(response_data, indent=4)
            return response_data
