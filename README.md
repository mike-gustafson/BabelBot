# BabelBot 🌐

<div align="center">
<table style="border: none; background: none;">
<tr style="border: none; background: none;">
<td style="border: none; background: none;">
  <img src="main_app/static/images/logo2.png" alt="BabelBot Logo" width="300"/>
</td>
<td style="border: none; background: none;">
  <a href="https://babelbot-80382e0f3acb.herokuapp.com/">
    <img src="main_app/static/images/qr-code.svg" alt="QR Code" width="150"/>
  </a>
  <br/>
  <em>Scan to access BabelBot on your mobile device</em>
</td>
</tr>
</table>
</div>

## 🚀 About BabelBot

BabelBot is your AI-powered language companion, breaking down language barriers with cutting-edge technology. Whether you're traveling abroad, learning a new language, or just need quick translations, BabelBot has you covered.

### ✨ Key Features

- **Real-time Translation**: Instantly translate text between 100+ languages
- **OCR Translation**: Snap a photo of text and get instant translations
- **Text-to-Speech**: Hear your translations in natural-sounding voices
- **Mobile-First Design**: Optimized for on-the-go translation needs
- **Dark/Light Mode**: Choose your preferred theme for any environment

## 📱 Mobile Magic

BabelBot is designed with mobile users in mind. Here's how you can use it on the go:

1. **Voice Input**: Use your device's built-in microphone to speak in your language
2. **Camera Translation**: Point your camera at signs, menus, or documents
3. **QR Code Access**: Scan the QR code above to open BabelBot instantly

## 🛠️ Tech Stack

### Core Technologies
- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Django, Python
- **Database**: PostgreSQL
- **Deployment**: Heroku
- **Package Management**: Pipenv

### App-Specific Technologies

#### OCR Module
- Google Cloud Vision API
- Image processing and text extraction
- Multi-language text detection
- Automatic language identification

#### Translator Module
- Google Translate API
- Real-time translation
- Language detection
- Translation history tracking

#### TTS Module
- Google Text-to-Speech API
- Natural-sounding voices
- Multiple language support
- Voice customization options

## 🗄️ Database Schema

```ascii
+---------------+       +----------------+       +----------------+
|     User      |       |    Profile     |       |  Translation   |
+---------------+       +----------------+       +----------------+
| id            |<----->| id             |       | id             |
| username      |       | user (FK)      |<----->| user (FK)      |
| email         |       | bio            |       | original_text  |
| password      |       | preferred_lang |       | translated_text|
| first_name    |       | created_at     |       | target_lang    |
| last_name     |       | updated_at     |       | translation_type|
| date_joined   |       +----------------+       | created_at     |
| last_login    |                               | updated_at     |
+---------------+                               +----------------+
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Django 4.0+
- Google Cloud account (for API access)
- PostgreSQL
- Pipenv

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BabelBot.git
cd BabelBot
```

2. Install dependencies using Pipenv:
```bash
pipenv install
pipenv shell
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

## 📚 Documentation

- [OCR Module](ocr/README.md)
- [Translator Module](translator/README.md)
- [TTS Module](tts/README.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Cloud Platform for their amazing APIs
- The Django community for their excellent framework
- All our contributors and users

---

<div align="center">
  <p>Made with ❤️ by the BabelBot Team</p>
  <p>Visit us at <a href="https://babelbot-80382e0f3acb.herokuapp.com/">BabelBot</a></p>
</div> 