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


class RestApi(http.Controller):

    @http.route('/api/sale_order_posting/create/', type='json', auth='public', methods=['POST'], cors="*", csrf=False)
    def create_sale_order_posting(self, **kwargs):
        try:
            BaseUrl = 'https://furor-ginkgo-api-9183196.dev.odoo.com'
            DB = 'furor-ginkgo-api-9183196'
            UserName = 'bilal.akhtar@edenrobe.com'
            Password = '123456'
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
                    if not SaleOrderCheck:
                        StockWarehouseCheck = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', int(Data['salesOrder']['shopId']))])
                        if not StockWarehouseCheck:
                            ResponseData = {
                                'data': {
                                    'status': 200,
                                    'success': True,
                                    'error': 'Invaild Warehouse'
                                }
                            }
                            return ResponseData
                        OrderStatus = Data['salesOrder']['OrderStatus']
                        Status = Data['salesOrder']['status']
                        OrderId = Data['salesOrder']['OrderId']
                        ShopId = Data['salesOrder']['shopId']
                        OrderDate = Data['salesOrder']['OrderDate']
                        FirstName = Data['salesOrder']['FirstName']
                        LastName = Data['salesOrder']['LastName']
                        CustomerEmail = Data['salesOrder']['CustomerEmail']
                        Address = Data['salesOrder']['Address']
                        DiscountVoucher = Data['salesOrder']['DiscountVoucher']
                        TotalQty = Data['salesOrder']['TotalQty']
                        HeaderDiscountPercentage = Data['salesOrder']['HeaderDiscountPercentage']
                        DiscountType = Data['salesOrder']['DiscountType']
                        Discount = Data['salesOrder']['Discount']
                        City = Data['salesOrder']['City']
                        Country = Data['salesOrder']['Country']
                        CountryCode = Data['salesOrder']['CountryCode']
                        CourierName = Data['salesOrder']['CourierName']
                        CourierCN = Data['salesOrder']['CourierCN']
                        Telephone = Data['salesOrder']['Telephone']
                        ShippingCost = Data['salesOrder']['ShippingCost']
                        FBRCharges = Data['salesOrder']['FBRCharges']
                        FBRId = Data['salesOrder']['FBRId']
                        PaymentSourceType = Data['salesOrder']['PaymentSourceType']
                        StockWarehouse = request.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', int(ShopId))])
                        if StockWarehouse:
                            LocationId = StockWarehouse[0].id
                        else:
                            LocationId = 4623
                        ResCountry = request.env['res.country'].sudo().search([('name', 'like', Country)])
                        if ResCountry:
                            CountryId = ResCountry[0].id
                            CountryName = ResCountry[0].name
                        else:
                            ResCountries = request.env['res.country'].sudo().create({
                                'name': CourierName,
                                'code': CountryCode
                            })
                            CountryId = ResCountries[0].id
                            CountryName = ResCountries[0].name
                        ResState = request.env['res.country.state'].sudo().search([('country_id', '=', CountryId)])
                        if ResState:
                            StateId = ResState[0].id
                            StateName = ResState[0].name
                        else:
                            ResStates = request.env['res.country.state'].sudo().create({
                                'country_id': ResCountry[0].id,
                                'name': 'Null',
                                'code': 'Null'
                            })
                            StateId = ResStates[0].id
                            StateName = ResStates[0].name
                        UtmSource = request.env['utm.source'].sudo().search([('name', 'like', 'Ginkgo')])
                        if UtmSource:
                            SourceId = UtmSource[0].id
                        else:
                            UtmSources = request.env['utm.source'].sudo().create({
                                'name': 'Ginkgo',
                            })
                            SourceId = UtmSources[0].id
                        ResPartner = request.env['res.partner'].sudo().search([('email', '=', CustomerEmail)])
                        if ResPartner:
                            ResPartner[0].write({
                                'display_name': f"{FirstName} {LastName}",
                                'name': f"{FirstName} {LastName}",
                                'street': Address,
                                'country_id': CountryId,
                                'state_id': StateId,
                                'city': City,
                                'phone': Telephone,
                                'mobile': Telephone,
                                'contact_address_complete': f"{Address}, {City}, {StateName}, {CountryName}",
                            })
                            PartnerId = ResPartner[0].id
                        else:
                            ResPartners = request.env['res.partner'].sudo().create({
                                'company_id': 1,
                                'display_name': f"{FirstName} {LastName}",
                                'name': f"{FirstName} {LastName}",
                                'email': CustomerEmail,
                                'street': Address,
                                'country_id': CountryId,
                                'state_id': StateId,
                                'city': City,
                                'phone': Telephone,
                                'mobile': Telephone,
                                'contact_address_complete': f"{Address}, {City}, {StateName}, {CountryName}",
                            })
                            PartnerId = ResPartners[0].id
                        Models = xmlrpc.client.ServerProxy(ObjectUrl)
                        RecordsList = []
                        for ProductData in Data['salesOrder']['Products']:
                            Sku = ProductData['sku']
                            Qty = ProductData['Qty']
                            DiscountAmount = float(ProductData['DiscountAmount'])
                            UnitPrice = float(ProductData['UnitPrice'])
                            ProductTemplate = request.env['product.template'].sudo().search([('barcode', '=', Sku)])
                            ProductTemplateId = ProductTemplate[0].id
                            ProductProduct = request.env['product.product'].sudo().search([('barcode', '=', Sku)])
                            ProductProductId = ProductProduct[0].id
                            # TaxesIds = ProductProduct[0].taxes_id.ids
                            # TaxesArray = ','.join(map(str, TaxesIds))
                            # AccountTax = request.env['account.tax'].sudo().search([('id', 'in', TaxesIds)])
                            # TotalTaxPercentage = sum(AccountTax.mapped('amount'))
                            # TotalTaxDiv = (TotalTaxPercentage/100)
                            # DiscountValue = (UnitPrice-ProductProduct[0].list_price)
                            # TaxesDiscount = (ProductProduct[0].list_price*TotalTaxDiv)
                            # TaxesValue = (TotalTaxDiv+1)
                            # TotalDiscountValue = ((DiscountValue-TaxesDiscount)/TaxesValue)
                            # TotalDiscountPercentage = ((TotalDiscountValue/ProductProduct[0].list_price*100)*-1)
                            if ProductProductId:
                                RecordData = [
                                    0,
                                    0,
                                    {
                                        'product_id': ProductProductId,
                                        'product_template_id': ProductTemplateId,
                                        'product_uom_qty': Qty,
                                        'product_uom': Qty,
                                        'price_unit': ProductProduct[0].list_price,
                                        'discount': DiscountAmount,
                                        'company_id': 1,
                                        'currency_id': 157,
                                        'order_partner_id': PartnerId,
                                        'state': 'sale',
                                        'qty_delivered_method': 'manual',
                                        'customer_lead': 0.0,
                                        'invoice_status': 'no',
                                    }
                                ]
                                RecordsList.append(RecordData)
                        RecordDataNew = [
                            0,
                            0,
                            {
                                'product_id': 26834,
                                'product_template_id': 6155,
                                'name': 'DHL',
                                'product_uom_qty': 1,
                                'product_uom': 1,
                                'price_unit': ShippingCost,
                                'tax_id': False,
                                'discount': 0.00,
                                'company_id': 1,
                                'currency_id': 157,
                                'order_partner_id': PartnerId,
                                'state': 'sale',
                                'qty_delivered_method': 'manual',
                                'customer_lead': 0.0,
                                'invoice_status': 'no',
                            }
                        ]
                        RecordsList.append(RecordDataNew)
                        SaleOrderData = {
                            'name': OrderId,
                            'partner_id': PartnerId,
                            'partner_invoice_id': PartnerId,
                            'partner_shipping_id': PartnerId,
                            'date_order': OrderDate,
                            'company_id': 1,
                            'warehouse_id': LocationId,
                            'state': 'sale',
                            'pricelist_id': 1,
                            'currency_id': 157,
                            'source_id': SourceId,
                            'order_line': RecordsList,
                            'post_data_fbr': True,
                            'invoice_number': FBRId,
                            'note': "Ginkgo Sale Order",
                            'user_id': UID,
                            'team_id': 1
                        }
                        SaleOrderId = Models.execute_kw(
                            DB, UID, Password,
                            'sale.order', 'create',
                            [SaleOrderData]
                        )
                        if SaleOrderId:
                            ResponseData = {
                                'data': {
                                    'status': 200,
                                    'success': True,
                                    'message': 'Record Insert Successfully'
                                }
                            }
                            return ResponseData
                        else:
                            ResponseData = {
                                'data': {
                                    'status': 200,
                                    'success': True,
                                    'error': 'Failed to create the Sales Order.'
                                }
                            }
                            return ResponseData
                    else:
                        ResponseData = {
                            'data': {
                                'status': 200,
                                'success': True,
                                'error': 'Already Insert Sale Order.'
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

    @http.route('/api/sale_order_status/update/', type='json', auth='public', methods=['PUT'], cors="*", csrf=False)
    def update_sale_order_status(self, **kwargs):
        try:
            BaseUrl = 'https://furor-ginkgo-api-9183196.dev.odoo.com'
            DB = 'furor-ginkgo-api-9183196'
            UserName = 'bilal.akhtar@edenrobe.com'
            Password = '123456'
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
