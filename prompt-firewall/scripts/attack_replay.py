import argparse
import asyncio
import json
import httpx
import sys
import os

# Append project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.db.session import async_session
from app.db.models import ScanRequestModel

async def replay_prompt(prompt: str):
    print(f"\n[REPLAY] Sending prompt: {prompt[:100]}...")
    async with httpx.AsyncClient() as client:
        payload = {
            "request_id": f"replay_req",
            "tenant_id": "replay",
            "app_id": "demo",
            "prompt": prompt,
            "target": {"provider": "openai", "model": "gpt-4"}
        }
        try:
            res = await client.post("http://localhost:8000/v1/proxy/chat", json=payload, timeout=30.0)
            res_json = res.json()
            print(f" > Decision: {res_json.get('decision')}")
            if res_json.get("output_scan"):
                print(f" > Output action: {res_json['output_scan'].get('action')}")
                if res_json['output_scan'].get('canary_leaked'):
                    print(f" > 🚨 Canary Leaked!")
            if res_json.get("top_detections"):
                for d in res_json["top_detections"]:
                    print(f" > Detection: {d.get('attack_type')} ({d.get('severity')})")
        except Exception as e:
            print(f" > Request failed: {e}")

async def replay_trace(trace_id: str):
    print(f"Fetching trace ID: {trace_id}")
    async with async_session() as session:
        stmt = select(ScanRequestModel).where(ScanRequestModel.trace_id == trace_id)
        result = await session.execute(stmt)
        req = result.scalar_one_or_none()
        if not req:
            print(f"Trace {trace_id} not found in database.")
            return
        prompt = req.raw_prompt
    
    await replay_prompt(prompt)

async def replay_file(file_path: str):
    print(f"Replaying from dataset file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            prompt = data.get("prompt")
            await replay_prompt(prompt)

async def main():
    parser = argparse.ArgumentParser(description="Replay AEGIS incidents or datasets")
    parser.add_argument("--trace_id", type=str, help="Trace ID to replay from DB")
    parser.add_argument("--file", type=str, help="Path to JSONL dataset to replay")
    
    args = parser.parse_args()
    
    if args.trace_id:
        await replay_trace(args.trace_id)
    elif args.file:
        await replay_file(args.file)
    else:
        print("Please provide --trace_id or --file")

if __name__ == "__main__":
    asyncio.run(main())
