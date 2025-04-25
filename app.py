from flask import Flask, render_template, request, jsonify, send_file
import os
from docx import Document
import spacy
from collections import Counter
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

try:
    nlp = spacy.load('nl_core_news_sm')
except OSError:
    nlp = spacy.load('nl_core_news_sm')

# Dictionary voor Nederlandse labels van woordsoorten
POS_LABELS = {
    'NOUN': 'Zelfstandig naamwoord',
    'VERB': 'Werkwoord',
    'AUX': 'Hulpwerkwoord',
    'ADJ': 'Bijvoeglijk naamwoord',
    'ADV': 'Bijwoord',
    'ADP': 'Voorzetsel',
    'DET': 'Lidwoord',
    'PRON': 'Voornaamwoord',
    'PROPN': 'Eigennaam',
    'NUM': 'Telwoord',
    'CCONJ': 'Nevenschikkend voegwoord',
    'SCONJ': 'Onderschikkend voegwoord',
    'INTJ': 'Tussenwerpsel',
    'PUNCT': 'Leesteken',
    'SYM': 'Symbool',
    'X': 'Overig'
}

def generate_wordcloud(text):
    # Verwerk de tekst met spaCy
    doc = nlp(text)
    
    # Filter betekenisvolle woorden (geen leestekens, lidwoorden etc.)
    words = [token.text.lower() for token in doc 
             if not token.is_stop and not token.is_punct 
             and not token.is_space and len(token.text) > 1]
    
    # Tel woorden
    word_freq = Counter(words)
    
    # Neem de top 50 woorden
    top_words = dict(word_freq.most_common(50))
    
    # Genereer word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='#242424',
        colormap='viridis',
        max_words=50,
        prefer_horizontal=0.7
    ).generate_from_frequencies(top_words)
    
    # Converteer naar base64 string
    img = BytesIO()
    plt.figure(figsize=(10, 5), facecolor='#242424')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png', facecolor='#242424', bbox_inches='tight', pad_inches=0)
    plt.close()
    img.seek(0)
    
    return base64.b64encode(img.getvalue()).decode()

def analyze_text(text):
    # Verwerk de tekst met spaCy
    doc = nlp(text)
    
    # Tel woordsoorten
    pos_counts = Counter(token.pos_ for token in doc if not token.is_space)
    
    # Maak een lijst van resultaten met Nederlandse labels
    results = []
    for pos, count in pos_counts.items():
        dutch_label = POS_LABELS.get(pos, pos)
        results.append({
            'type': dutch_label,
            'count': count,
            'examples': [token.text for token in doc if token.pos_ == pos][:5]  # Max 5 voorbeelden
        })
    
    # Sorteer op aantal (meest voorkomend eerst)
    results.sort(key=lambda x: x['count'], reverse=True)
    
    # Genereer word cloud
    wordcloud_image = generate_wordcloud(text)
    
    return results, wordcloud_image

def analyze_docx(file_path):
    doc = Document(file_path)
    full_text = ' '.join(paragraph.text for paragraph in doc.paragraphs)
    return analyze_text(full_text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Geen bestand geüpload'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Geen bestand geselecteerd'}), 400
    
    if file:
        # Controleer bestandsextensie
        if not file.filename.lower().endswith('.docx'):
            return jsonify({'error': 'Alleen Word documenten (.docx) zijn toegestaan'}), 400
        
        # Sla het bestand op
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Analyseer het document
            analysis_results, wordcloud_image = analyze_docx(file_path)
            
            # Verwijder het bestand na verwerking
            os.remove(file_path)
            
            return jsonify({
                'analysis': analysis_results,
                'total_words': sum(result['count'] for result in analysis_results),
                'wordcloud': wordcloud_image
            })
        except Exception as e:
            # Verwijder het bestand bij een fout
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': 'Fout bij het verwerken van het bestand'}), 500

if __name__ == '__main__':
    app.run(debug=True) 