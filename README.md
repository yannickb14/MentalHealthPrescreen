Watch our [official submission](https://www.youtube.com/watch?v=C8vKlanHUTI)

# McHacks x Backboard.io Hackathon Challenge!

## 🧠 NeuroFlow
**Automated Clinical Intake & SOAP Note Generation**

> *Built for McHacks 2026*

NeuroFlow is an intelligent conversational agent designed to combat physician burnout. It conducts dynamic, clinical interviews with patients in the waiting room and generates structured **SOAP notes** (Subjective, Objective, Assessment, Plan) for the doctor instantly. Check out [```client_notes```](https://github.com/yannickb14/MentalHealthPrescreen/tree/main/clinical_notes) for some example outputs.

---

### 🚨 The Problem
Doctors spend **2 hours on data entry for every 1 hour of patient care**.
This "desktop medicine" leads to:
* **Physician Burnout:** Doctors become data clerks.
* **Shorter Visits:** Less time for actual diagnosis.
* **Data Loss:** Critical patient details are lost in hurried manual notes.

**NeuroFlow solves this** by offloading the history-taking process to an asynchronous AI agent that knows *exactly* when it has enough information to stop.

---

### ✨ Key Features
* **🗣️ Dynamic Interviewing:** Doesn't just follow a script. If a patient says "migraine," it asks about light sensitivity.
* **🧠 Context-Aware Memory:** Remembers previous turns to avoid repetitive questioning.
* **🛑 Smart Termination Logic:** Uses semantic analysis to determine when the medical history is complete—preventing infinite chat loops.
* **📝 Instant SOAP Notes:** Automatically compiles informal chat logs into professional medical documentation (JSON/Markdown).

---

### 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/) (Async UI)
* **Backend:** Python 3.12 and `asyncio`
* **AI Orchestration:** [Backboard SDK](https://github.com/...) (LLM State Management)
* **Architecture:** Event-Driven Asynchronous Loop
