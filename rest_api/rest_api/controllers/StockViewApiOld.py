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


class StockViewApiOld(http.Controller):
    
    @http.route('/api/stock/view/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_stock_view(self, **kw):
        try:
            logger = logging.getLogger(__name__)
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