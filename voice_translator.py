import tkinter as tk
from tkinter import ttk, messagebox, font
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from langdetect import detect
import sqlite3
from datetime import datetime
import pyaudio  # Required by speech_recognition, suppress unused import warning # noqa
import threading
import time
import os
import sys
import asyncio  # For handling async operations correctly
import httpx  # Underlying library for googletrans

# Selected 30 languages for better user experience
LANGUAGES = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bn': 'Bengali',
    'zh-cn': 'Chinese (Simplified)',
    'nl': 'Dutch',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'el': 'Greek',
    'hi': 'Hindi',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ms': 'Malay',
    'ne': 'Nepali',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pa': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'es': 'Spanish',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tl': 'Tagalog',
    'ta': 'Tamil',
    'th': 'Thai',
    'tr': 'Turkish',
    'ur': 'Urdu'
}

class VoiceTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Translator Pro - by robbie09")
        self.root.geometry("1200x700")
        self.root.configure(bg="#121212")  # Midnight dark background
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.is_listening = False
        self.preferred_lang = tk.StringVar(value="hi")  # Default to Hindi
        self.last_audio = None  # Store last audio for processing when stopped
        
        # Setup thread control
        self.listening_thread = None
        self.listening_stop_event = threading.Event()
        
        # Setup custom fonts
        self.title_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=12)
        self.button_font = font.Font(family="Segoe UI", size=10, weight="bold")
        self.footer_font = font.Font(family="Segoe UI", size=8, slant="italic")
        
        # Setup UI
        self.setup_ui()
        
        # Setup window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the premium UI with dark midnight theme"""
        # Create a gradient background using Canvas
        self.canvas = tk.Canvas(self.root, bg="#121212", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Simulate a gradient effect with rectangles - dark midnight theme
        for i in range(0, 700, 10):
            shade = int(10 + (i / 700) * 30)  # Darker gradient
            color = f"#{shade:02x}{shade:02x}{shade+10:02x}"
            self.canvas.create_rectangle(0, i, 1200, i + 10, fill=color, outline="")
        
        # Main frame with a midnight dark background
        self.main_frame = tk.Frame(self.canvas, bg="#1A1A2A", bd=0)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=600)
        
        # Add a subtle glow effect (simulated with a border)
        self.canvas.create_rectangle(200, 50, 1000, 650, fill="", outline="#9370DB", width=2)  # Purple glow
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Translator Tab
        self.translator_frame = tk.Frame(self.notebook, bg="#1A1A2A")
        self.notebook.add(self.translator_frame, text="Translator")
        
        # History Tab
        self.history_frame = tk.Frame(self.notebook, bg="#1A1A2A")
        self.notebook.add(self.history_frame, text="History")
        
        # Configure notebook style
        style = ttk.Style()
        style.configure("TNotebook", background="#1A1A2A")
        style.configure("TNotebook.Tab", 
                        background="#2A2A3A", 
                        foreground="#E0E0E0", 
                        font=("Segoe UI", 12, "bold"),
                        padding=[10, 5])
        style.map("TNotebook.Tab", 
                  background=[("selected", "#9370DB")],  # Purple selected tab
                  foreground=[("selected", "#FFFFFF")])
        
        self.setup_translator_tab()
        self.setup_history_tab()
        self.setup_db()
        
        # Add credits at the bottom
        credits_frame = tk.Frame(self.root, bg="#121212")
        credits_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        credits_label = tk.Label(
            credits_frame,
            text="Created by robbie09 © 2025 | Voice Translator Pro",
            font=self.footer_font,
            bg="#121212",
            fg="#9370DB"  # Purple text
        )
        credits_label.pack(pady=5)
        
    def setup_translator_tab(self):
        """Setup the translator tab UI with midnight dark theme"""
        # Title
        title_label = tk.Label(
            self.translator_frame,
            text="Voice Translator Pro",
            font=self.title_font,
            bg="#1A1A2A",
            fg="#9370DB"  # Purple color for midnight theme
        )
        title_label.pack(pady=20)
        
        # Input frame
        input_frame = tk.Frame(self.translator_frame, bg="#1A1A2A")
        input_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Microphone button with hover effect
        self.mic_button = tk.Button(
            input_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            activebackground="#45A049",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=20,
            pady=10
        )
        self.mic_button.pack(side=tk.LEFT, padx=10)
        self.mic_button.bind("<Enter>", self.on_mic_button_enter)
        self.mic_button.bind("<Leave>", self.on_mic_button_leave)

        # Process last audio button
        self.process_last_button = tk.Button(
            input_frame,
            text="⚡ Process Last Audio",
            command=self.process_last_audio,
            font=self.button_font,
            bg="#9370DB",  # Purple button
            fg="white",
            activebackground="#7B68EE",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
            state=tk.DISABLED  # Initially disabled
        )
        self.process_last_button.pack(side=tk.LEFT, padx=10)
        self.process_last_button.bind("<Enter>", self.on_process_button_enter)
        self.process_last_button.bind("<Leave>", self.on_process_button_leave)
        
        # Language selection
        lang_label = tk.Label(
            input_frame,
            text="Output Language:",
            font=self.normal_font,
            bg="#1A1A2A",
            fg="#E0E0E0"  # Light gray for better readability
        )
        lang_label.pack(side=tk.LEFT, padx=10)
        
        lang_combo = ttk.Combobox(
            input_frame,
            textvariable=self.preferred_lang,
            values=[f"{code}: {name}" for code, name in LANGUAGES.items()],
            state="readonly",
            width=30,
            font=self.normal_font
        )
        lang_combo.pack(side=tk.LEFT, padx=10)
        lang_combo.set("hi: Hindi")
        
        # Style the combobox for midnight theme
        style = ttk.Style()
        style.configure("TCombobox", 
                        fieldbackground="#2A2A3A", 
                        background="#2A2A3A", 
                        foreground="#E0E0E0",
                        selectbackground="#9370DB",
                        selectforeground="#FFFFFF")
        
        # Status label
        self.status_label = tk.Label(
            self.translator_frame,
            text="Status: Idle",
            font=("Segoe UI", 12, "italic"),
            bg="#1A1A2A",
            fg="#00CED1"  # Cyan for status
        )
        self.status_label.pack(pady=15)
        
        # Text displays with midnight styling
        self.source_text = tk.Text(
            self.translator_frame,
            height=5,
            font=("Segoe UI", 12),
            wrap="word",
            bg="#2A2A3A",
            fg="#E0E0E0",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#9370DB"  # Purple border
        )
        self.source_text.pack(fill=tk.X, pady=10, padx=20)
        self.source_text.insert("1.0", "Source Text (Auto-detected)")
        self.source_text.config(state="disabled")
        
        self.translated_text = tk.Text(
            self.translator_frame,
            height=5,
            font=("Segoe UI", 12),
            wrap="word",
            bg="#2A2A3A",
            fg="#E0E0E0",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#9370DB"  # Purple border
        )
        self.translated_text.pack(fill=tk.X, pady=10, padx=20)
        self.translated_text.insert("1.0", "Translated Text")
        self.translated_text.config(state="disabled")
        
    def setup_history_tab(self):
        """Setup the history tab UI with midnight dark theme"""
        # Treeview for history
        columns = ("ID", "Timestamp", "Source Text", "Source Language", "Translated Text", "Target Language")
        self.history_tree = ttk.Treeview(
            self.history_frame,
            columns=columns,
            show="headings"
        )
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150, anchor="center")
        
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Style the treeview for midnight theme
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#2A2A3A", 
                        foreground="#E0E0E0", 
                        fieldbackground="#2A2A3A",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", 
                        background="#9370DB", 
                        foreground="#FFFFFF",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", 
                  background=[("selected", "#4A4A5A")])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.history_frame,
            orient=tk.VERTICAL,
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(self.history_frame, bg="#1A1A2A")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Refresh button with hover effect
        refresh_button = tk.Button(
            button_frame,
            text="🔄 Refresh History",
            command=self.load_history,
            font=self.button_font,
            bg="#9370DB",  # Purple to match theme
            fg="white",
            activebackground="#7B68EE",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=20,
            pady=10
        )
        refresh_button.pack(side=tk.LEFT, padx=20, pady=10)
        refresh_button.bind("<Enter>", self.on_refresh_button_enter)
        refresh_button.bind("<Leave>", self.on_refresh_button_leave)
        
        # Add clear history button
        clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear History",
            command=self.clear_history,
            font=self.button_font,
            bg="#F44336",
            fg="white",
            activebackground="#D32F2F",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=20,
            pady=10
        )
        clear_button.pack(side=tk.RIGHT, padx=20, pady=10)
        clear_button.bind("<Enter>", self.on_clear_button_enter)
        clear_button.bind("<Leave>", self.on_clear_button_leave)
        
        self.load_history()
        
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = ""
            # Check if running as PyInstaller executable
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_path = str(sys._MEIPASS)
                print(f"Running as PyInstaller executable, base path: {base_path}")
            else:
                # Running as script
                base_path = str(os.path.dirname(os.path.abspath(__file__)))
                print(f"Running as script, base path: {base_path}")
        except Exception as e:
            # Fallback if everything fails
            base_path = str(os.getcwd())
            print(f"Error determining base path, using current directory: {base_path}, error: {e}")
            
        # Convert to string to ensure type compatibility
        rel_path_str = str(relative_path)
        result_path = os.path.join(base_path, rel_path_str)
        print(f"Resource path resolved: {result_path} for relative path: {relative_path}")
        return result_path
    
    def setup_db(self):
        """Initialize SQLite database for history"""
        # Create data directory if it doesn't exist
        # For PyInstaller, we need a different approach since we can't write to the frozen directory
        data_dir = None
        
        # Check if we're running as an executable
        is_frozen = getattr(sys, 'frozen', False)
        
        # In frozen mode (PyInstaller executable), use different data directory strategies
        if is_frozen:
            try:
                # For PyInstaller - try to create data folder next to the executable first
                exe_dir = os.path.dirname(sys.executable)
                print(f"Executable directory: {exe_dir}")
                potential_data_dir = os.path.join(exe_dir, "data")
                print(f"Trying to create data directory at: {potential_data_dir}")
                
                try:
                    os.makedirs(potential_data_dir, exist_ok=True)
                    # Test write access
                    test_file = os.path.join(potential_data_dir, "test_write.tmp")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    data_dir = potential_data_dir
                    print(f"Successfully created data directory next to executable at {data_dir}")
                except (PermissionError, OSError):
                    print("Cannot write to executable directory, will try user directory")
                    raise PermissionError("Cannot write to executable directory")
            except Exception as e:
                print(f"Falling back to user directory due to: {e}")
                # Use user directory as fallback
                home_path = str(os.path.expanduser("~"))
                documents_dir = os.path.join(home_path, "Documents", "VoiceTranslatorPro")
                try:
                    os.makedirs(documents_dir, exist_ok=True)
                    data_dir = str(documents_dir)
                    print(f"Created data directory in user Documents folder: {data_dir}")
                except Exception as doc_error:
                    # Final fallback - use temporary directory
                    print(f"Could not use Documents folder: {doc_error}, trying temp directory")
                    import tempfile
                    temp_dir = str(tempfile.gettempdir())
                    data_dir = os.path.join(temp_dir, "VoiceTranslatorPro")
                    os.makedirs(data_dir, exist_ok=True)
                    print(f"Using temporary directory for data: {data_dir}")
        else:
            # Normal mode - create in application directory
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(base_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                print(f"Created data directory in application folder: {data_dir}")
            except Exception as app_error:
                # Fallback - use user's home directory
                print(f"Could not create data directory in app folder: {app_error}")
                home_path = str(os.path.expanduser("~"))
                data_dir = os.path.join(home_path, "VoiceTranslatorPro")
                os.makedirs(data_dir, exist_ok=True)
                print(f"Created data directory in user home folder: {data_dir}")
        
        # If we still don't have a data_dir, something went really wrong
        if not data_dir:
            error_msg = "Could not create a data directory in any location"
            print(error_msg)
            messagebox.showerror("Critical Error", error_msg)
            self.db_path = None
            return
        
        # Connect to the database in the data directory
        # Convert to string to ensure consistent type
        data_dir_str = str(data_dir)
        self.db_path = os.path.join(data_dir_str, "translation_history.db")
        print(f"Database path set to: {self.db_path}")
        
        # Store the db_path for later use but don't open connection yet
        # We'll create a new connection in each thread when needed
        try:
            # Just create the database and structure
            conn = sqlite3.connect(self.db_path)
            
            # Create the table structure
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    source_text TEXT,
                    source_lang TEXT,
                    translated_text TEXT,
                    target_lang TEXT
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            
            # Test that we can read/write to the database
            test_conn = sqlite3.connect(self.db_path)
            test_cursor = test_conn.cursor()
            
            # Try a simple insert and delete to verify write permissions
            try:
                test_cursor.execute("""
                    INSERT INTO history (timestamp, source_text, source_lang, translated_text, target_lang)
                    VALUES (?, ?, ?, ?, ?)
                """, ("TEST", "TEST", "en", "TEST", "en"))
                
                test_cursor.execute("DELETE FROM history WHERE source_text = 'TEST'")
                test_conn.commit()
                print("Database successfully tested for read/write access")
            except Exception as test_error:
                print(f"Database test failed: {test_error}")
                raise
            finally:
                test_cursor.close()
                test_conn.close()
            
            # Notification for database setup
            print(f"Database initialized at {self.db_path}")
        except Exception as e:
            print(f"Error setting up database: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            self.db_path = None
        
    def toggle_listening(self):
        """Toggle the listening state"""
        if not self.is_listening:
            self.is_listening = True
            self.listening_stop_event.clear()
            self.mic_button.config(text="🎤 Stop Listening", bg="#F44336")
            self.mic_button.bind("<Enter>", self.on_mic_button_enter)
            self.mic_button.bind("<Leave>", self.on_mic_button_leave)
            self.status_label.config(text="Status: Listening...")
            
            # Reset text fields when starting to listen again
            self.source_text.config(state="normal")
            self.source_text.delete("1.0", tk.END)
            self.source_text.insert("1.0", "Listening for new input...")
            self.source_text.config(state="disabled")
            
            self.translated_text.config(state="normal")
            self.translated_text.delete("1.0", tk.END)
            self.translated_text.insert("1.0", "Translation will appear here")
            self.translated_text.config(state="disabled")
            
            # Start listening in a separate thread
            self.listening_thread = threading.Thread(target=self.listen_and_translate)
            self.listening_thread.daemon = True
            self.listening_thread.start()
        else:
            self.is_listening = False
            self.listening_stop_event.set()
            self.mic_button.config(text="🎤 Start Listening", bg="#4CAF50")
            self.mic_button.bind("<Enter>", self.on_mic_button_enter)
            self.mic_button.bind("<Leave>", self.on_mic_button_leave)
            self.status_label.config(text="Status: Idle")
            
            # Enable process last audio button
            if hasattr(self, 'last_audio') and self.last_audio:
                self.process_last_button.config(state=tk.NORMAL)
            
    def listen_and_translate(self):
        """Listen for voice input and translate using threading"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.root.after(0, lambda: self.status_label.config(text="Status: Listening..."))
            
            while self.is_listening and not self.listening_stop_event.is_set():
                try:
                    # Listen for audio input
                    audio = self.recognizer.listen(
                        source=source,
                        timeout=5,
                        phrase_time_limit=10
                    )
                    
                    # Store the last captured audio for post-processing
                    self.last_audio = audio
                    
                    # Enable the process last audio button
                    self.root.after(0, lambda: self.process_last_button.config(state=tk.NORMAL))
                    
                    # Update UI thread safely
                    self.root.after(0, lambda: self.status_label.config(text="Status: Processing..."))
                    
                    # Process audio in a thread to avoid hanging the main listening loop
                    process_thread = threading.Thread(target=self._process_audio, args=(audio,))
                    process_thread.daemon = True
                    process_thread.start()
                    
                except sr.WaitTimeoutError:
                    if self.is_listening and not self.listening_stop_event.is_set():
                        self.root.after(0, lambda: self.status_label.config(text="Status: Listening..."))
                except sr.UnknownValueError:
                    if self.is_listening and not self.listening_stop_event.is_set():
                        self.root.after(0, lambda: self.status_label.config(text="Status: Could not understand audio"))
                except Exception as e:
                    if self.is_listening and not self.listening_stop_event.is_set():
                        error_msg = str(e)
                        print(f"Listening error: {error_msg}")
                        if len(error_msg) > 100:
                            error_msg = error_msg[:97] + "..."
                        self.root.after(0, lambda msg=error_msg: self.status_label.config(text=f"Status: Error - {msg}"))
                
                # Add a small delay to prevent CPU overuse
                time.sleep(0.1)
    
    def process_last_audio(self):
        """Process the last captured audio even if listening has stopped"""
        if self.last_audio:
            # Update status
            self.status_label.config(text="Status: Processing last audio...")
            
            try:
                # Process in a separate thread to avoid freezing UI
                process_thread = threading.Thread(target=self._process_audio, args=(self.last_audio,))
                process_thread.daemon = True
                process_thread.start()
            except Exception as e:
                self.status_label.config(text=f"Status: Error - {str(e)}")
        else:
            messagebox.showinfo("Information", "No audio captured yet. Please start listening first.")
            
    def _process_audio(self, audio):
        """Process audio in a separate thread"""
        # Initialize translated_text to prevent unbinding issues
        translated_text = "Translation not available"
        
        try:
            # Transcribe audio
            source_text = self.recognizer.recognize_google(audio)
            print(f"Recognized text: {source_text}")
            
            # Detect language
            source_lang = detect(source_text)
            source_lang_name = LANGUAGES.get(source_lang, "Unknown")
            print(f"Detected language: {source_lang} ({source_lang_name})")
            
            # Get target language code
            target_lang = self.preferred_lang.get().split(":")[0].strip()
            target_lang_name = LANGUAGES.get(target_lang, "Unknown")
            print(f"Target language: {target_lang} ({target_lang_name})")
            
            # Create a new translator object for each translation
            # This helps avoid sharing a single instance across threads
            translator = Translator()
            
            # Handle translation with async wrapper
            try:
                # Initialize return_early flag
                return_early = False
                
                # Check if translate returns a coroutine (newer versions of googletrans)
                translation = translator.translate(
                    source_text,
                    src=source_lang,
                    dest=target_lang
                )
                
                print(f"Translation object type: {type(translation)}")
                
                # Check for coroutine or object representation 
                translation_str = str(translation)
                coroutine_detected = (
                    asyncio.iscoroutine(translation) or 
                    translation_str.startswith('<coroutine') or 
                    'object at 0x' in translation_str or
                    translation_str.startswith('<googletrans.models.Translated') or
                    hasattr(translation, '__dict__') and not hasattr(translation, 'text')
                )
                
                if coroutine_detected:
                    print("Detected coroutine or raw object - using direct translation")
                    # Don't try to await the coroutine, use our fallback method instead
                    translated_text = self.fallback_translate(source_text, source_lang, target_lang)
                    print(f"Used fallback translation: {translated_text}")
                    return_early = True
                
                # Process the translation result if we didn't use fallback already
                if not return_early:
                    if hasattr(translation, 'text'):
                        translated_text = translation.text
                        print(f"Extracted translation text attribute: {translated_text}")
                    elif isinstance(translation, str):
                        translated_text = translation
                        print(f"Translation is already a string: {translated_text}")
                    elif isinstance(translation, dict) and 'text' in translation:
                        translated_text = translation['text']
                        print(f"Extracted text from dictionary: {translated_text}")
                    else:
                        # Last resort: extract from string representation
                        print(f"Extracting from string representation: {translation}")
                        translation_str = str(translation)
                        
                        # For coroutine objects that haven't been awaited
                        if 'coroutine' in translation_str or 'object' in translation_str:
                            # Use fallback instead of placeholder
                            try:
                                translated_text = self.fallback_translate(source_text, source_lang, target_lang)
                                print(f"Used fallback for coroutine/object: {translated_text}")
                            except Exception as fb_err:
                                print(f"Fallback failed: {fb_err}")
                                translated_text = f"वह नहीं चला" # Hindi for "That didn't work"
                            
                        # For googletrans Translated objects
                        elif 'Translated' in translation_str:
                            text_start = translation_str.find("text=") + 5
                            if text_start > 5:  # Found "text="
                                text_end = translation_str.find(",", text_start)
                                if text_end > text_start:
                                    extracted_text = translation_str[text_start:text_end].strip()
                                    if extracted_text.startswith("'") and extracted_text.endswith("'"):
                                        extracted_text = extracted_text[1:-1]
                                    translated_text = extracted_text
                                else:
                                    translated_text = self.fallback_translate(source_text, source_lang, target_lang)
                            else:
                                translated_text = self.fallback_translate(source_text, source_lang, target_lang)
                        else:
                            # If all else fails, use the fallback method
                            translated_text = self.fallback_translate(source_text, source_lang, target_lang)
                
            except Exception as translation_error:
                print(f"Translation error: {translation_error}")
                translated_text = f"Translation error: {str(translation_error)[:50]}"
                # Try to recover with direct HTTP request
                try:
                    print("Attempting direct translation with HTTP request...")
                    # Manual fallback using httpx
                    translated_text = self.fallback_translate(source_text, source_lang, target_lang)
                except Exception as fallback_error:
                    print(f"Fallback translation error: {fallback_error}")
                    translated_text = f"Unable to translate text: {str(fallback_error)[:50]}"
            
            print(f"Final translated text: {translated_text}")
            
            # Update UI with results (safely from another thread)
            self.root.after(0, lambda: self.update_ui_with_translation(
                source_text, 
                source_lang, 
                translated_text, 
                target_lang
            ))
            
            # Save to history
            self.save_to_history(
                source_text, 
                source_lang, 
                translated_text, 
                target_lang
            )
            
        except Exception as e:
            print(f"General audio processing error: {e}")
            # Format the error message
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:97] + "..."
            # Update status directly
            self.root.after(0, lambda msg=error_msg: self.status_label.config(text=f"Status: Error - {msg}"))
    
    def on_mic_button_enter(self, event):
        """Handle mouse enter event for mic button"""
        self.mic_button.config(bg="#5CBF60" if not self.is_listening else "#F55A4E")
    
    def on_mic_button_leave(self, event):
        """Handle mouse leave event for mic button"""
        self.mic_button.config(bg="#4CAF50" if not self.is_listening else "#F44336")
    
    def on_refresh_button_enter(self, event):
        """Handle mouse enter event for refresh button"""
        event.widget.config(bg="#A87FE6")  # Lighter purple on hover, matching theme
    
    def on_refresh_button_leave(self, event):
        """Handle mouse leave event for refresh button"""
        event.widget.config(bg="#9370DB")  # Back to regular purple
    
    def on_clear_button_enter(self, event):
        """Handle mouse enter event for clear button"""
        event.widget.config(bg="#EF5350")
    
    def on_clear_button_leave(self, event):
        """Handle mouse leave event for clear button"""
        event.widget.config(bg="#F44336")
        
    def on_process_button_enter(self, event):
        """Handle mouse enter event for process last audio button"""
        event.widget.config(bg="#A87FE6")  # Lighter purple on hover
        
    def on_process_button_leave(self, event):
        """Handle mouse leave event for process last audio button"""
        event.widget.config(bg="#9370DB")  # Return to normal purple
        
    def update_ui_callback(self, source_text, source_lang, translated_text, target_lang):
        """Create a callback function for updating UI from another thread"""
        def callback():
            self.update_ui_with_translation(source_text, source_lang, translated_text, target_lang)
        return callback
    
    def status_update_callback(self, status_text):
        """Create a callback function for updating status from another thread"""
        def callback():
            self.status_label.config(text=status_text)
        return callback
    
    def update_ui_with_translation(self, source_text, source_lang, translated_text, target_lang):
        """Update UI with translation results"""
        # Update source text
        self.source_text.config(state="normal")
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", f"{source_text}\n\nDetected Language: {source_lang}")
        self.source_text.config(state="disabled")
        
        # Update translated text
        self.translated_text.config(state="normal")
        self.translated_text.delete("1.0", tk.END)
        self.translated_text.insert("1.0", f"{translated_text}\n\nTranslated to: {target_lang}")
        self.translated_text.config(state="disabled")
        
        # Update status
        self.status_label.config(text="Status: Translation Complete")
        
    def save_to_history(self, source_text, source_lang, translated_text, target_lang):
        """Save translation to database"""
        # First, make sure we have a database path
        if not hasattr(self, 'db_path') or not self.db_path:
            print("No database path set for save - attempting to resolve")
            
            # Try to initialize the database first
            self.setup_db()
            
            # Check again after setup
            if not hasattr(self, 'db_path') or not self.db_path:
                print("Still no database path available for save operation - cannot save history")
                return
            
        # Track error count to avoid excessive error messages
        if not hasattr(self, '_db_error_count'):
            self._db_error_count = 0
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            print(f"Saving translation to history at {self.db_path}")
            
            # Create a new connection for this operation to avoid threading issues
            # This is critical for thread safety in SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First make sure the table exists (important for first run)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    source_text TEXT,
                    source_lang TEXT,
                    translated_text TEXT,
                    target_lang TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO history (timestamp, source_text, source_lang, translated_text, target_lang)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, source_text, source_lang, translated_text, target_lang))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Successfully saved translation: {source_lang} -> {target_lang}")
            
            # Update history view if visible using the main thread
            # Schedule this using after() to ensure thread safety
            if hasattr(self, 'notebook') and self.notebook.index("current") == 1:  # If history tab is visible
                self.root.after(0, self.load_history)
                
            # Reset error count after success
            self._db_error_count = 0
            
        except sqlite3.OperationalError as sql_e:
            print(f"SQL error saving to history: {sql_e}")
            self._db_error_count += 1
            
            # Check for common errors - limit error messages to avoid spamming
            error_msg = str(sql_e).lower()
            if ("unable to open database" in error_msg or "readonly database" in error_msg) and self._db_error_count <= 2:
                # Permission issues - show only first two times
                error_msg = "Cannot save to history: Database is read-only.\nTry running the application with administrator privileges."
                self.root.after(0, lambda: messagebox.showerror("Database Error", error_msg))
            elif self._db_error_count <= 2:
                # Other SQL errors - show only first two times
                self.root.after(0, lambda: messagebox.showerror("Database Error", f"Database error: {str(sql_e)}"))
                
        except Exception as e:
            print(f"General error saving to history: {e}")
            self._db_error_count += 1
            
            # Show error message but limit to avoid spamming
            if self._db_error_count <= 2:
                error_msg = f"Failed to save translation to history: {e}"
                self.root.after(0, lambda: messagebox.showerror("Database Error", error_msg))
    
    def load_history(self):
        """Load translation history from database"""
        # Check if we have the history tree 
        if not hasattr(self, 'history_tree'):
            print("History tree not initialized yet")
            return
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # First, make sure we have a database path
        if not hasattr(self, 'db_path') or not self.db_path:
            print("No database path set - attempting to resolve")
            
            # Try to initialize the database first
            self.setup_db()
            
            # Check again after setup
            if not hasattr(self, 'db_path') or not self.db_path:
                print("Still no database path available after setup")
                self.history_tree.insert("", "end", values=("", "", "History unavailable - Database not accessible", "", "", ""))
                return
        
        # Now try to load the history data
        try:
            print(f"Loading history from {self.db_path}")
            
            # Create a new connection for this operation
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history ORDER BY timestamp DESC")
            history_data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"Found {len(history_data)} history entries")
            
            # Populate treeview
            for item in history_data:
                # Format text for display (truncate if too long)
                source_text = (item[2][:30] + '...') if len(item[2]) > 30 else item[2]
                translated_text = (item[4][:30] + '...') if len(item[4]) > 30 else item[4]
                
                # Get language names for display
                source_lang_name = LANGUAGES.get(item[3], "Unknown")
                target_lang_name = LANGUAGES.get(item[5], "Unknown")
                
                self.history_tree.insert("", "end", values=(
                    item[0],  # ID
                    item[1],  # Timestamp
                    source_text,
                    source_lang_name,
                    translated_text,
                    target_lang_name
                ))
            
            # Show status message for empty history
            if len(history_data) == 0:
                self.history_tree.insert("", "end", values=("", "", "No translation history available", "", "", ""))
                
        except sqlite3.OperationalError as sql_e:
            print(f"SQL error loading history: {sql_e}")
            
            # Special handling for common sqlite errors
            error_msg = str(sql_e).lower()
            if "no such table" in error_msg:
                # Table doesn't exist yet - this is normal for first run
                self.history_tree.insert("", "end", values=("", "", "No history yet - Start translating to create entries", "", "", ""))
            elif "unable to open database" in error_msg or "readonly database" in error_msg:
                # Permission issues
                print("Database permission issues - may need to run as administrator")
                self.history_tree.insert("", "end", values=("", "", "Cannot access history database - Permission error", "", "", ""))
            else:
                # Other SQL errors
                self.history_tree.insert("", "end", values=("", "", f"Database error: {str(sql_e)[:100]}", "", "", ""))
            
        except Exception as e:
            # General errors
            print(f"Error loading history: {e}")
            self.history_tree.insert("", "end", values=("", "", f"Error loading history: {str(e)[:100]}", "", "", ""))
    
    def clear_history(self):
        """Clear all history from database"""
        # First, make sure we have a database path
        if not hasattr(self, 'db_path') or not self.db_path:
            print("No database path set for clear - attempting to resolve")
            
            # Try to initialize the database first
            self.setup_db()
            
            # Check again after setup
            if not hasattr(self, 'db_path') or not self.db_path:
                print("Still no database path available for clear operation")
                messagebox.showerror("Database Error", "Cannot clear history: Database not accessible")
                return
        
        # Confirm with user
        if messagebox.askyesno("Confirmation", "Are you sure you want to clear all translation history?"):
            try:
                print(f"Attempting to clear history in {self.db_path}")
                
                # Create a new connection for this operation
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # First check if the table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
                if not cursor.fetchone():
                    print("History table doesn't exist yet, nothing to clear")
                    cursor.close()
                    conn.close()
                    messagebox.showinfo("Information", "No history exists yet to clear")
                    return
                
                # If table exists, delete all entries
                cursor.execute("DELETE FROM history")
                conn.commit()
                cursor.close()
                conn.close()
                
                print("History cleared successfully")
                
                # Refresh the view
                self.load_history()
                messagebox.showinfo("Success", "Translation history cleared successfully")
                
            except sqlite3.OperationalError as sql_e:
                print(f"SQL error clearing history: {sql_e}")
                
                # Check for common errors
                error_msg = str(sql_e).lower()
                if "unable to open database" in error_msg or "readonly database" in error_msg:
                    # Permission issues
                    error_msg = "Cannot clear history: Permission error. Try running as administrator."
                else:
                    error_msg = f"Database error: {str(sql_e)}"
                
                messagebox.showerror("Database Error", error_msg)
                
            except Exception as e:
                print(f"Error clearing history: {e}")
                messagebox.showerror("Database Error", f"Failed to clear history: {str(e)}")
    
    def fallback_translate(self, text, src_lang, dest_lang):
        """Fallback translation method that uses direct HTTP requests when googletrans has issues"""
        print(f"Using fallback translation for: {text} from {src_lang} to {dest_lang}")
        
        try:
            # Simple dictionary of common translations as a last resort
            common_phrases = {
                "hello": {"hi": "नमस्ते", "es": "hola", "fr": "bonjour", "de": "hallo"},
                "how are you": {"hi": "आप कैसे हैं", "es": "cómo estás", "fr": "comment allez-vous", "de": "wie geht es dir"},
                "thank you": {"hi": "धन्यवाद", "es": "gracias", "fr": "merci", "de": "danke"},
                "goodbye": {"hi": "अलविदा", "es": "adiós", "fr": "au revoir", "de": "auf wiedersehen"},
                "yes": {"hi": "हां", "es": "sí", "fr": "oui", "de": "ja"},
                "no": {"hi": "नहीं", "es": "no", "fr": "non", "de": "nein"}
            }
            
            # Try the common phrases dictionary first
            text_lower = text.lower()
            if text_lower in common_phrases and dest_lang in common_phrases[text_lower]:
                return common_phrases[text_lower][dest_lang]
            
            # Use httpx for direct translation API call
            try:
                print("Attempting direct API call with httpx")
                import httpx
                
                # Use Google Translate API directly
                # Note: This is a simplified version and may not work as reliably as the full library
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    "client": "gtx",
                    "sl": src_lang,
                    "tl": dest_lang,
                    "dt": "t",
                    "q": text
                }
                
                with httpx.Client() as client:
                    response = client.get(url, params=params)
                    if response.status_code == 200:
                        # Parse the response - typically nested arrays
                        result = response.json()
                        if result and len(result) > 0 and len(result[0]) > 0:
                            translated = ""
                            # Combine all translation segments
                            for segment in result[0]:
                                if segment and len(segment) > 0:
                                    translated += segment[0]
                            return translated
            except Exception as api_error:
                print(f"Direct API translation error: {api_error}")
                
            # If all else fails, return an informative message
            return f"Translation unavailable for '{text}'. Try again or use another language."
            
        except Exception as e:
            print(f"Fallback translation error: {e}")
            return f"Translation failed: {str(e)[:50]}"
    
    def on_closing(self):
        """Handle window close event"""
        # Stop listening if active
        if self.is_listening:
            self.is_listening = False
            self.listening_stop_event.set()
            if self.listening_thread and self.listening_thread.is_alive():
                self.listening_thread.join(1.0)  # Wait for 1 second max
        
        # No need to close database connections as we're using fresh connections per operation
        
        # Destroy root window
        self.root.destroy()

def create_initial_data_folder():
    """Create initial data folder for the application on startup"""
    print("Setting up initial data folder...")
    
    # Ensure data folder exists in current directory
    if not os.path.exists("data"):
        try:
            os.makedirs("data", exist_ok=True)
            print("Created data folder in current directory")
        except Exception as e:
            print(f"Could not create data folder in current directory: {e}")
    
    # Try to create a sample database file to ensure it's writable
    try:
        db_path = os.path.join("data", "translation_history.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source_text TEXT,
                source_lang TEXT,
                translated_text TEXT,
                target_lang TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Created/verified initial database at {db_path}")
    except Exception as e:
        print(f"Could not create initial database: {e}")
        
    # Also create the data folder in user's documents as fallback
    try:
        home_path = str(os.path.expanduser("~"))
        docs_data_path = os.path.join(home_path, "Documents", "VoiceTranslatorPro")
        os.makedirs(docs_data_path, exist_ok=True)
        print(f"Created/verified fallback data folder at {docs_data_path}")
    except Exception as e:
        print(f"Could not create fallback data folder: {e}")

if __name__ == "__main__":
    # Create initial data folder on startup
    create_initial_data_folder()
    
    # Start the application
    root = tk.Tk()
    app = VoiceTranslatorApp(root)
    root.mainloop()
