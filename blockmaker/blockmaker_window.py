"""
Blockmaker Module - Grid-based block creation tool

RULES:
======
1. First block is numbered with "+"
2. Second block is numbered "2" 
3. Each additional block must be placed adjacent to a prior numbered block
4. Each block includes all numbers lower than itself
5. Blocks can be placed in any adjacent direction (up, down, left, right)

IMPLEMENTATION:
===============
- Grid-based interface with 24x24 pixel blocks (matching upgrade grid)
- Up/down counter and direct input for block count
- Visual feedback showing valid placement positions
- Consistent styling with main application
"""

import sys
import random
from typing import List, Tuple, Set, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QSpinBox, QLineEdit, QFrame, QSizePolicy,
    QApplication, QPlainTextEdit, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QBrush, QKeySequence

# Import project styling
sys.path.append('..')
from core.style import GOLD, UPGRADE_BG, TAB_BG, TEXT_COLOR, BORDER_COLOR, SECONDARY_ACCENT


class BlockmakerGrid(QWidget):
    """Grid widget for block placement and visualization"""
    
    def __init__(self, grid_size: int = 12, parent=None):
        super().__init__(parent)
        self.grid_size = grid_size
        self.cell_size = 24  # Match upgrade grid block size
        self.blocks = {}  # (row, col) -> block_number
        self.valid_positions = set()  # Valid positions for next block
        self.hover_pos = None  # Current hover position
        self.dragging = False  # Track if we're dragging
        self.drag_start_pos = None  # Starting position for drag
        self._drag_visited = set()  # Track cells filled in current drag
        self._processing_positions = set()  # Track positions currently being processed
        
        # Initialize valid positions for first block
        self.update_valid_positions()
        
        # Setup UI
        self.setMinimumSize(
            grid_size * self.cell_size + 20, 
            grid_size * self.cell_size + 20
        )
        self.setMaximumSize(
            grid_size * self.cell_size + 20, 
            grid_size * self.cell_size + 20
        )
        self.setStyleSheet(f"""
            background: {UPGRADE_BG};
            border: 2px solid {GOLD};
            border-radius: 5px;
        """)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        """Draw the grid and blocks"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(UPGRADE_BG))
        
        # Draw grid lines (only within the grid, no extra lines)
        painter.setPen(QPen(QColor(BORDER_COLOR), 1))
        for i in range(self.grid_size + 1):
            x = i * self.cell_size + 10
            y = i * self.cell_size + 10
            # Only draw lines within the grid area
            painter.drawLine(10, y, 10 + self.grid_size * self.cell_size, y)
            painter.drawLine(x, 10, x, 10 + self.grid_size * self.cell_size)
        
        # Draw blocks
        for pos, block_num in self.blocks.items():
            self.draw_block(painter, pos, block_num)
        
        # Draw valid positions
        for pos in self.valid_positions:
            self.draw_valid_position(painter, pos)
        
        # Draw hover effect
        if self.hover_pos and self.hover_pos in self.valid_positions:
            self.draw_hover_effect(painter, self.hover_pos)
    
    def draw_block(self, painter: QPainter, pos: Tuple[int, int], block_num: int):
        """Draw a numbered block"""
        row, col = pos
        x = col * self.cell_size + 11
        y = row * self.cell_size + 11
        width = self.cell_size - 2
        height = self.cell_size - 2
        
        # Block background
        if block_num == -999:
            painter.setBrush(QColor("#fffbe6"))
        else:
            painter.setBrush(QColor(GOLD))
        painter.setPen(QPen(QColor(BORDER_COLOR), 2))
        painter.drawRoundedRect(x, y, width, height, 3, 3)
        
        # Block number text - use terminal-like font
        painter.setPen(QColor("#000000"))
        font = QFont()
        font.setFamily("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(9)
        font.setBold(True)
        font.setFixedPitch(True)
        painter.setFont(font)
        
        # Format block number
        if block_num == 1:
            text = "+"
        elif block_num == -999:
            text = ""
        else:
            text = str(block_num)
        
        # Center text
        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = x + (width - text_rect.width()) // 2
        text_y = y + (height + text_rect.height()) // 2 - 2
        painter.drawText(text_x, text_y, text)
    
    def draw_valid_position(self, painter: QPainter, pos: Tuple[int, int]):
        """Draw a valid placement position"""
        row, col = pos
        x = col * self.cell_size + 11
        y = row * self.cell_size + 11
        width = self.cell_size - 2
        height = self.cell_size - 2
        
        # Dashed border for valid positions
        pen = QPen(QColor(GOLD), 2, Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(QBrush())
        painter.drawRoundedRect(x, y, width, height, 3, 3)
    
    def draw_hover_effect(self, painter: QPainter, pos: Tuple[int, int]):
        """Draw hover effect for valid positions"""
        row, col = pos
        x = col * self.cell_size + 11
        y = row * self.cell_size + 11
        width = self.cell_size - 2
        height = self.cell_size - 2
        
        # Semi-transparent highlight
        painter.setBrush(QColor(GOLD))
        painter.setPen(QPen())
        painter.setOpacity(0.3)
        painter.drawRoundedRect(x, y, width, height, 3, 3)
        painter.setOpacity(1.0)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks for block placement"""
        if event.button() == Qt.LeftButton:
            pos = self.get_grid_position(event.pos())
            if pos in self.valid_positions and pos not in self._processing_positions:
                self.dragging = True
                self.drag_start_pos = pos
                self._drag_visited = set()
                self._processing_positions = set()
                self._drag_visited.add(pos)
                self._processing_positions.add(pos)
                self.place_block_requested.emit(pos)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects and drag placement"""
        pos = self.get_grid_position(event.pos())
        if pos != self.hover_pos:
            self.hover_pos = pos
            self.update()
        
        # Handle drag placement - prevent duplicates with processing set
        if self.dragging and pos and pos in self.valid_positions:
            if pos not in self._drag_visited and pos not in self._processing_positions:
                self._drag_visited.add(pos)
                self._processing_positions.add(pos)
                self.place_block_requested.emit(pos)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_start_pos = None
            self._drag_visited = set()
            self._processing_positions = set()
    
    def get_grid_position(self, pos) -> Optional[Tuple[int, int]]:
        """Convert screen position to grid position"""
        x, y = pos.x(), pos.y()
        col = (x - 10) // self.cell_size
        row = (y - 10) // self.cell_size
        
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return (row, col)
        return None
    
    def add_block(self, pos: Tuple[int, int], block_num: int):
        """Add a block to the grid"""
        self.blocks[pos] = block_num
        self.update_valid_positions()
        self.update()
    
    def clear_grid(self, reset_spinbox=True):
        """Clear all blocks from the grid"""
        self.blocks.clear()
        self.valid_positions.clear()
        self.update_valid_positions()
        self.update()
        if reset_spinbox and hasattr(self, 'count_spinbox'):
            self.count_spinbox.setValue(1)
    
    def update_valid_positions(self):
        """Update the set of valid positions for the next block"""
        self.valid_positions.clear()
        
        if not self.blocks:
            # First block can go anywhere
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.valid_positions.add((row, col))
        else:
            # Subsequent blocks must be adjacent to existing blocks
            for pos in self.blocks.keys():
                row, col = pos
                # Check all adjacent positions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < self.grid_size and 
                        0 <= new_col < self.grid_size and
                        (new_row, new_col) not in self.blocks):
                        self.valid_positions.add((new_row, new_col))
    
    # Signal for block placement requests
    place_block_requested = pyqtSignal(tuple)


class BlockmakerWindow(QMainWindow):
    """Main window for the blockmaker tool"""
    
    def __init__(self):
        super().__init__()
        self.block_count = 1  # Start at 1, not 0
        self.auto_place_mode = False
        
        # Initialize UI components as None first
        self.grid = None
        self.count_spinbox = None
        self.create_btn = None
        self.random_btn = None
        self.stars_btn = None
        self.glyph_btn = None
        self.clear_btn = None
        self.debug_text = None
        self.clipboard_text = None
        self.status_label = None
        self.debug_toggle_btn = None
        self.mirror_h_btn = None
        self.mirror_v_btn = None
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
    
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Blockmaker - Grid Block Creator")
        self.setMinimumSize(800, 700)
        self.resize(1000, 800)
        
        # Center window on screen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
        
        # Apply styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {TAB_BG};
                color: {TEXT_COLOR};
            }}
        """)
    
    def setup_ui(self):
        """Create the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with QSplitter
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Blockmaker")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {GOLD};
            margin-bottom: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            letter-spacing: 2px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Create main splitter for left/right layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(3)
        main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {BORDER_COLOR};
                border-radius: 1px;
            }}
        """)
        
        # Left side - Controls and Grid
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background: {UPGRADE_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Block count controls
        count_layout = QHBoxLayout()
        
        count_label = QLabel("Block Count:")
        count_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
        count_layout.addWidget(count_label)
        
        # SpinBox for up/down counter
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 144)  # Allow up to 3 digits for 12x12 grid
        self.count_spinbox.setValue(1)
        self.count_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 80px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: {GOLD};
                border: none;
                border-radius: 2px;
                width: 20px;
            }}
        """)
        count_layout.addWidget(self.count_spinbox)
        
        controls_layout.addLayout(count_layout)
        
        # --- Create all buttons first ---
        self.create_btn = QPushButton("Create Block")
        self.random_btn = QPushButton("Random Generate")
        self.stars_btn = QPushButton("Stars Generate")
        self.glyph_btn = QPushButton("Glyph Generate")
        self.mirror_h_btn = QPushButton("Mirror Horizontally")
        self.mirror_v_btn = QPushButton("Mirror Vertically")
        self.clear_btn = QPushButton("Clear Grid")

        # --- Set styles for each button ---
        self.create_btn.setStyleSheet(f"""
            QPushButton {{ background: {GOLD}; color: #000000; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif; }}
            QPushButton:hover {{ background: #ffd700; }}
            QPushButton:pressed {{ background: #e6c200; }}
        """)
        for btn in [self.random_btn, self.stars_btn, self.glyph_btn, self.mirror_h_btn, self.mirror_v_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{ background: {SECONDARY_ACCENT}; color: #fff; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif; }}
                QPushButton:hover {{ background: #8ea6f8; }}
                QPushButton:pressed {{ background: #5c6bc0; }}
            """)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{ background: {BORDER_COLOR}; color: {TEXT_COLOR}; border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif; }}
            QPushButton:hover {{ background: #4a5568; }}
        """)

        # --- Layouts ---
        button_row1 = QHBoxLayout()
        button_row2 = QHBoxLayout()
        button_row1.addWidget(self.create_btn)
        button_row1.addWidget(self.random_btn)
        button_row1.addWidget(self.stars_btn)
        button_row1.addWidget(self.glyph_btn)
        button_row2.addWidget(self.mirror_h_btn)
        button_row2.addWidget(self.mirror_v_btn)
        button_row2.addStretch(1)
        button_row2.addWidget(self.clear_btn)
        button_vbox = QVBoxLayout()
        button_vbox.addLayout(button_row1)
        button_vbox.addLayout(button_row2)
        controls_layout.addLayout(button_vbox)
        
        left_layout.addWidget(controls_frame)
        
        # Grid section
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"""
            QFrame {{
                background: {UPGRADE_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        grid_layout = QVBoxLayout(grid_frame)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(5)
        
        grid_label = QLabel("Block Grid")
        grid_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 12px; font-family: 'Segoe UI', Arial, sans-serif;")
        grid_layout.addWidget(grid_label)
        
        # Create grid widget - always visible
        self.grid = BlockmakerGrid(grid_size=12)
        self.grid.setMinimumSize(400, 300)  # Larger minimum size
        self.grid.setMaximumWidth(500)      # Larger maximum width
        grid_layout.addWidget(self.grid, alignment=Qt.AlignCenter)
        
        left_layout.addWidget(grid_frame)
        
        # Add left widget to splitter
        main_splitter.addWidget(left_widget)
        
        # Right side - Debug and Clipboard with vertical splitter
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setChildrenCollapsible(False)
        right_splitter.setHandleWidth(3)
        right_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {BORDER_COLOR};
                border-radius: 1px;
            }}
        """)
        
        # Debug log (top)
        debug_frame = QFrame()
        debug_frame.setStyleSheet(f"""
            QFrame {{
                background: {UPGRADE_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        debug_frame.setMinimumHeight(200)
        debug_layout = QVBoxLayout(debug_frame)
        debug_layout.setContentsMargins(5, 5, 5, 5)
        debug_layout.setSpacing(2)
        
        debug_header = QLabel("Debug Log")
        debug_header.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 10px; font-family: 'Segoe UI', Arial, sans-serif;")
        debug_layout.addWidget(debug_header)
        
        self.debug_text = QPlainTextEdit()
        self.debug_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 3px;
                color: {TEXT_COLOR};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9px;
            }}
        """)
        self.debug_text.setReadOnly(True)
        debug_layout.addWidget(self.debug_text)
        
        # Add Show/Hide Debug toggle
        self.debug_toggle_btn = QPushButton("Hide Debug")
        self.debug_toggle_btn.setCheckable(True)
        self.debug_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {TAB_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 9px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:checked {{
                background: {BORDER_COLOR};
                color: {GOLD};
            }}
        """)
        self.debug_toggle_btn.setChecked(False)
        debug_layout.addWidget(self.debug_toggle_btn, alignment=Qt.AlignRight)
        
        right_splitter.addWidget(debug_frame)
        
        # Clipboard container (bottom)
        self.clipboard_frame = QFrame()
        self.clipboard_frame.setStyleSheet(f"""
            QFrame {{
                background: {UPGRADE_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        self.clipboard_frame.setMinimumHeight(150)
        clipboard_layout = QVBoxLayout(self.clipboard_frame)
        clipboard_layout.setContentsMargins(5, 5, 5, 5)
        clipboard_layout.setSpacing(2)
        
        clipboard_label = QLabel("Block Pattern")
        clipboard_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 10px; font-family: 'Segoe UI', Arial, sans-serif;")
        clipboard_layout.addWidget(clipboard_label)
        
        self.clipboard_text = QPlainTextEdit()
        self.clipboard_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 3px;
                color: {TEXT_COLOR};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 8px;
            }}
        """)
        self.clipboard_text.setReadOnly(True)
        clipboard_layout.addWidget(self.clipboard_text)
        
        # Copy button
        copy_btn = QPushButton("Copy")
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GOLD};
                color: #000;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background: #ffd700;
            }}
        """)
        copy_btn.clicked.connect(self.copy_to_clipboard)
        clipboard_layout.addWidget(copy_btn, alignment=Qt.AlignRight)
        
        right_splitter.addWidget(self.clipboard_frame)
        
        # Add right splitter to main splitter
        main_splitter.addWidget(right_splitter)
        
        # Set splitter proportions (70% left, 30% right) - give more space to grid
        main_splitter.setSizes([700, 300])
        
        main_layout.addWidget(main_splitter)
        
        # Status section - simplified small text
        self.status_label = QLabel("Ready to create blocks")
        self.status_label.setStyleSheet(f"""
            color: {GOLD};
            font-size: 12px;
            font-weight: bold;
            margin-top: 8px;
            padding: 4px 0;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Button feedback (highlight on press)
        button_feedback_style = """
            QPushButton:pressed {
                background: #fffbe6;
                color: #222;
                border: 2px solid #f7c873;
            }
        """
        for btn in [self.create_btn, self.random_btn, self.stars_btn, self.glyph_btn, self.clear_btn, self.mirror_h_btn, self.mirror_v_btn]:
            btn.setStyleSheet(btn.styleSheet() + button_feedback_style)

    def setup_connections(self):
        """Setup signal connections"""
        if self.create_btn:
            self.create_btn.clicked.connect(self.create_block)
        if self.clear_btn:
            self.clear_btn.clicked.connect(self.clear_grid)
        if self.grid:
            # Use a custom handler to increment block number for each placement
            self.grid.place_block_requested.connect(self.handle_place_block)
        if self.random_btn:
            self.random_btn.clicked.connect(self.generate_random_pattern)
            self.random_btn.setShortcut(QKeySequence("Ctrl+R"))
        if self.stars_btn:
            self.stars_btn.clicked.connect(self.generate_stars_pattern)
            self.stars_btn.setShortcut(QKeySequence("Ctrl+G"))
        if self.glyph_btn:
            self.glyph_btn.clicked.connect(self.generate_glyph_pattern)
            self.glyph_btn.setShortcut(QKeySequence("Ctrl+L"))
        if self.debug_toggle_btn:
            self.debug_toggle_btn.clicked.connect(self.toggle_debug_log)
        if self.create_btn:
            self.create_btn.setShortcut(QKeySequence(Qt.Key.Key_Return))
        if self.mirror_h_btn:
            self.mirror_h_btn.clicked.connect(self.mirror_grid_horizontally)
        if self.mirror_v_btn:
            self.mirror_v_btn.clicked.connect(self.mirror_grid_vertically)

    def create_block(self):
        """Create a new block based on current input"""
        if not self.grid or not self.count_spinbox:
            return
        # Always start with 1 if grid is empty
        if not self.grid.blocks:
            center = self.grid.grid_size // 2
            self.grid.add_block((center, center), 1)
            self.block_count = 2
            self.count_spinbox.setValue(self.block_count)
            self.status_label.setText(f"First block (+) placed! Click to place block {self.block_count}")
            self.log_debug(f"First block placed at center ({center}, {center})")
        else:
            self.block_count = self.count_spinbox.value()
            self.status_label.setText(f"Click on a highlighted position to place block {self.block_count}")
            self.log_debug(f"Manual placement mode: {len(self.grid.valid_positions)} valid positions")
        self.update_debug_log()
        self.update_clipboard_pattern()
    
    def handle_place_block(self, pos: Tuple[int, int]):
        """Place a block at the specified position with strict sequential numbering (no repeats, no overwrites)."""
        if not self.grid:
            return
        if len(self.grid.blocks) >= 144:
            self.status_label.setText("Maximum 12x12 blocks reached! Clear to start over.")
            self.log_debug("Maximum block limit reached")
            return
        # Only place a block if the cell is not already filled
        if pos not in self.grid.blocks:
            # If grid is empty, always start with 1 (+)
            if not self.grid.blocks:
                self.grid.add_block(pos, 1)
                self.block_count = 2
                self.count_spinbox.setValue(self.block_count)
                self.status_label.setText(f"First block (+) placed! Click to place block {self.block_count}")
                self.log_debug(f"First block placed at {pos}")
            else:
                self.grid.add_block(pos, self.block_count)
                self.flash_block(pos)
                self.log_debug(f"Block {self.block_count} placed at position {pos}")
                self.block_count += 1
                self.count_spinbox.setValue(self.block_count)
                if self.grid.valid_positions and len(self.grid.blocks) < 144:
                    self.status_label.setText(f"Block {self.block_count-1} placed! Click to place block {self.block_count}")
                else:
                    self.status_label.setText("Grid full! Clear to start over.")
                    self.log_debug("Grid is now full")
            # Clear the processing flag for this position
            if hasattr(self.grid, '_processing_positions'):
                self.grid._processing_positions.discard(pos)
            self.update_debug_log()
            self.update_clipboard_pattern()
        # If cell is already filled, do nothing (no increment, no overwrite)
    
    def clear_grid(self, reset_spinbox=True):
        """Clear the entire grid"""
        if not self.grid:
            return
            
        self.grid.clear_grid(reset_spinbox)
        self.block_count = 1
        if reset_spinbox and self.count_spinbox:
            self.count_spinbox.setValue(1)
        self.status_label.setText("Grid cleared. Ready to create blocks.")
        self.log_debug("Grid cleared")
        self.update_debug_log()
        self.update_clipboard_pattern()
    
    def generate_random_pattern(self):
        """Randomly generate a block pattern following blockmaker rules"""
        if not self.grid or not self.count_spinbox:
            return
            
        target_blocks = self.count_spinbox.value()  # Read before clearing grid
        self.log_debug(f"[RANDOM] Target block count from spinbox: {target_blocks}")
        self.clear_grid(reset_spinbox=False)  # Don't reset spinbox here
        
        # Place first block in center - always number as 1 (displays as "+")
        center = self.grid.grid_size // 2
        self.grid.add_block((center, center), 1)  # Always use 1 for first block
        blocks_placed = 1
        block_num = 2
        self.log_debug(f"Random: Placed block 1 at ({center}, {center})")
        
        # Continue placing blocks until target is reached, grid is full, or 12x12 limit
        while blocks_placed < target_blocks and self.grid.valid_positions and len(self.grid.blocks) < 144:
            pos = random.choice(list(self.grid.valid_positions))
            self.grid.add_block(pos, block_num)
            self.grid.update_valid_positions()  # Explicitly update valid positions
            self.log_debug(f"Random: Placed block {block_num} at {pos}")
            self.log_debug(f"Random: Valid positions after block {block_num}: {len(self.grid.valid_positions)}")
            blocks_placed += 1
            block_num += 1
        
        # Update UI state - set to next block number for manual placement
        self.block_count = block_num
        self.count_spinbox.setValue(target_blocks)  # Keep the original target count
        
        if blocks_placed == target_blocks:
            self.status_label.setText(f"Random pattern generated with {blocks_placed} blocks!")
        else:
            self.status_label.setText(f"Grid full! Generated {blocks_placed} blocks (max possible).")
        
        # Update debug log and clipboard
        self.update_debug_log()
        self.update_clipboard_pattern()
    
    def log_debug(self, message: str):
        """Add a message to the debug log"""
        if not self.debug_text:
            return
            
        timestamp = QTimer().remainingTime() if hasattr(QTimer(), 'remainingTime') else "N/A"
        self.debug_text.appendPlainText(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.debug_text.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
    
    def update_debug_log(self):
        """Update debug log with current grid state"""
        if not self.grid:
            return
            
        self.log_debug(f"Grid state: {len(self.grid.blocks)} blocks placed")
        if self.grid.blocks:
            positions = list(self.grid.blocks.keys())
            self.log_debug(f"Block positions: {positions}")
        if self.grid.valid_positions:
            valid_count = len(self.grid.valid_positions)
            self.log_debug(f"Valid positions: {valid_count}")
    
    def update_clipboard_pattern(self):
        """Generate and update clipboard pattern text"""
        if not self.grid or not self.clipboard_text:
            return
            
        if not self.grid.blocks:
            self.clipboard_text.setPlainText("No blocks placed")
            return
        
        # Create ASCII representation of the pattern
        pattern = self.generate_ascii_pattern()
        self.clipboard_text.setPlainText(pattern)
    
    def generate_ascii_pattern(self) -> str:
        """Generate ASCII representation of the block pattern, never show -999 (flash value)"""
        if not self.grid or not self.grid.blocks:
            return "No blocks placed"
        min_row = min(pos[0] for pos in self.grid.blocks.keys())
        max_row = max(pos[0] for pos in self.grid.blocks.keys())
        min_col = min(pos[1] for pos in self.grid.blocks.keys())
        max_col = max(pos[1] for pos in self.grid.blocks.keys())
        pattern_lines = []
        pattern_lines.append(f"Block Pattern ({len(self.grid.blocks)} blocks):")
        pattern_lines.append("=" * 30)
        for row in range(min_row, max_row + 1):
            line = ""
            for col in range(min_col, max_col + 1):
                if (row, col) in self.grid.blocks:
                    block_num = self.grid.blocks[(row, col)]
                    if block_num == -999:
                        line += ". "  # treat flash as empty
                    elif block_num == 1:
                        line += "+ "
                    else:
                        line += f"{block_num} "
                else:
                    line += ". "
            pattern_lines.append(line.rstrip())
        return "\n".join(pattern_lines)
    
    def copy_to_clipboard(self):
        """Copy the pattern text to system clipboard"""
        if not self.clipboard_text:
            return
            
        pattern_text = self.clipboard_text.toPlainText()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(pattern_text)
        self.status_label.setText("Pattern copied to clipboard!")
        self.log_debug("Pattern copied to clipboard")

    def toggle_debug_log(self):
        """Toggle debug log visibility"""
        if not self.debug_text or not self.debug_toggle_btn:
            return
            
        if self.debug_toggle_btn.isChecked():
            self.debug_text.hide()
            self.debug_toggle_btn.setText("Show Debug")
        else:
            self.debug_text.show()
            self.debug_toggle_btn.setText("Hide Debug")

    def flash_block(self, pos: Tuple[int, int]):
        """Flash a block for visual feedback"""
        if not self.grid:
            return
            
        import threading
        from PyQt5.QtCore import QTimer
        orig_color = GOLD
        flash_color = "#fffbe6"
        row, col = pos
        # Store the original block number before flashing
        original_block_num = self.grid.blocks[pos]
        # Temporarily override the block color
        self.grid.blocks[pos] = -999  # Use a special value
        self.grid.update()
        def restore():
            if self.grid:
                self.grid.blocks[pos] = original_block_num  # Restore original number
                self.grid.update()
        QTimer.singleShot(200, restore)

    def generate_stars_pattern(self):
        """Generate a stars pattern with hybrid rules: attraction, mirroring, and symmetry breaks"""
        if not self.grid or not self.count_spinbox:
            return
            
        target_blocks = self.count_spinbox.value()  # Read before clearing grid
        self.log_debug(f"[STARS] Target block count from spinbox: {target_blocks}")
        self.clear_grid(reset_spinbox=False)  # Don't reset spinbox here
        
        # Place first block in center - always number as 1 (displays as "+")
        center = self.grid.grid_size // 2
        self.grid.add_block((center, center), 1)  # Always use 1 for first block
        blocks_placed = 1
        block_num = 2
        last_pos = (center, center)  # Track the last block position
        mirror_target = None  # Track position to mirror from
        mirror_direction = None  # Track which direction to mirror
        
        self.log_debug(f"Stars: Placed block 1 at ({center}, {center})")
        
        # Continue placing blocks until target is reached, grid is full, or 12x12 limit
        while blocks_placed < target_blocks and len(self.grid.blocks) < 144:
            # Get all available positions (no adjacency requirement for stars)
            available_positions = []
            for row in range(self.grid.grid_size):
                for col in range(self.grid.grid_size):
                    if (row, col) not in self.grid.blocks:
                        available_positions.append((row, col))
            
            if not available_positions:
                break
                
            # Determine placement strategy
            if mirror_target and mirror_direction and random.random() > 0.2:  # 80% chance to follow mirror rule
                # Mirror in the specified direction
                pos = self.calculate_mirror_position(mirror_target, mirror_direction)
                if pos in available_positions:
                    self.grid.add_block(pos, block_num)
                    self.log_debug(f"Stars: Placed block {block_num} at mirrored {pos} ({mirror_direction} from {mirror_target})")
                else:
                    # Fallback to random if mirrored position not available
                    pos = random.choice(available_positions)
                    self.grid.add_block(pos, block_num)
                    self.log_debug(f"Stars: Placed block {block_num} at random {pos} (mirrored position not available)")
                mirror_target = None  # Reset mirror after use
                mirror_direction = None
                
            elif random.random() < 0.4:  # 40% chance of attraction
                # Place adjacent to last block
                adjacent_positions = self.get_adjacent_positions(last_pos)
                valid_adjacent = [pos for pos in adjacent_positions if pos in available_positions]
                
                if valid_adjacent:
                    pos = random.choice(valid_adjacent)
                    self.grid.add_block(pos, block_num)
                    self.log_debug(f"Stars: Placed block {block_num} at attracted {pos} (adjacent to {last_pos})")
                    
                    # Set up mirroring for next block
                    mirror_target = pos
                    mirror_direction = random.choice(['N', 'E', 'S', 'W'])
                    self.log_debug(f"Stars: Next block will mirror {mirror_direction} from {pos}")
                else:
                    # Fallback to random if no valid adjacent positions
                    pos = random.choice(available_positions)
                    self.grid.add_block(pos, block_num)
                    self.log_debug(f"Stars: Placed block {block_num} at random {pos} (no valid adjacent positions)")
                    
            else:  # Random placement
                pos = random.choice(available_positions)
                self.grid.add_block(pos, block_num)
                self.log_debug(f"Stars: Placed block {block_num} at random {pos}")
            
            last_pos = pos
            blocks_placed += 1
            block_num += 1
        
        # Update UI state - set to next block number for manual placement
        self.block_count = block_num
        self.count_spinbox.setValue(target_blocks)  # Keep the original target count
        
        if blocks_placed == target_blocks:
            self.status_label.setText(f"Stars pattern generated with {blocks_placed} blocks!")
        else:
            self.status_label.setText(f"Grid full! Generated {blocks_placed} blocks (max possible).")
        
        # Update debug log and clipboard
        self.update_debug_log()
        self.update_clipboard_pattern()
    
    def get_adjacent_positions(self, pos):
        """Get all adjacent positions to a given position"""
        row, col = pos
        adjacent = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # N, S, W, E
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.grid.grid_size and 0 <= new_col < self.grid.grid_size:
                adjacent.append((new_row, new_col))
        return adjacent
    
    def calculate_mirror_position(self, target_pos, direction):
        """Calculate mirrored position in specified direction"""
        row, col = target_pos
        grid_size = self.grid.grid_size
        
        if direction == 'N':  # Mirror North (top of grid)
            return (0, col)
        elif direction == 'S':  # Mirror South (bottom of grid)
            return (grid_size - 1, col)
        elif direction == 'E':  # Mirror East (right of grid)
            return (row, grid_size - 1)
        elif direction == 'W':  # Mirror West (left of grid)
            return (row, 0)
        else:
            return target_pos  # Fallback

    def generate_glyph_pattern(self):
        """Generate a glyph pattern: border, 4 inner corners, and multiple random vertical-symmetry rings with empty center."""
        import random
        if not self.grid or not self.count_spinbox:
            return
        
        # Step 1: Determine target block count
        user_blocks = self.count_spinbox.value()
        grid_size = self.grid.grid_size
        max_possible = grid_size * grid_size
        min_glyph_blocks = 62
        if user_blocks < min_glyph_blocks:
            target_blocks = random.randint(min_glyph_blocks, min(max_possible, min_glyph_blocks + 38))  # e.g. up to 100
            self.count_spinbox.setValue(target_blocks)
        else:
            target_blocks = user_blocks
        self.log_debug(f"[GLYPH] Target block count: {target_blocks}")
        self.clear_grid(reset_spinbox=False)
        
        blocks_placed = 0
        block_num = 1
        center_row = grid_size // 2
        center_col = grid_size // 2
        
        # Step 2: Fill the border (perimeter)
        perimeter_positions = self.get_grid_perimeter_positions()
        for pos in perimeter_positions:
            self.grid.add_block(pos, block_num)
            block_num += 1
            blocks_placed += 1
            if blocks_placed >= target_blocks:
                self._finalize_glyph(block_num, target_blocks, blocks_placed)
                return
        
        # Step 3: Place the four inner corners
        inner_corners = [(1,1), (1,grid_size-2), (grid_size-2,1), (grid_size-2,grid_size-2)]
        for pos in inner_corners:
            if pos not in self.grid.blocks:
                self.grid.add_block(pos, block_num)
                block_num += 1
                blocks_placed += 1
                if blocks_placed >= target_blocks:
                    self._finalize_glyph(block_num, target_blocks, blocks_placed)
                    return
        
        # Step 4: Randomly decide if the ring is attached to corners
        attach_ring = random.choice([True, False])
        self.log_debug(f"Glyph: Ring will be {'attached' if attach_ring else 'detached'} from corners")
        
        # Step 5: Generate 2-4 random symmetrical rings with empty center
        num_rings = random.randint(2, 4)
        possible_radii = list(range(2, (grid_size-1)//2))
        random.shuffle(possible_radii)
        used_radii = sorted(possible_radii[:num_rings])
        self.log_debug(f"Glyph: Using radii {used_radii}")
        for ring_radius in used_radii:
            ring_positions = []
            for row in range(1, grid_size-1):
                for col in range(1, grid_size-1):
                    # Manhattan distance from center
                    if abs(row - center_row) + abs(col - center_col) == ring_radius:
                        # For vertical symmetry, only add left half, mirror right
                        if col <= center_col:
                            ring_positions.append((row, col))
            # Randomly skip some positions for variety
            skip_chance = 0.25 if ring_radius > 2 else 0.1
            ring_positions = [pos for pos in ring_positions if random.random() > skip_chance]
            # Place ring blocks in vertical symmetry pairs
            for pos in ring_positions:
                mirror_col = grid_size - 1 - pos[1]
                mirror_pos = (pos[0], mirror_col)
                # If detached, skip if adjacent to any inner corner
                if not attach_ring:
                    if any(abs(pos[0]-c[0]) + abs(pos[1]-c[1]) == 1 for c in inner_corners):
                        continue
                    if any(abs(mirror_pos[0]-c[0]) + abs(mirror_pos[1]-c[1]) == 1 for c in inner_corners):
                        continue
                # Always keep the center empty
                if pos == (center_row, center_col) or mirror_pos == (center_row, center_col):
                    continue
                # Place both pos and its mirror if not already filled
                for p in [pos, mirror_pos]:
                    if p not in self.grid.blocks:
                        self.grid.add_block(p, block_num)
                        block_num += 1
                        blocks_placed += 1
                        if blocks_placed >= target_blocks:
                            self._finalize_glyph(block_num, target_blocks, blocks_placed)
                            return
        self._finalize_glyph(block_num, target_blocks, blocks_placed)

    def _finalize_glyph(self, block_num, target_blocks, blocks_placed):
        self.block_count = block_num
        # Always update the spinbox to the actual number of blocks placed (not just the target)
        if self.count_spinbox:
            self.count_spinbox.setValue(blocks_placed)
        if self.status_label:
            if blocks_placed == target_blocks:
                self.status_label.setText(f"Glyph pattern generated with {blocks_placed} blocks!")
            else:
                self.status_label.setText(f"Grid full! Generated {blocks_placed} blocks (max possible).")
        self.update_debug_log()
        self.update_clipboard_pattern()

    def get_grid_perimeter_positions(self):
        """Get all positions around the perimeter of the grid in order"""
        positions = []
        grid_size = self.grid.grid_size
        
        # Top row (left to right)
        for col in range(grid_size):
            positions.append((0, col))
        
        # Right column (top to bottom, excluding corners)
        for row in range(1, grid_size - 1):
            positions.append((row, grid_size - 1))
        
        # Bottom row (right to left, excluding corners)
        for col in range(grid_size - 1, -1, -1):
            positions.append((grid_size - 1, col))
        
        # Left column (bottom to top, excluding corners)
        for row in range(grid_size - 2, 0, -1):
            positions.append((row, 0))
        
        return positions

    def mirror_grid_horizontally(self):
        """Mirror the current grid horizontally (across the vertical axis)."""
        if not self.grid:
            return
        grid_size = self.grid.grid_size
        current_blocks = dict(self.grid.blocks)  # Copy to avoid modifying during iteration
        next_num = max(current_blocks.values(), default=0) + 1
        new_blocks = []
        for (row, col), num in current_blocks.items():
            mirror_col = grid_size - 1 - col
            mirror_pos = (row, mirror_col)
            if mirror_pos not in self.grid.blocks:
                new_blocks.append((mirror_pos, next_num))
                next_num += 1
        for pos, num in new_blocks:
            self.grid.add_block(pos, num)
        self.block_count = next_num
        if self.count_spinbox:
            self.count_spinbox.setValue(len(self.grid.blocks))
        self.status_label.setText(f"Mirrored horizontally. Total blocks: {len(self.grid.blocks)}")
        self.update_debug_log()
        self.update_clipboard_pattern()

    def mirror_grid_vertically(self):
        """Mirror the current grid vertically (across the horizontal axis)."""
        if not self.grid:
            return
        grid_size = self.grid.grid_size
        current_blocks = dict(self.grid.blocks)
        next_num = max(current_blocks.values(), default=0) + 1
        new_blocks = []
        for (row, col), num in current_blocks.items():
            mirror_row = grid_size - 1 - row
            mirror_pos = (mirror_row, col)
            if mirror_pos not in self.grid.blocks:
                new_blocks.append((mirror_pos, next_num))
                next_num += 1
        for pos, num in new_blocks:
            self.grid.add_block(pos, num)
        self.block_count = next_num
        if self.count_spinbox:
            self.count_spinbox.setValue(len(self.grid.blocks))
        self.status_label.setText(f"Mirrored vertically. Total blocks: {len(self.grid.blocks)}")
        self.update_debug_log()
        self.update_clipboard_pattern()


def main():
    """Main function to run the blockmaker as standalone"""
    app = QApplication(sys.argv)
    window = BlockmakerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 