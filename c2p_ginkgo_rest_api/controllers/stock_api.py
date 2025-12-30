from odoo import http
from odoo.http import request, Response
import json
import pycountry

class StockAPI(http.Controller):

    @http.route('/api/stock/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_stock(self, **kwargs):
        try:
            stocks = request.env['stock.quant'].sudo().search([])
            stock_data = []
            for stock in stocks:
                if stock.product_id.id:
                    products = request.env['product.product'].sudo().search([('id', '=', stock.product_id.id)])
                    for product in products:
                        if product.product_tmpl_id.id:
                            products_templates = request.env['product.template'].sudo().search([('id', '=', product.product_tmpl_id.id)])
                            for product_template in products_templates:
                                if product_template.default_code:
                                    stock_dict = {
                                        'ShopId': stock.id,
                                        'SKU': product_template.default_code,
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

    @http.route('/api/stock/view/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_stock_view(self, **kw):
        try:
            stock_query_params = http.request.params
            stock_params = []
            for key in stock_query_params:
                if isinstance(stock_query_params[key], str):
                    if stock_query_params[key].isdigit():
                        stock_params.append((f'{key}', '=', int(stock_query_params[key])))
                    else:
                        stock_params.append((f'{key}', '=', str(stock_query_params[key])))
                elif isinstance(stock_query_params[key], int):
                    stock_params.append((f'{key}', '=', int(stock_query_params[key])))
                elif isinstance(stock_query_params[key], bool):
                    stock_params.append((f'{key}', '=', str(stock_query_params[key])))
            stocks = request.env['stock.quant'].sudo().search(stock_params)
            stock_data = []
            for stock in stocks:
                if stock.product_id.id:
                    products = request.env['product.product'].sudo().search([('id', '=', stock.product_id.id)])
                    for product in products:
                        if product.product_tmpl_id.id:
                            products_templates = request.env['product.template'].sudo().search([('id', '=', product.product_tmpl_id.id)])
                            for product_template in products_templates:
                                if product_template.default_code:
                                    stock_dict = {
                                        'ShopId': stock.id,
                                        'SKU': product_template.default_code,
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

    @http.route('/api/price/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_price(self, **kwargs):
        try:
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
                                if product_template.default_code:
                                    productpricelistitem = request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', product.product_tmpl_id.id)])
                                    discount_price = productpricelistitem.fixed_price if productpricelistitem.fixed_price else 0.0
                                    price_dict = {
                                        'SKU': product_template.default_code,
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

    @http.route('/api/price/view/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_price_view(self, **kw):
        try:
            price_query_params = http.request.params
            price_params = []
            for key in price_query_params:
                if isinstance(price_query_params[key], str):
                    if price_query_params[key].isdigit():
                        price_params.append((f'{key}', '=', int(price_query_params[key])))
                    else:
                        price_params.append((f'{key}', '=', str(price_query_params[key])))
                elif isinstance(price_query_params[key], int):
                    price_params.append((f'{key}', '=', int(price_query_params[key])))
                elif isinstance(price_query_params[key], bool):
                    price_params.append((f'{key}', '=', str(price_query_params[key])))
            prices = request.env['stock.quant'].sudo().search(price_params)
            price_data = []
            for price in prices:
                if price.product_id.id:
                    products = request.env['product.product'].sudo().search([('id', '=', price.product_id.id)])
                    for product in products:
                        if product.product_tmpl_id.id:
                            products_templates = request.env['product.template'].sudo().search(
                                [('id', '=', product.product_tmpl_id.id)])
                            for product_template in products_templates:
                                if product_template.default_code:
                                    productpricelistitem = request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', product.product_tmpl_id.id)])
                                    discount_price = productpricelistitem.fixed_price if productpricelistitem.fixed_price else 0.0
                                    price_dict = {
                                        'SKU': product_template.default_code,
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

    @http.route('/api/order_posting/create/', type='http', auth='public', methods=['POST'], cors="*", csrf=False)
    def create_order_posting(self, **kwargs):
        try:
            request_json = http.request.httprequest.get_data().decode('utf-8')
            data = json.loads(request_json)
            if 'salesOrder' in data:
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
                sale_order_data = {
                    'partner_id': partner_id,
                    'date_order': order_date,
                    'company_id': 1,
                    'state': 'sale',
                    'pricelist_id': 1,
                    'currency_id': 157,
                    'source_id': source_id,
                }
                sale_order = request.env['sale.order'].sudo().create(sale_order_data)
                for product in data['salesOrder']['Products']:
                    sku = product['SKU']
                    qty = product['Qty']
                    unit_price = float(product['UnitPrice'])
                    discount_amount = float(product['DiscountAmount'])
                    product_tmpl = request.env['product.product'].sudo().search([('default_code', '=', sku)])
                    if product_tmpl:
                        product_tmpl_id = product_tmpl.product_tmpl_id.id
                        order_line_data = {
                            'order_id': sale_order.id,
                            'product_id': product_tmpl_id,
                            'product_uom_qty': qty,
                            'price_unit': unit_price - discount_amount,
                            'discount': discount_amount,
                            'company_id': 1,
                            'currency_id': 157,
                            'order_partner_id': partner_id,
                            'state': 'sale',
                            'qty_delivered_method': 'manual',
                            'customer_lead': 0.0,
                            'invoice_status': 'no',
                        }
                        request.env['sale.order.line'].sudo().create(order_line_data)
                response_data = {
                    'data': {
                        'success': True,
                        'message': 'Record Insert Successfully',
                        'sale_order_id': sale_order.id
                    }
                }
                order_posting_json = json.dumps(response_data, indent=4)
                return Response(order_posting_json, content_type='application/json', status=200)
            else:
                response_data = {
                    'data': {
                        'error': 'Invalid data',
                    }
                }
                order_posting_json = json.dumps(response_data, indent=4)
                return Response(order_posting_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            order_posting_json = json.dumps(response_data, indent=4)
            return Response(order_posting_json, content_type='application/json', status=500)

    @http.route('/api/get_order_status/', type='http', auth='public', methods=['POST'], cors="*", csrf=False)
    def get_order_status(self, **kwargs):
        try:
            request_json = http.request.httprequest.get_data().decode('utf-8')
            data = json.loads(request_json)
            sale_order = request.env['sale.order'].sudo().search([('name', '=', data['orderId'])])
            order_status_get = []
            for saleorder in sale_order:
                order_status_get.append({
                    'OrderId': saleorder.name,
                    'Status': saleorder.state,
                })
            print(order_status_get)

            response_data = {
                'data': {
                    'success': True,
                    'order_status': order_status_get
                }
            }
            order_status_json = json.dumps(response_data, indent=4)
            return Response(order_status_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            order_posting_json = json.dumps(response_data, indent=4)
            return Response(order_posting_json, content_type='application/json', status=500)

    @http.route('/api/order_fulfillment/update/', type='http', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_fulfillment(self, **kwargs):
        try:
            request_json = http.request.httprequest.get_data().decode('utf-8')
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
                            'success': True,
                            'message': 'Update Delivery Orders Successfully',
                        }
                    }
                    stock_picking_json = json.dumps(response_data, indent=4)
                    return Response(stock_picking_json, content_type='application/json', status=200)
                else:
                    response_data = {
                        'data': {
                            'success': True,
                            'message': 'Sorry No Delivery Orders',
                        }
                    }
                    stock_picking_json = json.dumps(response_data, indent=4)
                    return Response(stock_picking_json, content_type='application/json', status=200)
            else:
                response_data = {
                    'data': {
                        'success': True,
                        'message': 'Sorry No Shipping Methods Add or Your Please Add Shipping Methods',
                    }
                }
                stock_picking_json = json.dumps(response_data, indent=4)
                return Response(stock_picking_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            order_posting_json = json.dumps(response_data, indent=4)
            return Response(order_posting_json, content_type='application/json', status=500)

    @http.route('/api/update_order_status/update/', type='http', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_status(self, **kwargs):
        try:
            request_json = http.request.httprequest.get_data().decode('utf-8')
            data = json.loads(request_json)
            order_status_update = request.env['sale.order'].sudo().search([('name', '=', data['orderId'])])
            if order_status_update:
                order_status_update.write({
                    'state': data['Status'],
                })
                response_data = {
                    'data': {
                        'success': True,
                        'message': 'Update Order Status Successfully',
                    }
                }
                order_status_update_json = json.dumps(response_data, indent=4)
                return Response(order_status_update_json, content_type='application/json', status=200)
            else:
                response_data = {
                    'data': {
                        'success': True,
                        'message': 'No Order Record',
                    }
                }
                order_status_update_json = json.dumps(response_data, indent=4)
                return Response(order_status_update_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            order_posting_json = json.dumps(response_data, indent=4)
            return Response(order_posting_json, content_type='application/json', status=500)

    @http.route('/api/order_update/update/', type='http', auth='public', methods=['PUT'], cors="*", csrf=False)
    def order_update(self, **kwargs):
        try:
            request_json = http.request.httprequest.get_data().decode('utf-8')
            data = json.loads(request_json)
            if 'updateOrder' in data:
                order_id = data['updateOrder']['orderId']
                shop_id = data['updateOrder']['shopId']
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
                            product_tmpl = request.env['product.product'].sudo().search([('default_code', '=', sku)])
                            product_tmpl_id = product_tmpl.product_tmpl_id.id
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
                                'success': True,
                                'message': 'Update Sale Order Successfully',
                            }
                        }
                        order_update_json = json.dumps(response_data, indent=4)
                        return Response(order_update_json, content_type='application/json', status=200)
                    else:
                        response_data = {
                            'data': {
                                'error': 'Order Status Is Not Sale',
                            }
                        }
                        order_update_json = json.dumps(response_data, indent=4)
                        return Response(order_update_json, content_type='application/json', status=200)
                    #
                    # data['updateOrder']['customer']
                else:
                    response_data = {
                        'data': {
                            'error': 'No Sale Order Record',
                        }
                    }
                    order_update_json = json.dumps(response_data, indent=4)
                    return Response(order_update_json, content_type='application/json', status=200)
            else:
                response_data = {
                    'data': {
                        'error': 'Invalid data',
                    }
                }
                order_update_json = json.dumps(response_data, indent=4)
                return Response(order_update_json, content_type='application/json', status=200)
        except Exception as e:
            response_data = {
                'error': str(e)
            }
            order_update_json = json.dumps(response_data, indent=4)
            return Response(order_update_json, content_type='application/json', status=500)
