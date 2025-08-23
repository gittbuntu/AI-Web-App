{
    "name": "Weather App",
    "version": "1.0",
    "category": "Tools",
    "summary": "A simple weather application for Odoo.",
    "description": "This module provides weather data including temperature, humidity, and other related information.",
    "author": "Your Name",
    "website": "http://www.yourwebsite.com",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/weather_view.xml",
        "views/templates.xml"
    ],
    "installable": true,
    "application": true,
    "auto_install": false
}