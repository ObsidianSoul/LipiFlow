import azure.functions as func
import logging
import os
import base64
import io
import json
import PyPDF2
import uuid
import tempfile
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI

# Authorisation
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# SYSTEM PROMPT & HELPER FUNCTIONS
UNIFIED_SYSTEM_PROMPT = """
You are LipiFlow's Synthesis Core. Analyze the provided content (handwritten notes, document text, or audio transcript).
You MUST return a valid JSON object with EXACTLY these five keys:
{
    "latex": "Convert the underlying text, logic, and mathematical formulas into clean, structured LaTeX code.",
    "flashcards": "Create 3-5 study flashcards in Q&A format.",
    "important_topics": "Extract the most important exam-relevant concepts as concise bullet points.",
    "summary": "Summarize the entire content in 5 concise bullet points.",
    "logical_topics": "Divide the content into logical topics. For each topic provide a Title and 3-4 bullet point explanations."
}
Return ONLY the raw JSON object. Do not include markdown formatting like ```json.
"""

def clean_and_parse_json(raw_text):
    """Safely extracts JSON from GPT response, handling accidental markdown wrappers."""
    clean_text = raw_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:-3].strip()
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:-3].strip()
    return json.loads(clean_text)

def save_to_dashboard(user_id, item_type, content_dict):
    """Packages the AI output into a JSON document and pushes it to Cosmos DB."""
    try:
        conn_str = os.getenv("COSMOS_CONNECTION_STRING")
        if not conn_str:
            logging.error("CRITICAL: Cosmos DB connection string is missing!")
            return

        cosmos_client = CosmosClient.from_connection_string(conn_str)
        database = cosmos_client.get_database_client("LipiFlowDB")
        container = database.get_container_client("DashboardData")

        document = {
            "id": str(uuid.uuid4()),  
            "userId": user_id,        
            "type": item_type,        
            "content": content_dict,  # Now saving the structured dictionary directly
            "createdAt": datetime.utcnow().isoformat() 
        }
        container.upsert_item(document)
        logging.info(f"Successfully saved {item_type} to Cosmos DB!")
        
    except Exception as e:
        logging.error(f"Failed to save to Cosmos DB: {str(e)}")


# ROUTE 1:Image to Unified Notes
@app.route(route="process_notes")
def process_notes(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('LipiFlow: Processing Image upload...')
    try:
        file = req.files.get('image')
        if not file:
            return func.HttpResponse("Error: Upload an image using key 'image'.", status_code=400)

        base64_image = base64.b64encode(file.read()).decode('utf-8')
        client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version="2024-02-15-preview", azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": UNIFIED_SYSTEM_PROMPT},
                {"role": "user", "content": [{"type": "text", "text": "Process these notes."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
            ],
            max_tokens=2500
        )
        
        ai_data = clean_and_parse_json(response.choices[0].message.content)
        
        cosmos_payload = ai_data.copy()
        if "latex" in cosmos_payload:
            del cosmos_payload["latex"]
            
        save_to_dashboard("ObsidianSoul", "ImageNotes", cosmos_payload)
        
        return func.HttpResponse(json.dumps(ai_data), status_code=200, mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


# ROUTE 2: PDF to Unified Notes
@app.route(route="process_document")
def process_document(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('LipiFlow: Processing PDF upload...')
    try:
        pdf_file = req.files.get('document')
        if not pdf_file:
            return func.HttpResponse("Error: Upload PDF using key 'document'.", status_code=400)

        extracted_text = "".join([page.extract_text() for page in PyPDF2.PdfReader(io.BytesIO(pdf_file.read())).pages if page.extract_text()])
        if not extracted_text.strip():
            return func.HttpResponse("Error: No text found in PDF.", status_code=400)

        client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version="2024-02-15-preview", azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": UNIFIED_SYSTEM_PROMPT},
                {"role": "user", "content": f"Process this document:\n{extracted_text[:15000]}"}
            ],
            max_tokens=2500
        )
        
        ai_data = clean_and_parse_json(response.choices[0].message.content)

        cosmos_payload = ai_data.copy()
        if "latex" in cosmos_payload:
            del cosmos_payload["latex"]

        save_to_dashboard("ObsidianSoul", "PDFNotes", cosmos_payload)

        return func.HttpResponse(json.dumps(ai_data), status_code=200, mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


# ROUTE 3:WAV to Unified Notes
@app.route(route="process_media")
def process_media(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('LipiFlow: Processing Audio upload...')
    try:
        media_file = req.files.get('media')
        if not media_file:
            return func.HttpResponse("Error: Upload audio using key 'media'.", status_code=400)

        media_bytes = media_file.read()

        # 1. Store heavy audio file in Blob Storage (Claim Check)
        blob_service = BlobServiceClient.from_connection_string(os.getenv("BLOB_CONNECTION_STRING"))
        try: blob_service.create_container("notes")
        except: pass
        
        blob_client = blob_service.get_blob_client(container="notes", blob=f"{str(uuid.uuid4())}_{media_file.filename.lower()}")
        blob_client.upload_blob(media_bytes, overwrite=True)

        # 2. Extract Transcript
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_media:
            temp_media.write(media_bytes)
            temp_audio_path = temp_media.name

        # the file used to be kept open since it needed to listen ot the audio before processing it
        audio_config = speechsdk.audio.AudioConfig(filename=temp_audio_path)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speechsdk.SpeechConfig(subscription=os.getenv("SPEECH_KEY"), region=os.getenv("SPEECH_REGION")),
            audio_config=audio_config
        )
        
        result = speech_recognizer.recognize_once_async().get()
        
        # upar wala issue contd.
        del speech_recognizer
        del audio_config

        # Safely deleting the file without letting Windows crash the API
        try:
            os.remove(temp_audio_path)
        except Exception as e:
            logging.warning(f"Windows locked the temp file, bypassing cleanup: {str(e)}")

        if result.reason != speechsdk.ResultReason.RecognizedSpeech:
            return func.HttpResponse("Error: Could not transcribe audio.", status_code=400)

        client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version="2024-02-15-preview", azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": UNIFIED_SYSTEM_PROMPT},
                {"role": "user", "content": f"Process this transcript:\n{result.text}"}
            ],
            max_tokens=2500
        )

        ai_data = clean_and_parse_json(response.choices[0].message.content)
        
        ai_data["transcript"] = result.text
        ai_data["audio_url"] = blob_client.url

        save_to_dashboard("ObsidianSoul", "AudioNotes", ai_data)
        return func.HttpResponse(json.dumps(ai_data), status_code=200, mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)