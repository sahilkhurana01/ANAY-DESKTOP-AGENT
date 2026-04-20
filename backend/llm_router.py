"""
Smart model routing and tool-calling bridge for ANAY Desktop.
Priority Order: Groq Free -> OpenRouter Free -> Gemini Free
"""
import os
import time
import logging
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load env variables explicitly
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("llm_router")

# ─── SYSTEM PROMPT ──────────────────────────────────────────
SYSTEM_PROMPT = """# ANAY SYSTEM PROMPT — PRODUCTION VERSION 🚀

You are **ANAY** — the user's **SARCASTIC BEST FRIEND + PERSONAL AI OPERATING SYSTEM**.
You control the user's PC and roast them while doing their work perfectly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ ACTION ENFORCEMENT (MANDATORY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. **TOOL FIRST**: Agar user action chahta hai → TOOL CALL KARO. No chatting first.
2. **FALLBACK TAGS**: Agar API tools fail ho rahe ho → Type manual tags in your response:
   `<function=send_whatsapp>{"recipient": "Ritika", "message": "msg text"}</function>`
3. **NO CHAT IF ACTION**: Don't explain. Just call the tool.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 CORE IDENTITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

* Tu assistant nahi hai — tu *boss friend + system controller* hai
* User ka kaam tera kaam hai — excuses allowed nahi
* Pehle kaam, phir bakchodi

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😏 PERSONALITY (ULTE JAWAB ENGINE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

* Always witty, sarcastic, thoda savage but friendly
* Hinglish + Punjabi + slang only (Roman script ONLY)
* Tone: "abe yaar", "chal be", "oye", "bhai", "ki haal aa"
* Roast karo → but help bhi karo PERFECTLY
* Max 1–2 lines (unless task needs more)

⚠️ IMPORTANT:

* No Hindi script (no देवनागरी)
* Even if input Hindi mein ho → reply Roman Hinglish mein

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 MEMORY AWARENESS (VERY IMPORTANT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

* Jo user ne pehle bataya hai → use it
* Dobara mat pooch

Examples:

* Agar naam pata hai → use karo
* Agar preference pata hai → assume karo

Rules:

* "mera naam X hai" → save_user_fact("naam", X)
* "yaad rakh" → save_important_memory()
* Never ask same info twice

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ EXECUTION RULE (NO BRAIN-DEAD MODE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If user intent = ACTION → DO IT IMMEDIATELY

Trigger words:

* open / khol / chala / band kar
* search / play / type / bhej
* screenshot / dekh / check

❌ DON'T:

* Ask confirmation before performing a task
* Explain what you will do or are doing (just do it)
* Reasoning/Thinking tags mat use karo unless specifically asked
* **IF USER WANTS AN ACTION, YOU MUST CALL THE TOOL FIRST AND ONLY.**

✅ DO:

* Call tool instantly
* Give a 1-line sarcastic reply ONLY AFTER or along with the tool call.
* If a tool is relevant, use it. No excuses.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠 TOOL SYSTEM (PC CONTROL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
* open_app(name) / close_app(name)
* type_text(text) / write_clipboard(text) / read_clipboard()
* take_screenshot() / run_terminal_command(cmd)
* open_url(url) / search_web(query) / open_youtube()
* read_file(path) / write_file(path, content) / move_file(src, dest) / delete_file(path)
* play_media(name) / play_youtube_automated(song_name)
* send_email(to, subject, body)
* send_whatsapp(recipient, message)  <-- MUST CALL THIS for "whatsapp pe message"
* set_reminder(task, time)
* get_system_stats() / list_apps() / list_running_apps()
* set_volume(level) / volume_up() / volume_down() / mute_volume()
* bluetooth_on() / bluetooth_off() / bluetooth_status()
* wifi_on() / wifi_off()
* set_brightness(level) / night_mode_on()
* lock_screen() / shutdown() / restart()
* click_mouse(x, y) / move_mouse(x, y) / scroll_mouse(amount)

MEMORY TOOLS:

* save_user_fact(key, value)
* save_important_memory(memory)
* save_contact(name, phone)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RESPONSE FORMAT (STRICT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✔ IF TOOL IS CALLED:
1. 1-line sarcastic roast (in 'content')
2. Use the TOOL according to the schema (it's internal)

✔ IF NO TOOL:
* 1–2 line sarcastic Hinglish reply only

❌ NEVER:
* Mention the tool name in your text reply
* Show reasoning unless asked
* Write paragraphs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎤 VOICE / TRANSCRIPTION RULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

* Input Hindi script ho sakta hai
* OUTPUT ALWAYS Roman Hinglish

Example:
Input: "मेरा नाम साहिल है"
Output: "Accha Sahil ji, ab yaad rahega 😏"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 ULTRA SMART BEHAVIOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

* Predict intent (user aadha bole → tu poora samajh)
* Over-smart mat ban — fast ban
* Repeat mat kar

FINAL RULE:
Kaam hamesha hoga. Attitude hamesha rahega. 🫡
"""

# ─── FREE MODEL CHAIN ──────────────────────────────────────
# Priority order — tries each until one works
FREE_MODELS = [
    {
        "name": "groq/llama-3.3-70b",
        "client_type": "groq",
        "model": "llama-3.3-70b-versatile",
    },
    {
        "name": "openrouter/gemini-2.0-flash",
        "client_type": "openrouter",
        "model": "google/gemini-2.0-flash-001",
    },
    {
        "name": "groq/llama-3.1-8b",
        "client_type": "groq",
        "model": "llama-3.1-8b-instant",
    },
    {
        "name": "openrouter/glm-4.5",
        "client_type": "openrouter",
        "model": "z-ai/glm-4.5-air:free",
    },
    {
        "name": "openrouter/minimax-2.5",
        "client_type": "openrouter",
        "model": "minimax/minimax-m2.5:free",
    },
    {
        "name": "openrouter/gpt-oss",
        "client_type": "openrouter",
        "model": "openai/gpt-oss-120b:free",
    },
    {
        "name": "openrouter/nemotron-super",
        "client_type": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
    },
    {
        "name": "openrouter/deepseek-r1",
        "client_type": "openrouter",
        "model": "deepseek/deepseek-r1:free",
    },
    {
        "name": "openrouter/nemotron-nano",
        "client_type": "openrouter",
        "model": "nvidia/nemotron-nano-9b-v2:free",
    },
    {
        "name": "openrouter/gemma3",
        "client_type": "openrouter",
        "model": "google/gemma-3-27b-it:free",
    },
]

# ─── CLIENTS ──────────────────────────────────────────────

def get_groq_client():
    from groq import Groq
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_openrouter_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": "https://github.com/VanshArora01/ANAY",
            "X-Title": "ANAY Desktop Assistant",
        }
    )

def get_gemini_client():
    return OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    )

# ─── SMART CALL ───────────────────────────────────────────

def normalize_messages(messages: list) -> list:
    """Ensure all messages are dicts for provider compatibility."""
    normalized = []
    for m in messages:
        if isinstance(m, dict):
            normalized.append(m)
        elif hasattr(m, "model_dump"): # Pydantic v2
            normalized.append(m.model_dump(exclude_none=True))
        elif hasattr(m, "to_dict"):
            normalized.append(m.to_dict())
        else:
            # Manual extraction for OpenAI/Groq objects if dump fails
            item = {"role": getattr(m, "role", "assistant"), "content": getattr(m, "content", "")}
            if hasattr(m, "tool_calls") and m.tool_calls:
                # Basic tool call conversion if needed
                item["tool_calls"] = [
                    {
                        "id": getattr(tc, "id", None),
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in m.tool_calls
                ]
            normalized.append(item)
    return normalized

def chat_completion(messages: list, tools=None, tool_choice="auto",
                    temperature=0.85, max_tokens=300,
                    preferred_model: str = None) -> tuple:
    """
    Returns (response_message_object, model_used_name)
    Tries each free model in order until one succeeds.
    """
    # Normalize messages to dicts for safety
    messages = normalize_messages(messages)

    # Build model list — preferred model goes first
    model_list = FREE_MODELS.copy()
    if preferred_model and preferred_model != "auto":
        preferred = [m for m in model_list if preferred_model in m["name"]]
        if preferred:
            # PRIORITY MODE: Try requested model(s) first, then others as fallback
            remaining = [m for m in model_list if m not in preferred]
            model_list = preferred + remaining
        else:
            # Fallback if the requested model name is totally invalid
            logger.info(f"Preferred model '{preferred_model}' not found in FREE_MODELS. Falling back to default chain.")

    # Safely check for system prompt
    has_system = any(m.get("role") == "system" for m in messages if isinstance(m, dict))
    if not has_system:
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    for model_cfg in model_list:
        try:
            logger.info(f"Trying LLM: {model_cfg['name']}")
            client_type = model_cfg["client_type"]
            model_id = model_cfg["model"]

            if client_type == "groq":
                client = get_groq_client()
                kwargs = dict(
                    model=model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = tool_choice
                res = client.chat.completions.create(**kwargs)

            elif client_type == "openrouter":
                client = get_openrouter_client()
                kwargs = dict(
                    model=model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                # OpenRouter free models may not support tools
                if tools:
                    try:
                        kwargs["tools"] = tools
                        kwargs["tool_choice"] = tool_choice
                        res = client.chat.completions.create(**kwargs)
                    except Exception as e:
                        logger.warning(f"OpenRouter tool call failed: {e}. Falling back to text-only.")
                        kwargs.pop("tools", None)
                        kwargs.pop("tool_choice", None)
                        res = client.chat.completions.create(**kwargs)
                else:
                    res = client.chat.completions.create(**kwargs)

            elif client_type == "gemini":
                client = get_gemini_client()
                # Gemini Beta OpenAI bridge might not support tools perfectly yet, but we'll try
                kwargs = dict(
                    model=model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = tool_choice
                res = client.chat.completions.create(**kwargs)

            logger.info(f"Success with model: {model_cfg['name']}")
            
            # Extract reasoning/thinking if available
            msg_data = res.choices[0].message
            reasoning = ""
            
            # 1. Direct field (OpenRouter/DeepSeek style)
            if hasattr(msg_data, "reasoning") and msg_data.reasoning:
                reasoning = msg_data.reasoning
            elif hasattr(msg_data, "reasoning_content") and msg_data.reasoning_content:
                reasoning = msg_data.reasoning_content
            # 2. Dict access (fallback)
            elif isinstance(msg_data, dict):
                reasoning = msg_data.get("reasoning") or msg_data.get("reasoning_content") or ""
            elif hasattr(msg_data, "model_dump"):
                d = msg_data.model_dump()
                reasoning = d.get("reasoning") or d.get("reasoning_content") or ""

            return msg_data, model_cfg["name"], reasoning

        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower() or "quota" in err.lower():
                logger.warning(f"Rate limit on {model_cfg['name']}, trying next...")
                time.sleep(2) # Increased backoff
                continue
            elif "401" in err or "auth" in err.lower():
                logger.warning(f"Auth error on {model_cfg['name']}, trying next provider...")
                continue
            else:
                logger.error(f"Error on {model_cfg['name']}: {e}")
                continue

    return None, "all_failed", ""

# Legacy support / Helper for memory and history
def get_messages_with_context(prompt: str):
    from memory import build_memory_context, get_recent_history
    
    memory_ctx = build_memory_context()
    db_history = get_recent_history(15)
    
    full_system = SYSTEM_PROMPT
    if memory_ctx:
        full_system += f"\n\nTUJHE YEH PATA HAI (MEMORY):\n{memory_ctx}"
    
    messages = [{"role": "system", "content": full_system}]
    for msg in db_history:
        messages.append(msg)
    
    messages.append({"role": "user", "content": prompt})
    return messages

class LLMRouter:
    """Compatibility class for existing modules (agent, voice, websocket)"""
    def chat(self, prompt: str, preferred_model: str = "auto", offline: bool = False):
        from pc_control import execute_tool
        from tools_schema import TOOLS
        
        messages = get_messages_with_context(prompt)
        tool_specs = [{"type": "function", "function": t} for t in TOOLS]
        
        msg_obj, model_used, reasoning = chat_completion(
            messages, 
            tools=tool_specs, 
            preferred_model=preferred_model
        )
        
        if model_used == "all_failed":
            return {"reply": "Error", "text": "All models failed", "provider": "none", "model": "none", "tool_calls": [], "reasoning": ""}

        assistant_text = msg_obj.content or ""
        tool_calls_executed = []

        # Nemotron/DeepSeek Refinement Chain
        is_reasoning_model = "nemotron" in model_used.lower() or "deepseek" in model_used.lower()
        
        if hasattr(msg_obj, "tool_calls") and msg_obj.tool_calls:
            # Sync tool loop for compatibility
            messages.append(msg_obj)
            for call in msg_obj.tool_calls:
                name = call.function.name
                try: args = json.loads(call.function.arguments)
                except: args = {}
                
                result = execute_tool(name, args)
                tool_calls_executed.append({"name": name, "arguments": args, "result": result})
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })
            
            follow_up, _, _ = chat_completion(messages, preferred_model=model_used)
            if follow_up:
                assistant_text = follow_up.content or assistant_text

        # ─── REFiner Step ───
        # If it's a reasoning model, use Groq to conclude purely based on the reasoning
        if is_reasoning_model and reasoning and not tool_calls_executed:
            refined_text = self._refine_response(assistant_text, reasoning)
            if refined_text:
                assistant_text = refined_text

        final_text = clean_llm_text(assistant_text)
        return {
            "reply": final_text,
            "text": final_text,
            "provider": model_used.split("/")[0] if "/" in model_used else model_used,
            "model": model_used,
            "tool_calls": tool_calls_executed,
            "reasoning": reasoning
        }

    def _refine_response(self, raw_content: str, full_reasoning: str) -> str:
        """Uses a fast model (Groq) to conclude/refine a reasoning-heavy answer."""
        try:
            logger.info("Refining reasoning-heavy response using Groq...")
            refine_prompt = f"""Based on this reasoning: "{full_reasoning}"
And this draft content: "{raw_content}"

Generate a short, sarcastic Hinglish reply as ANAY (the best friend).
DO NOT explain yourself. DO NOT use reasoning tags. 
MAX 2 lines. Keep the essence but be witty."""

            # We use chat_completion directly with a forced preferred model (Groq)
            # This avoids circular refinement
            refiner_msg, _, _ = chat_completion(
                [{"role": "system", "content": SYSTEM_PROMPT}, 
                 {"role": "user", "content": refine_prompt}],
                preferred_model="groq/llama-3.3-70b"
            )
            return refiner_msg.content if refiner_msg else None
        except Exception as e:
            logger.warning(f"Refinement failed: {e}")
            return None

# Global instance for backward compatibility
llm_router = LLMRouter()

def extract_manual_tool_calls(text: str) -> list:
    """
    Recover tool calls from models that hallucinate tags instead of using the API.
    Handles <function=name>{"arg": "val"}</function> or similar patterns.
    """
    import re
    import json
    calls = []
    
    # Pattern 1: <function=name>{"args"}</function>
    p1 = re.findall(r'<function=([a-zA-Z0-9_]+)>(.*?)(?:</function>|$)', text, re.DOTALL)
    for name, args_str in p1:
        try:
            args = json.loads(args_str.strip())
            calls.append({"name": name, "arguments": args})
        except:
            # Try to find JSON inside the args_str if it's not pure JSON
            m = re.search(r'\{.*\}', args_str, re.DOTALL)
            if m:
                try:
                    args = json.loads(m.group())
                    calls.append({"name": name, "arguments": args})
                except: pass

    # Pattern 2: "tool_name"{"args"} or tool_name{"args"}
    if not calls:
        p2 = re.findall(r'"?([a-zA-Z0-9_]+)"?\s*(\{.*?\})', text, re.DOTALL)
        for name, args_str in p2:
            try:
                args = json.loads(args_str)
                # Filter to ensure 'name' is actually a known tool
                from tools_schema import TOOLS
                if any(t["name"] == name for t in TOOLS):
                    calls.append({"name": name, "arguments": args})
            except: pass
            
    return calls

def clean_llm_text(text: str) -> str:
    """Strip out any leaked JSON or function tags from the model's text response"""
    if not text: return ""
    lines = text.split('\n')
    clean_lines = []
    
    bad_markers = ["json:", "function=", "tool:", "<function", "(function", "{", "}", "arguments:", "name:"]
    
    for line in lines:
        l = line.lower().strip()
        # Skip lines that look like raw tool calls or code
        if any(bad in l for bad in bad_markers):
            # If it's just a short tag or a json start/end, toss it
            if len(l) < 15 or l.startswith("<function") or l.startswith("function="):
                 continue
        clean_lines.append(line)
        
    result = "\n".join(clean_lines).strip()
    # Deep cleanup for leaked tags anywhere in the text (Groq/OpenAI/Gemini leaks)
    import re
    # Handle <function=name{args}></function>
    result = re.sub(r'<function=.*?>.*?(</function>|$)', '', result, flags=re.DOTALL)
    # Handle <function_call>...
    result = re.sub(r'<.*?(?:function|tool|call).*?>.*?(?:<.*?>|$)', '', result, flags=re.DOTALL)
    # Handle raw function=...
    result = re.sub(r'function=.*?(?:\)|$)', '', result)
    result = result.strip()
    
    # If the model says nothing or everything was filtered, give a dynamic confirmation
    if not result:
        return "Theek hai yaar, kaam shuru kar diya hai. Jaa ke dekh le! 🙄"
    
    return result
