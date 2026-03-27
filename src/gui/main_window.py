from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QTextEdit,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HunskyBot | Twitch Chatbot")
        self.setMinimumSize(800, 500)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)

        title = QLabel("HunskyBot")
        title.setObjectName("sidebarTitle")
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(16)

        self._nav_buttons: list[QPushButton] = []
        pages = ["Dashboard", "Chat", "Commands", "Settings"]
        for i, name in enumerate(pages):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setObjectName("navButton")
            btn.clicked.connect(lambda checked, idx=i: self._switch_page(idx))
            sidebar_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # --- Content area ---
        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack)

        # Page 0: Dashboard
        self._dashboard = self._make_placeholder("Dashboard")
        self._stack.addWidget(self._dashboard)

        # Page 1: Chat display
        self._chat_log = QTextEdit()
        self._chat_log.setReadOnly(True)
        self._chat_log.setPlaceholderText("Chat messages will appear here...")
        self._stack.addWidget(self._chat_log)

        # Page 2: Commands (placeholder)
        self._stack.addWidget(self._make_placeholder("Commands"))

        # Page 3: Settings (placeholder)
        self._stack.addWidget(self._make_placeholder("Settings"))

        # Default to Dashboard
        self._switch_page(0)

    def _make_placeholder(self, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page

    def _switch_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)

    # --- Public slots for bot signals ---

    def append_chat_message(self, username: str, message: str) -> None:
        self._chat_log.append(f"<b>{username}</b>: {message}")

    def append_log(self, text: str) -> None:
        print(f"[LOG] {text}")
