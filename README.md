# LLMotive : Summarization of a Stack of Papers using LLMs (SSPL)

## Overview

This project is made for the class CS 4366 Senior Capstone Project.
Team Members (Group 7) - Atharva Dalvi, Khushi Nankani, Arianna Matienzo, Olu Ogunnirian

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

2. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy Language Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the Flask App**
   ```bash
   python implementation.py
   ```

5. **Access the Web Interface**
   Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

---

## Docker Deployment

If you prefer deploying using Docker, follow the steps below.

### 1. Build the Docker image

In the root directory of the project, run the following command to build the Docker image:

```bash
docker build -t paper-summarization-app .
```

### 2. Run the Docker container

Start the Docker container by running:

```bash
docker run -p 5000:5000 paper-summarization-app
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

## API Endpoints

### 1. `/upload`

* **Method**: POST
* **Description**: Upload PDF files for processing.
* **Request**:

  * Files: PDF files to be uploaded.
* **Response**: A message indicating that the files have been received.

### 2. `/start_summary`

* **Method**: POST
* **Description**: Start the summarization and knowledge graph generation process.
* **Request**:

  * Files: PDF files to be processed.
* **Response**: A message indicating the process has started.

### 3. `/check_progress`

* **Method**: GET
* **Description**: Check the current progress of the summarization task.
* **Response**: The current processing progress (e.g., percentage of PDFs processed).

---


## Future Enhancements
- Interactive graph visualisation (e.g., with PyVis).
- Summarisation model upgrade (e.g., `bart-large-cnn`).
- User authentication for file uploads.

---
