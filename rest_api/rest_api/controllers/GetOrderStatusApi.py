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


class GetOrderStatusApi(http.Controller):
    
    @http.route('/api/get_order_status/', type='json', auth='public', methods=['POST'], cors="*", csrf=False)
    def get_order_status(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
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