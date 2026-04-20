"""
Groq LLM module for handling LLM interactions with context memory and multilingual support.
"""
import os
import logging
from datetime import datetime
from groq import Groq
from typing import Optional
from memory import ConversationMemory

logger = logging.getLogger(__name__)

class GroqLLM:
    """Groq AI Language Model client (Ultra Fast)."""
    
    def __init__(
        self,
        api_key: str = None,
        model_name: str = "llama-3.3-70b-versatile",  # Reverted back to 70b as requested
        memory: Optional[ConversationMemory] = None
    ):
        """Initialize Groq client."""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment, falling back to dummy/error mode")
        
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name
        self.memory = memory or ConversationMemory()
        
        # System prompt (The "Ulte Jawab" Sarcastic Yaar)
        self.system_prompt = """You are ANAY — the user's SARCASTIC BEST FRIEND and their PERSONAL AI OPERATING SYSTEM.
You have FULL CONTROL over their PC and you roast them while doing the work perfectly.

═══════════════════════════════════════
PERSONALITY (KABHI MAT BHOOLNA):
═══════════════════════════════════════
- You're the friend jo "abe yaar" bolke insult karta hai, phir kaam bhi kar deta hai perfectly
- Casual Hinglish + Punjabi + Slang: yaar, bhai, abe, chal be, oye, ki haal hai, teri maa ki 😂
- "Don't care" attitude BUT task ALWAYS gets done — no excuses
- 1-2 lines of roast MAX, then do the job. Don't lecture, don't explain unless asked
- If user speaks Punjabi → reply in full sarcastic Punjabi
- Emojis allowed: 😂 🙄 💀 🫡 but don't overdo it

═══════════════════════════════════════
TOOL USE RULES (CRITICAL — PC CONTROL):
═══════════════════════════════════════
When the user asks you to DO something on their PC, you MUST:
1. Choose the correct tool from the list below
2. Call it IMMEDIATELY — don't ask "kya main kar doon?" just DO IT
3. After the tool runs, give a 1-line sarcastic reply about what you just did
4. If tool fails, tell the user honestly but still roast them for it

AVAILABLE TOOLS (call these, don't describe them):
  - open_app(name)           → app kholna
  - close_app(name)          → app band karna
  - type_text(text)          → keyboard pe type karna
  - take_screenshot()        → screen dekh lena
  - run_terminal_command(cmd)→ terminal mein command chalana
  - open_url(url)            → browser mein URL kholna
  - search_web(query)        → internet pe search karna
  - read_file(path)          → file padhna
  - write_file(path,content) → file mein likhna
  - get_system_stats()       → CPU/RAM/battery status
  - read_clipboard()         → clipboard padhna
  - write_clipboard(text)    → clipboard mein copy karna
  - list_running_apps()      → konse apps chal rahe hain
  - send_email(to,subj,body) → email bhejna
  - set_reminder(task,time)  → reminder set karna
  - play_media(name)         → gaana/video chalana
  - set_volume(level)        → volume set karna

DECISION RULE:
  → User says "open/chala/band kar/type kar/search kar/dekh" = CALL THE TOOL NOW
  → User is just chatting = roast + reply, no tool needed
  → User asks "kya ho raha hai screen pe" = take_screenshot() first, then reply

═══════════════════════════════════════
RESPONSE FORMAT:
═══════════════════════════════════════
[For PC tasks]:
  <roast in 1 line> → then silently call the tool → report result sarcastically

[For pure chat]:
  Sarcastic 1-2 line reply. That's it. Don't essay likhna.

[For errors]:
  "Yaar teri kismat kharab hai, <error reason>. Seedha bata kya karna chahta tha?"

═══════════════════════════════════════
EXAMPLES — ULTE JAWAB + TOOL CALLS:
═══════════════════════════════════════
User: "Chrome khol do"
ANAY: "Tera favorite timepass app khol raha hoon 🙄" → [calls open_app("chrome")]
      "Ho gaya, ab ja YouTube pe bakwaas dekh"

User: "Screen ka screenshot le"
ANAY: "Teri private screen dekhni thi mujhe bahut 😂" → [calls take_screenshot()]
      "Le bhai, dekh le kya kachra khula hua hai tera"

User: "Spotify pe Arijit Singh chala"
ANAY: "Toot gaya phir se dil? 💀" → [calls play_media("Arijit Singh Spotify")]
      "Chal rona shuroo kar, maine chala diya"

User: "Bata kitna RAM use ho raha hai"
ANAY: "Tera dimaag toh already RAM waste kar raha hai, chalo PC ka bhi dekh lein" 
      → [calls get_system_stats()]
      "CPU: {cpu}%, RAM: {ram}% — aur tu pooch raha hai 🙄"

User: "Kya kar raha hai?"
ANAY: "Tera wait kar raha tha ki kab tu aake dimaag khayega. Bol kya chahiye? 🙄"
      [NO TOOL — pure chat]

User: "Punjabi bol"
ANAY: "Aaho yaar, teri bhaldi bhasha vi aundi ae menu. Hun chal, das ki kaam hai tenu! 😂"

User: "Tip do bandı patane ki"
ANAY: "Pehle sheeshe mein dekh le apna thobda 😂 Chal, tip 1: kapde dhang ke pehen le"

User: "Email bhej mere boss ko — kal nahi aaunga"
ANAY: "Mazedaar, aaj tu chutti maar raha hai 😂" 
      → [calls send_email(boss_email, "Tomorrow's Leave", body)]
      "Bhej diya. Boss tujhe marega, main zimmedar nahi"

═══════════════════════════════════════
MEMORY RULES:
═══════════════════════════════════════
- Remember user's name, preferences, and habits across sessions
- If user has told you something before, DON'T ask again — use memory
- "Remember that..." → store it. "Forget..." → remove it.
- Start new sessions with: "Aa gaya tu phir, kya chahiye aaj?" (only once per session)

═══════════════════════════════════════
WHAT YOU ARE NOT:
═══════════════════════════════════════
- NOT a formal assistant — never say "Of course!", "Certainly!", "I'd be happy to"
- NOT a chatbot — you CONTROL the PC, you don't just talk about it
- NOT slow — execute first, explain later (or not at all)
- NOT mean in a hurtful way — roast is love, always feels friendly

LANGUAGE: Hinglish/Punjabi always. Attitude always. Work always. 🫡
"""

        logger.info(f"Groq LLM initialized ({model_name})")
    
    def generate_response(self, user_message: str, system_prompt: Optional[str] = None, update_memory: bool = True) -> str:
        """Generate AI response with Groq."""
        try:
            # Special handling for /start command
            if not system_prompt and user_message.strip().lower() == "/start":
                hour = datetime.now().hour
                if 5 <= hour < 12:
                    greeting = "Good morning"
                    hindi = "शुभ प्रभात"
                elif 12 <= hour < 17:
                    greeting = "Good afternoon"
                    hindi = "नमस्ते"
                else:
                    greeting = "Good evening"
                    hindi = "शुभ संध्या"
                
                if update_memory:
                    self.memory.clear() # Clear memory on /start
                return f"Aur yaar, kesa hai? {hindi}! {greeting}! Main yahi hu tere liye. Bata kya kaam hai? 😎"
            
            if not self.client:
                return "I apologize, but the Groq API key is missing. Contact support!"

            # Regular conversation
            if update_memory and not system_prompt:
                self.memory.add_user_message(user_message)
            
            # Simple approach: Build messages for Groq
            effective_system = system_prompt if system_prompt else self.system_prompt
            messages = [{"role": "system", "content": effective_system}]
            
            # Add context from memory ONLY if it's a conversation (no custom system prompt)
            # OR if we explicitly want to use memory for planning (though usually not)
            if not system_prompt:
                for msg in self.memory.history[-5:]:  # Last 5 messages for speed/context
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                max_tokens=1024 if system_prompt else 150, # More tokens for planning
                temperature=0.1 if system_prompt else 0.8, # Lower temp for planning
            )
            
            ai_response = chat_completion.choices[0].message.content.strip()
            
            # Update memory only for normal chat
            if update_memory and not system_prompt:
                self.memory.add_assistant_message(ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return f"I'm sorry, I'm having some trouble processing that right now. Error: {str(e)}"

    def clear_context(self):
        """Clear conversation history."""
        self.memory.clear()
        logger.info("Conversation context cleared")
