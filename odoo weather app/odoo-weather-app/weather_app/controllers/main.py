from odoo import http
from odoo.http import request

class WeatherController(http.Controller):

    @http.route('/weather', auth='public', type='json', methods=['GET'], csrf=False)
    def get_weather(self):
        # Logic to fetch weather data
        weather_data = {
            'temperature': 25,
            'humidity': 60,
            'description': 'Clear sky'
        }
        return weather_data

    @http.route('/weather/report', auth='public', type='http', methods=['GET'], csrf=False)
    def weather_report(self, **kwargs):
        # Logic to render weather report page
        return request.render('weather_app.weather_report_template', {})