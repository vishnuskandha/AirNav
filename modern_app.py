import sys
import time
# Import engines first to avoid DLL conflicts with PyQt5
from gesture_engine import GestureEngine

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRectF, QTimer
from PyQt5.QtGui import QImage, QPainter, QPainterPath, QColor, QBrush, QPen, QCursor

# PiP Window Sizes (macOS-style)
SIZES = {
    'default': (320, 200),  # 16:10 - macOS FaceTime style
    'medium': (426, 240),   # 16:9
    'large': (640, 360),    # 16:9
    'max': (960, 540)       # 16:9
}

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    authenticated_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.mode = "gesture"  # Skip auth, go directly to gesture
        self.face_engine = None
        self.gesture_engine = GestureEngine()
        self.target_fps = 30
        
    def run(self):
        # Open camera with optimized resolution (1280×720)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_time = 1.0 / self.target_fps
        last_frame_time = time.time()
        
        while self._run_flag:
            current_time = time.time()
            elapsed = current_time - last_frame_time
            
            # FPS limiting
            if elapsed < frame_time:
                self.msleep(int((frame_time - elapsed) * 1000))
                continue
                
            last_frame_time = current_time
            
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process gesture controls directly (no authentication)
            if self.gesture_engine:
                processed_frame = self.gesture_engine.process_frame(frame)
                self.change_pixmap_signal.emit(processed_frame)
            
        cap.release()
        
    def stop(self):
        self._run_flag = False
        self.wait()

class FloatingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AirNav PiP")
        
        # Set to macOS-like default PiP size
        self.current_size_key = 'default'
        w, h = SIZES[self.current_size_key]
        self.setGeometry(100, 100, w, h)
        self.setMinimumSize(160, 100)  # Minimum PiP size
        
        # Frameless and Transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # State
        self.image = None
        self.drag_pos = None
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.border_radius = 15
        self.resize_margin = 8
        
        # Double-click detection
        self.last_click_time = 0
        self.double_click_threshold = 0.3  # seconds
        
        # Video Thread
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.authenticated_signal.connect(self.on_authenticated)
        self.thread.start()
        
    def update_image(self, cv_img):
        """Updates the display with a new opencv image"""
        self.image = cv_img
        self.update()  # Trigger paintEvent
        
    def on_authenticated(self, name):
        print(f"✓ Authenticated: {name}")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Create rounded path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.border_radius, self.border_radius)
        
        # Clip to rounded rect
        painter.setClipPath(path)
        
        # Draw background (dark gray)
        painter.fillPath(path, QBrush(QColor(30, 30, 30)))
        
        if self.image is not None:
            # Convert CV image to QImage
            rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            # Draw image centered
            x = (self.width() - p.width()) // 2
            y = (self.height() - p.height()) // 2
            painter.drawImage(x, y, p)
            
        # Draw Border
        painter.setClipping(False)
        painter.setPen(QPen(QColor(80, 80, 80, 180), 1))
        painter.drawPath(path)
        
    def get_resize_edge(self, pos):
        """Determine which edge/corner is being hovered for resizing"""
        margin = self.resize_margin
        rect = self.rect()
        
        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin
        
        if bottom and right:
            return 'bottom_right'
        elif bottom and left:
            return 'bottom_left'
        elif top and right:
            return 'top_right'
        elif top and left:
            return 'top_left'
        elif bottom:
            return 'bottom'
        elif right:
            return 'right'
        elif top:
            return 'top'
        elif left:
            return 'left'
        
        return None
    
    def update_cursor(self, edge):
        """Update cursor shape based on resize edge"""
        if edge in ['top_left', 'bottom_right']:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif edge in ['top_right', 'bottom_left']:
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif edge in ['top', 'bottom']:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        elif edge in ['left', 'right']:
            self.setCursor(QCursor(Qt.SizeHorCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            current_time = time.time()
            
            # Check for double-click
            if current_time - self.last_click_time < self.double_click_threshold:
                self.toggle_size()
                self.last_click_time = 0
                return
            
            self.last_click_time = current_time
            
            # Check if clicking on edge for resize
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
            else:
                # Start dragging
                self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
            event.accept()
            
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.resize_edge:
                # Handle resizing
                self.handle_resize(event.globalPos())
            elif self.drag_pos:
                # Handle dragging
                self.move(event.globalPos() - self.drag_pos)
            event.accept()
        else:
            # Update cursor based on position
            edge = self.get_resize_edge(event.pos())
            self.update_cursor(edge)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.resize_edge = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            self.drag_pos = None
            event.accept()
    
    def handle_resize(self, global_pos):
        """Handle window resizing based on edge"""
        if not self.resize_start_geometry or not self.resize_start_pos:
            return
        
        delta = global_pos - self.resize_start_pos
        geo = self.resize_start_geometry
        
        new_geo = geo
        
        if 'right' in self.resize_edge:
            new_geo.setRight(geo.right() + delta.x())
        if 'left' in self.resize_edge:
            new_geo.setLeft(geo.left() + delta.x())
        if 'bottom' in self.resize_edge:
            new_geo.setBottom(geo.bottom() + delta.y())
        if 'top' in self.resize_edge:
            new_geo.setTop(geo.top() + delta.y())
        
        # Respect minimum size
        if new_geo.width() >= self.minimumWidth() and new_geo.height() >= self.minimumHeight():
            self.setGeometry(new_geo)
    
    def toggle_size(self):
        """Toggle between preset sizes on double-click"""
        size_order = ['default', 'medium', 'large', 'max']
        current_idx = size_order.index(self.current_size_key)
        next_idx = (current_idx + 1) % len(size_order)
        self.current_size_key = size_order[next_idx]
        
        w, h = SIZES[self.current_size_key]
        self.resize(w, h)
        print(f"Resized to {self.current_size_key}: {w}×{h}px")
            
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Size options
        size_menu = menu.addMenu("Resize To")
        for size_name, (w, h) in SIZES.items():
            action = QAction(f"{size_name.title()} ({w}×{h})", self)
            action.triggered.connect(lambda checked, s=size_name: self.set_size(s))
            size_menu.addAction(action)
        
        menu.addSeparator()
        
        # Exit
        quit_action = QAction("Exit AirNav", self)
        quit_action.triggered.connect(self.close_app)
        menu.addAction(quit_action)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def set_size(self, size_key):
        """Set window to a specific preset size"""
        self.current_size_key = size_key
        w, h = SIZES[size_key]
        self.resize(w, h)
        
    def close_app(self):
        self.thread.stop()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    window.show()
    sys.exit(app.exec_())
