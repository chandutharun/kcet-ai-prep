# 🎓 KCET AI Prep Assistant

An offline RAG-based AI assistant for KCET exam preparation using NCERT textbooks. Supports English and Kannada languages.

## Features

- ✅ **100% Offline** - No internet required after initial setup
- ✅ **NCERT-based Q&A** - Answers from NCERT textbooks
- ✅ **English + Kannada** - Hybrid mode with Kannada translation
- ✅ **Previous Year Questions** - PYQ support for KCET exam
- ✅ **Auto Embedding** - Automatically embeds PDFs into RAG vector database
- ✅ **Local LLMs** - Uses llama3.1 and sarvam-1 via Ollama

## Your PDF Folder Structure

Your PDFs are organized like this:
kcet_ai_prep/
├── pdfs/
│ └── ncert/
│ ├── biology/
│ │ ├── NCERT-Class-12-Biology.pdf
│ │ └── ...
│ ├── chemistry/
│ │ ├── NCERT-Class-12-Chemistry.pdf
│ │ └── ...
│ ├── computer Science/
│ │ ├── NCERT-Class-11-ComputerScience.pdf
│ │ └── ...
│ ├── electronics/
│ │ ├── NCERT-Class-12-Electronics.pdf
│ │ └── ...
│ ├── mathematics/
│ │ ├── NCERT-Class-12-Mathematics.pdf
│ │ └── ...
│ ├── physics/
│ │ ├── NCERT-Class-11-Physics-Part-1.pdf
│ │ ├── NCERT-Class-11-Physics-Part-2.pdf
│ │ └── ...
│ └── pyq/
│ ├── kcet-2024-physics.pdf
│ └── ...



**✅ Perfect!** Your structure is already correct - just add PDF files inside each subject folder.

## How to Run

### Option 1: Run Locally (Recommended for First Time)

#### Step 1: Install Ollama

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Windows
# Download from https://ollama.ai/download
```

#### Step 2: Pull LLM Models

```bash
# Pull llama3.1 (English Q&A)
ollama pull llama3.1

# Pull sarvam-1 (Kannada translation)
ollama pull sarvam-1
```

#### Step 3: Start Ollama Server

```bash
# Run in background
ollama serve
```

**Keep this terminal open** while using the app.

#### Step 4: Install Python Dependencies

```bash
# Navigate to project folder
cd ~/kcet_ai_prep

# Create virtual environment (if not created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 5: Add NCERT PDFs

Put PDF files in their subject folders:

```bash
# Biology
cp /path/to/your/biology.pdf ~/kcet_ai_prep/pdfs/ncert/biology/

# Physics
cp /path/to/your/physics.pdf ~/kcet_ai_prep/pdfs/ncert/physics/

# Chemistry
cp /path/to/your/chemistry.pdf ~/kcet_ai_prep/pdfs/ncert/chemistry/

# Computer Science
cp /path/to/your/compsci.pdf ~/kcet_ai_prep/pdfs/ncert/computer Science/

# Electronics
cp /path/to/your/electronics.pdf ~/kcet_ai_prep/pdfs/ncert/electronics/

# Mathematics
cp /path/to/your/math.pdf ~/kcet_ai_prep/pdfs/ncert/mathematics/

# Previous Year Questions
cp /path/to/your/kcet-pyq.pdf ~/kcet_ai_prep/pdfs/ncert/pyq/
```

#### Step 6: Run the App

```bash
# Navigate to project
cd ~/kcet_ai_prep

# Activate virtual environment
source venv/bin/activate

# Start Streamlit app
streamlit run app.py
```

#### Step 7: Access the App

Open browser and go to:
http://localhost:8501



**First Run:**
- App will auto-detect PDFs in `pdfs/ncert/`
- Embed all PDFs into ChromaDB (5-10 minutes)
- Ready to answer questions!

---

### Option 2: Run with Docker (For Production)

#### Step 1: Install Docker

```bash
# Linux
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### Step 2: Pull LLM Models (Outside Docker)

```bash
# Install Ollama first
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.1
ollama pull sarvam-1

# Start Ollama
ollama serve
```

#### Step 3: Add PDFs

Same as local setup - put PDFs in `pdfs/ncert/` folders.

#### Step 4: Build and Run Docker

```bash
# Navigate to project
cd ~/kcet_ai_prep

# Build Docker image
docker-compose build

# Run with Docker Compose
docker-compose up
```

Or run without Compose:

```bash
# Build image
docker build -t kcet-ai-prep .

# Run container (connects to Ollama on same host)
docker run -d \
  -p 8501:8501 \
  -v ./pdfs:/app/pdfs \
  -v ./chroma_db:/app/chroma_db \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --name kcet-app \
  kcet-ai-prep
```

#### Step 5: Access the App
http://localhost:8501



#### Step 6: Stop Docker

```bash
# Stop container
docker-compose down

# Or
docker stop kcet-app
```

---

### Option 3: Run with Setup Script (Quick Start)

```bash
# Navigate to project
cd ~/kcet_ai_prep

# Run setup script (automates everything)
chmod +x setup.sh
source setup.sh

# Then run app
streamlit run app.py
```

---

## Project Structure
kcet_ai_prep/
├── app.py # Streamlit UI
├── src/
│ ├── _init_.py
│ ├── rag.py # RAG pipeline
│ ├── models.py # LLM configuration
│ ├── database.py # SQLite database
│ └── config.py # Configuration
├── pdfs/ # 📁 PDFs folder
│ └── ncert/
│ ├── biology/
│ ├── chemistry/
│ ├── computer Science/
│ ├── electronics/
│ ├── mathematics/
│ ├── physics/
│ └── pyq/
├── chroma_db/ # 🗄️ Vector database (auto-created)
├── kcet_progress.sqlite # Student database
├── requirements.txt # Python dependencies
├── Dockerfile # Docker config
├── docker-compose.yml # Docker Compose config
├── setup.sh # Setup script
├── README.md # This file
└── venv/ # Python virtual environment



## Configuration

Edit `src/config.py`:

```python
# PDF Folder (matches your structure)
PDF_FOLDER = "./pdfs/ncert"

# Vector Database
CHROMA_PATH = "./chroma_db"

# Database
DATABASE_PATH = "./kcet_progress.sqlite"

# LLM Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 5
```

## Student Analytics

Your progress is saved in `kcet_progress.sqlite`:

- Total questions asked
- Chat history
- Subject preferences

## Usage Examples

### Ask NCERT Questions
Q: "explain about photosynthesis"
✅ From NCERT textbook | NCERT-Class-12-Biology.pdf | Page 277 | Biology



### Ask PYQ Questions
Q: "give me kcet sample question on physics"
📚 kcet-2024-physics.pdf | Page 21 | PYQ Physics



### Kannada Translation
Language: English + Kannada (Hybrid)
→ Shows English answer + Kannada translation



## Troubleshooting

### Ollama not running?
```bash
ollama serve
ollama list
```

### Models not found?
```bash
ollama pull llama3.1
ollama pull sarvam-1
```

### PDFs not detected?
```bash
# Check PDFs are in correct folders
ls pdfs/ncert/biology/
ls pdfs/ncert/physics/

# Restart app
streamlit run app.py
```

### ChromaDB not created?
```bash
# First run will auto-create it
rm -rf chroma_db/
streamlit run app.py
```

### Docker can't connect to Ollama?
```bash
# Add host.docker.internal to /etc/docker/daemon.json
echo '{"hosts":["tcp://host.docker.internal:11434"]}' | sudo tee /etc/docker/daemon.json

# Restart Docker
sudo systemctl restart docker
```

## License

MIT License
## Author
Tharun K
AI Developer / Red Teamer 📍 Bengaluru, Karnataka, India
🔗 GitHub: @chandutharun


🎓 **Happy KCET Preparation!**