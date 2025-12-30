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


class OrderStatusUpdateApi(http.Controller):
    
    @http.route('/api/update_order_status/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_order_status(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
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