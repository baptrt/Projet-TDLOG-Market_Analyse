# mvc/views/login_dialog.py

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTabWidget

class LoginDialog(QDialog):
    """
    Fenêtre de connexion/inscription.
    """
    
    # Signal émis lors d'une connexion réussie
    login_successful = QtCore.pyqtSignal(str, str)  # username, password
    register_successful = QtCore.pyqtSignal(str, str, str)  # username, password, email
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Market Sentiment Analyzer - Connexion")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Construction de l'interface."""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("<h1>Authentification</h1>")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Onglets Connexion / Inscription
        tabs = QTabWidget()
        tabs.addTab(self._create_login_tab(), "Connexion")
        tabs.addTab(self._create_register_tab(), "Inscription")
        layout.addWidget(tabs)
        
        # Message d'erreur
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
    
    def _create_login_tab(self):
        """Onglet de connexion."""
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addSpacing(20)
        
        # Champs
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Nom d'utilisateur")
        layout.addWidget(QLabel("Nom d'utilisateur :"))
        layout.addWidget(self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Mot de passe")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Mot de passe :"))
        layout.addWidget(self.login_password)
        
        layout.addSpacing(20)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self._on_login_clicked)
        btn_layout.addWidget(self.login_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_button)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        # Enter pour valider
        self.login_password.returnPressed.connect(self._on_login_clicked)
        
        return widget
    
    def _create_register_tab(self):
        """Onglet d'inscription."""
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addSpacing(20)
        
        # Champs
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Nom d'utilisateur")
        layout.addWidget(QLabel("Nom d'utilisateur :"))
        layout.addWidget(self.register_username)
        
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("email@exemple.com (optionnel)")
        layout.addWidget(QLabel("Email (optionnel) :"))
        layout.addWidget(self.register_email)
        
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Mot de passe")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Mot de passe :"))
        layout.addWidget(self.register_password)
        
        self.register_password_confirm = QLineEdit()
        self.register_password_confirm.setPlaceholderText("Confirmer le mot de passe")
        self.register_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Confirmer le mot de passe :"))
        layout.addWidget(self.register_password_confirm)
        
        layout.addSpacing(20)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        self.register_button = QPushButton("S'inscrire")
        self.register_button.clicked.connect(self._on_register_clicked)
        btn_layout.addWidget(self.register_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_button)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        # Enter pour valider
        self.register_password_confirm.returnPressed.connect(self._on_register_clicked)
        
        return widget
    
    def _on_login_clicked(self):
        """Gère le clic sur le bouton de connexion."""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            self.show_error("Veuillez remplir tous les champs")
            return
        
        # Émet le signal vers le contrôleur
        self.login_successful.emit(username, password)
    
    def _on_register_clicked(self):
        """Gère le clic sur le bouton d'inscription."""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        password_confirm = self.register_password_confirm.text()
        
        # Validations
        if not username or not password:
            self.show_error("Nom d'utilisateur et mot de passe requis")
            return
        
        if len(username) < 3:
            self.show_error("Le nom d'utilisateur doit contenir au moins 3 caractères")
            return
        
        if len(password) < 6:
            self.show_error("Le mot de passe doit contenir au moins 6 caractères")
            return
        
        if password != password_confirm:
            self.show_error("Les mots de passe ne correspondent pas")
            return
        
        # Émet le signal vers le contrôleur
        self.register_successful.emit(username, password, email if email else None)
    
    def show_error(self, message: str):
        """Affiche un message d'erreur."""
        self.error_label.setText(f"{message}")
    
    def show_success(self, message: str):
        """Affiche un message de succès."""
        self.error_label.setStyleSheet("color: green;")
        self.error_label.setText(f"{message}")
    
    def clear_error(self):
        """Efface le message d'erreur."""
        self.error_label.setText("")