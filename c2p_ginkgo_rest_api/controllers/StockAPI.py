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

class StockAPI(http.Controller):

    @http.route('/api/stock/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_stock(self, **kwargs):
        try:
            stock_query_params = http.request.params
            limit = None
            offset = None
            if 'limit' in stock_query_params:
                limit = int(stock_query_params['limit'])
            if 'offset' in stock_query_params:
                offset = int(stock_query_params['offset'])
            stocks_length = request.env['stock.quant'].sudo().search([])
            length = len(stocks_length)
            if limit is not None:
                if limit > length:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Record Length is out of limit',
                            'total_limit': length,
                        }
                    }
                    stock_json = json.dumps(response_data, indent=4)
                    return Response(stock_json, content_type='application/json', status=200)
            if offset is not None:
                if offset > length:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Record Length is out of offset',
                            'total_limit': length,
                        }
                    }
                    stock_json = json.dumps(response_data, indent=4)
                    return Response(stock_json, content_type='application/json', status=200)
            if stock_query_params:
                stock_params = []
                for key in stock_query_params:
                    if key not in ['offset', 'limit']:
                        if isinstance(stock_query_params[key], str):
                            if stock_query_params[key].isdigit():
                                stock_params.append((f'{key}', '=', int(stock_query_params[key])))
                            else:
                                stock_params.append((f'{key}', '=', str(stock_query_params[key])))
                        elif isinstance(stock_query_params[key], int):
                            stock_params.append((f'{key}', '=', int(stock_query_params[key])))
                        elif isinstance(stock_query_params[key], bool):
                            stock_params.append((f'{key}', '=', str(stock_query_params[key])))
                # stocks_length_check = request.env['stock.quant'].sudo().search(stock_params, limit=limit)
                # length_check = len(stocks_length_check)
                # if length_check <= 80:
                #     offset = 0
                stocks = request.env['stock.quant'].sudo().search(stock_params, limit=limit, offset=offset)
            else:
                stocks = request.env['stock.quant'].sudo().search([])
            stock_data = []
            for stock in stocks:
                if stock.product_id.id:
                    products = request.env['product.product'].sudo().search([('id', '=', stock.product_id.id)])
                    for product in products:
                        if product.product_tmpl_id.id:
                            products_templates = request.env['product.template'].sudo().search(
                                [('id', '=', product.product_tmpl_id.id)])
                            for product_template in products_templates:
                                if product_template.barcode:
                                    stock_dict = {
                                        'ShopId': stock.location_id.id,
                                        'SKU': product.barcode,
                                        'Quantity': stock.quantity,
                                    }
                                    stock_data.append(stock_dict)
            response_data = {
                'data': stock_data
            }
            stock_json = json.dumps(response_data, indent=4)
            return Response(stock_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            stock_json = json.dumps(response_data, indent=4)
            return Response(stock_json, content_type='application/json', status=500)
    
    # @http.route('/api/stock/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    # def get_stock(self, **kwargs):
    #     try:
    #         stock_query_params = http.request.params
    #         stock_params = []
    #         for key in stock_query_params:
    #             if isinstance(stock_query_params[key], str):
    #                 if stock_query_params[key].isdigit():
    #                     stock_params.append((f'{key}', '=', int(stock_query_params[key])))
    #                 else:
    #                     stock_params.append((f'{key}', '=', str(stock_query_params[key])))
    #             elif isinstance(stock_query_params[key], int):
    #                 stock_params.append((f'{key}', '=', int(stock_query_params[key])))
    #             elif isinstance(stock_query_params[key], bool):
    #                 stock_params.append((f'{key}', '=', str(stock_query_params[key])))
    #         stocks = request.env['stock.quant'].sudo().search([], limit=10, offset=5)
    #         stock_data = []
    #         for stock in stocks:
    #             if stock.product_id.id:
    #                 products = request.env['product.product'].sudo().search([('id', '=', stock.product_id.id)])
    #                 for product in products:
    #                     if product.product_tmpl_id.id:
    #                         products_templates = request.env['product.template'].sudo().search([('id', '=', product.product_tmpl_id.id)])
    #                         for product_template in products_templates:
    #                             if product_template.default_code:
    #                                 stock_dict = {
    #                                     'ShopId': stock.location_id.id,
    #                                     'SKU': product.barcode,
    #                                     'Quantity': stock.quantity,
    #                                 }
    #                                 stock_data.append(stock_dict)
    #         response_data = {
    #             'data': stock_data
    #         }
    #         stock_json = json.dumps(response_data, indent=4)
    #         return Response(stock_json, content_type='application/json', status=200)
    #     except Exception as e:
    #         response_data = {
    #             'error': str(e)
    #         }
    #         stock_json = json.dumps(response_data, indent=4)
    #         return Response(stock_json, content_type='application/json', status=500)

    # @http.route('/api/stock/view/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    # def get_stock_view(self, **kw):
    #     try:
    #         stock_query_params = http.request.params
    #         stock_params = []
    #         for key in stock_query_params:
    #             if isinstance(stock_query_params[key], str):
    #                 if stock_query_params[key].isdigit():
    #                     stock_params.append((f'{key}', '=', int(stock_query_params[key])))
    #                 else:
    #                     stock_params.append((f'{key}', '=', str(stock_query_params[key])))
    #             elif isinstance(stock_query_params[key], int):
    #                 stock_params.append((f'{key}', '=', int(stock_query_params[key])))
    #             elif isinstance(stock_query_params[key], bool):
    #                 stock_params.append((f'{key}', '=', str(stock_query_params[key])))
    #         stocks = request.env['stock.quant'].sudo().search(stock_params)
    #         stock_data = []
    #         for stock in stocks:
    #             if stock.product_id.id:
    #                 products = request.env['product.product'].sudo().search([('id', '=', stock.product_id.id)])
    #                 for product in products:
    #                     if product.product_tmpl_id.id:
    #                         products_templates = request.env['product.template'].sudo().search([('id', '=', product.product_tmpl_id.id)])
    #                         for product_template in products_templates:
    #                             if product_template.default_code:
    #                                 stock_dict = {
    #                                     'ShopId': stock.location_id.id,
    #                                     'SKU': product.barcode,
    #                                     'Quantity': stock.quantity,
    #                                 }
    #                                 stock_data.append(stock_dict)
    #         response_data = {
    #             'data': stock_data
    #         }
    #         stock_json = json.dumps(response_data, indent=4)
    #         return Response(stock_json, content_type='application/json', status=200)
    #     except Exception as e:
    #         response_data = {
    #             'error': str(e)
    #         }
    #         stock_json = json.dumps(response_data, indent=4)
    #         return Response(stock_json, content_type='application/json', status=500)

    @http.route('/api/price/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_price(self, **kwargs):
        try:
            price_query_params = http.request.params
            limit = None
            offset = None
            if 'limit' in price_query_params:
                limit = int(price_query_params['limit'])
            if 'offset' in price_query_params:
                offset = int(price_query_params['offset'])
            prices_length = request.env['stock.quant'].sudo().search([])
            length = len(prices_length)
            if limit is not None:
                if limit > length:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Record Length is out of limit',
                            'total_limit': length,
                        }
                    }
                    price_json = json.dumps(response_data, indent=4)
                    return Response(price_json, content_type='application/json', status=200)
            if offset is not None:
                if offset > length:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Record Length is out of offset',
                            'total_limit': length,
                        }
                    }
                    price_json = json.dumps(response_data, indent=4)
                    return Response(price_json, content_type='application/json', status=200)
            if price_query_params:
                price_params = []
                for key in price_query_params:
                    if key not in ['offset', 'limit']:
                        if isinstance(price_query_params[key], str):
                            if price_query_params[key].isdigit():
                                price_params.append((f'{key}', '=', int(price_query_params[key])))
                            else:
                                price_params.append((f'{key}', '=', str(price_query_params[key])))
                        elif isinstance(price_query_params[key], int):
                            price_params.append((f'{key}', '=', int(price_query_params[key])))
                        elif isinstance(price_query_params[key], bool):
                            price_params.append((f'{key}', '=', str(price_query_params[key])))
                # prices_length_check = request.env['stock.quant'].sudo().search(price_params, limit=limit)
                # length_check = len(prices_length_check)
                # if length_check <= 80:
                #     offset = 0
                prices = request.env['stock.quant'].sudo().search(price_params, limit=limit, offset=offset)
            else:
                prices = request.env['stock.quant'].sudo().search([])
            price_data = []
            for price in prices:
                if price.product_id.id:
                    products = request.env['product.product'].sudo().search([('id', '=', price.product_id.id)])
                    for product in products:
                        if product.product_tmpl_id.id:
                            products_templates = request.env['product.template'].sudo().search(
                                [('id', '=', product.product_tmpl_id.id)])
                            for product_template in products_templates:
                                if product_template.barcode:
                                    productpricelistitem = request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', product.product_tmpl_id.id)])
                                    discount_price = productpricelistitem.fixed_price if productpricelistitem.fixed_price else 0.0
                                    price_dict = {
                                        'SKU': product.barcode,
                                        'Price': product_template.list_price,
                                        'Discount_Price': discount_price,
                                    }
                                    price_data.append(price_dict)
            response_data = {
                'data': price_data
            }
            price_json = json.dumps(response_data, indent=4)
            return Response(price_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            price_json = json.dumps(response_data, indent=4)
            return Response(price_json, content_type='application/json', status=500)

    # @http.route('/api/price/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    # def get_price(self, **kwargs):
    #     try:
    #         prices = request.env['stock.quant'].sudo().search([])
    #         price_data = []
    #         for price in prices:
    #             if price.product_id.id:
    #                 products = request.env['product.product'].sudo().search([('id', '=', price.product_id.id)])
    #                 for product in products:
    #                     if product.product_tmpl_id.id:
    #                         products_templates = request.env['product.template'].sudo().search(
    #                             [('id', '=', product.product_tmpl_id.id)])
    #                         for product_template in products_templates:
    #                             if product_template.default_code:
    #                                 productpricelistitem = request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', product.product_tmpl_id.id)])
    #                                 discount_price = productpricelistitem.fixed_price if productpricelistitem.fixed_price else 0.0
    #                                 price_dict = {
    #                                     'SKU': product.barcode,
    #                                     'Price': product_template.list_price,
    #                                     'Discount_Price': discount_price,
    #                                 }
    #                                 price_data.append(price_dict)
    #         response_data = {
    #             'data': price_data
    #         }
    #         price_json = json.dumps(response_data, indent=4)
    #         return Response(price_json, content_type='application/json', status=200)
    #     except Exception as e:
    #         response_data = {
    #             'error': str(e)
    #         }
    #         price_json = json.dumps(response_data, indent=4)
    #         return Response(price_json, content_type='application/json', status=500)

    # @http.route('/api/price/view/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    # def get_price_view(self, **kw):
    #     try:
    #         price_query_params = http.request.params
    #         price_params = []
    #         for key in price_query_params:
    #             if isinstance(price_query_params[key], str):
    #                 if price_query_params[key].isdigit():
    #                     price_params.append((f'{key}', '=', int(price_query_params[key])))
    #                 else:
    #                     price_params.append((f'{key}', '=', str(price_query_params[key])))
    #             elif isinstance(price_query_params[key], int):
    #                 price_params.append((f'{key}', '=', int(price_query_params[key])))
    #             elif isinstance(price_query_params[key], bool):
    #                 price_params.append((f'{key}', '=', str(price_query_params[key])))
    #         prices = request.env['stock.quant'].sudo().search(price_params)
    #         price_data = []
    #         for price in prices:
    #             if price.product_id.id:
    #                 products = request.env['product.product'].sudo().search([('id', '=', price.product_id.id)])
    #                 for product in products:
    #                     if product.product_tmpl_id.id:
    #                         products_templates = request.env['product.template'].sudo().search(
    #                             [('id', '=', product.product_tmpl_id.id)])
    #                         for product_template in products_templates:
    #                             if product_template.default_code:
    #                                 productpricelistitem = request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', product.product_tmpl_id.id)])
    #                                 discount_price = productpricelistitem.fixed_price if productpricelistitem.fixed_price else 0.0
    #                                 price_dict = {
    #                                     'SKU': product.barcode,
    #                                     'Price': product_template.list_price,
    #                                     'Discount_Price': discount_price,
    #                                 }
    #                                 price_data.append(price_dict)
    #         response_data = {
    #             'data': price_data
    #         }
    #         price_json = json.dumps(response_data, indent=4)
    #         return Response(price_json, content_type='application/json', status=200)
    #     except Exception as e:
    #         response_data = {
    #             'error': str(e)
    #         }
    #         price_json = json.dumps(response_data, indent=4)
    #         return Response(price_json, content_type='application/json', status=500)

    # @http.route('/api/order_posting/create/', type='json', auth='public', methods=['POST'], cors="*", csrf=False)
    # def create_order_posting(self, **kwargs):
    #     try:
    #         request_json = request.httprequest.data.decode('utf-8')
    #         data = json.loads(request_json)
    #         if 'salesOrder' in data:
    #             order_id = data['salesOrder']['OrderId']
    #             shop_id = data['salesOrder']['ShopId']
    #             order_date = data['salesOrder']['OrderDate']
    #             discount_voucher = data['salesOrder']['DiscountVoucher']
    #             discount_type = data['salesOrder']['DiscountType']
    #             total_qty = data['salesOrder']['TotalQty']
    #             first_name = data['salesOrder']['FirstName']
    #             last_name = data['salesOrder']['LastName']
    #             customer_email = data['salesOrder']['CustomerEmail']
    #             address1 = data['salesOrder']['Address1']
    #             address2 = data['salesOrder']['Address2']
    #             city = data['salesOrder']['City']
    #             countrys = data['salesOrder']['Country']
    #             states = data['salesOrder']['State']
    #             tele_phone = data['salesOrder']['Telephone']
    #             discount_amounts = data['salesOrder']['DiscountAmount']
    #             discount_percentage = data['salesOrder']['DiscountPercentage']
    #             shipping_cost = data['salesOrder']['ShippingCost']
    #             stock_warehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', shop_id)])
    #             if stock_warehouse:
    #                 location_id = stock_warehouse.id
    #             else:
    #                 location_id = 1
    #             res_country = request.env['res.country'].sudo().search([('name', 'like', countrys)])
    #             if res_country.id:
    #                 country = res_country.id
    #             else:
    #                 country_codes = pycountry.countries.get(name=countrys)
    #                 country_code = country_codes.alpha_2 if country_codes.alpha_2 else ''
    #                 res_countrys = request.env['res.country'].sudo().create({
    #                     'name': countrys,
    #                     'code': country_code
    #                 })
    #                 country = res_countrys.id
    #             res_state = request.env['res.country.state'].sudo().search(
    #                 [('country_id', '=', country), ('name', 'like', states)])
    #             if res_state.id:
    #                 state = res_state.id
    #             else:
    #                 state_codes = pycountry.countries.get(name=countrys)
    #                 if state_codes.alpha_2:
    #                     state_code = state_codes.alpha_2
    #                     res_states = request.env['res.country.state'].sudo().create({
    #                         'country_id': country,
    #                         'name': states,
    #                         'code': state_code
    #                     })
    #                 else:
    #                     state_code = ''
    #                     res_states = request.env['res.country.state'].sudo().create({
    #                         'country_id': country,
    #                         'name': states,
    #                         'code': state_code
    #                     })
    #                 state = res_states.id
    #             res_partner = request.env['res.partner'].sudo().search([('email', '=', customer_email)])
    #             if res_partner.id:
    #                 res_partner.write({
    #                     'display_name': f"{first_name} {last_name}",
    #                     'name': f"{first_name} {last_name}",
    #                     'street': address1,
    #                     'street2': address2,
    #                     'country_id': country,
    #                     'state_id': state,
    #                     'city': city,
    #                     'phone': tele_phone,
    #                     'mobile': tele_phone,
    #                     'contact_address_complete': f"{address1}, {address2}, {city}, {res_state.name}, {res_country.name}",
    #                 })
    #                 partner_id = res_partner.id
    #             else:
    #                 res_partners = request.env['res.partner'].sudo().create({
    #                     'company_id': 1,
    #                     'display_name': f"{first_name} {last_name}",
    #                     'name': f"{first_name} {last_name}",
    #                     'email': customer_email,
    #                     'street': address1,
    #                     'street2': address2,
    #                     'country_id': country,
    #                     'state_id': state,
    #                     'city': city,
    #                     'phone': tele_phone,
    #                     'mobile': tele_phone,
    #                     'contact_address_complete': f"{address1}, {address2}, {city}, {res_state.name}, {res_country.name}",
    #                 })
    #                 partner_id = res_partners.id
    #             utm_source = request.env['utm.source'].sudo().search([('name', 'like', 'Ginkgo')])
    #             if utm_source:
    #                 source_id = utm_source.id
    #             else:
    #                 utm_sources = request.env['utm.source'].sudo().create({
    #                     'name': 'Ginkgo',
    #                 })
    #                 source_id = utm_sources.id
    #             sale_order_data = {
    #                 'name': order_id,
    #                 'partner_id': partner_id,
    #                 'partner_invoice_id': partner_id,
    #                 'partner_shipping_id': partner_id,
    #                 'note':"",
    #                 'user_id': 305,
    #                 'team_id': 1,
    #                 'date_order': order_date,
    #                 'company_id': 1,
    #                 'state': 'sale',
    #                 'pricelist_id': 1,
    #                 'currency_id': 157,
    #                 'source_id': source_id,
    #                 'warehouse_id': location_id,
    #             }
    #             sale_order = request.env['sale.order'].sudo().create(sale_order_data)
    #             for product in data['salesOrder']['Products']:
    #                 sku = product['SKU']
    #                 qty = product['Qty']
    #                 unit_price = float(product['UnitPrice'])
    #                 discount_amount = float(product['DiscountAmount'])
    #                 product_template = request.env['product.template'].sudo().search([('default_code', '=', sku)])
    #                 product_template_id = product_template[0].id
    #                 product_product = request.env['product.product'].sudo().search([('default_code', '=', sku)])
    #                 product_product_id = product_product[0].id
    #                 if product_product_id:
    #                     order_line_data = {
    #                         'order_id': sale_order.id,
    #                         'name': order_id,
    #                         'product_id': product_product_id,
    #                         'product_template_id': product_template_id,
    #                         'product_uom_qty': qty,
    #                         "product_uom": qty,
    #                         'price_unit': unit_price - discount_amount,
    #                         'discount': discount_amount,
    #                         'company_id': 1,
    #                         'currency_id': 157,
    #                         'order_partner_id': partner_id,
    #                         'state': 'sale',
    #                         'qty_delivered_method': 'manual',
    #                         'customer_lead': 0.0,
    #                         'invoice_status': 'no',
    #                     }
    #                     request.env['sale.order.line'].sudo().create(order_line_data)
    #             stock_picking_status_update = request.env['stock.picking'].sudo().search([('sale_id', '=', sale_order.id)])
    #             if stock_picking_status_update:
    #                 stock_picking_status_update.write({
    #                     'state': 'done'
    #                 })
    #             stock_move_status_update = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_status_update.id)])
    #             if stock_move_status_update:
    #                 for line in stock_move_status_update:
    #                     line.write({
    #                         'state': 'done'
    #                     })
    #             stock_move_line_status_update = request.env['stock.move.line'].sudo().search([('picking_id', '=', stock_picking_status_update.id)])
    #             if stock_move_line_status_update:
    #                 for line in stock_move_line_status_update:
    #                     line.write({
    #                         'state': 'done'
    #                     })
    #             response_data = {
    #                 'data': {
    #                     'status': 200,
    #                     'success': True,
    #                     'message': 'Record Insert Successfully',
    #                     'sale_order_id': sale_order.id
    #                 }
    #             }
    #             # order_posting_json = json.dumps(response_data, indent=4)
    #             return response_data
    #         else:
    #             response_data = {
    #                 'data': {
    #                     'status': 200,
    #                     'error': 'Invalid data',
    #                 }
    #             }
    #             # order_posting_json = json.dumps(response_data, indent=4)
    #             return response_data
    #     except Exception as e:
    #         response_data = {
    #             'data': {
    #                 'status': 500,
    #                 'error': str(e)
    #             }
    #         }
    #         # order_posting_json = json.dumps(response_data, indent=4)
    #         return response_data

    @http.route('/api/order_posting/create/', type='json', auth='public', methods=['POST'], cors="*", csrf=False)
    def create_order_posting(self, **kwargs):
        try:
            base_url = 'https://furor-ginkgo-api-9183196.dev.odoo.com'
            db = 'furor-ginkgo-api-9183196'
            username = 'bilal.akhtar@edenrobe.com'
            password = '123456'
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
        
    @http.route('/api/get_order_status/', type='json', auth='public', methods=['POST'], cors="*", csrf=False)
    def get_order_status(self, **kwargs):
        try:
            request_json = request.httprequest.data.decode('utf-8')
            data = json.loads(request_json)
            sale_order = request.env['sale.order'].sudo().search([('name', '=', data['orderId'])])
            order_status_get = []
            for saleorder in sale_order:
                order_status_get.append({
                    'OrderId': saleorder.name,
                    'Status': saleorder.state,
                })

            response_data = {
                'data': {
                    'status': 200,
                    'success': True,
                    'order_status': order_status_get
                }
            }
            # order_status_json = json.dumps(response_data, indent=4)
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

    @http.route('/api/order_fulfillment/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_fulfillment(self, **kwargs):
        try:
            request_json = request.httprequest.data.decode('utf-8')
            data = json.loads(request_json)
            delivery_carrier = request.env['delivery.carrier'].sudo().search([('name', '=', data['courierCompany'])])
            if delivery_carrier:
                stock_picking = request.env['stock.picking'].sudo().search([('origin', '=', data['orderId'])])
                if stock_picking:
                    stock_picking.write({
                        'carrier_id': delivery_carrier.id,
                        'carrier_tracking_ref': data['courierNumber'],
                    })
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Update Order Fulfillment Successfully',
                        }
                    }
                    # stock_picking_json = json.dumps(response_data, indent=4)
                    return response_data
                else:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Sorry No Delivery Orders',
                        }
                    }
                    # stock_picking_json = json.dumps(response_data, indent=4)
                    return response_data
            else:
                response_data = {
                    'data': {
                        'status': 200,
                        'success': True,
                        'message': 'Sorry No Shipping Methods Add or Your Please Add Shipping Methods',
                    }
                }
                # stock_picking_json = json.dumps(response_data, indent=4)
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

    @http.route('/api/order_fulfillment/cancel/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_fulfillment_cancel(self, **kwargs):
        try:
            request_json = request.httprequest.data.decode('utf-8')
            data = json.loads(request_json)
            delivery_carrier = request.env['delivery.carrier'].sudo().search([('name', '=', data['courierCompany'])])
            if delivery_carrier:
                stock_picking = request.env['stock.picking'].sudo().search([('origin', '=', data['orderId'])])
                if stock_picking:
                    if stock_picking.state == 'done':
                        if stock_picking:
                            stock_picking.write({
                                'state': 'assigned',
                            })
                            stock_move_update = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking.id)])
                            if stock_move_update:
                                for move in stock_move_update:
                                    move.write({
                                        'state': 'assigned'
                                    })
                        stock_picking.write({
                            'carrier_id': None,
                            'carrier_tracking_ref': None,
                        })
                        if stock_picking:
                            stock_picking.write({
                                'state': 'done',
                            })
                            stock_move_update = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking.id)])
                            if stock_move_update:
                                for move in stock_move_update:
                                    move.write({
                                        'state': 'done'
                                    })
                        response_data = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'message': 'Update Cancelled Order Fulfillment Successfully',
                            }
                        }
                        # stock_picking_json = json.dumps(response_data, indent=4)
                        return response_data
                    else:
                        stock_picking.write({
                            'carrier_id': None,
                            'carrier_tracking_ref': None,
                        })
                        response_data = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'message': 'Update Cancelled Order Fulfillment Successfully',
                            }
                        }
                        # stock_picking_json = json.dumps(response_data, indent=4)
                        return response_data
                else:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Sorry No Delivery Orders',
                        }
                    }
                    # stock_picking_json = json.dumps(response_data, indent=4)
                    return response_data
            else:
                response_data = {
                    'data': {
                        'status': 200,
                        'success': True,
                        'message': 'Sorry No Shipping Methods Add or Your Please Add Shipping Methods',
                    }
                }
                # stock_picking_json = json.dumps(response_data, indent=4)
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

    @http.route('/api/update_order_status/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_status(self, **kwargs):
        try:
            request_json = request.httprequest.data.decode('utf-8')
            data = json.loads(request_json)
            order_status_update = request.env['sale.order'].sudo().search([('state', '=', 'sale'), ('name', '=', data['orderId'])])
            stock_picking_update = request.env['stock.picking'].sudo().search([('state', '=', 'done'), ('origin', '=', data['orderId'])])
            account_move_update = request.env['account.move'].sudo().search([('state', '=', 'posted'), ('invoice_origin', '=', data['orderId'])])
            if order_status_update:
                if data['Status'] == 'Cancelled':
                    order_status_update.write({
                        'state': 'cancel',
                    })
                    if stock_picking_update:
                        stock_picking_update.write({
                            'state': 'cancel',
                        })
                        stock_move_update = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_update.id)])
                        if stock_move_update:
                            for move in stock_move_update:
                                move.write({
                                    'state': 'cancel'
                                })
                    if account_move_update:
                        account_move_update.write({
                            'state': 'cancel',
                        })
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Update Order Status Cancelled Successfully',
                        }
                    }
                    # order_status_update_json = json.dumps(response_data, indent=4)
                    return response_data
                elif data['Status'] == 'Delivered':
                    stock_picking_update_delivered = request.env['stock.picking'].sudo().search([('sale_id', '=', order_status_update.id)])
                    if stock_picking_update_delivered:
                        stock_picking_update_delivered.write({
                            'state': 'done'
                        })
                        stock_move_update_delivered = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_update_delivered.id)])
                        if stock_move_update_delivered:
                            for move_delivered in stock_move_update_delivered:
                                move_delivered.write({
                                    'quantity_done': move_delivered.product_uom_qty,
                                    'state': 'done'
                                })
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Update Order Status Delivered Successfully',
                        }
                    }
                    # order_status_update_json = json.dumps(response_data, indent=4)
                    return response_data
                elif data['Status'] == 'Returned':
                    if stock_picking_update:
                        stock_warehouse_update = request.env['stock.warehouse'].sudo().search([('name', 'like', 'Online Warehouse')])
                        if stock_warehouse_update:
                            stock_warehouse_id = stock_warehouse_update.id
                        else:
                            stock_warehouse_id = 0
                        stock_picking_type_update = request.env['stock.picking.type'].sudo().search([('warehouse_id', '=', stock_warehouse_id), ('name', 'like', 'Delivery Orders')])
                        stock_picking_type_receipt_update = request.env['stock.picking.type'].sudo().search([('warehouse_id', '=', stock_warehouse_id), ('name', 'like', 'Receipts')])
                        stock_location_update = request.env['stock.location'].sudo().search([('name', '=', 'Customers')])
                        parent_location_update = request.env['stock.location'].sudo().search([('name', '=', 'Online Warehouse')])
                        if parent_location_update:
                            parent_location_id = parent_location_update.id
                        else:
                            parent_location_id = 0 
                        original_location = request.env['stock.location'].sudo().search([('location_id', '=', parent_location_id), ('name', '=', 'Stock')])
                        parent_location = request.env['stock.location'].sudo().search([('name', '=', 'WH')])
                        if stock_picking_type_update:
                            picking_type_id = stock_picking_type_update.id
                        else:
                            picking_type_id = 0
                        if stock_picking_type_receipt_update:
                            picking_type_receipt_id = stock_picking_type_receipt_update.id
                        else:
                            picking_type_receipt_id = 0
                        if stock_location_update:
                            location_id = stock_location_update.id
                        else:
                            location_id = 0
                        if original_location:
                            original_location_id = original_location.id
                        else:
                            original_location_id = 0
                        if parent_location:
                            parent_location_id = parent_location.id
                        else:
                            parent_location_id = 0
                        return_data = {
                            'location_id': location_id,
                            'location_dest_id': original_location_id,
                            'picking_type_id': picking_type_receipt_id,
                            'partner_id': stock_picking_update.partner_id.id,
                            'company_id': stock_picking_update.company_id.id,
                            'origin': f'Return of {stock_picking_update.name}',
                            'move_type': stock_picking_update.move_type,
                            'is_locked': True,
                            'sale_id': stock_picking_update.sale_id.id,
                            'carrier_price': 0.0,
                        }
                        stock_picking = request.env['stock.picking'].sudo().create(return_data)
                        stock_picking_last_update = request.env['stock.picking'].sudo().search(
                            [('id', '=', stock_picking.id)])
                        if stock_picking_last_update:
                            stock_picking_last_update.write({
                                'group_id': stock_picking_update.group_id.id,
                                'state': 'assigned',
                                'weight': stock_picking_update.weight,
                            })
                        stock_return_picking_data = {
                            'picking_id': stock_picking_update.id,
                            'original_location_id': original_location_id,
                            'parent_location_id': parent_location_id,
                        }
                        stock_return_picking = request.env['stock.return.picking'].sudo().create(
                            stock_return_picking_data)
                        stock_lines = request.env['stock.move'].sudo().search(
                            [('picking_id', '=', stock_picking_update.id)])
                        for line in stock_lines:
                            return_line_data = {
                                'sequence': line.sequence,
                                'company_id': line.company_id.id,
                                'product_id': line.product_id.id,
                                'product_uom': line.product_uom.id,
                                'location_id': location_id,
                                'location_dest_id': original_location_id,
                                'partner_id': line.partner_id.id,
                                'picking_id': stock_picking.id,
                                'group_id': line.group_id.id,
                                'rule_id': line.rule_id.id,
                                'picking_type_id': picking_type_receipt_id,
                                'origin_returned_move_id': line.id,
                                'warehouse_id': line.warehouse_id.id,
                                'next_serial_count': 0,
                                'name': line.name,
                                'origin': line.origin,
                                'procure_method': line.procure_method,
                                # 'reservation_date': datetime.date.today(),
                                # 'propagate_cancel': False,
                                'description_picking': line.description_picking,
                                # 'is_inventory': False,
                                'product_uom_qty': line.product_uom_qty,
                                # 'unit_factor': line.unit_factor,
                                # 'cost_share': 0.00,
                                # 'to_refund': True,
                                'sale_line_id': line.sale_line_id.id,
                            }
                            moves = request.env['stock.move'].sudo().create(return_line_data)
                            stock_move_last_update = request.env['stock.move'].sudo().search([('id', '=', moves.id)])
                            if stock_move_last_update:
                                stock_move_last_update.write({
                                    'state': 'assigned',
                                    'weight': line.weight
                                })
                            # stock_move_return_line_data = {
                            #     'picking_id': stock_picking.id,
                            #     'move_id': moves.id,
                            #     'company_id': line.company_id.id,
                            #     'product_id': line.product_id.id,
                            #     'product_uom_id': line.product_uom.id,
                            #     'location_id': location_id,
                            #     'location_dest_id': original_location_id,
                            #     'state': 'assigned',
                            #     'product_uom_qty': line.product_uom_qty,
                            #     'qty_done': line.product_uom_qty,
                            # }
                            # request.env['stock.move.line'].sudo().create(stock_move_return_line_data)
                            # stock_return_picking_line_data = {
                            #     'product_id': line.product_id.id,
                            #     'wizard_id': stock_return_picking.id,
                            #     'move_id': line.id,
                            #     'quantity': line.product_uom_qty,
                            #     'to_refund': True,
                            # }
                            # request.env['stock.return.picking.line'].sudo().create(stock_return_picking_line_data)
                        stock_picking_status_update = request.env['stock.picking'].sudo().search([('id', '=', stock_picking_last_update.id)])
                        if stock_picking_status_update:
                            stock_picking_status_update.write({
                                'state': 'done'
                            })
                            stock_move_status_update = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_status_update.id)])
                            if stock_move_status_update:
                                for move in stock_move_status_update:
                                    move.write({
                                        'quantity_done': move.product_uom_qty,
                                        'state': 'done'
                                    })
                            # stock_move_line_status_update = request.env['stock.move.line'].sudo().search([('picking_id', '=', stock_picking_status_update.id)])
                            # if stock_move_line_status_update:
                            #     for move_line in stock_move_line_status_update:
                            #         move_line.write({
                            #             'state': 'done'
                            #         })
                        sale_order_line_update = request.env['sale.order.line'].sudo().search([('order_id', '=', order_status_update.id)])
                        for line in sale_order_line_update:
                            line.write({
                                'qty_delivered': 0,
                            });
                        response_data = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'message': 'Update Order Status Returned Successfully',
                            }
                        }
                        # order_status_update_json = json.dumps(response_data, indent=4)
                        return response_data
                    else:
                        response_data = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'message': 'Please Delivery Order Status Posted',
                            }
                        }
                        # order_status_update_json = json.dumps(response_data, indent=4)
                        return response_data
                elif data['Status'] == 'Invoiced':
                    if stock_picking_update:
                        if not account_move_update:
                            try:
                                invoice_data = {
                                    'ref': order_status_update.client_order_ref,
                                    'type': 'out_invoice',
                                    'partner_id': order_status_update.partner_invoice_id.id,
                                    'partner_shipping_id': order_status_update.partner_invoice_id.id,
                                    'invoice_origin': order_status_update.name,
                                    'invoice_user_id': order_status_update.user_id.id,
                                    'currency_id': order_status_update.currency_id.id,
                                    'date': order_status_update.date_order,
                                    'journal_id': 1,
                                    'state': 'draft',
                                }
                                invoice = request.env['account.move'].sudo().create(invoice_data)
                                sale_order_line_update = request.env['sale.order.line'].sudo().search([('order_id', '=', order_status_update.id)])
                                account_move_line_data_list = []
                                for line in sale_order_line_update:
                                    account_move_line_data = {
                                        'move_id': invoice.id,
                                        'product_id': line.product_id.id,
                                        'analytic_account_id': 127,
                                        'quantity': line.product_uom_qty,
                                        'product_uom_id': line.product_uom.id,
                                        'price_unit': line.price_unit,
                                        'discount': line.discount,
                                        'tax_ids': [(6, 0, line.tax_id.ids)],
                                        'sale_line_ids': [(6, 0, [line.id])],
                                        'parent_state': 'draft',
                                    }
                                    account_move_line_data_list.append(account_move_line_data)
                                request.env['account.move.line'].sudo().create(account_move_line_data_list)
                                # move_update = request.env['account.move'].sudo().search([('state', '=', 'draft'), ('invoice_origin', '=', data['orderId'])])
                                # if move_update:
                                #     move_update.write({
                                #         'state': 'posted',
                                #     })
                                response_data = {
                                    'data': {
                                        'status': 200,
                                        'success': True,
                                        'message': 'Update Order Status Invoiced Successfully',
                                    }
                                }
                                # order_status_update_json = json.dumps(response_data, indent=4)
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
                        else:
                            response_data = {
                                'data': {
                                    'status': 200,
                                    'success': True,
                                    'message': 'Already Invoiced Create',
                                }
                            }
                            # order_status_update_json = json.dumps(response_data, indent=4)
                            return response_data
                    else:
                        response_data = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'message': 'Delivery Order Status Only Done',
                            }
                        }
                        # order_status_update_json = json.dumps(response_data, indent=4)
                        return response_data
                elif data['Status'] == 'Cancel_Fulfillment':
                    if stock_picking_update:
                        stock_picking_update.write({
                            'state': 'cancel',
                        })
                        stock_move_update = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_update.id)])
                        if stock_move_update:
                            for move in stock_move_update:
                                move.write({
                                    'state': 'cancel'
                                })
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Update Order Status Cancel_Fulfillment Successfully',
                        }
                    }
                    # order_status_update_json = json.dumps(response_data, indent=4)
                    return response_data
                elif data['Status'] == 'Sales':
                    if order_status_update:
                        order_status_update.write({
                            'state': 'sale',
                        })
                        order_line_status_update = request.env['sale.order.line'].sudo().search([('order_id', '=', order_status_update.id)])
                        if order_line_status_update:
                            for line in order_line_status_update:
                                line.write({
                                    'state': 'sale'
                                })
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Update Order Status Cancel_Fulfillment Successfully',
                        }
                    }
                    # order_status_update_json = json.dumps(response_data, indent=4)
                    return response_data
                else:
                    response_data = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'message': 'Use This Order Status Cancelled / Returned / Sales / Delivered / Cancel_Fulfillment',
                        }
                    }
                    # order_status_update_json = json.dumps(response_data, indent=4)
                    return response_data
            else:
                response_data = {
                    'data': {
                        'status': 200,
                        'success': True,
                        'message': 'No Order Record',
                    }
                }
                # order_status_update_json = json.dumps(response_data, indent=4)
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

    # @http.route('/api/order_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    # def order_update(self, **kwargs):
    #     try:
    #         request_json = request.httprequest.data.decode('utf-8')
    #         data = json.loads(request_json)
    #         if 'updateOrder' in data:
    #             order_id = data['updateOrder']['orderId']
    #             shop_id = data['updateOrder']['shopId']
    #             stock_warehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', shop_id)])
    #             if stock_warehouse:
    #                 location_id = stock_warehouse.id
    #             else:
    #                 location_id = 1
    #             sale_order_update = request.env['sale.order'].sudo().search([('name', '=', order_id)])
    #             if sale_order_update:
    #                 if sale_order_update.state == 'sale':
    #                     tele_phone = data['updateOrder']['customer']['Telephone']
    #                     email = data['updateOrder']['customer']['CustomerEmail']
    #                     first_name = data['updateOrder']['customer']['FirstName']
    #                     last_name = data['updateOrder']['customer']['LastName']
    #                     address1 = data['updateOrder']['customer']['Address1']
    #                     address2 = data['updateOrder']['customer']['Address2']
    #                     city = data['updateOrder']['customer']['City']

    #                     res_partner_update = request.env['res.partner'].sudo().search([('name', '=', email)])
    #                     if res_partner_update:
    #                         res_partner_update.write({
    #                             'display_name': f"{first_name} {last_name}",
    #                             'name': f"{first_name} {last_name}",
    #                             'street': address1,
    #                             'street2': address2,
    #                             'city': city,
    #                             'phone': tele_phone,
    #                             'mobile': tele_phone,
    #                         })
    #                     for item in data['updateOrder']['items']:
    #                         sku = item['SKU']
    #                         qty = item['Quantity']
    #                         unit_price = float(item['UnitPrice'])
    #                         discount_amount = float(item['DiscountAmount'])
    #                         product_tmpl = request.env['product.template'].sudo().search([('default_code', '=', sku)])
    #                         product_tmpl_id = product_tmpl.id
    #                         if product_tmpl_id:
    #                             sale_order_line_update = request.env['sale.order.line'].sudo().search([('order_id', '=', sale_order_update.id),('product_id', '=', product_tmpl.product_tmpl_id.id)])
    #                             if sale_order_line_update:
    #                                 order_line_data = {
    #                                     'product_uom_qty': qty,
    #                                     'price_unit': unit_price - discount_amount,
    #                                     'discount': discount_amount,
    #                                 }
    #                                 request.env['sale.order.line'].sudo().write(order_line_data)
    #                             else:
    #                                 order_line_data = {
    #                                     'order_id': sale_order_update.id,
    #                                     'product_id': product_tmpl_id,
    #                                     'product_uom_qty': qty,
    #                                     'price_unit': unit_price - discount_amount,
    #                                     'discount': discount_amount,
    #                                     'company_id': 1,
    #                                     'currency_id': 157,
    #                                     'order_partner_id': res_partner_update.id,
    #                                     'state': 'sale',
    #                                     'qty_delivered_method': 'manual',
    #                                     'customer_lead': 0.0,
    #                                     'invoice_status': 'no',
    #                                 }
    #                                 request.env['sale.order.line'].sudo().create(order_line_data)
    #                     response_data = {
    #                         'data': {
    #                             'status': 200,
    #                             'success': True,
    #                             'message': 'Update Sale Order Successfully',
    #                         }
    #                     }
    #                     # order_update_json = json.dumps(response_data, indent=4)
    #                     return response_data
    #                 else:
    #                     response_data = {
    #                         'data': {
    #                             'status': 200,
    #                             'error': 'Order Status Is Not Sale',
    #                         }
    #                     }
    #                     # order_update_json = json.dumps(response_data, indent=4)
    #                     return response_data
    #                 #
    #                 # data['updateOrder']['customer']
    #             else:
    #                 response_data = {
    #                     'data': {
    #                         'status': 200,
    #                         'error': 'No Sale Order Record',
    #                     }
    #                 }
    #                 # order_update_json = json.dumps(response_data, indent=4)
    #                 return response_data
    #         else:
    #             response_data = {
    #                 'data': {
    #                     'status': 200,
    #                     'error': 'Invalid data',
    #                 }
    #             }
    #             # order_update_json = json.dumps(response_data, indent=4)
    #             return response_data
    #     except Exception as e:
    #         response_data = {
    #             'data': {
    #                 'status': 500,
    #                 'error': str(e)
    #             }
    #         }
    #         # order_update_json = json.dumps(response_data, indent=4)
    #         return response_data
    
    # @http.route('/api/order_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    # def order_update(self, **kwargs):
    #     try:
    #         base_url = 'https://furor-ginkgo-api-9183196.dev.odoo.com'
    #         db = 'furor-ginkgo-api-9183196'
    #         username = 'bilal.akhtar@edenrobe.com'
    #         password = '123456'
    #         common_url = f"{base_url}/xmlrpc/2/common"
    #         object_url = f"{base_url}/xmlrpc/2/object"
    #         common = xmlrpc.client.ServerProxy(common_url)
    #         uid = common.authenticate(db, username, password, {})
    #         if uid:
    #             models = xmlrpc.client.ServerProxy(object_url)
    #             request_json = request.httprequest.data.decode('utf-8')
    #             data = json.loads(request_json)
    #             if 'updateOrder' in data:
    #                 account_move_update = request.env['account.move'].sudo().search([('invoice_origin', '=', data['updateOrder']['orderId'])])
    #                 if not account_move_update:
    #                     stock_warehouse_check = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', data['updateOrder']['shopId'])])
    #                     if not stock_warehouse_check:
    #                         response_data = {
    #                             'data': {
    #                                 'status': 200,
    #                                 'error': 'Invaild Warehouse',
    #                             }
    #                         }
    #                         # order_posting_json = json.dumps(response_data, indent=4)
    #                         return response_data
    #                     order_id = data['updateOrder']['orderId']
    #                     shop_id = data['updateOrder']['shopId']
    #                     tele_phone = data['updateOrder']['customer']['Telephone']
    #                     email = data['updateOrder']['customer']['CustomerEmail']
    #                     first_name = data['updateOrder']['customer']['FirstName']
    #                     last_name = data['updateOrder']['customer']['LastName']
    #                     address1 = data['updateOrder']['customer']['Address1']
    #                     address2 = data['updateOrder']['customer']['Address2']
    #                     city = data['updateOrder']['customer']['City']
    #                     stock_picking_check = request.env['stock.picking'].sudo().search([('origin', '=', order_id)])
    #                     if stock_picking_check.state != 'done':
    #                         sale_order_update = request.env['sale.order'].sudo().search([('name', '=', order_id)])
    #                         if sale_order_update:
    #                             if sale_order_update.state == 'done':
    #                                 sale_order_update.write({
    #                                      'state': 'sale'
    #                                 })
    #                             if sale_order_update.state == 'sale':
    #                                 stock_picking_delete = request.env['stock.picking'].sudo().search([('sale_id', '=', sale_order_update.id)])
    #                                 if stock_picking_delete:
    #                                     stock_move_status_delete = request.env['stock.move'].sudo().search([('picking_id', '=', stock_picking_delete.id)])
    #                                     if stock_move_status_delete:
    #                                         stock_move_status_delete.write({
    #                                             'state': 'draft'
    #                                         })
    #                                         stock_move_line_status_delete = request.env['stock.move.line'].sudo().search([('picking_id', '=', stock_picking_delete.id)])
    #                                         for move_line_update in stock_move_line_status_delete:
    #                                             move_line_update.write({
    #                                                 'state': 'draft'
    #                                             })
    #                                         for line_update in stock_move_status_delete:
    #                                             line_update.write({
    #                                                 'state': 'draft'
    #                                             })
    #                                         for move_line in stock_move_line_status_delete:
    #                                             move_line.unlink()
    #                                         for line in stock_move_status_delete:
    #                                             line.unlink()
    #                                     stock_picking_delete.unlink()
    #                                 stock_warehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', shop_id)])
    #                                 if stock_warehouse:
    #                                     location_id = 696
    #                                 else:
    #                                     location_id = 4623
    #                                 sale_order_line_update = request.env['sale.order.line'].search([('order_id', '=', sale_order_update.id)])
    #                                 if sale_order_line_update:
    #                                     sale_order_update.write({
    #                                          'state': 'draft'
    #                                     })
    #                                     for line in sale_order_line_update:
    #                                         line.write({
    #                                              'state': 'draft'
    #                                         })
    #                                     for line in sale_order_line_update:
    #                                         line.unlink()
    #                                     sale_order_update.write({
    #                                         'warehouse_id': location_id
    #                                     })
    #                                     res_partner_update = request.env['res.partner'].sudo().search([('email', '=', email)])
    #                                     if res_partner_update:
    #                                         res_partner_update.write({
    #                                             'display_name': f"{first_name} {last_name}",
    #                                             'name': f"{first_name} {last_name}",
    #                                             'street': address1,
    #                                             'street2': address2,
    #                                             'city': city,
    #                                             'phone': tele_phone,
    #                                             'mobile': tele_phone,
    #                                         })
    #                                     sale_order_update.write({
    #                                          'state': 'sale'
    #                                     })
    #                                     # records_list = []
    #                                     for item in data['updateOrder']['items']:
    #                                         sku = item['SKU']
    #                                         qty = item['Quantity']
    #                                         unit_price = float(item['UnitPrice'])
    #                                         discount_amount = float(item['DiscountAmount'])
    #                                         product_template = request.env['product.template'].sudo().search([('default_code', '=', sku)])
    #                                         product_template_id = product_template[0].id
    #                                         product_product = request.env['product.product'].sudo().search([('default_code', '=', sku)])
    #                                         product_product_id = product_product[0].id
    #                                         taxes_ids = product_product[0].taxes_id.ids
    #                                         taxes_array = ','.join(map(str, taxes_ids))
    #                                         account_tax = request.env['account.tax'].sudo().search([('id', 'in', taxes_ids)])
    #                                         total_tax_percentage = sum(account_tax.mapped('amount'))
    #                                         total_tax_div = (total_tax_percentage/100)
    #                                         discount_value = (unit_price-product_product[0].list_price)
    #                                         taxes_discount = (product_product[0].list_price*total_tax_div)
    #                                         taxes_value = (total_tax_div+1)
    #                                         total_discount_value = ((discount_value-taxes_discount)/taxes_value)
    #                                         total_discount_percentage = ((total_discount_value/product_product[0].list_price*100)*-1)
    #                                         if product_product_id:
    #                                             order_line_data = {
    #                                                 'order_id': sale_order_update.id,
    #                                                 'product_id': product_product_id,
    #                                                 'product_template_id': product_template_id,
    #                                                 'product_uom_qty': qty,
    #                                                 'product_uom': qty,
    #                                                 'price_unit': product_product[0].list_price,
    #                                                 'discount': total_discount_percentage,
    #                                                 'company_id': 1,
    #                                                 'currency_id': 157,
    #                                                 'order_partner_id': res_partner_update.id,
    #                                                 'state': 'sale',
    #                                                 'qty_delivered_method': 'manual',
    #                                                 'customer_lead': 0.0,
    #                                                 'invoice_status': 'no',
    #                                             }
    #                                             request.env['sale.order.line'].sudo().create(order_line_data)
    #                                     #         record = [
    #                                     #             0,
    #                                     #             0,
    #                                     #             {
    #                                     #                 'product_id': product_product_id,
    #                                     #                 'product_template_id': product_template_id,
    #                                     #                 'product_uom_qty': qty,
    #                                     #                 'product_uom': qty,
    #                                     #                 'price_unit': unit_price - discount_amount,
    #                                     #                 'discount': discount_amount,
    #                                     #                 'company_id': 1,
    #                                     #                 'currency_id': 157,
    #                                     #                 'order_partner_id': res_partner_update.id,
    #                                     #                 'state': 'sale',
    #                                     #                 'qty_delivered_method': 'manual',
    #                                     #                 'customer_lead': 0.0,
    #                                     #                 'invoice_status': 'no',
    #                                     #             }
    #                                     #         ]
    #                                     #         records_list.append(record)
    #                                     # updated_data = {
    #                                     #     'state': 'sale',
    #                                     #     'order_line': records_list,
    #                                     #     'note': "Updated Sales Order",
    #                                     #     'user_id': uid,
    #                                     #     'team_id': 1
    #                                     # }
    #                                     # updated_sale_order = models.execute_kw(
    #                                     #     db, uid, password,
    #                                     #     'sale.order', 'write',
    #                                     #     [[sale_order_update.id], updated_data]
    #                                     # )
    #                                     if sale_order_update:
    #                                         response_data = {
    #                                             'data': {
    #                                                 'status': 200,
    #                                                 'success': True,
    #                                                 'message': 'Update Sale Order Successfully',
    #                                                 'sale_order_id': sale_order_update.id,
    #                                             }
    #                                         }
    #                                         # order_update_json = json.dumps(response_data, indent=4)
    #                                         return response_data
    #                                     else:
    #                                         response_data = {
    #                                             'data': {
    #                                                 'status': 200,
    #                                                 'error': 'Failed to update the Sales Order.',
    #                                             }
    #                                         }
    #                                         # order_posting_json = json.dumps(response_data, indent=4)
    #                                         return response_data
    #                                 else:
    #                                     response_data = {
    #                                         'data': {
    #                                             'status': 200,
    #                                             'error': 'No Sale Order Items',
    #                                         }
    #                                     }
    #                                     # order_posting_json = json.dumps(response_data, indent=4)
    #                                     return response_data
    #                             else:
    #                                 response_data = {
    #                                     'data': {
    #                                         'status': 200,
    #                                         'error': 'Order Status Is Not Sale',
    #                                     }
    #                                 }
    #                                 # order_update_json = json.dumps(response_data, indent=4)
    #                                 return response_data        
    #                         else:
    #                             response_data = {
    #                                 'data': {
    #                                     'status': 200,
    #                                     'error': 'No Sale Order Record',
    #                                 }
    #                             }
    #                             # order_update_json = json.dumps(response_data, indent=4)
    #                             return response_data                        
    #                     else:
    #                         response_data = {
    #                             'data': {
    #                                 'status': 200,
    #                                 'error': 'Delivery Order Status Only Draft/Waiting/Ready',
    #                             }
    #                         }
    #                         # order_update_json = json.dumps(response_data, indent=4)
    #                         return response_data
    #                 else:
    #                     response_data = {
    #                         'data': {
    #                             'status': 200,
    #                             'error': 'Sorry Invoice Create Already',
    #                         }
    #                     }
    #                     # order_posting_json = json.dumps(response_data, indent=4)
    #                     return response_data     
    #             else:
    #                 response_data = {
    #                     'data': {
    #                         'status': 200,
    #                         'error': 'Json Format Issues {salesOrder}',
    #                     }
    #                 }
    #                 # order_posting_json = json.dumps(response_data, indent=4)
    #                 return response_data
    #         else:
    #             response_data = {
    #                 'data': {
    #                     'status': 200,
    #                     'error': 'Authentication failed.',
    #                 }
    #             }
    #             # order_posting_json = json.dumps(response_data, indent=4)
    #             return response_data
    #     except Exception as e:
    #         response_data = {
    #             'data': {
    #                 'status': 500,
    #                 'error': str(e)
    #             }
    #         }
    #         # order_update_json = json.dumps(response_data, indent=4)
    #         return response_data

    @http.route('/api/order_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def order_update(self, **kwargs):
        try:
            base_url = 'https://furor-ginkgo-api-9183196.dev.odoo.com'
            db = 'furor-ginkgo-api-9183196'
            username = 'bilal.akhtar@edenrobe.com'
            password = '123456'
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
    
    @http.route('/api/fbt_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def fbt_update(self, **kwargs):
        try:
            request_json = request.httprequest.data.decode('utf-8')
            data = json.loads(request_json)
            order_id = data['updateOrder']['orderId']
            sale_order_update = request.env['sale.order'].sudo().search([('name', '=', order_id)])
            if sale_order_update:
                fbr_number = data['updateOrder']['FbrNumber']
                return_fbr_number = data['updateOrder']['ReturnFbrNumber']
                fbr_sale_update = request.env['sale.order'].sudo().search([('name', '=', order_id)])
                fbr_sale_update.write({
                    'fbr_number': fbr_number,
                    'return_fbr_number': return_fbr_number,
                })
                response_data = {
                    'data': {
                        'status': 200,
                        'success': True,
                        'message': 'Update Sale Order Successfully',
                    }
                }
                # fbt_update_json = json.dumps(response_data, indent=4)
                return response_data
            else:
                response_data = {
                    'data': {
                        'status': 200,
                        'error': 'No Sale Order Record',
                    }
                }
                # fbt_update_json = json.dumps(response_data, indent=4)
                return response_data
        except Exception as e:
            response_data = {
                'data': {
                    'status': 500,
                    'error': str(e)
                }
            }
            # fbt_update_json = json.dumps(response_data, indent=4)
            return response_data

