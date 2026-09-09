"""Sliding settings bar and cursor hit-testing above a foreign video HWND."""
import sys
from PySide6.QtCore import QEasingCurve, QVariantAnimation
from PySide6.QtWidgets import QWidget

if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    _user32 = ctypes.WinDLL('user32', use_last_error=True)
    _user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    _user32.GetCursorPos.restype = wintypes.BOOL
    _user32.WindowFromPoint.argtypes = [wintypes.POINT]
    _user32.WindowFromPoint.restype = wintypes.HWND
    _user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    _user32.GetAncestor.restype = wintypes.HWND


def cursor_over_window(window, position):
    if window.isMinimized() or not window.isVisible():
        return False
    if not window.rect().contains(window.mapFromGlobal(position)):
        return False
    if sys.platform == 'win32':
        # Qt does not receive mouse moves over the engine-owned video window.
        # Its GA_ROOT is still the Qt top-level window. Also reject other apps
        # covering our window, rather than reacting to their mouse movement.
        # Win32 hit-testing needs physical pixels; QCursor uses Qt logical
        # coordinates on scaled monitors. Read the native cursor separately.
        native_position = wintypes.POINT()
        if not _user32.GetCursorPos(ctypes.byref(native_position)):
            return False
        hit = _user32.WindowFromPoint(native_position)
        return bool(hit) and _user32.GetAncestor(hit, 2) == int(window.winId())
    return True


class SettingsBar(QWidget):
    expanded_height = 84

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panel = QWidget(self)
        self.setFixedHeight(self.expanded_height)
        self.expanded = True
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(180)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(lambda value: self.setFixedHeight(int(value)))

    def set_expanded(self, expanded):
        if self.expanded == expanded:
            return
        self.expanded = expanded
        self.animation.stop()
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(self.expanded_height if expanded else 0)
        self.animation.start()

    def resizeEvent(self, event):
        # Clip the panel at the top edge while it slides, rather than shrinking
        # the button. The native video area fills the space released underneath.
        self.panel.setGeometry(0, self.height() - self.expanded_height,
                               self.width(), self.expanded_height)
        super().resizeEvent(event)
