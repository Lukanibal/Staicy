import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

def on_button_click():
    label.setText("Button clicked!")

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle("Staicy Interface")

# Create a layout
layout = QVBoxLayout()

# Create a label
label = QLabel("Hello, PyQt5!")
layout.addWidget(label)

# Create a button
button = QPushButton("Click Me")
button.clicked.connect(on_button_click)
layout.addWidget(button)

# Set the layout for the main window
window.setLayout(layout)

# Show the window
window.show()

# Start the application
sys.exit(app.exec_())
