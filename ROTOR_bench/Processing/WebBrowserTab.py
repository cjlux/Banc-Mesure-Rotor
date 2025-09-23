from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class WebBrowserTab(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)

        # Top bar: navigation buttons + URL combo + field + OK button
        hbox = QHBoxLayout()

        self.url_combo = QComboBox()
        self.predefined_urls = [
            "https://matplotlib.org/stable/gallery/color/named_colors.html",
            "https://github.com/cjlux/Banc-Mesure-Rotor", 
        ]
        self.url_combo.addItems(self.predefined_urls)
        self.url_combo.setMinimumWidth(300)
        self.url_combo.currentIndexChanged.connect(self.on_combo_url_selected)
        hbox.addWidget(QLabel("URL:"))
        hbox.addWidget(self.url_combo)

        # Left arrow (Back)
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedWidth(30)
        self.back_btn.clicked.connect(self.go_back)
        hbox.addWidget(self.back_btn)

        # Right arrow (Forward)
        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedWidth(30)
        self.forward_btn.clicked.connect(self.go_forward)
        hbox.addWidget(self.forward_btn)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter web URL...")
        self.url_edit.setMinimumWidth(300)
        hbox.addWidget(self.url_edit)

        self.go_btn = QPushButton("OK")
        self.go_btn.clicked.connect(self.load_url)
        hbox.addWidget(self.go_btn)
        vbox.addLayout(hbox)

        # Web view
        self.web_view = QWebEngineView()
        vbox.addWidget(self.web_view)

        # Update edit field when page changes
        self.web_view.urlChanged.connect(self.on_url_changed)

        # Set default page
        self.url_edit.setText(self.predefined_urls[0])
        self.load_url()

    def on_combo_url_selected(self, index):
        url = self.url_combo.currentText()
        self.url_edit.setText(url)
        self.load_url()

    def load_url(self):
        url = self.url_edit.text().strip()
        if not url.startswith("http"):
            url = "https://" + url
        self.web_view.setUrl(QUrl(url))

    def on_url_changed(self, qurl):
        self.url_edit.setText(qurl.toString())

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()