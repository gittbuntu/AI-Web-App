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


class PriceApiOld(http.Controller):
    
    @http.route('/api/price/', type='http', auth='public', methods=['GET'], cors="*", csrf=False)
    def get_price(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
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