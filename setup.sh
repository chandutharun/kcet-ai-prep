#!/bin/bash

echo "🎓 KCET AI Prep - Setup Script"
echo "================================"

# 1. Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# 2. Pull LLM Models
echo "📦 Pulling LLM models..."
ollama pull llama3.1
ollama pull sarvam-1

# 3. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# 4. Create directories
echo "📁 Creating directories..."
mkdir -p pdfs chroma_db

# 5. Download embeddings (ONE TIME - uses internet)
echo "📦 Downloading embeddings (Hugging Face - ONE TIME)..."
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 6. Start Ollama
echo "🚀 Starting Ollama server..."
ollama serve

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add NCERT PDFs to 'pdfs/' folder"
echo "2. Run: streamlit run app.py"
echo "3. Access: http://localhost:8501"