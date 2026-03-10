# LipiFlow: Serverless Backend API

This repository contains the backend infrastructure for **LipiFlow**, an AI-powered academic synthesis engine. Built entirely on an event-driven Azure cloud architecture, this API instantly ingests unstructured study materials (Images, PDFs, Audio) and outputs structured, exam-ready JSON payloads.

## Cloud Tech Stack
* **Compute:** Azure Functions (Serverless Python API)
* **AI Core:** Azure OpenAI (GPT-4o)
* **Audio Processing:** Azure Speech SDK (Speech-to-Text)
* **Metadata Database:** Azure Cosmos DB (NoSQL)
* **Heavy Media Vault:** Azure Blob Storage

## Architectural Highlights
* **The "Claim-Check" Pattern:** To bypass Cosmos DB document size limits, heavy `.wav` lecture files are routed directly to Azure Blob Storage. The API then stores only the lightweight retrieval URL alongside the AI metadata.
* **Unified Data Normalization:** A single GPT-4o "Master Prompt" normalizes chaotic multimodal inputs into a strict, predictable JSON format containing LaTeX equations, Q&A flashcards, and logical summaries.
* **In-Memory Processing:** PDFs and Images are processed directly in RAM to eliminate slow disk-write bottlenecks during serverless cold starts.

## How to Run Locally

### 1. Prerequisites
* Python 3.10+
* [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)

### 2. Environment Variables
Create a `local.settings.json` file in the root directory. **(Note: This file MUST be included in your `.gitignore` to prevent secret leakage).**

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_CONNECTION_STRING": "your_cosmos_string",
    "BLOB_CONNECTION_STRING": "your_blob_string",
    "OPENAI_ENDPOINT": "your_openai_endpoint",
    "OPENAI_API_KEY": "your_openai_key",
    "SPEECH_KEY": "your_speech_key",
    "SPEECH_REGION": "your_speech_region"
  }
}
# Create and activate virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the local Azure Function server
func start