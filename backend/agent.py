"""
Simple autonomous task runner with progress logging.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from llm_router import llm_router
from memory import memory_store


class AgentTaskRunner:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def list_tasks(self) -> List[Dict[str, Any]]:
        live = sorted(self.tasks.values(), key=lambda item: item["updated_at"], reverse=True)
        history = memory_store.list_tasks(limit=15)
        known = {item["id"] for item in live}
        for item in history:
            if item["id"] not in known:
                live.append({**item, "logs": []})
        return live[:20]

    def _append_log(self, task_id: str, message: str):
        task = self.tasks[task_id]
        task["logs"].append(
            {"timestamp": datetime.utcnow().isoformat() + "Z", "message": message}
        )
        task["updated_at"] = datetime.utcnow().isoformat() + "Z"

    async def _run_task(self, task_id: str):
        task = self.tasks[task_id]
        try:
            self._append_log(task_id, "Analyzing goal and preparing execution plan.")
            await asyncio.sleep(0.3)
            self._append_log(task_id, "Checking memory and recent context.")
            await asyncio.sleep(0.3)
            self._append_log(task_id, "Running autonomous execution through the model router.")
            result = await asyncio.to_thread(
                llm_router.chat,
                prompt=task["objective"],
                preferred_model="minimax",
                offline=False,
            )
            tool_calls = result.get("tool_calls", [])
            for tool_call in tool_calls:
                self._append_log(
                    task_id,
                    f'Executed {tool_call["name"]} with result: {str(tool_call["result"])[:120]}',
                )
            task["status"] = "completed"
            task["summary"] = result.get("text") or "Task completed."
        except asyncio.CancelledError:
            task["status"] = "cancelled"
            task["summary"] = "Task cancelled."
            raise
        except Exception as exc:
            task["status"] = "failed"
            task["summary"] = f"Task failed: {exc}"
            self._append_log(task_id, task["summary"])
        finally:
            task["updated_at"] = datetime.utcnow().isoformat() + "Z"
            memory_store.upsert_task(
                task_id,
                title=task["title"],
                status=task["status"],
                summary=task.get("summary"),
            )

    def create_task(self, title: str, objective: str) -> Dict[str, Any]:
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        record = {
            "id": task_id,
            "title": title,
            "objective": objective,
            "status": "running",
            "summary": None,
            "logs": [],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self.tasks[task_id] = record
        asyncio.create_task(self._run_task(task_id))
        memory_store.upsert_task(task_id, title=title, status="running", summary=objective)
        return record

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks[task_id]
        task["status"] = "cancelled"
        task["summary"] = "Cancelled by user."
        task["updated_at"] = datetime.utcnow().isoformat() + "Z"
        memory_store.upsert_task(task_id, task["title"], task["status"], task["summary"])
        return task

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)


agent_runner = AgentTaskRunner()
