import os
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import tempfile
import zipfile
import uvicorn
import argparse
import shlex

# Initialize FastAPI app
app = FastAPI()

# Custom output directory inside the container (persistent within container)
OUTPUT_DIR = "/app/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create an argument parser for handling dynamic port, SSL key, and SSL cert input
def parse_arguments():
    parser = argparse.ArgumentParser(description="FastAPI server with dynamic port and SSL")
    
    # Arguments for port, SSL key, and SSL cert
    parser.add_argument("--port", type=int, default=2222, help="Port to run the FastAPI server on (default: 2222)")
    parser.add_argument("--ssl_key", type=str, help="Path to SSL key file")
    parser.add_argument("--ssl_cert", type=str, help="Path to SSL certificate file")
    
    return parser.parse_args()

@app.post("/")
async def create_tts(request: dict, background_tasks: BackgroundTasks):
    # Extract arguments from the request
    text = request.get("text", "")
    voice = request.get("voice", "en-US-ChristopherNeural")
    word_by_word = request.get("word_by_word", "False")

    # Use custom directory for storing files
    audio_file = os.path.join(OUTPUT_DIR, "output.mp3")
    srt_file = os.path.join(OUTPUT_DIR, "output.srt")
    zip_file = os.path.join(OUTPUT_DIR, "tts_files.zip")

    # Safely quote the text to prevent issues in the shell command
    safe_text = shlex.quote(text)
    
    # Command to generate TTS using edge-tts
    command = f'edge-tts --text "{safe_text}" --voice "{voice}" --write-media "{audio_file}" --write-subtitles "{srt_file}"'
    if word_by_word.lower() == "true":
        command += " --word-by-word"

    try:
        # Run edge-tts to generate the audio and subtitle files
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

        # Create a ZIP file containing the .mp3 and .srt files
        with zipfile.ZipFile(zip_file, "w") as zipf:
            zipf.write(audio_file, "output.mp3")
            zipf.write(srt_file, "output.srt")

        # Cleanup function to delete the files after the download
        def cleanup_files():
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(srt_file):
                os.remove(srt_file)
            if os.path.exists(zip_file):
                os.remove(zip_file)

        # Add cleanup task to background after the response is sent
        background_tasks.add_task(cleanup_files)
        # Return ZIP file for download
        return FileResponse(zip_file, media_type="application/zip", filename="tts_files.zip")

    except subprocess.CalledProcessError as e:
        print(f"Error while running command: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Error during file generation: {e.stderr}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

# Function to run FastAPI with SSL
def run_fastapi_with_ssl(port, ssl_key_path, ssl_cert_path):
    uvicorn.run(
        "server:app", 
        host="0.0.0.0", 
        port=port, 
        ssl_keyfile=ssl_key_path, 
        ssl_certfile=ssl_cert_path
    )

# Function to run FastAPI without SSL
def run_fastapi(port):
    uvicorn.run(
        "server:app", 
        host="0.0.0.0", 
        port=port
    )

if __name__ == "__main__":
    args = parse_arguments()  # Parse command-line arguments for port, ssl_key, and ssl_cert
    port = args.port  # Retrieve the port from arguments
    
    # Check if SSL arguments are provided
    if args.ssl_key and args.ssl_cert:
        ssl_key_path = args.ssl_key
        ssl_cert_path = args.ssl_cert
        run_fastapi_with_ssl(port, ssl_key_path, ssl_cert_path)  # Run with SSL
    else:
        run_fastapi(port)  # Run without SSL
