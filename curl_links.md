# BabelBot API CURL Commands

## OCR Endpoints

### OCR Only (Detect Text)
```bash
curl -X POST -F "image=@main_app/static/images/test.png" http://localhost:8000/ocr/api/ocr/
```
Extracts text from an image using OCR and returns the detected text and language.

### OCR + Translation to Spanish
```bash
curl -X POST -F "image=@main_app/static/images/test.png" -F "target_language=es" http://localhost:8000/ocr/api/ocr-translate/
```
Extracts text from an image and translates it to Spanish.

### OCR + Translation to French
```bash
curl -X POST -F "image=@main_app/static/images/test.png" -F "target_language=fr" http://localhost:8000/ocr/api/ocr-translate/
```
Extracts text from an image and translates it to French.

### OCR + Language Detection
```bash
curl -X POST -F "image=@main_app/static/images/test.png" -F "target_language=detect" http://localhost:8000/ocr/api/ocr-translate/
```
Extracts text from an image and detects the language without translation.

## Text Translation Endpoints

### Translate to Spanish
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text_to_translate":"This is a test", "target_language":"es"}' http://localhost:8000/api/translate/
```
Translates the text "This is a test" to Spanish.

### Translate to French
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text_to_translate":"This is a test", "target_language":"fr"}' http://localhost:8000/api/translate/
```
Translates the text "This is a test" to French.

### Translate to German
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text_to_translate":"This is a test", "target_language":"de"}' http://localhost:8000/api/translate/
```
Translates the text "This is a test" to German.

### Language Detection
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text_to_translate":"This is a test", "target_language":"detect"}' http://localhost:8000/api/translate/
```
Detects the language of the text "This is a test" without translation.

## Notes
- All OCR endpoints accept image files in common formats (PNG, JPG, etc.)
- All text translation endpoints require JSON content type
- The `target_language` parameter accepts standard language codes (es, fr, de, etc.)
- Use `detect` as the target language to only detect the language without translation
- All responses are in JSON format 