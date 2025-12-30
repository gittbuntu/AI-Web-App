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


class FbtUpdateApi(http.Controller):
    
    @http.route('/api/fbt_update/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def fbt_update(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
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

