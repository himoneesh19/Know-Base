# KnowBase - AI-Powered Searchable Knowledge Base

A local knowledge base application where you can ingest Markdown documents and query them using natural language. An LLM synthesizes answers grounded in your ingested documents.

## Features

✨ **Simple Document Ingestion** - Add Markdown files to your knowledge base with a single command
🤖 **AI-Powered Answers** - Ask natural language questions and get contextual answers
📚 **Multiple Documents** - Ingest and search across multiple documents
💻 **Local-First Design** - All data stored locally, no cloud dependencies
🎨 **Beautiful UI** - Clean, responsive web interface for easy interaction

## Tech Stack

- **Backend**: FastAPI (Python)
- **Document Management**: OpenKB
- **LLM**: OpenRouter API with Llama 3.3 70B model (free tier)
- **Frontend**: HTML/CSS/JavaScript (single page)
- **Database**: File-based knowledge base

## Project Structure

```
knowbase/
├── main.py              # FastAPI application with REST endpoints
├── kb_manager.py        # Knowledge base manager (OpenKB wrapper)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API keys)
├── .env.example         # Example environment file
├── README.md            # This file
├── knowledge_base/      # OpenKB data directory (auto-created)
├── sample_docs/         # Sample Markdown files
│   ├── doc1.md         # Climate Change document
│   └── doc2.md         # Machine Learning document
└── frontend/
    └── index.html       # Single-page web UI
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2. Clone or Download the Project

```bash
cd KnowBase
```

### 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Get OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up for a free account
3. Navigate to **Settings** → **Keys** or **API Keys**
4. Create a new API key
5. Copy the key

### 6. Configure Environment Variables

Open `.env` file in the project root and add your API key:

```env
OPENROUTER_API_KEY=your_actual_key_here
```

**Important**: Never commit `.env` to version control. The `.env` file is gitignored by default.

### 7. Run the Application

```bash
python main.py
```

Or alternatively:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### 8. Access the Web Interface

Open your browser and navigate to:

```
http://localhost:8000
```

## Usage

### Ingesting Documents

1. In the left sidebar under "📄 Ingest Document", either select a Markdown or PDF file from your computer or enter the path to your file
2. Example: `sample_docs/doc1.md` or full path like `C:\path\to\myfile.md`
3. Click the **Upload from Device** button for direct file upload, or **Upload by Path** to ingest from a file path
4. The document will be added to your knowledge base and appear in the documents list

### Querying the Knowledge Base

1. In the right panel, enter your question in the text input
2. Click **Ask** or press Enter
3. The AI will synthesize an answer based on your ingested documents
4. The answer appears in the styled card below

### Sample Queries to Try

Once you've ingested the sample documents, try these queries:

**Query 1: Climate & Technology**
```
What are the main causes of climate change and how does machine learning help address it?
```

**Query 2: Environmental Impact**
```
Describe the impacts of climate change and what steps should be taken to mitigate it.
```

**Query 3: AI Applications**
```
What are the practical applications of machine learning in healthcare and finance?
```

**Query 4: Cross-Domain**
```
How can machine learning techniques be applied to monitor and predict climate patterns?
```

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns: `{ "status": "ok" }`

### Ingest Document
- **POST** `/ingest`
  - Body: `{ "filepath": "path/to/file.md" }`
  - Returns: `{ "status": "success", "message": "..." }`

### Query Knowledge Base
- **POST** `/query`
  - Body: `{ "question": "Your question here?" }`
  - Returns: `{ "answer": "The AI's answer..." }`

### List Documents
- **GET** `/documents`
  - Returns: `{ "documents": [...], "count": N }`

### Frontend
- **GET** `/`
  - Returns: The HTML interface

## Directory Structure After First Run

After running the application, the directory structure will expand:

```
knowbase/
├── main.py
├── kb_manager.py
├── requirements.txt
├── .env                          # With your API key
├── .env.example
├── knowledge_base/               # Created automatically
│   ├── .openkb/
│   │   ├── config.yaml          # OpenKB configuration
│   │   └── documents.json       # Metadata about ingested documents
│   └── wiki/                    # Ingested documents stored here
│       ├── doc1.md
│       ├── doc2.md
│       └── ... (your added documents)
├── sample_docs/
│   ├── doc1.md
│   └── doc2.md
└── frontend/
    └── index.html
```

## Adding Your Own Documents

1. Create or export your Markdown documents
2. Place them in the `sample_docs/` folder or anywhere on your system
3. Use the web interface to ingest them by providing the file path
4. Once ingested, you can query across all your documents

### Markdown Format Tips

- Use standard Markdown syntax
- Include headers (`#`, `##`, `###`) for structure
- Use bullet points and numbered lists
- Include relevant details and context
- Longer, well-structured documents work best

## Troubleshooting

### "OPENROUTER_API_KEY environment variable not set"
- Make sure you've edited the `.env` file with your actual API key
- Ensure the `.env` file is in the project root directory
- Restart the application after updating `.env`

### "Cannot connect to backend"
- Make sure the server is running: `python main.py`
- Check that it's running on `http://localhost:8000`
- Try accessing `http://localhost:8000/health` directly

### "File not found"
- Use relative paths from the project root: `sample_docs/doc1.md`
- Or provide the full absolute path to the file

### Slow responses
- Check your internet connection (API calls are made to OpenRouter)
- The free tier may have rate limiting - wait a moment between queries
- Longer documents will take slightly longer to process

## Performance Notes

- **First Query**: May take 10-30 seconds as the model processes your documents
- **Subsequent Queries**: Usually 5-15 seconds
- **Large Documents**: Multiple large documents (>50KB each) may take longer
- **Free Tier**: OpenRouter's free tier has fair usage limits

## Security Considerations

- Keep your `.env` file secure and never share your API key
- The `.env` file is automatically ignored in `.gitignore`
- This application is designed for local use
- All document data is stored locally

## Limitations

- OpenRouter free tier may have usage limits
- Large knowledge bases (100+ MB) may need optimization
- The AI's answers are based only on ingested documents
- Complex queries work best with well-organized documents

## Future Enhancements

- [ ] Vector embeddings for semantic search
- [ ] Document preprocessing and chunking
- [ ] Search history
- [ ] Export answers as PDF
- [ ] Multi-user support
- [ ] Document versioning
- [ ] Advanced query filters

## License

MIT License - Feel free to use, modify, and distribute.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Verify your OpenRouter API key is valid
4. Check that the backend is running with `python main.py`

## Getting Help

- **OpenRouter API Issues**: Visit [OpenRouter Support](https://openrouter.ai)
- **FastAPI Documentation**: [FastAPI Docs](https://fastapi.tiangolo.com)
- **OpenKB Documentation**: Check OpenKB GitHub repository

---

**Version**: 1.0.0  
**Last Updated**: 2026  
**Built with ❤️ using Python, FastAPI, and AI**
