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
import json
import math
import os
from datetime import datetime, date
from typing import List, Tuple, Set, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QSpinBox, QLineEdit, QFrame, QSizePolicy,
    QApplication, QPlainTextEdit, QSplitter, QTabWidget, QDateEdit,
    QTextEdit, QGroupBox, QFormLayout, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDate
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QBrush, QKeySequence, QFontDatabase

# Import GATE CREATOR and gate portal modules
try:
    from gate_creator import GateCreator, create_gate_from_glyph, verify_gate_pattern
    GATE_CREATOR_AVAILABLE = True
    print("GATE Creator module imported successfully")
except ImportError as e:
    GATE_CREATOR_AVAILABLE = False
    print(f"Warning: Gate Creator module not available - {e}")
    print(f"Import error details: {type(e).__name__}: {str(e)}")
except Exception as e:
    GATE_CREATOR_AVAILABLE = False
    print(f"Unexpected error importing Gate Creator: {type(e).__name__}: {str(e)}")

try:
    from gate_portal import GatePortal, create_gate_portal, verify_gate_portal, get_integration_types
    GATE_PORTAL_AVAILABLE = True
    print("GATE Portal module imported successfully")
except ImportError as e:
    GATE_PORTAL_AVAILABLE = False
    print(f"Warning: Gate Portal module not available - {e}")
    print(f"Import error details: {type(e).__name__}: {str(e)}")
except Exception as e:
    GATE_PORTAL_AVAILABLE = False
    print(f"Unexpected error importing Gate Portal: {type(e).__name__}: {str(e)}")

print(f"DEBUG: GATE_CREATOR_AVAILABLE = {GATE_CREATOR_AVAILABLE}")
print(f"DEBUG: GATE_PORTAL_AVAILABLE = {GATE_PORTAL_AVAILABLE}")

# Style constants for Blockmaker
GOLD = "#f7c873"
UPGRADE_BG = "#2d3748"
TAB_BG = "#4a5568"
TEXT_COLOR = "#e2e8f0"
BORDER_COLOR = "#718096"
SECONDARY_ACCENT = "#667eea"

# Font constants
DREAM_MECHA_FONT = "NCL Razor Demo"  # This will be the loaded font name
FALLBACK_FONTS = "'Consolas', 'Monaco', 'Courier New', monospace"


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


class DreamMechaIntegration(QWidget):
    """Dream Mecha game integration panel for content generation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generated_pieces = []
        self.generated_enemies = []
        self.manual_pieces = []  # Separate list for manual pieces
        self.current_date = date.today()
        self.setup_ui()
        
    def setup_ui(self):
        """Create the Dream Mecha integration UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Dream Mecha - Content Generator")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {GOLD};
            margin-bottom: 10px;
            font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
            letter-spacing: 1px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Main splitter for left/right layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(3)
        main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {BORDER_COLOR};
                border-radius: 1px;
            }}
        """)
        
        # Left side - Generation Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        
        # Generation Parameters Group
        params_group = QGroupBox("Generation Parameters")
        params_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        params_layout = QFormLayout(params_group)
        
        # Player Count
        self.player_count_spinbox = QSpinBox()
        self.player_count_spinbox.setRange(1, 100)
        self.player_count_spinbox.setValue(10)
        self.player_count_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 80px;
            }}
        """)
        params_layout.addRow("Active Player Count:", self.player_count_spinbox)
        
        # Voidstate
        self.voidstate_spinbox = QSpinBox()
        self.voidstate_spinbox.setRange(1, 50)
        self.voidstate_spinbox.setValue(1)
        self.voidstate_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 80px;
            }}
        """)
        params_layout.addRow("Current Voidstate:", self.voidstate_spinbox)
        
        # Generation Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet(f"""
            QDateEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 120px;
            }}
        """)
        params_layout.addRow("Generation Date:", self.date_edit)
        
        left_layout.addWidget(params_group)
        
        # Generation Controls Group
        controls_group = QGroupBox("Generation Controls")
        controls_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        controls_layout = QVBoxLayout(controls_group)
        
        # Generation Buttons
        self.generate_btn = QPushButton("Generate Daily Content")
        self.generate_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {GOLD}; 
                color: #000000; 
                border: none; 
                border-radius: 5px; 
                padding: 12px 20px; 
                font-weight: bold; 
                font-size: 14px;
            }}
            QPushButton:hover {{ background: #ffd700; }}
            QPushButton:pressed {{ background: #e6c200; }}
        """)
        controls_layout.addWidget(self.generate_btn)
        
        self.export_btn = QPushButton("Export to JSON")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {SECONDARY_ACCENT}; 
                color: #fff; 
                border: none; 
                border-radius: 5px; 
                padding: 10px 16px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ background: #8ea6f8; }}
            QPushButton:pressed {{ background: #5c6bc0; }}
        """)
        controls_layout.addWidget(self.export_btn)
        
        self.preview_btn = QPushButton("Preview Shop")
        self.preview_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {SECONDARY_ACCENT}; 
                color: #fff; 
                border: none; 
                border-radius: 5px; 
                padding: 10px 16px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ background: #8ea6f8; }}
            QPushButton:pressed {{ background: #5c6bc0; }}
        """)
        controls_layout.addWidget(self.preview_btn)
        
        # Manual Piece Generation
        manual_group = QGroupBox("Manual Piece Generation")
        manual_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        manual_layout = QFormLayout(manual_group)
        
        self.manual_block_count = QSpinBox()
        self.manual_block_count.setRange(1, 80)
        self.manual_block_count.setValue(5)
        self.manual_block_count.setStyleSheet(f"""
            QSpinBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 80px;
            }}
        """)
        manual_layout.addRow("Block Count:", self.manual_block_count)
        
        self.manual_stat_type = QComboBox()
        self.manual_stat_type.addItems(["random", "hp", "attack", "defense", "speed"])
        self.manual_stat_type.setStyleSheet(f"""
            QComboBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 100px;
            }}
        """)
        manual_layout.addRow("Stat Type:", self.manual_stat_type)
        
        self.generate_manual_btn = QPushButton("Generate Manual Piece")
        self.generate_manual_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {BORDER_COLOR}; 
                color: {TEXT_COLOR}; 
                border: none; 
                border-radius: 5px; 
                padding: 8px 16px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ background: #4a5568; }}
        """)
        manual_layout.addRow("", self.generate_manual_btn)
        
        controls_layout.addWidget(manual_group)
        left_layout.addWidget(controls_group)
        
        # Add left widget to splitter
        main_splitter.addWidget(left_widget)
        
        # Right side - Status and Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Status Group
        status_group = QGroupBox("Generation Status")
        status_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 10px;
            }}
        """)
        self.status_text.setMaximumHeight(200)
        status_layout.addWidget(self.status_text)
        
        right_layout.addWidget(status_group)
        
        # Preview Group
        preview_group = QGroupBox("Generated Content Preview")
        preview_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 11px;
            }}
        """)
        self.preview_text.setMinimumHeight(400)  # Make preview area larger
        preview_layout.addWidget(self.preview_text)
        
        right_layout.addWidget(preview_group)
        
        # Manual Piece Preview Group
        manual_preview_group = QGroupBox("Manual Piece Preview")
        manual_preview_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        manual_preview_layout = QVBoxLayout(manual_preview_group)
        
        self.manual_preview_text = QTextEdit()
        self.manual_preview_text.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 11px;
            }}
        """)
        self.manual_preview_text.setMinimumHeight(200)
        manual_preview_layout.addWidget(self.manual_preview_text)
        
        right_layout.addWidget(manual_preview_group)
        
        # Add right widget to splitter
        main_splitter.addWidget(right_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 600])
        
        layout.addWidget(main_splitter)
        
        # Connect signals
        self.generate_btn.clicked.connect(self.generate_daily_content)
        self.export_btn.clicked.connect(self.export_to_json)
        self.preview_btn.clicked.connect(self.preview_shop)
        self.generate_manual_btn.clicked.connect(self.generate_manual_piece)
        
        # Initial status
        self.log_status("Dream Mecha integration ready. Set parameters and generate content.")
        
    def log_status(self, message: str):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        
    def generate_daily_content(self):
        """Generate daily shop pieces and enemies"""
        try:
            player_count = self.player_count_spinbox.value()
            voidstate = self.voidstate_spinbox.value()
            gen_date = self.date_edit.date().toPyDate()
            
            self.log_status(f"Generating daily content for {gen_date}...")
            self.log_status(f"Player count: {player_count}, Voidstate: {voidstate}")
            
            # Generate shop pieces
            self.generated_pieces = self.generate_daily_pieces_beta(player_count, voidstate, gen_date)
            self.log_status(f"Generated {len(self.generated_pieces)} shop pieces")
            
            # Generate enemies
            estimated_power = self.estimate_player_power(player_count)
            self.generated_enemies = self.generate_daily_enemies(voidstate, estimated_power)
            self.log_status(f"Generated {len(self.generated_enemies)} enemies")
            
            self.log_status("Daily content generation complete!")
            self.update_preview()
            
        except Exception as e:
            self.log_status(f"Error generating content: {str(e)}")
            
    def generate_daily_pieces_beta(self, player_count: int, voidstate: int, gen_date: date) -> List[Dict[str, Any]]:
        """Generate pieces for daily shop using random algorithm only"""
        pieces = []
        
        # Calculate total pieces needed
        base_pieces = 8
        scaling_pieces = math.floor(player_count * 1.5)
        total_pieces = base_pieces + scaling_pieces
        
        # Size distribution (all using random algorithm)
        small_pieces = math.floor(total_pieces * 0.5)    # 1-5 blocks
        medium_pieces = math.floor(total_pieces * 0.4)   # 6-15 blocks  
        large_pieces = math.floor(total_pieces * 0.1)    # 16-25 blocks
        
        # Generate pieces by size category
        piece_id_counter = 1
        
        # Small pieces (1-5 blocks)
        for i in range(small_pieces):
            block_count = random.randint(1, 5)
            piece = self.generate_single_piece_manual(block_count, "random")
            piece["id"] = f"piece_{gen_date.strftime('%Y%m%d')}_{piece_id_counter:03d}"
            piece["size_category"] = "small"
            piece["generation_method"] = "random"
            piece["beta_mode"] = True
            pieces.append(piece)
            piece_id_counter += 1
            
        # Medium pieces (6-15 blocks)
        for i in range(medium_pieces):
            block_count = random.randint(6, 15)
            piece = self.generate_single_piece_manual(block_count, "random")
            piece["id"] = f"piece_{gen_date.strftime('%Y%m%d')}_{piece_id_counter:03d}"
            piece["size_category"] = "medium"
            piece["generation_method"] = "random"
            piece["beta_mode"] = True
            pieces.append(piece)
            piece_id_counter += 1
            
        # Large pieces (16-25 blocks)
        for i in range(large_pieces):
            block_count = random.randint(16, 25)
            piece = self.generate_single_piece_manual(block_count, "random")
            piece["id"] = f"piece_{gen_date.strftime('%Y%m%d')}_{piece_id_counter:03d}"
            piece["size_category"] = "large"
            piece["generation_method"] = "random"
            piece["beta_mode"] = True
            pieces.append(piece)
            piece_id_counter += 1
            
        return pieces
        
    def generate_single_piece_manual(self, block_count: int, stat_type: str) -> Dict[str, Any]:
        """Generate pieces using REAL blockmaker algorithms"""
        # Determine generation method
        # ONLY use random generation - no stars or glyphs
        algorithm = "random"
        
        # Generate pattern using REAL blockmaker algorithms
        pattern = self.generate_blockmaker_pattern(block_count, algorithm)
        
        # Calculate stats using proper game rules
        stats = self.calculate_proper_piece_stats(block_count, stat_type, algorithm)
        
        # Determine stat type
        if stat_type == "random":
            stat_types = ["hp", "attack", "defense", "speed"]
            weights = [0.4, 0.25, 0.2, 0.15]  # 40% HP, 25% Attack, 20% Defense, 15% Speed
            stat_type = random.choices(stat_types, weights=weights)[0]
            
        # Create piece data
        piece_data = {
            "pattern": pattern,
            "pattern_array": self.pattern_to_array(pattern),
            "blocks": block_count,
            "stats": stats,
            "stat_type": stat_type,
            "price": self.calculate_proper_piece_price(block_count, stats),
            "rarity": self.determine_rarity(block_count),
            "algorithm": algorithm
        }
        
        return piece_data
        
    def generate_blockmaker_pattern(self, block_count: int, algorithm: str) -> str:
        """Generate pattern using REAL blockmaker algorithms"""
        # Get the main blockmaker window instance
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, BlockmakerWindow):
                main_window = widget
                break
        
        if not main_window or not main_window.grid:
            # Fallback if main window not available
            return self.generate_fallback_pattern(block_count)
        
        # Store original state
        original_blocks = main_window.grid.blocks.copy()
        original_count = main_window.block_count
        original_spinbox_value = main_window.count_spinbox.value() if main_window.count_spinbox else 1
        
        try:
            # Set up for generation
            main_window.grid.clear_grid(reset_spinbox=False)
            if main_window.count_spinbox:
                main_window.count_spinbox.setValue(block_count)
            
            # Generate pattern using random algorithm only
            main_window.generate_random_pattern()
            
            # Get the generated pattern
            pattern = main_window.generate_ascii_pattern()
            
            # Extract just the pattern part (remove header)
            lines = pattern.split('\n')
            pattern_lines = []
            in_pattern = False
            for line in lines:
                if line.startswith('='):
                    in_pattern = True
                    continue
                if in_pattern and line.strip():
                    pattern_lines.append(line.rstrip())
            
            result_pattern = '\n'.join(pattern_lines) if pattern_lines else self.generate_fallback_pattern(block_count)
            
        except Exception as e:
            print(f"Error generating blockmaker pattern: {e}")
            result_pattern = self.generate_fallback_pattern(block_count)
        
        finally:
            # Restore original state
            main_window.grid.blocks = original_blocks
            main_window.block_count = original_count
            if main_window.count_spinbox:
                main_window.count_spinbox.setValue(original_spinbox_value)
            main_window.grid.update_valid_positions()
            main_window.grid.update()
        
        return result_pattern
    
    def generate_fallback_pattern(self, block_count: int) -> str:
        """Simple fallback pattern if real blockmaker unavailable"""
        # At least generate a proper adjacent pattern
        if block_count <= 0:
            return "+ "
        elif block_count == 1:
            return "+"
        elif block_count == 2:
            return "+ 2"
        elif block_count == 3:
            return "+ 2\n3 ."
        elif block_count == 4:
            return "+ 2\n3 4"
        else:
            # For larger pieces, create a simple rectangular pattern
            pattern = "+ 2\n3 4"
            remaining = block_count - 4
            if remaining > 0:
                pattern += f"\n{5} {6 if remaining > 1 else '.'}"
            if remaining > 2:
                pattern += f"\n{7} {8 if remaining > 3 else '.'}"
        return pattern
        
    def pattern_to_array(self, pattern: str) -> List[List[int]]:
        """Convert pattern string to 2D array"""
        lines = pattern.strip().split('\n')
        result = []
        for line in lines:
            row = []
            for char in line:
                if char == '+':
                    row.append(1)
                elif char == '.':
                    row.append(0)
                elif char.isdigit():
                    row.append(int(char))
                else:
                    row.append(0)
            result.append(row)
        return result
        
    def calculate_proper_piece_stats(self, block_count: int, stat_type: str, algorithm: str) -> Dict[str, int]:
        """Calculate stats using proper game rules exponential scaling"""
        # Game rules: exponential scaling ~100 HP per block base, exponentially increasing
        base_hp = 100
        scaling_factor = 1.6  # Game rules scaling factor
        total_stat_power = int(base_hp * (block_count ** scaling_factor))
        
        # Distribute stats based on algorithm and type
        if algorithm == "random":
            # Balanced distribution
            hp_ratio, att_ratio, def_ratio, spd_ratio = 0.4, 0.25, 0.2, 0.15
        elif algorithm == "stars":
            # Attack-focused
            hp_ratio, att_ratio, def_ratio, spd_ratio = 0.3, 0.4, 0.15, 0.15
        elif algorithm == "glyph":
            # Defense-focused
            hp_ratio, att_ratio, def_ratio, spd_ratio = 0.35, 0.15, 0.35, 0.15
        else:
            # Default balanced
            hp_ratio, att_ratio, def_ratio, spd_ratio = 0.4, 0.25, 0.2, 0.15
        
        # Each piece gives ONLY ONE stat (random selection)
        stat_types = ["hp", "attack", "defense", "speed"]
        chosen_stat = random.choice(stat_types)
        
        # All power goes to the chosen stat
        base_stats = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "speed": 0
        }
        base_stats[chosen_stat] = total_stat_power
        
        # Add variance (±15%)
        variance = 0.15
        base_value = base_stats[chosen_stat]
        min_value = int(base_value * (1 - variance))
        max_value = int(base_value * (1 + variance))
        base_stats[chosen_stat] = random.randint(min_value, max_value)
        
        # Convert to expected format
        return {
            "hp": base_stats["hp"],
            "att": base_stats["attack"],
            "def": base_stats["defense"],
            "spd": base_stats["speed"]
        }
        
    def calculate_proper_piece_price(self, block_count: int, stats: Dict[str, int]) -> int:
        """Calculate piece price using game rules exponential scaling"""
        # Game rules: base_cost * (block_count ^ scaling_factor)
        base_cost = 100
        scaling_factor = 1.8
        block_price = int(base_cost * (block_count ** scaling_factor))
        
        # Add stat bonus (30% of total stats value)
        total_stats = stats["hp"] + stats["att"] + stats["def"] + stats["spd"]
        stat_bonus = int(total_stats * 0.3)
        
        final_price = block_price + stat_bonus
        
        # Add price variance (±10%)
        variance = 0.1
        min_price = int(final_price * (1 - variance))
        max_price = int(final_price * (1 + variance))
        
        return random.randint(min_price, max_price)
        
    def determine_rarity(self, block_count: int) -> str:
        """Determine piece rarity based on block count"""
        if block_count <= 5:
            return "common"
        elif block_count <= 15:
            return "uncommon"
        elif block_count <= 25:
            return "rare"
        else:
            return "legendary"
            
    def estimate_player_power(self, player_count: int) -> Dict[str, int]:
        """Estimate average player power for enemy scaling"""
        # For first day, use generic values that 4 people could handle
        return {
            "avg_hp": 50000,
            "avg_att": 8000,
            "avg_def": 3000,
            "avg_spd": 2000
        }
        
    def generate_daily_enemies(self, voidstate: int, estimated_power: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate enemies based on voidstate and estimated player power"""
        enemies = []
        
        # Generate 1-3 enemies based on voidstate
        enemy_count = min(3, 1 + voidstate // 5)
        
        for i in range(enemy_count):
            # Base enemy scales with estimated community power
            base_hp = estimated_power["avg_hp"] * 0.8
            base_att = estimated_power["avg_att"] * 0.6
            
            # Voidstate multiplier  
            void_multiplier = 1 + (voidstate * 0.2)
            
            enemy_hp = int(base_hp * void_multiplier)
            enemy_att = int(base_att * void_multiplier)
            enemy_def = int(enemy_hp * 0.1)  # 10% of HP
            enemy_spd = int(enemy_att * 0.3) # 30% of attack
            
            description = self.generate_enemy_description(enemy_hp, enemy_att, enemy_def, enemy_spd)
            
            enemy = {
                "id": f"enemy_{date.today().strftime('%Y%m%d')}_{i+1:03d}",
                "hp": enemy_hp,
                "att": enemy_att, 
                "def": enemy_def,
                "spd": enemy_spd,
                "description": description,
                "threat_level": self.determine_threat_level(enemy_hp, enemy_att)
            }
            
            enemies.append(enemy)
            
        return enemies
        
    def generate_enemy_description(self, hp: int, att: int, def_val: int, spd: int) -> str:
        """Generate procedural enemy description based on stats"""
        # Simplified descriptor system for now
        descriptors = {
            "size": {
                "tier1": ["small", "tiny", "diminutive"],
                "tier2": ["hulking", "large", "imposing"],
                "tier3": ["colossal", "gigantic", "enormous"],
                "tier4": ["world-ending", "cosmic", "reality-bending"]
            },
            "threat": {
                "tier1": ["with gnashing teeth", "sporting sharp claws"],
                "tier2": ["bristling with razor spikes", "wreathed in shadow flames"],
                "tier3": ["channeling destructive force", "emanating reality-warping power"],
                "tier4": ["radiating universe-ending power", "bending space-time"]
            }
        }
        
        # Determine tiers based on stats
        hp_tier = min(4, 1 + hp // 100000)  # Scale tiers based on HP
        att_tier = min(4, 1 + att // 10000)  # Scale tiers based on attack
        
        # Select descriptors
        size_desc = random.choice(descriptors["size"][f"tier{hp_tier}"])
        threat_desc = random.choice(descriptors["threat"][f"tier{att_tier}"])
        
        return f"A {size_desc} void beast {threat_desc}"
        
    def determine_threat_level(self, hp: int, att: int) -> str:
        """Determine enemy threat level"""
        total_power = hp + att
        if total_power < 50000:
            return "low"
        elif total_power < 150000:
            return "moderate"
        elif total_power < 500000:
            return "high"
        else:
            return "extreme"
            
    def generate_manual_piece(self):
        """Generate a single piece for testing"""
        try:
            block_count = self.manual_block_count.value()
            stat_type = self.manual_stat_type.currentText()
            
            self.log_status(f"Generating manual piece: {block_count} blocks, {stat_type} stat")
            
            piece = self.generate_single_piece_manual(block_count, stat_type)
            piece["id"] = f"manual_piece_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            piece["size_category"] = "manual"
            piece["generation_method"] = "manual"
            piece["beta_mode"] = True
            
            self.manual_pieces.append(piece)
            self.log_status(f"Manual piece generated: {piece['id']}")
            self.update_manual_preview()
            
        except Exception as e:
            self.log_status(f"Error generating manual piece: {str(e)}")
            
    def export_to_json(self):
        """Export generated content to JSON file"""
        try:
            if not self.generated_pieces and not self.generated_enemies:
                self.log_status("No content to export. Generate content first.")
                return
                
            gen_date = self.date_edit.date().toPyDate()
            player_count = self.player_count_spinbox.value()
            voidstate = self.voidstate_spinbox.value()
            
            # Create export data
            export_data = {
                "date": gen_date.strftime("%Y-%m-%d"),
                "voidstate": voidstate,
                "generation_metadata": {
                    "player_count": player_count,
                    "pieces_generated": len(self.generated_pieces),
                    "generation_time": datetime.now().isoformat() + "Z"
                },
                "shop_pieces": self.generated_pieces,
                "enemies": self.generated_enemies,
                "economy_data": {
                    "base_zoltan_reward": 50000,
                    "voidstate_bonus": voidstate * 10000,
                    "total_zoltan_reward": 50000 + (voidstate * 10000),
                    "repair_cost_multiplier": 0.05
                }
            }
            
            # Ensure directory exists
            export_dir = os.path.join("dream_mecha", "database", "daily")
            os.makedirs(export_dir, exist_ok=True)
            
            # Export file
            filename = f"{gen_date.strftime('%Y-%m-%d')}.json"
            filepath = os.path.join(export_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            self.log_status(f"Exported daily content to: {filepath}")
            
        except Exception as e:
            self.log_status(f"Error exporting to JSON: {str(e)}")
            
    def preview_shop(self):
        """Preview the generated shop pieces"""
        if not self.generated_pieces:
            self.log_status("No pieces to preview. Generate content first.")
            return
            
        preview_text = "=== DREAM MECHA DAILY SHOP ===\n\n"
        
        for i, piece in enumerate(self.generated_pieces, 1):
            preview_text += f"Piece {i}: {piece['id']}\n"
            preview_text += f"  Size: {piece['size_category']} ({piece['blocks']} blocks)\n"
            # Only show the single stat that has value
            active_stat = None
            for stat_name, stat_value in piece['stats'].items():
                if stat_value > 0:
                    active_stat = (stat_name.upper(), stat_value)
                    break
            
            if active_stat:
                preview_text += f"  Stats: {active_stat[0]}:{active_stat[1]}\n"
            else:
                preview_text += f"  Stats: ERROR - No active stat found\n"
            preview_text += f"  Type: {piece['stat_type']}\n"
            preview_text += f"  Price: {piece['price']} Zoltans\n"
            preview_text += f"  Rarity: {piece['rarity']}\n"
            preview_text += f"  Pattern:\n{piece['pattern']}\n\n"
            
        if self.generated_enemies:
            preview_text += "=== DAILY ENEMIES ===\n\n"
            for i, enemy in enumerate(self.generated_enemies, 1):
                preview_text += f"Enemy {i}: {enemy['id']}\n"
                preview_text += f"  Stats: HP:{enemy['hp']} ATK:{enemy['att']} DEF:{enemy['def']} SPD:{enemy['spd']}\n"
                preview_text += f"  Threat: {enemy['threat_level']}\n"
                preview_text += f"  Description: {enemy['description']}\n\n"
                
        self.preview_text.setPlainText(preview_text)
        self.log_status("Shop preview updated")
        
    def update_preview(self):
        """Update the preview with current generated content"""
        if self.generated_pieces or self.generated_enemies:
            self.preview_shop()
    
    def update_manual_preview(self):
        """Update the manual piece preview display"""
        if not self.manual_pieces:
            self.manual_preview_text.setPlainText("No manual pieces generated yet.")
            return
            
        preview_text = "=== MANUAL PIECE TESTING ===\n\n"
        
        for i, piece in enumerate(self.manual_pieces[-5:], 1):  # Show last 5 manual pieces
            preview_text += f"Piece {i}: {piece['id']}\n"
            preview_text += f"  Size: {piece.get('size_category', 'manual')} ({piece['blocks']} blocks)\n"
            
            # Only show the single active stat
            active_stat = None
            for stat_name, stat_value in piece['stats'].items():
                if stat_value > 0:
                    active_stat = (stat_name.upper(), stat_value)
                    break
            
            if active_stat:
                preview_text += f"  Stats: {active_stat[0]}:{active_stat[1]}\n"
            else:
                preview_text += f"  Stats: ERROR - No active stat found\n"
                
            preview_text += f"  Type: {piece['stat_type']}\n"
            preview_text += f"  Price: {piece['price']} Zoltans\n"
            preview_text += f"  Pattern:\n{piece['pattern']}\n\n"
            
        self.manual_preview_text.setPlainText(preview_text)


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
        """Create the user interface with tab system"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
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
            font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
            letter-spacing: 2px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                background: {UPGRADE_BG};
            }}
            QTabBar::tab {{
                background: {TAB_BG};
                color: {TEXT_COLOR};
                padding: 10px 20px;
                margin-right: 3px;
                min-width: 100px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QTabBar::tab:selected {{
                background: {GOLD};
                color: #000000;
            }}
            QTabBar::tab:hover {{
                background: {SECONDARY_ACCENT};
                color: #ffffff;
            }}
        """)
        
        # Create shared grid first (needed by GATE tabs)
        self.grid = BlockmakerGrid(grid_size=12)
        
        # Create Blockmaker tab
        self.create_blockmaker_tab()
        
        # Create Dream Mecha tab
        self.create_dream_mecha_tab()
        
        # Create Unique Piece Generation tab
        self.create_unique_piece_tab()
        
        # Create GATE tab if available
        if GATE_CREATOR_AVAILABLE:
            print("Creating GATE tab...")
            self.create_gate_tab()
            print("GATE tab created")
        else:
            print("GATE modules not available, skipping tab")
        
        main_layout.addWidget(self.tab_widget)
        
        # Debug: Check tab count
        print(f"DEBUG: Total tabs in widget: {self.tab_widget.count()}")
        for i in range(self.tab_widget.count()):
            tab_text = self.tab_widget.tabText(i)
            print(f"DEBUG: Tab {i}: '{tab_text}'")
    
    def create_blockmaker_tab(self):
        """Create the original Blockmaker tab"""
        blockmaker_widget = QWidget()
        
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
        
        # Add existing grid widget
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
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
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
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
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
        
        # Add main splitter to the blockmaker widget layout
        blockmaker_layout = QVBoxLayout(blockmaker_widget)
        blockmaker_layout.addWidget(main_splitter)
        
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
        blockmaker_layout.addWidget(self.status_label)
        
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
            
        # Add the blockmaker widget to the tab
        self.tab_widget.addTab(blockmaker_widget, "Blockmaker")
        
    def create_dream_mecha_tab(self):
        """Create the Dream Mecha integration tab"""
        self.dream_mecha_integration = DreamMechaIntegration()
        self.tab_widget.addTab(self.dream_mecha_integration, "Dream Mecha")
    
    def create_unique_piece_tab(self):
        """Create the Unique Piece Generation tab with full grid functionality"""
        unique_widget = QWidget()
        layout = QVBoxLayout(unique_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Unique Piece Generation")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {GOLD};
            margin-bottom: 10px;
            font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
            letter-spacing: 1px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        
        # Left side - Grid and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create a new grid instance for unique pieces
        self.unique_grid = BlockmakerGrid(grid_size=12)
        
        # Initialize counter for unique blocks
        self._unique_block_counter = 1
        
        # Connect grid signals
        self.unique_grid.place_block_requested.connect(self.handle_unique_place_block)
        
        # Grid controls from original blockmaker
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
        count_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        count_layout.addWidget(count_label)
        
        self.unique_count_spinbox = QSpinBox()
        self.unique_count_spinbox.setRange(1, 144)
        self.unique_count_spinbox.setValue(1)
        self.unique_count_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 80px;
            }}
        """)
        count_layout.addWidget(self.unique_count_spinbox)
        
        controls_layout.addLayout(count_layout)
        
        # Grid action buttons
        button_layout = QHBoxLayout()
        

        
        self.unique_clear_btn = QPushButton("Clear Grid")
        self.unique_clear_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {BORDER_COLOR}; 
                color: {TEXT_COLOR}; 
                border: none; 
                border-radius: 5px; 
                padding: 8px 16px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ background: #555; }}
            QPushButton:pressed {{ background: #333; }}
        """)
        self.unique_clear_btn.clicked.connect(self.clear_unique_grid)
        button_layout.addWidget(self.unique_clear_btn)
        
        controls_layout.addLayout(button_layout)
        
        left_layout.addWidget(controls_frame)
        
        # Add the grid
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
        
        grid_label = QLabel("Piece Grid")
        grid_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 14px;")
        grid_layout.addWidget(grid_label)
        
        self.unique_grid.setMinimumSize(400, 400)
        grid_layout.addWidget(self.unique_grid, alignment=Qt.AlignCenter)
        
        left_layout.addWidget(grid_frame)
        main_splitter.addWidget(left_widget)
        
        # Right side - Generation controls and preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Generation parameters
        gen_group = QGroupBox("Generation Parameters")
        gen_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        gen_layout = QFormLayout(gen_group)
        
        self.unique_stat_type = QComboBox()
        self.unique_stat_type.addItems(["random", "hp", "attack", "defense", "speed"])
        self.unique_stat_type.setStyleSheet(f"""
            QComboBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
            }}
        """)
        gen_layout.addRow("Stat Type:", self.unique_stat_type)
        
        self.unique_generate_btn = QPushButton("Generate Unique Piece")
        self.unique_generate_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {GOLD}; 
                color: #000000; 
                border: none; 
                border-radius: 5px; 
                padding: 12px 20px; 
                font-weight: bold; 
                font-size: 14px;
            }}
            QPushButton:hover {{ background: #ffd700; }}
            QPushButton:pressed {{ background: #e6c200; }}
        """)
        self.unique_generate_btn.clicked.connect(self.generate_unique_piece)
        gen_layout.addRow("", self.unique_generate_btn)
        
        right_layout.addWidget(gen_group)
        
        # Preview area
        preview_group = QGroupBox("Unique Piece Preview")
        preview_group.setStyleSheet(f"""
            QGroupBox {{
                background: {UPGRADE_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {GOLD};
            }}
        """)
        preview_layout = QVBoxLayout(preview_group)
        
        self.unique_preview_text = QTextEdit()
        self.unique_preview_text.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 11px;
            }}
        """)
        self.unique_preview_text.setMinimumHeight(300)
        preview_layout.addWidget(self.unique_preview_text)
        
        right_layout.addWidget(preview_group)
        
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([500, 400])
        
        layout.addWidget(main_splitter)
        
        self.tab_widget.addTab(unique_widget, "Unique Pieces")
    
    def create_gate_tab(self):
        """Create the GATE tab"""
        if not GATE_CREATOR_AVAILABLE:
            return None
        
        gate_tab_widget = QWidget()
        layout = QVBoxLayout(gate_tab_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("🚪 GATE - Glyph Cryptography and Portal Code Generator")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {GOLD};
            margin-bottom: 10px;
            font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
            letter-spacing: 1px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Create encryption using glyphs as cryptographic algorithms and generate a universal GATE portal code.")
        desc.setStyleSheet(f"color: {TEXT_COLOR}; margin: 5px; text-align: center;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(3)
        main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {BORDER_COLOR};
                border-radius: 1px;
            }}
        """)
        
        # Left side - Grid and Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        
        # Grid section
        grid_label = QLabel("Create Your Glyph:")
        grid_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 16px;")
        left_layout.addWidget(grid_label)
        
        # Add the existing grid
        if hasattr(self, 'grid'):
            left_layout.addWidget(self.grid)
        
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
        
        # Password input
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        password_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password for additional entropy...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
            }}
        """)
        password_layout.addWidget(self.password_input)
        
        controls_layout.addLayout(password_layout)
        
        # Generate GATE button
        generate_gate_btn = QPushButton("🚪 Create GATE from Glyph")
        generate_gate_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GOLD};
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #ffd700;
            }}
        """)
        generate_gate_btn.clicked.connect(self.generate_gate_from_glyph)
        controls_layout.addWidget(generate_gate_btn)
        
        left_layout.addWidget(controls_frame)
        main_splitter.addWidget(left_widget)
        
        # Right side - GATE Creator and Portal
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        
        # GATE Creator section
        gate_creator_label = QLabel("GATE Creator - Cryptography:")
        gate_creator_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 16px;")
        right_layout.addWidget(gate_creator_label)
        
        # GATE display
        self.gate_display = QTextEdit()
        self.gate_display.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 11px;
            }}
        """)
        self.gate_display.setMaximumHeight(150)
        right_layout.addWidget(self.gate_display)
        
        # GATE info section
        gate_info_label = QLabel("GATE Information:")
        gate_info_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 16px;")
        right_layout.addWidget(gate_info_label)
        
        self.gate_info = QTextEdit()
        self.gate_info.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 10px;
            }}
        """)
        right_layout.addWidget(self.gate_info)
        
        # Copy GATE button
        copy_gate_btn = QPushButton("Copy GATE Data to Clipboard")
        copy_gate_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SECONDARY_ACCENT};
                color: #fff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #8ea6f8;
            }}
        """)
        copy_gate_btn.clicked.connect(self.copy_gate_data)
        right_layout.addWidget(copy_gate_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background: {BORDER_COLOR}; margin: 10px 0;")
        right_layout.addWidget(separator)
        
        # GATE Portal section
        gate_portal_label = QLabel("GATE Portal - Universal Code Generator:")
        gate_portal_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 16px;")
        right_layout.addWidget(gate_portal_label)
        
        # Portal controls
        portal_controls_frame = QFrame()
        portal_controls_frame.setStyleSheet(f"""
            QFrame {{
                background: {UPGRADE_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        portal_controls_layout = QVBoxLayout(portal_controls_frame)
        
        # Symbol selection
        symbol_layout = QHBoxLayout()
        symbol_label = QLabel("Portal Symbol:")
        symbol_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        symbol_layout.addWidget(symbol_label)
        
        self.portal_symbol_combo = QComboBox()
        self.portal_symbol_combo.addItems(['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '[', ']', '{', '}', '|', ';', ':', ',', '.', '<', '>', '?', '/', '~', '`', '"', "'", '\\'])
        self.portal_symbol_combo.setStyleSheet(f"""
            QComboBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 60px;
            }}
        """)
        symbol_layout.addWidget(self.portal_symbol_combo)
        
        # Random symbol button
        random_portal_symbol_btn = QPushButton("Random Symbol")
        random_portal_symbol_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SECONDARY_ACCENT};
                color: #fff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #8ea6f8;
            }}
        """)
        random_portal_symbol_btn.clicked.connect(self.set_random_portal_symbol)
        symbol_layout.addWidget(random_portal_symbol_btn)
        
        portal_controls_layout.addLayout(symbol_layout)
        
        # Integration type selection
        integration_layout = QHBoxLayout()
        integration_label = QLabel("Integration Type:")
        integration_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        integration_layout.addWidget(integration_label)
        
        self.integration_combo = QComboBox()
        if GATE_PORTAL_AVAILABLE:
            integration_types = get_integration_types()
            for code, name in integration_types.items():
                self.integration_combo.addItem(f"{code}: {name}", code)
        else:
            self.integration_combo.addItem("GATE Portal not available")
        self.integration_combo.setStyleSheet(f"""
            QComboBox {{
                background: {TAB_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 5px;
                color: {TEXT_COLOR};
                min-width: 150px;
            }}
        """)
        integration_layout.addWidget(self.integration_combo)
        
        portal_controls_layout.addLayout(integration_layout)
        
        # Generate portal button
        generate_portal_btn = QPushButton("Generate GATE Portal")
        generate_portal_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GOLD};
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #ffd700;
            }}
        """)
        generate_portal_btn.clicked.connect(self.generate_gate_portal)
        portal_controls_layout.addWidget(generate_portal_btn)
        
        right_layout.addWidget(portal_controls_frame)
        
        # Portal display
        portal_display_label = QLabel("Generated GATE Portal:")
        portal_display_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 14px;")
        right_layout.addWidget(portal_display_label)
        
        self.portal_display = QTextEdit()
        self.portal_display.setStyleSheet(f"""
            QTextEdit {{
                background: {TAB_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 10px;
                color: {TEXT_COLOR};
                font-family: '{DREAM_MECHA_FONT}', {FALLBACK_FONTS};
                font-size: 11px;
            }}
        """)
        self.portal_display.setMaximumHeight(100)
        right_layout.addWidget(self.portal_display)
        
        # Copy portal button
        copy_portal_btn = QPushButton("Copy Portal Code to Clipboard")
        copy_portal_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SECONDARY_ACCENT};
                color: #fff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #8ea6f8;
            }}
        """)
        copy_portal_btn.clicked.connect(self.copy_gate_portal)
        right_layout.addWidget(copy_portal_btn)
        
        main_splitter.addWidget(right_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 400])
        
        layout.addWidget(main_splitter)
        self.tab_widget.addTab(gate_tab_widget, "GATE")
        print("GATE tab added to widget")
    
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
    
    # Blocklock methods
    def set_random_symbol(self):
        """Set a random symbol in the combo box"""
        if hasattr(self, 'symbol_combo'):
            symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '[', ']', '{', '}', '|', ';', ':', ',', '.', '<', '>', '?', '/', '~', '`', '"', "'", '\\']
            random_symbol = random.choice(symbols)
            index = self.symbol_combo.findText(random_symbol)
            if index >= 0:
                self.symbol_combo.setCurrentIndex(index)
    
    def generate_gate_from_glyph(self):
        """Generate a GATE system from the current glyph"""
        if not GATE_CREATOR_AVAILABLE:
            self.log_debug("Gate Creator module not available")
            return
        
        if not self.grid or not self.grid.blocks:
            self.log_debug("No glyph pattern to generate GATE from")
            return
        
        try:
            # Get the password
            password = self.password_input.text() or "default_password"
            
            # Convert grid to glyph pattern
            glyph_pattern = self.generate_ascii_pattern()
            
            # Generate GATE using gate creator
            gate_creator = GateCreator()
            gate_data = gate_creator.create_gate_from_glyph(glyph_pattern, password)
            
            # Display the GATE data
            if hasattr(self, 'gate_display'):
                self.gate_display.setPlainText(json.dumps(gate_data, indent=2))
            
            # Display GATE information
            if hasattr(self, 'gate_info'):
                gate_info = gate_creator.get_gate_info(gate_data)
                info_text = f"""Glyph Pattern:
{glyph_pattern}

GATE System:
- Block Count: {gate_info['block_count']}
- Grid Size: {gate_info['grid_size']}
- Complexity Score: {gate_info['complexity_score']:.4f}
- Complexity Level: {gate_info['complexity']['complexity_level']}
- Spatial Combinations: {gate_info['spatial_combinations']}

GLYPH KEY (Key Derivation Source):
- Spatial Entropy: {len(gate_creator._extract_spatial_entropy(gate_creator._parse_glyph_structure(glyph_pattern)))} bytes
- Encryption Method: AES-GCM with PBKDF2 key derivation
- Key Length: 256 bits
- Authentication: GCM tag for integrity

Security Notes:
- Glyph provides spatial entropy for key derivation
- Password provides additional entropy
- AES-GCM provides proven cryptographic security
- Each glyph creates unique key derivation
- PBKDF2 with 100,000 iterations for key stretching"""
                self.gate_info.setPlainText(info_text)
            
            self.log_debug(f"Generated GATE system with {gate_info['block_count']} blocks")
            
        except Exception as e:
            self.log_debug(f"Error generating GATE: {e}")
            if hasattr(self, 'gate_display'):
                self.gate_display.setPlainText(f"Error: {e}")
            if hasattr(self, 'gate_info'):
                self.gate_info.setPlainText("")
    
    def copy_gate_data(self):
        """Copy the generated GATE data to clipboard"""
        if hasattr(self, 'gate_display'):
            gate_data = self.gate_display.toPlainText()
            if gate_data:
                clipboard = QApplication.clipboard()
                clipboard.setText(gate_data)
                self.log_debug("GATE data copied to clipboard")
            else:
                self.log_debug("No GATE data to copy")
        else:
            self.log_debug("Gate display not available")
    
    def verify_gate_system(self):
        """Verify a GATE system and show reconstruction"""
        if not GATE_CREATOR_AVAILABLE:
            self.log_debug("Gate Creator module not available")
            return
        
        gate_data_text = self.verify_gate_input.text().strip()
        if not gate_data_text:
            self.log_debug("No GATE data to verify")
            return
        
        try:
            # Parse the GATE data
            gate_data = json.loads(gate_data_text)
            
            # Extract the gate lock
            gate_lock = gate_data.get('gate_lock', {})
            visual_pattern = gate_lock.get('visual_pattern', '')
            
            # Verify the GATE
            gate_creator = GateCreator()
            result = gate_creator.verify_gate(gate_lock, visual_pattern)
            
            if hasattr(self, 'verify_gate_result'):
                if result['valid']:
                    result_text = f"""✅ GATE System Valid!

Visual Pattern:
{result['stored_hash']}

Verification Hash: {result['test_hash']}
Glyph Match: {result['glyph_match']}

Verification: SUCCESS
- Pattern matches stored hash
- Glyph reconstruction successful
- Visual verification passed
- Quantum-resistant encryption confirmed"""
                else:
                    result_text = f"""❌ GATE System Invalid!

Visual Pattern:
{result['stored_hash']}

Verification Hash: {result['test_hash']}
Glyph Match: {result['glyph_match']}

Error: Pattern does not match stored hash

Verification: FAILED
- Pattern does not match stored hash
- Glyph reconstruction failed
- Visual verification failed"""
                
                self.verify_gate_result.setPlainText(result_text)
            
            self.log_debug(f"GATE system verification: {'SUCCESS' if result['valid'] else 'FAILED'}")
            
        except Exception as e:
            self.log_debug(f"Error verifying GATE system: {e}")
            if hasattr(self, 'verify_gate_result'):
                self.verify_gate_result.setPlainText(f"Error: {e}")
    
    # GATE Portal methods
    def set_random_portal_symbol(self):
        """Set a random symbol in the portal combo box"""
        if hasattr(self, 'portal_symbol_combo'):
            symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '[', ']', '{', '}', '|', ';', ':', ',', '.', '<', '>', '?', '/', '~', '`', '"', "'", '\\']
            random_symbol = random.choice(symbols)
            index = self.portal_symbol_combo.findText(random_symbol)
            if index >= 0:
                self.portal_symbol_combo.setCurrentIndex(index)
    
    def generate_gate_portal(self):
        """Generate a universal GATE portal code"""
        if not GATE_PORTAL_AVAILABLE:
            self.log_debug("Gate Portal module not available")
            return
        
        if not self.grid or not self.grid.blocks:
            self.log_debug("No sigil pattern to generate portal from")
            return
        
        try:
            # Get the symbol and integration type
            symbol = self.portal_symbol_combo.currentText()
            integration_type = self.integration_combo.currentData()
            
            # Convert grid to sigil pattern
            sigil_pattern = self.generate_ascii_pattern()
            
            # Generate portal using gate portal system
            portal = GatePortal()
            result = portal.generate_gate_portal(sigil_pattern, symbol, integration_type)
            
            # Display the portal code
            if hasattr(self, 'portal_display'):
                portal_text = f"""Portal Code: {result['portal_code']}

Gate Pattern: {result['gate_pattern']}
Integration: {result['metadata']['integration_name']}
Version: {result['version']}"""
                self.portal_display.setPlainText(portal_text)
            
            # Display portal information
            if hasattr(self, 'portal_info'):
                info_text = f"""Portal Information:
===================

Portal Code: {result['portal_code']}
Gate Pattern: {result['gate_pattern']}
Integration Type: {result['integration_type']}
Integration Name: {result['metadata']['integration_name']}
Symbol Used: {result['metadata']['symbol_used']}
Version: {result['version']}
Generated At: {result['generated_at']}

Sigil Complexity:
- Total Elements: {result['metadata']['sigil_complexity']['total_elements']}
- Numeric Elements: {result['metadata']['sigil_complexity']['numeric_elements']}
- Symbol Positions: {result['metadata']['sigil_complexity']['symbol_positions']}
- Entropy Estimate: ~{result['metadata']['sigil_complexity']['entropy_estimate']} bits

Verification Hash: {result['verification_hash'][:32]}...

Universal Format: GATE-VERSION-TYPE-HASH
This portal code can be used across any compatible system."""
                self.portal_info.setPlainText(info_text)
            
            self.log_debug(f"Generated GATE portal: {result['portal_code']}")
            
        except Exception as e:
            self.log_debug(f"Error generating GATE portal: {e}")
    
    def copy_gate_portal(self):
        """Copy the generated portal code to clipboard"""
        if hasattr(self, 'portal_display'):
            portal_text = self.portal_display.toPlainText()
            if portal_text:
                # Extract just the portal code
                lines = portal_text.split('\n')
                portal_code = None
                for line in lines:
                    if line.startswith('Portal Code:'):
                        portal_code = line.split(':', 1)[1].strip()
                        break
                
                if portal_code:
                    clipboard = QApplication.clipboard()
                    clipboard.setText(portal_code)
                    self.log_debug("GATE portal code copied to clipboard")
                else:
                    self.log_debug("No portal code found to copy")
            else:
                self.log_debug("No portal code to copy")
        else:
            self.log_debug("Portal display not available")
    
    def generate_pattern_from_grid(self, grid):
        """Generate ASCII pattern from a grid instance"""
        if not grid or not grid.blocks:
            return ""
            
        min_row = min(pos[0] for pos in grid.blocks.keys())
        max_row = max(pos[0] for pos in grid.blocks.keys())
        min_col = min(pos[1] for pos in grid.blocks.keys())
        max_col = max(pos[1] for pos in grid.blocks.keys())
        
        pattern_lines = []
        for row in range(min_row, max_row + 1):
            line = ""
            for col in range(min_col, max_col + 1):
                if (row, col) in grid.blocks:
                    block_num = grid.blocks[(row, col)]
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
    
    def generate_unique_piece(self):
        """Generate a unique piece using the unique grid"""
        try:
            # Get grid pattern
            if not self.unique_grid.blocks:
                self.unique_preview_text.setPlainText("Error: Grid is empty. Create blocks first!")
                return
                
            # Generate pattern from grid
            pattern = self.generate_pattern_from_grid(self.unique_grid)
            if not pattern or pattern == "+ ":
                self.unique_preview_text.setPlainText("Error: Grid is empty. Create blocks first!")
                return
                
            # Count blocks
            block_count = sum(1 for char in pattern if char.isdigit())
            if block_count == 0:
                self.unique_preview_text.setPlainText("Error: No blocks in grid!")
                return
                
            stat_type = self.unique_stat_type.currentText()
            
            # Generate piece stats using DreamMecha integration
            piece = self.dream_mecha_integration.generate_single_piece_manual(block_count, stat_type)
            piece["id"] = f"unique_piece_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            piece["pattern"] = pattern
            piece["size_category"] = "unique"
            piece["generation_method"] = "unique_grid"
            
            # Display preview
            preview_text = f"=== UNIQUE PIECE GENERATED ===\n\n"
            preview_text += f"ID: {piece['id']}\n"
            preview_text += f"Blocks: {block_count}\n"
            
            # Only show the active stat
            active_stat = None
            for stat_name, stat_value in piece['stats'].items():
                if stat_value > 0:
                    active_stat = (stat_name.upper(), stat_value)
                    break
                    
            if active_stat:
                preview_text += f"Stats: {active_stat[0]}:{active_stat[1]}\n"
            else:
                preview_text += f"Stats: ERROR - No active stat\n"
                
            preview_text += f"Type: {piece['stat_type']}\n"
            preview_text += f"Price: {piece['price']} Zoltans\n"
            preview_text += f"\nPattern:\n{pattern}\n"
            
            self.unique_preview_text.setPlainText(preview_text)
            
        except Exception as e:
            self.unique_preview_text.setPlainText(f"Error generating unique piece: {str(e)}")
    
    def handle_unique_place_block(self, pos):
        """Handle block placement in unique grid"""
        if not hasattr(self, '_unique_block_counter'):
            self._unique_block_counter = 1
            
        self.unique_grid.add_block(pos, self._unique_block_counter)
        self._unique_block_counter += 1
        
        # Update the spinbox to show current block count
        self.unique_count_spinbox.setValue(len(self.unique_grid.blocks))
    
    def clear_unique_grid(self):
        """Clear the unique grid and reset counter"""
        self.unique_grid.clear_grid(reset_spinbox=False)
        self._unique_block_counter = 1
        self.unique_count_spinbox.setValue(1)
        self.unique_preview_text.setPlainText("Grid cleared. Click on grid to place blocks.")


def main():
    """Main function to run the blockmaker as standalone"""
    app = QApplication(sys.argv)
    
    # Load Dream Mecha font
    font_path = os.path.join(os.path.dirname(__file__), "..", "dream_mecha", "font", "NCLRaxor-Demo.otf")
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                print(f"Loaded Dream Mecha font: {font_families[0]}")
    
    window = BlockmakerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 