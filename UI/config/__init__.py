"""Cấu hình ứng dụng tập trung (Application Configuration Package)."""
try:
    from config.settings import Settings, settings
except ImportError:
    from UI.config.settings import Settings, settings

__all__ = ["Settings", "settings"]
