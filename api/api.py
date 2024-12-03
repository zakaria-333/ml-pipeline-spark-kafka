import pandas as pd
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
from typing import Generator, List, Dict, Any, AsyncGenerator

app = FastAPI()

INTERVAL = 20
BATCH_SIZE = 200
CSV_FILE = "co2_processed.csv"

def read_csv(file_path: str) -> Generator[Dict[str, Any], None, None]:
    try:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            yield row.to_dict()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier CSV non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du CSV: {str(e)}")

async def emit_lines(file_path: str) -> AsyncGenerator[str, None]:
    csv_generator = read_csv(file_path)
    while True:
        batch: List[Dict[str, Any]] = []
        for _ in range(BATCH_SIZE):
            try:
                row = next(csv_generator)
                batch.append(row)
            except StopIteration:
                break
        
        if not batch:
            break
        
        yield json.dumps(batch) + "\n"
        await asyncio.sleep(INTERVAL)

@app.get("/stream")
async def stream_csv():
    headers = {
        'Content-Type': 'application/x-ndjson',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    return StreamingResponse(
        emit_lines(CSV_FILE),
        headers=headers,
        media_type="application/x-ndjson"
    )