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


class PriceApi(http.Controller):

    @http.route('/api/price/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_price(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
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