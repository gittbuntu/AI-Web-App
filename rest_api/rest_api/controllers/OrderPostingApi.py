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


class OrderPostingApi(http.Controller):
    
    @http.route('/api/order_posting/create/', type='json', auth='public', methods=['POST'], cors="*", csrf=False)
    def create_order_posting(self, **kwargs):
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
                if 'salesOrder' in data:
                    sale_order_check = request.env['sale.order'].sudo().search([('name', '=', data['salesOrder']['OrderId'])])
                    if not sale_order_check:
                        stock_warehouse_check = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', data['salesOrder']['ShopId'])])
                        if not stock_warehouse_check:
                            response_data = {
                                'data': {
                                    'status': 200,
                                    'error': 'Invaild Warehouse',
                                }
                            }
                            # order_posting_json = json.dumps(response_data, indent=4)
                            return response_data
                        order_id = data['salesOrder']['OrderId']
                        shop_id = data['salesOrder']['ShopId']
                        order_date = data['salesOrder']['OrderDate']
                        discount_voucher = data['salesOrder']['DiscountVoucher']
                        discount_type = data['salesOrder']['DiscountType']
                        total_qty = data['salesOrder']['TotalQty']
                        first_name = data['salesOrder']['FirstName']
                        last_name = data['salesOrder']['LastName']
                        customer_email = data['salesOrder']['CustomerEmail']
                        address1 = data['salesOrder']['Address1']
                        address2 = data['salesOrder']['Address2']
                        city = data['salesOrder']['City']
                        countrys = data['salesOrder']['Country']
                        states = data['salesOrder']['State']
                        tele_phone = data['salesOrder']['Telephone']
                        discount_amounts = data['salesOrder']['DiscountAmount']
                        discount_percentage = data['salesOrder']['DiscountPercentage']
                        shipping_cost = data['salesOrder']['ShippingCost']
                        stock_warehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', shop_id)])
                        if stock_warehouse:
                            location_id = stock_warehouse[0].id
                        else:
                            location_id = 4623
                        res_country = request.env['res.country'].sudo().search([('name', 'like', countrys)])
                        if res_country.id:
                            country = res_country.id
                        else:
                            country_codes = pycountry.countries.get(name=countrys)
                            country_code = country_codes.alpha_2 if country_codes.alpha_2 else ''
                            res_countrys = request.env['res.country'].sudo().create({
                                'name': countrys,
                                'code': country_code
                            })
                            country = res_countrys.id
                        res_state = request.env['res.country.state'].sudo().search(
                            [('country_id', '=', country), ('name', 'like', states)])
                        if res_state.id:
                            state = res_state.id
                        else:
                            state_codes = pycountry.countries.get(name=countrys)
                            if state_codes.alpha_2:
                                state_code = state_codes.alpha_2
                                res_states = request.env['res.country.state'].sudo().create({
                                    'country_id': country,
                                    'name': states,
                                    'code': state_code
                                })
                            else:
                                state_code = ''
                                res_states = request.env['res.country.state'].sudo().create({
                                    'country_id': country,
                                    'name': states,
                                    'code': state_code
                                })
                            state = res_states.id
                        res_partner = request.env['res.partner'].sudo().search([('email', '=', customer_email)])
                        if res_partner.id:
                            res_partner.write({
                                'display_name': f"{first_name} {last_name}",
                                'name': f"{first_name} {last_name}",
                                'street': address1,
                                'street2': address2,
                                'country_id': country,
                                'state_id': state,
                                'city': city,
                                'phone': tele_phone,
                                'mobile': tele_phone,
                                'contact_address_complete': f"{address1}, {address2}, {city}, {res_state.name}, {res_country.name}",
                            })
                            partner_id = res_partner.id
                        else:
                            res_partners = request.env['res.partner'].sudo().create({
                                'company_id': 1,
                                'display_name': f"{first_name} {last_name}",
                                'name': f"{first_name} {last_name}",
                                'email': customer_email,
                                'street': address1,
                                'street2': address2,
                                'country_id': country,
                                'state_id': state,
                                'city': city,
                                'phone': tele_phone,
                                'mobile': tele_phone,
                                'contact_address_complete': f"{address1}, {address2}, {city}, {res_state.name}, {res_country.name}",
                            })
                            partner_id = res_partners.id
                        utm_source = request.env['utm.source'].sudo().search([('name', 'like', 'Ginkgo')])
                        if utm_source:
                            source_id = utm_source.id
                        else:
                            utm_sources = request.env['utm.source'].sudo().create({
                                'name': 'Ginkgo',
                            })
                            source_id = utm_sources.id
                        models = xmlrpc.client.ServerProxy(object_url)
                        records_list = []
                        for product in data['salesOrder']['Products']:
                            sku = product['SKU']
                            qty = product['Qty']
                            unit_price = float(product['UnitPrice'])
                            discount_amount = float(product['DiscountAmount'])
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
                                record = [
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
                                        'order_partner_id': partner_id,
                                        'state': 'draft',
                                        'qty_delivered_method': 'manual',
                                        'customer_lead': 0.0,
                                        'invoice_status': 'no',
                                    }
                                ]
                                records_list.append(record)
                        sale_order_data = {
                            'name': order_id,
                            'partner_id': partner_id,
                            'partner_invoice_id': partner_id,
                            'partner_shipping_id': partner_id,
                            'date_order': order_date,
                            'company_id': 1,
                            'warehouse_id': location_id,
                            'state': 'draft',
                            'pricelist_id': 1,
                            'currency_id': 157,
                            'source_id': source_id,
                            'order_line': records_list,
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
                            response_data = {
                                'data': {
                                    'status': 200,
                                    'success': True,
                                    'message': 'Record Insert Successfully',
                                    'sale_order_id': sale_order_id
                                }
                            }
                            # order_posting_json = json.dumps(response_data, indent=4)
                            return response_data
                        else:
                            response_data = {
                                'data': {
                                    'status': 200,
                                    'error': 'Failed to create the Sales Order.',
                                }
                            }
                            # order_posting_json = json.dumps(response_data, indent=4)
                            return response_data
                    else:
                        response_data = {
                            'data': {
                                'status': 200,
                                'error': 'Already Insert Sale Order.',
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
            # order_posting_json = json.dumps(response_data, indent=4)
            return response_data
        
