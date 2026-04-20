"""
ANAY Desktop backend entrypoint.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import json
import warnings

# pydub warns when ffmpeg is not on PATH (we often send webm straight to Deepgram)
warnings.filterwarnings("ignore", message=".*ffmpeg.*", category=RuntimeWarning, module="pydub.utils")
warnings.filterwarnings("ignore", message=".*ffprobe.*", category=RuntimeWarning, module="pydub.utils")
from typing import Any, Dict, Optional

import os
import uvicorn
from dotenv import load_dotenv

# Load env variables BEFORE importing local modules that rely on them
# Point it explicitly to backend/.env since cwd is the root project folder
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from concurrent.futures import ThreadPoolExecutor
from agent import agent_runner
from llm_router import chat_completion, get_messages_with_context, clean_llm_text, normalize_messages, extract_manual_tool_calls
from memory import memory_store, save_message, extract_and_save_facts
from pc_control import execute_tool, get_system_stats
from scheduler import reminder_scheduler
from settings import runtime_settings
from tools_schema import TOOLS
from vision import vision_service
from voice import get_voice_status
from wake_word import get_wake_word_status
from websocket_manager import WebSocketManager

executor = ThreadPoolExecutor(max_workers=4)

os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler("anay_backend.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

manager = WebSocketManager()


async def lifespan(app_: FastAPI):
    # Startup
    logger.info("ANAY Desktop backend starting")
    metrics_task = asyncio.create_task(manager.broadcast_metrics())
    reminder_scheduler.register_callback(lambda item: manager.broadcast_notification(item["task"]))    
    scheduler_task = asyncio.create_task(reminder_scheduler.start())
    
    yield
    
    # Shutdown
    logger.info("ANAY Desktop backend shutting down")
    metrics_task.cancel()
    scheduler_task.cancel()
    try:
        await asyncio.gather(metrics_task, scheduler_task, return_exceptions=True)
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="ANAY Desktop API",
    version="2.0.0",
    description="Local AI desktop agent backend for chat, tools, memory and automation.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "auto"
    preferred_model: Optional[str] = None
    offline: bool = False


class ToolRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class RememberRequest(BaseModel):
    content: str
    kind: str = "note"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    title: str
    objective: str


class VisionRequest(BaseModel):
    prompt: str = "Describe what is on the screen and identify actionable UI elements."


class SettingsRequest(BaseModel):
    default_model: Optional[str] = None
    offline_mode: Optional[bool] = None
    voice_mode: Optional[str] = None
    tts_enabled: Optional[bool] = None






@app.get("/")
async def root():
    return {
        "status": "running",
        "app": "ANAY Desktop",
        "mode": "local-agent",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": memory_store.list_tasks(limit=1)[0]["updated_at"]
        if memory_store.list_tasks(limit=1)
        else None,
    }


@app.get("/api/desktop/state")
async def desktop_state():
    return {
        "system": get_system_stats(),
        "voice": get_voice_status(),
        "wake_word": get_wake_word_status(),
        "models": {
            "default": runtime_settings.default_model,
            "available": ["auto", "groq", "minimax", "gemini", "ollama"],
        },
        "runtime_settings": runtime_settings.get(),
        "memory": {
            "recent": memory_store.list_memories(limit=5),
            "reminders": memory_store.list_reminders(limit=5),
        },
        "tasks": agent_runner.list_tasks(),
    }


@app.get("/api/tools")
async def list_tools():
    return {"tools": TOOLS}


@app.post("/api/tools/execute")
async def run_tool(payload: ToolRequest):
    try:
        result = execute_tool(payload.tool, payload.arguments)
        return {"tool": payload.tool, "result": result}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


async def run_tool_async(name: str, args: dict) -> Any:
    """Run tool in thread pool so it doesn't block the API"""
    loop = asyncio.get_event_loop()
    try:
        # Run in executor so FastAPI doesn't timeout
        result = await loop.run_in_executor(executor, lambda: execute_tool(name, args))
        return result
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return {"error": str(e)}

@app.post("/api/chat")
async def chat(payload: ChatRequest):
    try:
        # Broadcast the incoming user message to the desktop UI
        await manager.broadcast_chat_event(role="user", content=payload.message)
        
        # 1. Save user msg to memory
        save_message("user", payload.message)

        # 2. Build messages with context
        messages = get_messages_with_context(payload.message)
        
        # 3. Model selection logic
        pref = payload.preferred_model or payload.model or runtime_settings.default_model
        logger.info(f"Chat request - Message: {payload.message[:50]}... | Model: {pref}")

        # Format tools for OpenAI
        tool_specs = [
            {"type": "function", "function": t} for t in TOOLS
        ]

        # 4. LLM Call
        msg_obj, model_used, reasoning = chat_completion(
            messages, 
            tools=tool_specs, 
            preferred_model=pref
        )

        if model_used == "all_failed":
            reply = "Yaar sab models thak gaye hain abhi, 1 minute baad try karo 🙄"
            await manager.broadcast_chat_event(role="assistant", content=reply)
            return {"reply": reply, "text": reply, "model_used": "none", "tool_calls": [], "reasoning": ""}

        assistant_text = msg_obj.content or ""
        tool_calls_executed = []

        # 5. Handle Tool Calls
        tool_calls = []
        if hasattr(msg_obj, "tool_calls") and msg_obj.tool_calls:
            tool_calls = msg_obj.tool_calls
        elif hasattr(msg_obj, "additional_kwargs") and "tool_calls" in msg_obj.additional_kwargs:
            # Some providers like OpenRouter might put tool_calls here
            tool_calls = msg_obj.additional_kwargs["tool_calls"]
            
        if tool_calls:
            # Normalize msg_obj to dict before appending to history
            normalized_msg = normalize_messages([msg_obj])[0]
            messages.append(normalized_msg)
            
            for call in tool_calls:
                # Handle both object-style (OpenAI) and dict-style (some OpenRouter) calls
                if hasattr(call, "function"):
                    name = call.function.name
                    raw_args = call.function.arguments
                else:
                    name = call.get("function", {}).get("name")
                    raw_args = call.get("function", {}).get("arguments", "{}")
                
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except:
                    args = {}
                
                logger.info(f"Executing tool: {name}({args})")
                result = await run_tool_async(name, args)
                
                tool_calls_executed.append({
                    "name": name,
                    "arguments": args,
                    "result": result
                })
                
                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })

            # 6. Follow-up LLM Call after tool execution
            reasoning_followup = ""
            follow_up_obj, _, reasoning_followup = chat_completion(messages, preferred_model=model_used)
            if follow_up_obj:
                assistant_text = follow_up_obj.content or assistant_text
                if reasoning_followup:
                    reasoning = (reasoning + "\n\n" + reasoning_followup).strip()
        else:
            # Logic 6: Check for manual tool calls in text (fail-safe)
            manual_calls = extract_manual_tool_calls(assistant_text)
            if manual_calls:
                logger.info(f"Manual tool calls extracted: {[c['name'] for c in manual_calls]}")
                for call in manual_calls:
                    name = call["name"]
                    args = call["arguments"]
                    logger.info(f"Executing manual tool: {name}({args})")
                    result = await run_tool_async(name, args)
                    tool_calls_executed.append({"name": name, "arguments": args, "result": result, "manual": True})
                
                # Check for follow-up after manual execution
                follow_up_obj, _, _ = chat_completion(messages + [{"role": "assistant", "content": assistant_text}], preferred_model=model_used)
                if follow_up_obj:
                    assistant_text = follow_up_obj.content or assistant_text
            else:
                # If no tool calls were detected at all, log raw response
                logger.info(f"No tool calls detected. Raw assistant response: {assistant_text[:200]}...")

        # 7. Final polishing
        final_text = clean_llm_text(assistant_text)
        save_message("assistant", final_text)
        extract_and_save_facts(payload.message, final_text)

        # Broadcast response
        await manager.broadcast_chat_event(
            role="assistant", 
            content=final_text,
            meta={
                "provider": model_used.split("/")[0] if "/" in model_used else model_used,
                "model": model_used,
                "tool_calls": tool_calls_executed,
                "reasoning": reasoning
            }
        )
        
        return {
            "reply": final_text,
            "text": final_text,
            "provider": model_used.split("/")[0] if "/" in model_used else model_used,
            "model": model_used,
            "tool_calls": tool_calls_executed,
            "reasoning": reasoning
        }

    except Exception as e:
        logger.exception("Error in /api/chat endpoint")
        return {"reply": f"Error: {str(e)}", "text": f"Error: {str(e)}", "tool_calls": []}


@app.get("/api/settings")
async def get_settings():
    return runtime_settings.get()


@app.post("/api/settings")
async def update_settings(payload: SettingsRequest):
    patch = payload.model_dump(exclude_none=True)
    return runtime_settings.update(patch)


@app.get("/api/memory")
async def get_memory():
    from memory import memory_store
    return {
        "items": memory_store.list_memories(limit=30),
        "reminders": memory_store.list_reminders(limit=20),
    }


class ContactRequest(BaseModel):
    name: str
    phone: str

@app.get("/api/contacts")
async def list_contacts():
    import sqlite3
    from memory import DB_PATH
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT name, phone, updated_at FROM contacts ORDER BY name ASC").fetchall()
        conn.close()
        return [{"name": r[0], "phone": r[1], "updated_at": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts")
async def add_contact(payload: ContactRequest):
    from memory import save_contact
    try:
        save_contact(payload.name, payload.phone)
        return {"status": "success", "message": f"Contact {payload.name} saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/contacts/{name}")
async def delete_contact(name: str):
    import sqlite3
    from memory import DB_PATH
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM contacts WHERE name = ?", (name.lower().strip(),))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Contact {name} deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/remember")
async def remember(payload: RememberRequest):
    from memory import memory_store
    record = memory_store.remember(payload.content, kind=payload.kind, metadata=payload.metadata)
    return {"item": record}


@app.delete("/api/memory/{memory_id}")
async def forget(memory_id: str):
    deleted = memory_store.forget(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True}


@app.post("/api/vision/inspect")
async def inspect_screen(payload: VisionRequest):
    return vision_service.inspect_screen(payload.prompt)


@app.get("/api/agent/tasks")
async def list_tasks():
    return {"tasks": agent_runner.list_tasks()}


@app.post("/api/agent/tasks")
async def create_task(payload: TaskRequest):
    task = agent_runner.create_task(payload.title, payload.objective)
    return {"task": task}


@app.post("/api/agent/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    task = agent_runner.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": agent_runner.cancel_task(task_id)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.handle_voice_session(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.error("WebSocket error: %s", exc)
        manager.disconnect(websocket)


# Run via CLI: uvicorn main:app --reload
pass
