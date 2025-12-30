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


class OrderUpdateApiOld(http.Controller):
    
    @http.route('/api/order_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def order_update(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
            request_json = request.httprequest.data.decode('utf-8')
            data = json.loads(request_json)
            if 'updateOrder' in data:
                order_id = data['updateOrder']['orderId']
                shop_id = data['updateOrder']['shopId']
                stock_warehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', shop_id)])
                if stock_warehouse:
                    location_id = stock_warehouse.id
                else:
                    location_id = 1
                sale_order_update = request.env['sale.order'].sudo().search([('name', '=', order_id)])
                if sale_order_update:
                    if sale_order_update.state == 'sale':
                        tele_phone = data['updateOrder']['customer']['Telephone']
                        email = data['updateOrder']['customer']['CustomerEmail']
                        first_name = data['updateOrder']['customer']['FirstName']
                        last_name = data['updateOrder']['customer']['LastName']
                        address1 = data['updateOrder']['customer']['Address1']
                        address2 = data['updateOrder']['customer']['Address2']
                        city = data['updateOrder']['customer']['City']

                        res_partner_update = request.env['res.partner'].sudo().search([('name', '=', email)])
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
                        for item in data['updateOrder']['items']:
                            sku = item['SKU']
                            qty = item['Quantity']
                            unit_price = float(item['UnitPrice'])
                            discount_amount = float(item['DiscountAmount'])
                            product_tmpl = request.env['product.template'].sudo().search([('default_code', '=', sku)])
                            product_tmpl_id = product_tmpl.id
                            if product_tmpl_id:
                                sale_order_line_update = request.env['sale.order.line'].sudo().search([('order_id', '=', sale_order_update.id),('product_id', '=', product_tmpl.product_tmpl_id.id)])
                                if sale_order_line_update:
                                    order_line_data = {
                                        'product_uom_qty': qty,
                                        'price_unit': unit_price - discount_amount,
                                        'discount': discount_amount,
                                    }
                                    request.env['sale.order.line'].sudo().write(order_line_data)
                                else:
                                    order_line_data = {
                                        'order_id': sale_order_update.id,
                                        'product_id': product_tmpl_id,
                                        'product_uom_qty': qty,
                                        'price_unit': unit_price - discount_amount,
                                        'discount': discount_amount,
                                        'company_id': 1,
                                        'currency_id': 157,
                                        'order_partner_id': res_partner_update.id,
                                        'state': 'sale',
                                        'qty_delivered_method': 'manual',
                                        'customer_lead': 0.0,
                                        'invoice_status': 'no',
                                    }
                                    request.env['sale.order.line'].sudo().create(order_line_data)
                        response_data = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'message': 'Update Sale Order Successfully',
                            }
                        }
                        # order_update_json = json.dumps(response_data, indent=4)
                        return response_data
                    else:
                        response_data = {
                            'data': {
                                'status': 200,
                                'error': 'Order Status Is Not Sale',
                            }
                        }
                        # order_update_json = json.dumps(response_data, indent=4)
                        return response_data
                    #
                    # data['updateOrder']['customer']
                else:
                    response_data = {
                        'data': {
                            'status': 200,
                            'error': 'No Sale Order Record',
                        }
                    }
                    # order_update_json = json.dumps(response_data, indent=4)
                    return response_data
            else:
                response_data = {
                    'data': {
                        'status': 200,
                        'error': 'Invalid data',
                    }
                }
                # order_update_json = json.dumps(response_data, indent=4)
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