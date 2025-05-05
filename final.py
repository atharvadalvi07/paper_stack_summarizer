import os
import re
import nltk
import torch
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import PyPDF2
from concurrent.futures import ThreadPoolExecutor
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure nltk punkt is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logger.error(f"Error reading {pdf_path}: {e}")
    return text

def clean_text(text):
    text = re.sub(r"(Table of Contents|References|Bibliography).*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def process_pdf(file_path):
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    return os.path.basename(file_path), cleaned_text if len(cleaned_text.split()) > 100 else None

def load_papers_from_pdfs(directory):
    pdf_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    papers = {}
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_pdf, pdf_files), total=len(pdf_files), desc="Loading PDFs"))
    for result in results:
        if result and result[1]:
            papers[result[0]] = result[1]
    return papers

def build_knowledge_graph(papers):
    graph = nx.Graph()
    sentence_map = defaultdict(str)
    for paper, text in papers.items():
        doc = nlp(text)
        for sent in doc.sents:
            ents = [ent.text for ent in sent.ents if ent.label_ in {"PERSON", "ORG", "GPE", "EVENT", "WORK_OF_ART", "PRODUCT", "LOC", "LAW"}]
            for i in range(len(ents)):
                for j in range(i+1, len(ents)):
                    graph.add_edge(ents[i], ents[j])
                    sentence_map[(ents[i], ents[j])] = sent.text
    return graph, sentence_map

def generate_combined_summary(papers, summarizer, max_length=150, min_length=50):
    full_text = " ".join(papers.values())
    chunks = split_text_into_chunks(full_text, max_chunk_length=512)
    summaries = summarizer(chunks, max_length=max_length, min_length=min_length, do_sample=False)
    return " ".join([s['summary_text'] for s in summaries])

def split_text_into_chunks(text, max_chunk_length=512):
    sentences = nltk.sent_tokenize(text)
    chunks, current_chunk = [], []
    current_length = 0
    for sentence in sentences:
        if current_length + len(sentence) > max_chunk_length:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [sentence], len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def summarize_text(text, summarizer, max_length=80, min_length=30, chunk_size=512):
    chunks = split_text_into_chunks(text, chunk_size)
    summaries = summarizer(chunks, max_length=max_length, min_length=min_length, do_sample=False)
    return " ".join([s['summary_text'] for s in summaries])

def visualize_knowledge_graph(graph, output_file="results/graph.png", top_n=70):
    top_nodes = sorted(graph.degree, key=lambda x: x[1], reverse=True)[:top_n]
    subgraph = graph.subgraph([n for n, _ in top_nodes])

    centrality = nx.degree_centrality(subgraph)
    node_sizes = [1000 * centrality[n] for n in subgraph.nodes()]
    node_colors = [centrality[n] for n in subgraph.nodes()]

    pos = nx.spring_layout(subgraph, k=1.2, iterations=50)

    plt.figure(figsize=(14, 10))
    nx.draw_networkx_nodes(subgraph, pos, node_size=node_sizes, node_color=node_colors, cmap=plt.cm.Blues, alpha=0.8)
    nx.draw_networkx_edges(subgraph, pos, alpha=0.3)

    top_labels = {node: node for node, _ in top_nodes[:20]}
    nx.draw_networkx_labels(subgraph, pos, labels=top_labels, font_size=10, font_color='black')

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def main():
    start_time = time.time()
    os.makedirs("results", exist_ok=True)
    pdf_directory = "papers"
    logger.info("Loading papers from %s", pdf_directory)
    papers = load_papers_from_pdfs(pdf_directory)

    if len(papers) < 2:
        raise ValueError("Not enough valid papers. Ensure at least two non-empty PDFs are available.")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_name = "t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1, batch_size=8)

    logger.info("Generating individual summaries...")
    individual_summaries = {}
    # for name, text in papers.items():
    #     individual_summaries[name] = summarize_text(text, summarizer)
    for i, (name, text) in enumerate(papers.items()):
        individual_summaries[name] = summarize_text(text, summarizer)
        print(f"Summarizing Paper number {i + 1} - {((i + 1) / len(papers)) * 100:.2f}% Completed")


    logger.info("Generating combined summary...")
    combined_summary = generate_combined_summary(papers, summarizer)

    logger.info("Building knowledge graph...")
    graph, sentence_map = build_knowledge_graph(papers)
    visualize_knowledge_graph(graph)

    # Write individual summaries
    output_file = os.path.join("results", "summaries.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Individual Paper Summaries:\n\n")
        for name, summary in individual_summaries.items():
            f.write(f"--- {name} ---\n{summary}\n\n")

    # Write combined summary to separate file
    combined_file = os.path.join("results", "combined_summary.txt")
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("Combined Summary of All Papers:\n\n")
        f.write(combined_summary + "\n")

    logger.info("Summaries written to %s and %s", output_file, combined_file)
    logger.info("Total processing time: %.2f seconds", time.time() - start_time)

if __name__ == "__main__":
    main()
