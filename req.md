Here's your converted, well-structured English prompt:

---

**Act as an expert Full-Stack AI Engineer. I have an existing codebase that I need you to thoroughly analyze and understand first before making any changes.**

## Phase 1: Code Analysis & Audit
- Read through the entire codebase and explain what each part does.
- Identify all current functions and verify which ones are actually working vs. broken.
- List every external API being used in the code.

## Phase 2: API Setup Guide
- For each API found, tell me exactly:
  - What the API does
  - Where to get it for **FREE** (direct links to sign up / get API key)
  - Exactly **WHERE in the code** to place the API key/credentials so it works
- If any API is paid-only, suggest a **free alternative** that does the same job.

## Phase 3: New Feature — Full Computer Control
Add a feature that gives the AI **complete control over the user's computer** (Windows/macOS/Linux). It should:

1. **Execute ANY terminal/command-line command** the user speaks or types
2. **File & Folder Operations:**
   - Create folders anywhere (e.g., "create a project folder on Desktop")
   - Create, read, write, move, delete files
3. **Application Control:**
   - Open any installed application by name
   - Perform tasks inside applications (e.g., send a WhatsApp message, play a song, search something in browser)
4. **Command Logging:**
   - Every command given by the user must be saved in **JSON format**
   - Stored inside a dedicated folder on the Desktop (e.g., `Desktop/AI_Command_Logs/`)
   - Each chat session gets its own JSON file, structured like:
   ```json
   {
     "session_id": "unique_id",
     "timestamp": "2025-01-15T10:30:00Z",
     "command": "open notepad and write hello world",
     "status": "success/failed",
     "output": "details of what happened"
   }
   ```

## Phase 4: Self-Sufficiency
- You have **full terminal access** — install any library, package, or tool needed via pip, npm, brew, or any package manager.
- Use **whatever programming language** is best suited for each part of the task.
- **Everything must be fully working** — no placeholders, no mock functions, no "TODO" comments.

## Important Rules
- Do NOT assume anything — if you're unsure about the OS or environment, write cross-platform code or detect the OS at runtime.
- All API keys should be loaded from a `.env` file (create one with placeholder values).
- Include clear setup instructions (what to install, what to run, in what order).
- Test every feature mentally before presenting the final code — if something won't work, fix it first.

---

**Copy-paste this prompt as-is into your AI coding tool (like Cursor, Claude, ChatGPT, etc.) and it will give you a proper, working result.**