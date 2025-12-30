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


class OrderFulfillmentUpdateApi(http.Controller):
    
    @http.route('/api/order_fulfillment/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_fulfillment(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
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