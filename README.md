# Voice Translator Pro

A sophisticated desktop application for real-time voice translation across multiple languages, featuring a modern UI and translation history tracking.

## Features

- Real-time voice translation with automatic language detection
- Support for 30 languages 
- Sleek midnight-dark UI theme with purple accents
- Translation history storage and management
- Ability to process audio even after stopping listening
- Cross-platform compatibility

## Requirements

- Python 3.8 or higher
- Required Python packages (installed automatically):
  - SpeechRecognition
  - googletrans==4.0.0-rc1
  - PyAudio
  - langdetect

## Setup & Running

### Running from Source

1. Ensure Python 3.8+ is installed on your system
2. Install required packages:
   ```
   pip install SpeechRecognition googletrans==4.0.0-rc1 pyaudio langdetect
   ```
3. Run the application:
   ```
   python voice_translator.py
   ```

### Building an Executable

#### Option 1: Simple Build (Recommended)

1. Run the `build.bat` script (Windows)
2. Choose from the build options presented
3. The executable will be created in the `dist` folder

#### Option 2: Standard Build

1. Run the `build_exe.bat` script (Windows)
2. The executable will be created in the `dist` folder

## Using the Application

1. **Translator Tab**: Main interface for voice translation
   - Click "Start Listening" to begin capturing audio
   - Choose your desired output language from the dropdown
   - Speak clearly into your microphone
   - View the detected language and translation results
   - Click "Stop Listening" when finished
   - Use "Process Last Audio" to translate the last captured segment even after stopping

2. **History Tab**: View and manage your translation history
   - Browse previous translations
   - Click "Refresh History" to update the view
   - Click "Clear History" to delete all saved translations

## Troubleshooting Executable Issues

If you experience issues with the executable version:

1. **Database Connection Errors**:
   - Try running the application as administrator
   - Ensure a `data` folder exists in the same directory as the executable
   - The application will automatically use your Documents folder if both options fail

2. **Translator Object Display Issues**:
   - These may sometimes appear in the PyInstaller environment
   - The application includes built-in workarounds to handle these issues 

3. **Debug Mode**:
   - For troubleshooting, build using option 2 in the simple_build script
   - This creates a version with a visible console that shows error messages

## Advanced Configuration

The application automatically creates and manages its database in one of these locations:

1. The `data` folder in the application directory (primary)
2. A `VoiceTranslatorPro` folder in your Documents (fallback)
3. A `VoiceTranslatorPro` folder in your system temp directory (final fallback)

## Credits

Created by robbie09 © 2025 | Voice Translator Protor Pro