"""
Universal Qt compatibility shim.
Supports PySide6 and PyQt6 seamlessly.
"""
from __future__ import annotations

import sys

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import (
        QEasingCurve, QLineF, QMimeData, QObject, QParallelAnimationGroup, QPointF,
        QPoint, QPropertyAnimation, QRect, QRectF, QSize, QSizeF, Qt, QTimer,
        QUrl, Signal as pyqtSignal, Slot as pyqtSlot,
    )
    from PySide6.QtGui import (
        QBrush, QColor, QConicalGradient, QDragEnterEvent, QDropEvent, QFont,
        QFontDatabase, QKeySequence, QLinearGradient, QPainter, QPainterPath,
        QPen, QPixmap, QPolygonF, QRadialGradient, QShortcut,
    )
    from PySide6.QtWidgets import (
        QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
        QMainWindow, QPushButton, QScrollArea, QSizePolicy, QSplitter,
        QGraphicsScene, QGraphicsView,
        QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QProgressBar,
    )
    QT_API = "PySide6"
except ImportError:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import (
        QEasingCurve, QLineF, QMimeData, QObject, QParallelAnimationGroup, QPointF,
        QPoint, QPropertyAnimation, QRect, QRectF, QSize, QSizeF, Qt, QTimer,
        QUrl, pyqtSignal, pyqtSlot,
    )
    from PyQt6.QtGui import (
        QBrush, QColor, QConicalGradient, QDragEnterEvent, QDropEvent, QFont,
        QFontDatabase, QKeySequence, QLinearGradient, QPainter, QPainterPath,
        QPen, QPixmap, QPolygonF, QRadialGradient, QShortcut,
    )
    from PyQt6.QtWidgets import (
        QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
        QMainWindow, QPushButton, QScrollArea, QSizePolicy, QSplitter,
        QGraphicsScene, QGraphicsView,
        QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QProgressBar,
    )
    QT_API = "PyQt6"

__all__ = [
    "QT_API",
    "QtCore", "QtGui", "QtWidgets",
    "QEasingCurve", "QLineF", "QMimeData", "QObject", "QParallelAnimationGroup",
    "QPointF", "QPoint", "QPropertyAnimation", "QRect", "QRectF", "QSize", "QSizeF",
    "Qt", "QTimer", "QUrl", "pyqtSignal", "pyqtSlot",
    "QBrush", "QColor", "QConicalGradient", "QDragEnterEvent", "QDropEvent", "QFont",
    "QFontDatabase", "QKeySequence", "QLinearGradient", "QPainter", "QPainterPath",
    "QPen", "QPixmap", "QPolygonF", "QRadialGradient", "QShortcut",
    "QApplication", "QComboBox", "QFileDialog", "QFrame", "QHBoxLayout", "QLabel",
    "QLineEdit", "QMainWindow", "QPushButton", "QScrollArea", "QSizePolicy",
    "QSplitter", "QGraphicsScene", "QGraphicsView", "QStackedWidget", "QTextEdit",
    "QVBoxLayout", "QWidget", "QProgressBar",
]
