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


class SaleOrderStatusApi(http.Controller):
   
    @http.route('/api/sale_order_status/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_sale_order_status(self, **kwargs):
        try:
            logger = logging.getLogger(__name__)
            BaseUrl = 'https://furor.odoo.com'
            DB = 'effjayapparel-furor-furor-prod-2368041'
            UserName = 'api@edenrobe.com'
            Password = 'apieden123!@#'
            CommonUrl = f"{BaseUrl}/xmlrpc/2/common"
            ObjectUrl = f"{BaseUrl}/xmlrpc/2/object"
            Common = xmlrpc.client.ServerProxy(CommonUrl)
            UID = Common.authenticate(DB, UserName, Password, {})
            if UID:
                RequestJson = request.httprequest.data.decode('utf-8')
                Data = json.loads(RequestJson)
                logger = logging.getLogger(__name__)
                if 'salesOrder' in Data:
                    SaleOrderCheck = request.env['sale.order'].sudo().search([('name', '=', Data['salesOrder']['OrderId'])])
                    if SaleOrderCheck:
                        Models = xmlrpc.client.ServerProxy(ObjectUrl)
                        if Data['salesOrder']['status'] == 'Delivered':
                            OrderId = Data['salesOrder']['OrderId']
                            Status = Data['salesOrder']['status']
                            CourierName = Data['salesOrder']['CourierName']
                            CourierCN = Data['salesOrder']['CourierCN']
                            StockPickingUpdate = request.env['stock.picking'].sudo().search([('sale_id', '=', int(SaleOrderCheck.id))])
                            DeliveryCarrier = request.env['delivery.carrier'].sudo().search([('name', '=', CourierName)])
                            if DeliveryCarrier:
                                DeliveryCarriers = DeliveryCarrier[0].id
                            else:
                                DeliveryCarriers = False
                            if StockPickingUpdate:
                                StockPickingUpdate.write({
                                    'carrier_id': DeliveryCarriers,
                                    'carrier_tracking_ref': CourierCN,
                                    'state': 'done'
                                })
                                StockMoveUpdate = request.env['stock.move'].sudo().search([('picking_id', '=', StockPickingUpdate.id)])
                                if StockMoveUpdate:
                                    for MoveLine in StockMoveUpdate:
                                        MoveLine.write({
                                            'quantity_done': MoveLine.product_uom_qty,
                                            'state': 'done'
                                        })
                            ResponseData = {
                                'data': {
                                    'status': 200,
                                    'success': True,
                                    'message': 'Record Update Delivered Status Successfully'
                                }
                            }
                            return ResponseData
                        elif Data['salesOrder']['status'] == 'Returned':
                            StockPickingUpdate = request.env['stock.picking'].sudo().search([('state', '=', 'done'), ('origin', '=', Data['salesOrder']['OrderId'])])
                            if StockPickingUpdate:
                                StockWarehouseUpdate = request.env['stock.warehouse'].sudo().search([('name', 'like', 'Online Warehouse')])
                                if StockWarehouseUpdate:
                                    StockWarehouseId = StockWarehouseUpdate[0].id
                                else:
                                    StockWarehouseId = 0
                                StockPickingTypeUpdate = request.env['stock.picking.type'].sudo().search([('warehouse_id', '=', StockWarehouseId), ('name', 'like', 'Delivery Orders')])
                                StockPickingTypeReceiptUpdate = request.env['stock.picking.type'].sudo().search([('warehouse_id', '=', StockWarehouseId), ('name', 'like', 'Receipts')])
                                StockLocationUpdate = request.env['stock.location'].sudo().search([('name', '=', 'Customers')])
                                ParentLocationUpdate = request.env['stock.location'].sudo().search([('name', '=', 'Online Warehouse')])
                                if ParentLocationUpdate:
                                    ParentLocationId= ParentLocationUpdate[0].id
                                else:
                                    ParentLocationId = 0
                                ParentLocationUpdateCheck = request.env['stock.location'].sudo().search([('id', '=', StockPickingUpdate[0].location_id.id)])
                                if ParentLocationUpdateCheck:
                                    ParentLocationCheckId = ParentLocationUpdateCheck[0].id
                                else:
                                    ParentLocationCheckId = ParentLocationUpdate[0].id
                                OriginalLocation = request.env['stock.location'].sudo().search([('location_id', '=', ParentLocationId), ('name', '=', 'Stock')])
                                OriginalLocationCheck = request.env['stock.location'].sudo().search([('id', '=', ParentLocationCheckId), ('name', '=', 'Stock')])
                                if OriginalLocationCheck:
                                    OriginalLocationCheckId = OriginalLocationCheck[0].id
                                else:
                                    OriginalLocationCheckId = OriginalLocation[0].id
                                ParentLocation = request.env['stock.location'].sudo().search([('name', '=', 'WH')])
                                if StockPickingTypeUpdate:
                                    PickingTypeId = StockPickingTypeUpdate[0].id
                                else:
                                    PickingTypeId = 0
                                if StockPickingTypeReceiptUpdate:
                                    StockPickingTypeReceiptId = StockPickingTypeReceiptUpdate[0].id
                                else:
                                    StockPickingTypeReceiptId = 0
                                if StockLocationUpdate:
                                    LocationId = StockLocationUpdate[0].id
                                else:
                                    LocationId = 0
                                if OriginalLocation:
                                    OriginalLocationId = OriginalLocation[0].id
                                else:
                                    OriginalLocationId = 0
                                if ParentLocation:
                                    ParentLocationId = ParentLocation[0].id
                                else:
                                    ParentLocationId = 0
                                ReturnData = {
                                    'location_id': LocationId,
                                    'location_dest_id': OriginalLocationCheckId,
                                    'picking_type_id': StockPickingTypeReceiptId,
                                    'partner_id': StockPickingUpdate[0].partner_id.id,
                                    'company_id': StockPickingUpdate[0].company_id.id,
                                    'origin': f'Return of {StockPickingUpdate[0].name}',
                                    'move_type': StockPickingUpdate[0].move_type,
                                    'is_locked': True,
                                    'sale_id': StockPickingUpdate[0].sale_id.id,
                                    'carrier_price': 0.0,
                                }
                                StockPicking = request.env['stock.picking'].sudo().create(ReturnData)
                                StockPickingLastUpdate = request.env['stock.picking'].sudo().search([('id', '=', StockPicking[0].id)])
                                if StockPickingLastUpdate:
                                    StockPickingLastUpdate.write({
                                        'group_id': StockPickingUpdate[0].group_id.id,
                                        'state': 'assigned',
                                        'weight': StockPickingUpdate[0].weight,
                                    })
                                StockReturnPickingData = {
                                    'picking_id': StockPickingUpdate[0].id,
                                    'original_location_id': OriginalLocationCheckId,
                                    'parent_location_id': ParentLocationCheckId,
                                }
                                StockReturnPicking = request.env['stock.return.picking'].sudo().create(StockReturnPickingData)
                                StockLines = request.env['stock.move'].sudo().search([('picking_id', '=', StockPickingUpdate[0].id)])
                                for Line in StockLines:
                                    return_line_data = {
                                        'sequence': Line.sequence,
                                        'company_id': Line.company_id.id,
                                        'product_id': Line.product_id.id,
                                        'product_uom': Line.product_uom.id,
                                        'location_id': LocationId,
                                        'location_dest_id': OriginalLocationCheckId,
                                        'partner_id': Line.partner_id.id,
                                        'picking_id': StockPicking.id,
                                        'group_id': Line.group_id.id,
                                        'rule_id': Line.rule_id.id,
                                        'picking_type_id': StockPickingTypeReceiptId,
                                        'origin_returned_move_id': Line.id,
                                        'warehouse_id': Line.warehouse_id.id,
                                        'next_serial_count': 0,
                                        'name': Line.name,
                                        'origin': Line.origin,
                                        'procure_method': Line.procure_method,
                                        'description_picking': Line.description_picking,
                                        'product_uom_qty': Line.product_uom_qty,
                                        'sale_line_id': Line.sale_line_id.id,
                                    }
                                    Moves = request.env['stock.move'].sudo().create(return_line_data)
                                    StockMoveLastUpdate = request.env['stock.move'].sudo().search([('id', '=', Moves[0].id)])
                                    if StockMoveLastUpdate:
                                        StockMoveLastUpdate.write({
                                            'state': 'assigned',
                                            'weight': Line.weight
                                        })
                                StockPickingStatusUpdate = request.env['stock.picking'].sudo().search([('id', '=', StockPickingLastUpdate[0].id)])
                                if StockPickingStatusUpdate:
                                    StockPickingStatusUpdate.write({
                                        'state': 'done'
                                    })
                                    StockMoveStatusUpdate = request.env['stock.move'].sudo().search([('picking_id', '=', StockPickingStatusUpdate[0].id)])
                                    if StockMoveStatusUpdate:
                                        for Move in StockMoveStatusUpdate:
                                            Move.write({
                                                'quantity_done': Move.product_uom_qty,
                                                'state': 'done'
                                            })
                                SaleOrderLineUpdate = request.env['sale.order.line'].sudo().search([('order_id', '=', SaleOrderCheck[0].id)])
                                for Line in SaleOrderLineUpdate:
                                    Line.write({
                                        'qty_delivered': 0,
                                    })
                                ResponseData = {
                                    'data': {
                                        'status': 200,
                                        'success': True,
                                        'message': 'Update Order Status Returned Successfully',
                                    }
                                }
                                return ResponseData
                            else:
                                ResponseData = {
                                    'data': {
                                        'status': 200,
                                        'success': True,
                                        'message': 'Please Delivery Order Status Posted',
                                    }
                                }
                                return ResponseData
                    else:
                        ResponseData = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'error': 'No Record Sale Order.'
                            }
                        }
                        return ResponseData
                else:
                    ResponseData = {
                        'data': {
                            'status': 200,
                            'success': True,
                            'error': 'Json Format Issues {salesOrder}'
                        }
                    }
                    return ResponseData
            else:
                ResponseData = {
                    'data': {
                        'status': 200,
                        'success': True,
                        'error': 'Authentication failed.'
                    }
                }
                return ResponseData
        except Exception as e:
            ResponseData = {
                'data': {
                    'status': 500,
                    'success': True,
                    'error': str(e)
                }
            }
            return ResponseData
