import subprocess
import platform
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
                             QFileDialog, QProgressBar, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            for line in process.stdout:
                self.progress_signal.emit(line.strip())
            
            process.wait()
            self.finished_signal.emit(process.returncode == 0)
        except Exception as e:
            self.progress_signal.emit(f"Erreur: {str(e)}")
            self.finished_signal.emit(False)

class VideoDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT-DLP Manager Pro - Kali Linux")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5aa0f0;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #7a7a7a;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #3c3f41;
                color: white;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4a90e2;
            }
        """)

        self.init_ui()
        self.download_thread = None

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Create tabs
        tabs = QTabWidget()
        self.single_tab = self.create_single_download_tab()
        self.batch_tab = self.create_batch_download_tab()
        
        tabs.addTab(self.single_tab, "Téléchargement unique")
        tabs.addTab(self.batch_tab, "Téléchargement multiple")

        main_layout.addWidget(tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_single_download_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL de la vidéo:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Quality selection
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualité:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "2160", "1440", "1080", "720", "480", "360"])
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)

        # Browser selection for cookies
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Navigateur pour cookies:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Aucun", "Chrome (Linux)", "Chrome (Kali)", "Firefox (Linux)", "Chromium (Linux)", "Brave (Linux)"])
        browser_layout.addWidget(self.browser_combo)
        layout.addLayout(browser_layout)

        # Cookies file input
        cookies_layout = QHBoxLayout()
        cookies_layout.addWidget(QLabel("Fichier cookies:"))
        self.cookies_input = QLineEdit()
        self.cookies_input.setPlaceholderText("Chemin vers cookies.txt (optionnel)")
        cookies_layout.addWidget(self.cookies_input)
        self.cookies_browse_button = QPushButton("Parcourir...")
        self.cookies_browse_button.clicked.connect(self.browse_cookies_file)
        cookies_layout.addWidget(self.cookies_browse_button)
        layout.addLayout(cookies_layout)

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Fichier de sortie:"))
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("video.%(ext)s")
        output_layout.addWidget(self.output_input)
        self.browse_button = QPushButton("Parcourir...")
        self.browse_button.clicked.connect(self.browse_output_file)
        output_layout.addWidget(self.browse_button)
        layout.addLayout(output_layout)

        # Download button
        self.download_button = QPushButton("Télécharger")
        self.download_button.clicked.connect(self.start_single_download)
        layout.addWidget(self.download_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        tab.setLayout(layout)
        return tab

    def create_batch_download_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # URLs input
        layout.addWidget(QLabel("URLs (une par ligne):"))
        self.urls_input = QTextEdit()
        self.urls_input.setPlaceholderText("https://www.youtube.com/watch?v=...\nhttps://vimeo.com/...")
        layout.addWidget(self.urls_input)

        # Quality selection
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualité:"))
        self.batch_quality_combo = QComboBox()
        self.batch_quality_combo.addItems(["best", "2160", "1440", "1080", "720", "480", "360"])
        quality_layout.addWidget(self.batch_quality_combo)
        layout.addLayout(quality_layout)

        # Browser selection for cookies
        batch_browser_layout = QHBoxLayout()
        batch_browser_layout.addWidget(QLabel("Navigateur pour cookies:"))
        self.batch_browser_combo = QComboBox()
        self.batch_browser_combo.addItems(["Aucun", "Chrome (Linux)", "Chrome (Kali)", "Firefox (Linux)", "Chromium (Linux)", "Brave (Linux)"])
        batch_browser_layout.addWidget(self.batch_browser_combo)
        layout.addLayout(batch_browser_layout)

        # Cookies file input
        batch_cookies_layout = QHBoxLayout()
        batch_cookies_layout.addWidget(QLabel("Fichier cookies:"))
        self.batch_cookies_input = QLineEdit()
        self.batch_cookies_input.setPlaceholderText("Chemin vers cookies.txt (optionnel)")
        batch_cookies_layout.addWidget(self.batch_cookies_input)
        self.batch_cookies_browse_button = QPushButton("Parcourir...")
        self.batch_cookies_browse_button.clicked.connect(self.browse_batch_cookies_file)
        batch_cookies_layout.addWidget(self.batch_cookies_browse_button)
        layout.addLayout(batch_cookies_layout)

        # Output pattern
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Modèle de fichier:"))
        self.batch_output_input = QLineEdit()
        self.batch_output_input.setPlaceholderText("video_%(autonumber)s.%(ext)s")
        output_layout.addWidget(self.batch_output_input)
        layout.addLayout(output_layout)

        # Download button
        self.batch_download_button = QPushButton("Télécharger la liste")
        self.batch_download_button.clicked.connect(self.start_batch_download)
        layout.addWidget(self.batch_download_button)

        # Progress bar
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setTextVisible(False)
        layout.addWidget(self.batch_progress_bar)

        # Log output
        self.batch_log_output = QTextEdit()
        self.batch_log_output.setReadOnly(True)
        layout.addWidget(self.batch_log_output)

        tab.setLayout(layout)
        return tab

    def browse_output_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Enregistrer la vidéo sous", "", "Fichiers vidéo (*.mp4 *.mkv *.webm);;Tous les fichiers (*)")
        if filename:
            self.output_input.setText(filename)

    def browse_cookies_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Sélectionner le fichier cookies", "", "Fichiers texte (*.txt);;Tous les fichiers (*)")
        if filename:
            self.cookies_input.setText(filename)

    def browse_batch_cookies_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Sélectionner le fichier cookies", "", "Fichiers texte (*.txt);;Tous les fichiers (*)")
        if filename:
            self.batch_cookies_input.setText(filename)

    def get_browser_cookies_command(self, browser_name):
        """Retourne la commande appropriée pour les cookies selon le navigateur sur Kali Linux"""
        browser_mapping = {
            "Chrome (Linux)": "chrome",
            "Chrome (Kali)": "chrome:linux-kali",
            "Firefox (Linux)": "firefox",
            "Chromium (Linux)": "chromium",
            "Brave (Linux)": "brave"
        }
        return browser_mapping.get(browser_name, "")

    def start_single_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide")
            return

        quality = self.quality_combo.currentText()
        output = self.output_input.text().strip() or "video.%(ext)s"
        browser = self.browser_combo.currentText()
        cookies_file = self.cookies_input.text().strip()

        format_option = f"-f bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "-f best"
        
        command = ["yt-dlp", url, format_option, "-o", output, "--newline"]
        
        # Ajouter l'option cookies du navigateur si sélectionné
        if browser != "Aucun":
            browser_cmd = self.get_browser_cookies_command(browser)
            if browser_cmd:
                command.extend(["--cookies-from-browser", browser_cmd])
            else:
                self.log_output.append(f"Option de navigateur non supportée: {browser}")
        
        # Ajouter l'option cookies fichier si spécifié
        if cookies_file:
            command.extend(["--cookies", cookies_file])

        self.log_output.clear()
        self.log_output.append(f"Début du téléchargement: {url}")
        self.log_output.append(f"Qualité: {quality}, Fichier de sortie: {output}")
        
        if browser != "Aucun":
            self.log_output.append(f"Utilisation des cookies de {browser}")
        if cookies_file:
            self.log_output.append(f"Utilisation du fichier cookies: {cookies_file}")
        
        self.download_button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        self.download_thread = DownloadThread(command)
        self.download_thread.progress_signal.connect(self.update_single_log)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    def start_batch_download(self):
        urls = self.urls_input.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer au moins une URL valide")
            return

        quality = self.batch_quality_combo.currentText()
        output_pattern = self.batch_output_input.text().strip() or "video_%(autonumber)s.%(ext)s"
        browser = self.batch_browser_combo.currentText()
        cookies_file = self.batch_cookies_input.text().strip()

        format_option = f"-f bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "-f best"
        
        self.batch_log_output.clear()
        self.batch_log_output.append(f"Début du téléchargement batch ({len(urls)} vidéos)")
        self.batch_log_output.append(f"Qualité: {quality}, Modèle de fichier: {output_pattern}")
        
        if browser != "Aucun":
            self.batch_log_output.append(f"Utilisation des cookies de {browser}")
        if cookies_file:
            self.batch_log_output.append(f"Utilisation du fichier cookies: {cookies_file}")
        
        self.batch_download_button.setEnabled(False)
        self.batch_progress_bar.setRange(0, len(urls))
        self.batch_progress_bar.setValue(0)

        # Create a list of commands to execute
        self.batch_commands = []
        for url in urls:
            command = ["yt-dlp", url, format_option, "-o", output_pattern, "--newline"]
            
            # Ajouter les options cookies pour chaque commande
            if browser != "Aucun":
                browser_cmd = self.get_browser_cookies_command(browser)
                if browser_cmd:
                    command.extend(["--cookies-from-browser", browser_cmd])
            if cookies_file:
                command.extend(["--cookies", cookies_file])
            
            self.batch_commands.append(command)
        
        self.current_batch_index = 0
        self.process_next_batch_download()

    def process_next_batch_download(self):
        if self.current_batch_index < len(self.batch_commands):
            command = self.batch_commands[self.current_batch_index]
            url = command[1]
            
            self.batch_log_output.append(f"\nTéléchargement vidéo {self.current_batch_index + 1}/{len(self.batch_commands)}: {url}")
            self.batch_progress_bar.setValue(self.current_batch_index)
            
            self.download_thread = DownloadThread(command)
            self.download_thread.progress_signal.connect(self.update_batch_log)
            self.download_thread.finished_signal.connect(self.batch_download_finished)
            self.download_thread.start()
        else:
            self.batch_download_button.setEnabled(True)
            self.batch_progress_bar.setValue(len(self.batch_commands))
            QMessageBox.information(self, "Terminé", "Tous les téléchargements sont terminés!")

    def update_single_log(self, text):
        self.log_output.append(text)

    def update_batch_log(self, text):
        self.batch_log_output.append(text)

    def download_finished(self, success):
        self.download_button.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
        if success:
            self.log_output.append("Téléchargement terminé avec succès!")
        else:
            self.log_output.append("Erreur pendant le téléchargement!")

    def batch_download_finished(self, success):
        self.current_batch_index += 1
        if success:
            self.batch_log_output.append("Terminé avec succès!")
        else:
            self.batch_log_output.append("Erreur pendant le téléchargement!")
        
        self.process_next_batch_download()

    def closeEvent(self, event):
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Téléchargement en cours",
                "Un téléchargement est en cours. Voulez-vous vraiment quitter?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.download_thread.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoDownloaderApp()
    window.show()
    sys.exit(app.exec_())
