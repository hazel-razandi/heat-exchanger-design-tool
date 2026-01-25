"""
Design Storage Module
Save and load heat exchanger designs using browser localStorage via Streamlit.
"""

import json
from datetime import datetime


class DesignStorage:
    """
    Manage saving and loading of heat exchanger designs.
    Note: This uses Streamlit's session state for storage.
    For persistent storage, users can export/import JSON files.
    """
    
    def __init__(self):
        """Initialize design storage."""
        pass
    
    def create_design_snapshot(self, design_data, design_name=None):
        """
        Create a snapshot of current design with metadata.
        
        Args:
            design_data (dict): All design parameters and results
            design_name (str): Custom name for the design
            
        Returns:
            dict: Design snapshot with metadata
        """
        timestamp = datetime.now()
        
        if not design_name:
            design_name = f"Design_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        snapshot = {
            'design_name': design_name,
            'timestamp': timestamp.isoformat(),
            'date_readable': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'data': design_data
        }
        
        return snapshot
    
    def export_design_json(self, design_snapshot):
        """
        Export design as JSON string for download.
        
        Args:
            design_snapshot (dict): Design snapshot
            
        Returns:
            str: JSON string
        """
        return json.dumps(design_snapshot, indent=2)
    
    def import_design_json(self, json_string):
        """
        Import design from JSON string.
        
        Args:
            json_string (str): JSON string
            
        Returns:
            dict: Design snapshot or None if invalid
        """
        try:
            design = json.loads(json_string)
            
            # Validate required fields
            if 'design_name' not in design or 'data' not in design:
                return None
            
            return design
        except json.JSONDecodeError:
            return None
    
    def create_design_comparison(self, designs_list):
        """
        Create comparison data for multiple designs.
        
        Args:
            designs_list (list): List of design snapshots
            
        Returns:
            dict: Comparison data
        """
        if not designs_list or len(designs_list) < 2:
            return None
        
        comparison = {
            'n_designs': len(designs_list),
            'designs': [],
            'best_by_effectiveness': None,
            'best_by_area': None,
            'best_by_cost': None
        }
        
        best_eff = 0
        best_eff_design = None
        min_area = float('inf')
        min_area_design = None
        
        for design in designs_list:
            data = design.get('data', {})
            results = data.get('results', {})
            
            design_summary = {
                'name': design.get('design_name', 'Unnamed'),
                'date': design.get('date_readable', 'N/A'),
                'effectiveness': results.get('effectiveness', 0),
                'area': results.get('area', 0),
                'Q': results.get('Q', 0),
                'NTU': results.get('NTU', 0)
            }
            
            comparison['designs'].append(design_summary)
            
            # Track best effectiveness
            if design_summary['effectiveness'] > best_eff:
                best_eff = design_summary['effectiveness']
                best_eff_design = design_summary['name']
            
            # Track minimum area
            if design_summary['area'] < min_area and design_summary['area'] > 0:
                min_area = design_summary['area']
                min_area_design = design_summary['name']
        
        comparison['best_by_effectiveness'] = best_eff_design
        comparison['best_by_area'] = min_area_design
        
        return comparison
    
    def generate_design_summary(self, design_snapshot):
        """
        Generate human-readable summary of a design.
        
        Args:
            design_snapshot (dict): Design snapshot
            
        Returns:
            str: Summary text
        """
        data = design_snapshot.get('data', {})
        results = data.get('results', {})
        inputs = data.get('inputs', {})
        
        summary_lines = []
        summary_lines.append(f"Design: {design_snapshot.get('design_name', 'Unnamed')}")
        summary_lines.append(f"Date: {design_snapshot.get('date_readable', 'N/A')}")
        summary_lines.append("")
        summary_lines.append("Configuration:")
        summary_lines.append(f"  Flow: {results.get('flow_type', 'N/A')}")
        summary_lines.append(f"  Method: {results.get('method', 'N/A')}")
        summary_lines.append("")
        summary_lines.append("Key Results:")
        summary_lines.append(f"  Heat Transfer: {results.get('Q', 0):.2f} kW")
        summary_lines.append(f"  Area: {results.get('area', 0):.2f} m²")
        summary_lines.append(f"  Effectiveness: {results.get('effectiveness', 0)*100:.1f}%")
        summary_lines.append(f"  NTU: {results.get('NTU', 0):.2f}")
        
        return "\n".join(summary_lines)


def create_design_library_entry(design_name, description, typical_application, 
                                default_values):
    """
    Create a template entry for design library.
    
    Args:
        design_name (str): Name of the template
        description (str): Description
        typical_application (str): Where this is typically used
        default_values (dict): Default input values
        
    Returns:
        dict: Template entry
    """
    return {
        'template_name': design_name,
        'description': description,
        'typical_application': typical_application,
        'default_values': default_values,
        'created': datetime.now().isoformat()
    }


# Pre-defined design templates
DESIGN_TEMPLATES = {
    'HVAC_Cooling_Coil': {
        'name': 'HVAC Cooling Coil',
        'description': 'Typical air conditioning cooling coil design',
        'application': 'Building HVAC systems',
        'defaults': {
            'flow_type': 'Counter Flow',
            'method': 'LMTD',
            'hot_fluid': 'Air',
            'T_hot_in': 30,
            'T_hot_out': 15,
            'm_hot': 1.5,
            'cold_fluid': 'Water',
            'T_cold_in': 7,
            'T_cold_out': 12,
            'm_cold': 2.0,
            'U_value': 50,
            'hx_type': 'Finned Tube'
        }
    },
    'Chiller_Evaporator': {
        'name': 'Chiller Evaporator',
        'description': 'Water chiller evaporator design',
        'application': 'Central chilled water plants',
        'defaults': {
            'flow_type': 'Counter Flow',
            'method': 'LMTD',
            'hot_fluid': 'Water',
            'T_hot_in': 12,
            'T_hot_out': 7,
            'm_hot': 10.0,
            'cold_fluid': 'R-134a',
            'T_cold_in': 2,
            'T_cold_out': 2,
            'm_cold': 2.5,
            'U_value': 800,
            'hx_type': 'Shell-and-Tube'
        }
    },
    'Oil_Cooler': {
        'name': 'Oil Cooler',
        'description': 'Industrial hydraulic/engine oil cooler',
        'application': 'Industrial machinery, hydraulic systems',
        'defaults': {
            'flow_type': 'Counter Flow',
            'method': 'LMTD',
            'hot_fluid': 'Engine Oil',
            'T_hot_in': 95,
            'T_hot_out': 65,
            'm_hot': 0.5,
            'cold_fluid': 'Water',
            'T_cold_in': 25,
            'T_cold_out': 35,
            'm_cold': 1.2,
            'U_value': 250,
            'hx_type': 'Plate'
        }
    },
    'Heat_Recovery': {
        'name': 'Heat Recovery Unit',
        'description': 'Air-to-air heat recovery ventilator',
        'application': 'Energy recovery ventilation systems',
        'defaults': {
            'flow_type': 'Counter Flow',
            'method': 'NTU',
            'hot_fluid': 'Air',
            'T_hot_in': 60,
            'm_hot': 3.0,
            'cold_fluid': 'Air',
            'T_cold_in': 20,
            'm_cold': 3.0,
            'U_value': 30,
            'area': 15,
            'hx_type': 'Plate'
        }
    },
    'Automotive_Radiator': {
        'name': 'Automotive Radiator',
        'description': 'Engine cooling radiator',
        'application': 'Automotive engine cooling',
        'defaults': {
            'flow_type': 'Counter Flow',
            'method': 'NTU',
            'hot_fluid': 'Ethylene Glycol (50%)',
            'T_hot_in': 95,
            'm_hot': 0.8,
            'cold_fluid': 'Air',
            'T_cold_in': 35,
            'm_cold': 3.0,
            'U_value': 60,
            'area': 2.5,
            'hx_type': 'Finned Tube'
        }
    }
}


def get_template(template_name):
    """
    Get a pre-defined design template.
    
    Args:
        template_name (str): Name of template
        
    Returns:
        dict: Template data or None
    """
    return DESIGN_TEMPLATES.get(template_name, None)


def list_available_templates():
    """
    Get list of available templates.
    
    Returns:
        list: List of template names with descriptions
    """
    templates = []
    for key, template in DESIGN_TEMPLATES.items():
        templates.append({
            'key': key,
            'name': template['name'],
            'description': template['description'],
            'application': template['application']
        })
    return templates


# Testing
if __name__ == "__main__":
    print("Testing Design Storage Module\n")
    print("="*80)
    
    storage = DesignStorage()
    
    # Create sample design
    sample_design = {
        'inputs': {
            'T_hot_in': 90,
            'T_hot_out': 50,
            'T_cold_in': 25,
            'T_cold_out': 45
        },
        'results': {
            'Q': 335.2,
            'area': 12.4,
            'effectiveness': 0.615,
            'NTU': 2.07,
            'flow_type': 'Counter Flow',
            'method': 'LMTD'
        }
    }
    
    # Create snapshot
    snapshot = storage.create_design_snapshot(sample_design, "Test Design 1")
    print("Design Snapshot Created:")
    print(f"  Name: {snapshot['design_name']}")
    print(f"  Date: {snapshot['date_readable']}")
    
    # Export to JSON
    json_str = storage.export_design_json(snapshot)
    print(f"\nExported JSON (first 200 chars):")
    print(json_str[:200] + "...")
    
    # Generate summary
    summary = storage.generate_design_summary(snapshot)
    print(f"\nDesign Summary:")
    print(summary)
    
    # List templates
    print("\n" + "="*80)
    print("Available Design Templates:")
    print("-"*80)
    templates = list_available_templates()
    for template in templates:
        print(f"\n{template['name']}")
        print(f"  Application: {template['application']}")
        print(f"  Description: {template['description']}")
    
    print("\n" + "="*80)
