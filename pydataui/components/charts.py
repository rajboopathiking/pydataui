from __future__ import annotations
import json
from typing import Any, List, Optional
from .base import Component

class Chart(Component):
    tag = 'div'
    def __init__(self, type='bar', data=None, options=None, width=None, height='300px', responsive=True, **props):
        super().__init__(**props)
        self.type = type
        self.data = data or {}
        self.options = options or {}
        self.width = width
        self.height = height
        self.responsive = responsive
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-chart-container']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width: s += f" width: {self.width};"
        if self.height: s += f" height: {self.height};"
        s += " position: relative;"
        return s.strip()
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        chart_data = self._resolve_value(self.data, state_snapshot)
        chart_options = self._resolve_value(self.options, state_snapshot)
        
        if self.responsive and 'responsive' not in chart_options:
            chart_options['responsive'] = True
            chart_options['maintainAspectRatio'] = False
            
        data_json = json.dumps(chart_data)
        options_json = json.dumps(chart_options)
        
        canvas_id = f"{self.id}-canvas"
        
        script = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof Chart !== 'undefined') {{
                const ctx = document.getElementById('{canvas_id}').getContext('2d');
                new Chart(ctx, {{
                    type: '{self.type}',
                    data: {data_json},
                    options: {options_json}
                }});
            }}
        }});
        </script>
        """
        
        return f"<{self.tag} {attrs}><canvas id='{canvas_id}'></canvas></{self.tag}>{script}"

class Sparkline(Chart):
    def __init__(self, data=None, type='line', color=None, width='100px', height='30px', **props):
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {'legend': {'display': False}, 'tooltip': {'enabled': False}},
            'scales': {'x': {'display': False}, 'y': {'display': False}},
            'elements': {'point': {'radius': 0}}
        }
        
        if isinstance(data, list):
            color = color or '#3b82f6' # default primary
            dataset = {
                'data': data,
                'borderColor': color,
                'borderWidth': 2,
                'fill': False,
                'tension': 0.4
            }
            if type == 'bar':
                dataset['backgroundColor'] = color
            chart_data = {'labels': [''] * len(data), 'datasets': [dataset]}
        else:
            chart_data = data or {}
            
        super().__init__(type=type, data=chart_data, options=options, width=width, height=height, **props)
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-chart-container' in classes: classes.remove('pdu-chart-container')
        classes.append('pdu-sparkline')
        return classes
