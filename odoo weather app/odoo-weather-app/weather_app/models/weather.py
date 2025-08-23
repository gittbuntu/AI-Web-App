from odoo import models, fields

class Weather(models.Model):
    _name = 'weather.app'
    _description = 'Weather Information'

    name = fields.Char(string='Location', required=True)
    temperature = fields.Float(string='Temperature (°C)')
    humidity = fields.Float(string='Humidity (%)')
    description = fields.Text(string='Description')
    date = fields.Datetime(string='Date Recorded', default=fields.Datetime.now)

    