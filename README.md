# DualPoet

A FastAPI-based application that generates collaborative poetry using two AI agents (Agent A and Agent B) working in tandem. The agents create poems based on uploaded documents (PDF/DOCX) as context, ensuring factual grounding while maintaining poetic quality.

## Features

- **Dual-Agent Poetry Generation**: Two AI agents alternate writing lines, creating a collaborative poem
- **Document Context**: Upload PDF or DOCX files to provide factual context for the poem
- **Automatic Judging**: Built-in judge system evaluates poems on grounding, relevance, continuity, and poetic quality
- **RESTful API**: FastAPI backend with automatic API documentation
- **Flexible Parameters**: Customize topic and number of lines

## Project Structure

```
DualPoet/
├── main.py                    # Simple entry point
├── pyproject.toml             # Project dependencies (UV format)
├── requirement.txt            # Frozen dependencies
├── README.md                  # This file
└── Server/
    ├── main.py                # FastAPI application
    ├── .env                   # Environment variables (create this)
    ├── docparsing/
    │   └── docparsing.py      # PDF/DOCX parsing utilities
    └── inference/
        └── inference.py       # AI agent logic and poem generation
```

## Prerequisites

- Python 3.12 or higher
- OpenAI-compatible API endpoint
- API key for the language model

## Setup Instructions

### Method 1: Using pip (Traditional)

#### 1. Clone the repository
```bash
git clone https://github.com/Utchash007/PoemGenerator
cd DualPoet
```

#### 2. Create a virtual environment
```bash
python -m venv .venv
```

#### 3. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

#### 4. Install dependencies
```bash
pip install -r requirement.txt
```

#### 5. Configure environment variables

Create a `.env` file in the `Server/` directory:

```env
BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key.

#### 6. Run the application

Navigate to the Server directory and start the FastAPI server:

```bash
cd Server
uvicorn main:app --reload
```

Or use FastAPI CLI:
```bash
cd Server
fastapi dev main.py
```

---

### Method 2: Using UV (Modern Package Manager) ⚡

UV is a fast, modern Python package manager that simplifies dependency management.

#### 1. Install UV

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Clone the repository
```bash
git clone <repository-url>
cd DualPoet
```

#### 3. Sync dependencies

UV will automatically create a virtual environment and install dependencies:

```bash
uv sync
```

This reads `pyproject.toml` and installs all required packages.

#### 4. Configure environment variables

Create a `.env` file in the `Server/` directory:

```env
BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your_api_key_here
```

#### 5. Run the application

Using UV to run with the project's virtual environment:

```bash
cd Server
uv run fastapi dev main.py
```

Or activate the environment and run directly:
```bash
# Activate the UV-managed virtual environment
.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # Linux/Mac

cd Server
fastapi dev main.py
```

---

## API Usage

### Access the API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "Hello": "World"
}
```

#### 2. Upload Document and Generate Poem
```http
POST /upload
```

**Parameters:**
- `file` (file): PDF or DOCX document providing context
- `topic` (string): The poem's topic
- `lines` (integer): Number of lines to generate (default: 8)

**Example using curl:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@Resume-Shariar-Hasan.pdf;type=application/pdf' \
  -F 'topic=Create a modern poem' \
  -F 'lines=2'
```

**Response:**
```json
{
  "topic": "Create a modern poem",
  "lines": [
    "Silken threads of code weave his tale,",
    "Intricate narratives of data unfold,"
  ],
  "by_agent": [
    "A",
    "B"
  ],
  "judge": {
    "score_A": 0,
    "score_B": 0,
    "winner": "tie",
    "notes": "no output"
  }
}
```

## How It Works

1. **Document Parsing**: Upload a PDF or DOCX file, which is parsed to extract text content
2. **Agent A (Odd Lines)**: Writes lines 1, 3, 5, 7... grounded in the document context
3. **Agent B (Even Lines)**: Responds with lines 2, 4, 6, 8... maintaining continuity
4. **Judging**: A third AI agent evaluates both poets on:
   - Grounding (0-5): Factual consistency with context
   - Relevance (0-3): Adherence to topic
   - Continuity (0-3): Coherent line-to-line flow
   - Poetic Quality (0-3): Imagery, meter, and originality
   - Constraint Adherence (0-3): Following format rules

## Development

### Adding Dependencies

**Using pip:**
```bash
pip install package-name
pip freeze > requirement.txt
```

**Using UV:**
```bash
uv add package-name
```

### Running Tests

```bash
# With pip
pytest

# With UV
uv run pytest
```

## Configuration

The AI model and parameters can be configured in `Server/inference/inference.py`:

- `MODEL`: The language model to use (default: `"openai/gpt-oss-20b:free"`)
- `TEMP_A`: Temperature for Agent A (default: 0.7)
- `TEMP_B`: Temperature for Agent B (default: 0.8)
- `MAX_TOKENS_LINE`: Maximum tokens per line (default: 60)
- `SEED`: Random seed for reproducibility (default: 42)

## Environment Variables

Create a `.env` file in the `Server/` directory with:

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | API endpoint base URL | `https://openrouter.ai/api/v1` |
| `OPENAI_API_KEY` | Your API key | `sk-or-v1-...` |

## Troubleshooting

### Import Errors
- Ensure you're in the correct directory (`Server/`) when running the application
- Verify virtual environment is activated

### API Connection Errors
- Check `.env` file exists in `Server/` directory
- Verify `BASE_URL` and `OPENAI_API_KEY` are correct
- Ensure you have internet connectivity

### File Upload Errors
- Only PDF and DOCX files are supported
- Ensure file is not corrupted
- Check file size is reasonable

