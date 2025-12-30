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
                                    taxes_ids = product[0].taxes_id.ids
                                    account_tax = request.env['account.tax'].sudo().search([('id', 'in', taxes_ids)])
                                    total_tax_percentage = sum(account_tax.mapped('amount'))
                                    stock_dict = {
                                        'ShopId': stock.location_id.id,
                                        'SKU': product.barcode,
                                        'BarCode': product.barcode,
                                        'SalesTaxes': str(total_tax_percentage) + '%',
                                        'HSCode': product.hs_code,
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

            