# Word Counter en Tekstanalyse

Een Flask-applicatie voor het analyseren van Nederlandse teksten. De applicatie biedt de volgende functionaliteiten:
- Woordentelling
- Parts of Speech (POS) analyse
- Woordenwolk van de 50 meest voorkomende woorden
- Ondersteuning voor .txt en .docx bestanden

## Installatie

1. Zorg dat Python 3.8+ is geïnstalleerd
2. Installeer de vereiste packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Installeer het Nederlandse taalmodel voor spaCy:
   ```bash
   python -m spacy download nl_core_news_sm
   ```

## Gebruik

1. Start de server:
   ```bash
   python app.py
   ```
2. Open een webbrowser en ga naar `http://localhost:5000`
3. Upload een tekst- of Word-bestand voor analyse

## Technische Details

- Backend: Flask (Python)
- NLP: spaCy met Nederlands taalmodel
- Frontend: Tailwind CSS
- Woordenwolk: WordCloud package 