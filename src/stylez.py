## stylez.py
## last updated: 20/8/2025 <d/m/y>
## p-y-l-i
STYLE_SHEET = """
QWidget {
    font-family: 'MS Shell Dlg 2', 'Tahoma', 'Arial';
    font-size: 10pt;
    color: #C0C0C0;
    background-color: #2D2D2D;
}
QFrame#mainFrame {
    border: 2px solid #5A5A5A;
    background-color: #1E1E1E;
    border-radius: 0px;
    padding: 10px;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #3C3C3C;
    border: 1px solid #5A5A5A;
    color: #E0E0E0;
    padding: 3px;
}
QPushButton {
    background-color: #4A4A4A;
    border: 1px solid #757575;
    color: #E0E0E0;
    padding: 5px 15px;
}
QPushButton:hover {
    background-color: #555555;
    border: 1px solid #8A8A8A;
}
QPushButton:pressed {
    background-color: #3D3D3D;
    border: 1px solid #666666;
}
QLabel {
    color: #E0E0E0;
}
QProgressBar {
    border: 1px solid #5A5A5A;
    background-color: #3C3C3C;
    color: #E0E0E0;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #4CAF50;
}
QGroupBox {
    border: 1px solid #5A5A5A;
    border-radius: 5px;
    margin-top: 1em;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
    background-color: #2D2D2D;
    color: #C0C0C0;
}
QTabWidget::pane {
    border-top: 2px solid #5A5A5A;
    background: #1E1E1E;
}
QTabBar::tab {
    background: #3C3C3C;
    color: #C0C0C0;
    border: 1px solid #5A5A5A;
    border-bottom-color: #5A5A5A;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 8ex;
    padding: 4px;
}
QTabBar::tab:selected {
    background: #1E1E1E;
    border-color: #5A5A5A;
    border-bottom-color: #1E1E1E;
}
"""

## end
