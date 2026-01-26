"""
Design Storage
Author: KAKAROTONCLOUD
"""
from datetime import datetime

class DesignStorage:
    def create_design_snapshot(self, data, name):
        return {
            'design_name': name,
            'date_readable': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'data': data
        }

# Simple templates to get started
DESIGN_TEMPLATES = {
    'default': {
        'name': 'Default Water-Water',
        'key': 'default',
        'description': 'Standard test case',
        'defaults': {
            'T_hot_in': 90, 'T_hot_out': 50, 'm_hot': 2.0,
            'T_cold_in': 25, 'T_cold_out': 45, 'm_cold': 3.0,
            'U_value': 800
        }
    }
}

def list_available_templates():
    return [DESIGN_TEMPLATES['default']]
