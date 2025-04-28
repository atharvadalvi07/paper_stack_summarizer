# Summarization of a Stack of Papers using LLMs (SSPL)

## Overview
This project provides a web-based system to upload, summarize, and visualize a collection of research papers.

The system:
- Generates individual summaries for each uploaded paper.
- Generates a combined, coherent summary of all papers.
- Constructs a knowledge graph based on key entities extracted from the documents.
- Visualizes the knowledge graph to highlight important relationships.

Built with **Flask**, **Transformers**, **NetworkX**, and **spaCy**.

---

## Project Structure

```
/papers              # Uploaded PDF files
/results             # Output summaries and knowledge graph
/static              # Static assets (CSS, JS)
templates/main.html  # Front-end HTML
implementation.py    # Flask web server
final.py             # Main summarization and knowledge graph pipeline
requirements.txt     # Python dependencies
README.md            # Project documentation
```

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Mac/Linux
   venv\\Scripts\\activate   # For Windows
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy Language Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the Flask App**
   ```bash
   python implementation.py
   ```

6. **Access the Web Interface**
   Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

---

## Key Features
- **Upload PDFs**: Upload one or more research papers in PDF format.
- **Summarization**:
  - Generate individual summaries for each paper.
  - Generate one combined overall summary.
- **Knowledge Graph**:
  - Build and visualize relationships between key entities across documents.
  - Save as a clean, clear graph image.

---

## Output Files
- `results/summaries.txt` : Individual paper summaries.
- `results/combined_summary.txt` : Combined single summary.
- `results/graph.png` : Knowledge graph visualization.

---

## Requirements
See `requirements.txt`.

---

## Future Enhancements
- Interactive graph visualization (e.g., with PyVis).
- Summarization model upgrade (e.g., `bart-large-cnn`).
- User authentication for file uploads.

---

## License
MIT License © 2025

```
