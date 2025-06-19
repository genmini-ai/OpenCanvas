"""
Theme definitions for presentations
"""

class ThemeManager:
    """Manages presentation themes and color schemes"""
    
    def __init__(self):
        self.themes = {
            "professional blue": {
                "primary": "#2563eb",
                "secondary": "#64748b", 
                "accent": "#3b82f6",
                "background": "#ffffff",
                "text": "#1e293b",
                "description": "Clean, professional theme with blue accents"
            },
            "clean minimalist": {
                "primary": "#374151",
                "secondary": "#9ca3af",
                "accent": "#6b7280", 
                "background": "#f9fafb",
                "text": "#111827",
                "description": "Minimal design with subtle grays"
            },
            "bold high contrast": {
                "primary": "#dc2626",
                "secondary": "#1f2937",
                "accent": "#ef4444",
                "background": "#ffffff", 
                "text": "#000000",
                "description": "High contrast theme for maximum impact"
            },
            "cool professional": {
                "primary": "#0891b2",
                "secondary": "#475569",
                "accent": "#06b6d4",
                "background": "#f8fafc",
                "text": "#0f172a",
                "description": "Cool tones for professional presentations"
            },
            "natural earth": {
                "primary": "#059669",
                "secondary": "#78716c",
                "accent": "#10b981",
                "background": "#fefdf8",
                "text": "#1c1917",
                "description": "Earth tones for sustainability themes"
            },
            "muted morandi tones": {
                "primary": "#a78bfa",
                "secondary": "#94a3b8",
                "accent": "#c4b5fd",
                "background": "#f1f5f9",
                "text": "#334155",
                "description": "Soft, muted colors inspired by Morandi"
            },
            "modern contemporary": {
                "primary": "#7c3aed",
                "secondary": "#64748b",
                "accent": "#8b5cf6",
                "background": "#ffffff",
                "text": "#1e293b",
                "description": "Modern purple and gray combination"
            },
            "warm earth tones": {
                "primary": "#ea580c",
                "secondary": "#78716c",
                "accent": "#fb923c",
                "background": "#fffbeb",
                "text": "#1c1917",
                "description": "Warm oranges and browns for approachable feel"
            },
            "soft pastels": {
                "primary": "#ec4899",
                "secondary": "#94a3b8",
                "accent": "#f472b6",
                "background": "#fdf2f8",
                "text": "#374151",
                "description": "Gentle pastels for personal or creative topics"
            },
            "academic": {
                "primary": "#1e40af",
                "secondary": "#64748b",
                "accent": "#3b82f6",
                "background": "#ffffff",
                "text": "#1e293b",
                "description": "Traditional academic presentation style"
            }
        }
    
    def get_theme(self, theme_name: str) -> dict:
        """Get theme configuration by name"""
        return self.themes.get(theme_name.lower(), self.themes["professional blue"])
    
    def list_themes(self) -> list:
        """List all available themes"""
        return list(self.themes.keys())
    
    def get_theme_description(self, theme_name: str) -> str:
        """Get theme description"""
        theme = self.get_theme(theme_name)
        return theme.get("description", "No description available")
    
    def validate_theme(self, theme_name: str) -> bool:
        """Check if theme exists"""
        return theme_name.lower() in self.themes