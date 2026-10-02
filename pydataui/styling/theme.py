from __future__ import annotations
from typing import Dict, Any

class Theme:
    """Theme configuration for PyDataUI."""
    def __init__(
        self,
        name: str,
        colors: Dict[str, str],
        fonts: Dict[str, str],
        spacing: Dict[str, str],
        radii: Dict[str, str],
        shadows: Dict[str, str],
        font_sizes: Dict[str, str],
        breakpoints: Dict[str, str]
    ):
        self.name = name
        self.colors = colors
        self.fonts = fonts
        self.spacing = spacing
        self.radii = radii
        self.shadows = shadows
        self.font_sizes = font_sizes
        self.breakpoints = breakpoints

    def to_css_variables(self) -> str:
        """Generate CSS custom properties from theme."""
        lines = []
        for key, value in self.colors.items():
            lines.append(f"  --pdu-color-{key}: {value};")
        for key, value in self.fonts.items():
            lines.append(f"  --pdu-font-{key}: {value};")
        for key, value in self.spacing.items():
            lines.append(f"  --pdu-spacing-{key}: {value};")
        for key, value in self.radii.items():
            lines.append(f"  --pdu-radius-{key}: {value};")
        for key, value in self.shadows.items():
            lines.append(f"  --pdu-shadow-{key}: {value};")
        for key, value in self.font_sizes.items():
            lines.append(f"  --pdu-font-size-{key}: {value};")
        
        # Breakpoints aren't typically CSS vars, but we can add them if needed
        # Alternatively, they are used in Python-level responsive styling
        for key, value in self.breakpoints.items():
            lines.append(f"  --pdu-breakpoint-{key}: {value};")
            
        return "\\n".join(lines)

    def to_css(self) -> str:
        """Generate complete CSS :root block."""
        return ":root {\\n" + self.to_css_variables() + "\\n}\\n"

default_theme = Theme(
    name='default',
    colors={
        'primary': '#3b82f6',
        'primary-hover': '#2563eb',
        'primary-light': '#eff6ff',
        'secondary': '#6b7280',
        'secondary-hover': '#4b5563',
        'success': '#22c55e',
        'success-hover': '#16a34a',
        'success-light': '#f0fdf4',
        'danger': '#ef4444',
        'danger-hover': '#dc2626',
        'danger-light': '#fef2f2',
        'warning': '#f59e0b',
        'warning-hover': '#d97706',
        'warning-light': '#fffbeb',
        'info': '#06b6d4',
        'info-hover': '#0891b2',
        'info-light': '#ecfeff',
        'bg': '#ffffff',
        'bg-secondary': '#f9fafb',
        'bg-tertiary': '#f3f4f6',
        'text': '#111827',
        'text-secondary': '#6b7280',
        'text-muted': '#9ca3af',
        'border': '#e5e7eb',
        'border-hover': '#d1d5db',
        'overlay': 'rgba(0,0,0,0.5)',
    },
    fonts={
        'body': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'heading': "inherit",
        'mono': "'SF Mono', SFMono-Regular, 'Consolas', 'Liberation Mono', Menlo, Courier, monospace",
    },
    spacing={'xs': '0.25rem', 'sm': '0.5rem', 'md': '1rem', 'lg': '1.5rem', 'xl': '2rem', '2xl': '3rem', '3xl': '4rem'},
    radii={'none': '0', 'sm': '0.25rem', 'md': '0.375rem', 'lg': '0.5rem', 'xl': '0.75rem', '2xl': '1rem', 'full': '9999px'},
    shadows={
        'none': 'none',
        'sm': '0 1px 2px 0 rgba(0,0,0,0.05)',
        'md': '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)',
        'lg': '0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)',
        'xl': '0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)',
    },
    font_sizes={'xs': '0.75rem', 'sm': '0.875rem', 'md': '1rem', 'lg': '1.125rem', 'xl': '1.25rem', '2xl': '1.5rem', '3xl': '1.875rem'},
    breakpoints={'sm': '640px', 'md': '768px', 'lg': '1024px', 'xl': '1280px', '2xl': '1536px'},
)

dark_theme = Theme(
    name='dark',
    colors={
        'primary': '#3b82f6',      # Keeps same primary identity usually, or adapt to '#60a5fa'
        'primary-hover': '#2563eb',
        'primary-light': '#1e3a8a',
        'secondary': '#9ca3af',
        'secondary-hover': '#d1d5db',
        'success': '#22c55e',
        'success-hover': '#16a34a',
        'success-light': '#14532d',
        'danger': '#ef4444',
        'danger-hover': '#dc2626',
        'danger-light': '#7f1d1d',
        'warning': '#f59e0b',
        'warning-hover': '#d97706',
        'warning-light': '#78350f',
        'info': '#06b6d4',
        'info-hover': '#0891b2',
        'info-light': '#164e63',
        'bg': '#111827',
        'bg-secondary': '#1f2937',
        'bg-tertiary': '#374151',
        'text': '#f9fafb',
        'text-secondary': '#d1d5db',
        'text-muted': '#9ca3af',
        'border': '#374151',
        'border-hover': '#4b5563',
        'overlay': 'rgba(0,0,0,0.7)',
    },
    fonts=default_theme.fonts,
    spacing=default_theme.spacing,
    radii=default_theme.radii,
    shadows={
        'none': 'none',
        'sm': '0 1px 2px 0 rgba(0,0,0,0.5)',
        'md': '0 4px 6px -1px rgba(0,0,0,0.5), 0 2px 4px -2px rgba(0,0,0,0.5)',
        'lg': '0 10px 15px -3px rgba(0,0,0,0.5), 0 4px 6px -4px rgba(0,0,0,0.5)',
        'xl': '0 20px 25px -5px rgba(0,0,0,0.5), 0 8px 10px -6px rgba(0,0,0,0.5)',
    },
    font_sizes=default_theme.font_sizes,
    breakpoints=default_theme.breakpoints,
)
