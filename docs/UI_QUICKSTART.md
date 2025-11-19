# 🚀 Chat UI Quick Start

## Running the New Web Interface

The CLI has been replaced with a modern **Streamlit web UI** that looks like ChatGPT!

---

## 🏃 Quick Start (3 Steps)

### Step 1: Install Streamlit

```bash
cd /Users/madhan.dhandapani/Documents/schedule

# Option A: Using pip3
pip3 install streamlit plotly

# Option B: Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install streamlit plotly

# Option C: Install all requirements
pip3 install -r requirements.txt
```

### Step 2: Run the UI

```bash
streamlit run demo/chat_ui.py
```

### Step 3: Use the Chat Interface

The UI will open in your browser at `http://localhost:8501`

**Try these commands:**
- `therapist departed T001` - Run the full workflow
- `show audit` - View last workflow results
- `show mocks` - See what's mocked
- `help` - View all commands

---

## 🎨 UI Features

### Main Chat Interface
- **ChatGPT-like design** - Familiar and intuitive
- **Real-time responses** - Instant workflow execution
- **Rich formatting** - Tables, metrics, tabs for data

### Sidebar Features
- **Quick Commands** - One-click buttons
- **Statistics** - Success rates and workflow counts
- **System Status** - Mock mode indicator
- **Clear Chat** - Fresh start anytime

### Workflow Visualization
- **6 Tabs** - One for each workflow stage
  1. 🚨 Trigger - Affected appointments
  2. 🔍 Filtering - Provider qualification
  3. ⭐ Scoring - Rankings with breakdown
  4. 💬 Consent - Patient communication
  5. 📅 Booking - Final confirmation
  6. 📊 Audit - Complete log

### Data Display
- **Provider Scores** - Interactive tables
- **Metrics** - Key stats at a glance
- **JSON Export** - Download full results
- **Expandable Sections** - Details on demand

---

## 📸 What You'll See

```
┌────────────────────────────────────────────────────────┐
│  🏥 Therapist Replacement System                       │
│  Automated provider matching powered by AI agents      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  💬 Chat Messages                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 🤖 Assistant:                                    │ │
│  │ Hi! I'm the Therapist Replacement Assistant...  │ │
│  │                                                  │ │
│  │ Try: therapist departed T001                    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 👤 You:                                          │ │
│  │ therapist departed T001                          │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 🤖 Assistant:                                    │ │
│  │ ✅ Workflow Complete - SUCCESS!                  │ │
│  │                                                  │ │
│  │ [Trigger] [Filtering] [Scoring] [Consent] ...   │ │
│  │                                                  │ │
│  │ 🏆 Winner: Dr. Emily Ross - 75/150 points       │ │
│  │ 📅 Booked: Tuesday 11/20 at 10 AM               │ │
│  │                                                  │ │
│  │ [📥 Download JSON] [📋 Copy Session ID]         │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Type a command...                         [Send] │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘

Sidebar:
  📋 Quick Commands
    🚨 Therapist Departed T001
    📊 Audit | 🎭 Mocks
    ❓ Help
  
  📈 Statistics
    Workflows Run: 1
    Success Rate: 100%
  
  ⚙️ System Status
    ✅ Mock Mode Active
```

---

## 🎯 Demo Workflow

### Command: `therapist departed T001`

**What you'll see:**

1. **Stage 1: Trigger** 🚨
   - Found 1 affected appointment
   - Patient: Maria Rodriguez
   - Date: 2024-11-20 at 10:00 AM

2. **Stage 2: Filtering** 🔍
   - 3 candidates → 2 qualified
   - ❌ P003 eliminated (15 miles, exceeds limit)
   - ✅ P001, P004 qualified

3. **Stage 3: Scoring** ⭐
   - **Provider Scores Table:**
     | Rank | Provider | Total | Continuity | Specialty | Preference | Load | Time | Rating |
     |------|----------|-------|------------|-----------|------------|------|------|--------|
     | #1 | Dr. Emily Ross | 75/150 | 0/40 | 35/35 | 30/30 | 10/25 | 20/20 | EXCELLENT |
     | #2 | Dr. Michael Lee | 48/150 | 40/40 | 25/35 | 5/30 | 3/25 | 5/20 | ACCEPTABLE |

4. **Stage 4: Consent** 💬
   - Channel: SMS
   - Patient Response: YES
   - Response Time: 45 minutes

5. **Stage 5: Booking** 📅
   - ✅ Appointment Booked Successfully!
   - Patient: PAT001
   - Provider: P001 (Dr. Emily Ross)
   - Date: 2024-11-20 at 10:00 AM
   - Confirmation: CONF-2024-001

6. **Stage 6: Audit** 📊
   - Processed: 1 appointment
   - Rebooked: 1 appointment
   - Success Rate: 100%

---

## 🎭 Mock Mode Indicators

The UI clearly shows what's mocked:

```
⚙️ System Status
✅ Mock Mode Active
Using mocked services (no API costs)
```

**View Details:** Click "🎭 Mocks" to see:
- What's mocked (LLM, SMS, etc.)
- How to swap to real services
- Estimated effort for each swap

---

## 💡 Tips & Tricks

### Quick Actions
- Use **sidebar buttons** for fast command execution
- Click **tabs** to view different workflow stages
- Use **expandable sections** to see details

### Keyboard Shortcuts
- `Enter` - Send command
- `Ctrl+K` - Focus on input
- Refresh page to reset state

### Data Export
- **Download JSON** - Get full workflow results
- **Copy Session ID** - For debugging
- **Tables** - Can be copied/pasted to Excel

### Multiple Sessions
- Each chat session is independent
- Use "Clear Chat" to start fresh
- Workflow history is preserved (see stats)

---

## 🔧 Configuration

### Port Configuration

By default, Streamlit runs on port 8501. To change:

```bash
streamlit run demo/chat_ui.py --server.port 8502
```

### Theme Customization

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Browser Auto-Open

Disable auto-open:

```bash
streamlit run demo/chat_ui.py --server.headless true
```

---

## 🐛 Troubleshooting

### Issue: Module not found

```bash
# Solution: Install requirements
pip3 install -r requirements.txt
```

### Issue: Port already in use

```bash
# Solution: Use different port
streamlit run demo/chat_ui.py --server.port 8502
```

### Issue: Workflow not loading

```bash
# Solution: Check you're in the correct directory
cd /Users/madhan.dhandapani/Documents/schedule
streamlit run demo/chat_ui.py
```

### Issue: Styles not showing

```bash
# Solution: Clear Streamlit cache
streamlit cache clear
```

---

## 📊 Comparing CLI vs UI

| Feature | CLI (`demo/cli.py`) | UI (`demo/chat_ui.py`) |
|---------|-------------------|----------------------|
| **Interface** | Terminal text | Modern web UI |
| **Visualization** | Text output | Tables, charts, tabs |
| **Navigation** | Command-based | Buttons + chat |
| **Data Display** | JSON text | Formatted, interactive |
| **Export** | Copy-paste | Download buttons |
| **User Experience** | Developer-focused | User-friendly |
| **Learning Curve** | Low | Very low |
| **Demo Quality** | Good | Excellent |

**Verdict:** UI is better for demos, CLI is still available for automation/scripts.

---

## 🚀 Next Steps

### Immediate
1. ✅ Run the UI: `streamlit run demo/chat_ui.py`
2. ✅ Test the demo: `therapist departed T001`
3. ✅ Show to stakeholders

### Enhancements (Optional)
- Add charts (provider capacity, historical trends)
- Add file upload (for future PDF knowledge)
- Add authentication (for multi-user)
- Add dark mode toggle
- Add export to PDF reports

### Production
- Deploy to Streamlit Cloud (free hosting)
- Add SSL certificate
- Configure custom domain
- Enable authentication

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Project Docs:** `docs/QUICKSTART_DEMO.md`
- **Mocks Guide:** `docs/MOCKS.md`
- **Architecture:** `docs/ARCHITECTURE.md`

---

## 🎉 Ready to Go!

**Start the UI now:**

```bash
streamlit run demo/chat_ui.py
```

**Open browser:** http://localhost:8501

**Try command:** `therapist departed T001`

**Watch the magic! ✨**

---

**Built with:** Streamlit 1.30+ (Open Source)  
**Total Implementation Time:** 2-3 hours  
**Cost:** $0 (open source + mocked)

