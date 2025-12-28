# 🏗️ XER Assistant Setup Guide

Complete guide to set up your custom LLM assistant for XER file analysis.

---

## 📋 Prerequisites

### 1. Python Installation
```bash
python --version  # Should be 3.8 or higher
```

### 2. Install Required Packages
```bash
pip install anthropic streamlit pathlib
```

### 3. Get Anthropic API Key
1. Go to https://console.anthropic.com
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new key
5. Copy the key (starts with `sk-ant-...`)

---

## 🚀 Quick Start

### Step 1: Configure API Key

Open `xer_assistant.py` and replace:
```python
ANTHROPIC_API_KEY = "YOUR_API_KEY_HERE"
```

With your actual key:
```python
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxxxx"
```

**Security Note:** For production, use environment variables:
```python
import os
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

Then set it in your terminal:
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
```

### Step 2: Run the Application

```bash
streamlit run xer_assistant.py
```

### Step 3: Use the Assistant

1. Browser opens automatically at http://localhost:8501
2. Upload your XER files in the sidebar
3. Ask questions or select quick queries
4. Get AI-powered analysis!

---

## 💡 Example Queries

### Project Status
- "What's the overall project health?"
- "Is the project on schedule?"
- "What's the current completion percentage?"

### Schedule Analysis
- "Identify activities on the critical path"
- "What's causing the schedule delay?"
- "Which activities have negative float?"
- "Calculate the schedule performance index"

### Resource Management
- "Which resources are over-allocated?"
- "Show me resource utilization trends"
- "Are there any resource conflicts?"

### Comparison
- "Compare baseline vs current schedule"
- "What changed between Feb and Mar updates?"
- "Show me variance in completion dates"

### Risk Analysis
- "Identify high-risk activities"
- "What activities have the most dependencies?"
- "Which work packages are behind schedule?"

---

## 🎨 Customization Options

### 1. Change AI Model

In `xer_assistant.py`, modify:
```python
model="claude-sonnet-4-5-20250929"  # Most capable
# or
model="claude-3-5-sonnet-20241022"  # Faster, cheaper
# or
model="claude-3-haiku-20240307"     # Fastest, cheapest
```

### 2. Add Custom Analysis Functions

```python
def calculate_critical_path(tasks, dependencies):
    """Custom CPM calculation"""
    # Your logic here
    return critical_path

# Then add as a tool for Claude
tools=[
    {
        "name": "calculate_cpm",
        "description": "Calculate critical path method",
        ...
    }
]
```

### 3. Customize UI Theme

In `xer_assistant.py`, add:
```python
st.set_page_config(
    page_title="My Company - XER Analyzer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.stButton>button {
    background-color: #0066cc;
    color: white;
}
</style>
""", unsafe_allow_html=True)
```

---

## 🔧 Alternative Setups

### Option A: Use GPT-4 Instead of Claude

```python
# Install OpenAI
pip install openai

# Modify xer_assistant.py
from openai import OpenAI

client = OpenAI(api_key="sk-proj-xxxxx")

def analyze_with_gpt4(query, xer_data):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a Primavera P6 expert."},
            {"role": "user", "content": f"Data: {json.dumps(xer_data)}\n\nQuery: {query}"}
        ]
    )
    return response.choices[0].message.content
```

### Option B: Local LLM (Free, No API Key)

```python
# Install Ollama
# Download from: https://ollama.com

# Pull model
ollama pull llama3:70b

# Modify xer_assistant.py
import requests

def analyze_with_ollama(query, xer_data):
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama3:70b',
        'prompt': f"Data: {json.dumps(xer_data)}\n\nQuery: {query}"
    })
    return response.json()['response']
```

### Option C: Google Gemini

```python
# Install Google AI
pip install google-generativeai

import google.generativeai as genai

genai.configure(api_key="YOUR_GOOGLE_API_KEY")
model = genai.GenerativeModel('gemini-pro')

def analyze_with_gemini(query, xer_data):
    response = model.generate_content(
        f"Data: {json.dumps(xer_data)}\n\nQuery: {query}"
    )
    return response.text
```

---

## 📊 Cost Estimates

### Claude API (Recommended)
- **Input:** $0.003 per 1K tokens
- **Output:** $0.015 per 1K tokens
- **Typical query:** ~$0.05-0.10 per analysis

### GPT-4
- **Input:** $0.01 per 1K tokens
- **Output:** $0.03 per 1K tokens
- **Typical query:** ~$0.15-0.30 per analysis

### Gemini Pro
- **Input:** $0.00025 per 1K tokens
- **Output:** $0.0005 per 1K tokens
- **Typical query:** ~$0.01-0.02 per analysis

### Local (Ollama)
- **FREE** (but requires powerful PC)
- RTX 4090 or better recommended

---

## 🐛 Troubleshooting

### Error: "No module named 'anthropic'"
```bash
pip install anthropic
```

### Error: "API key not valid"
- Check you copied the full key (starts with `sk-ant-`)
- Verify at https://console.anthropic.com

### Error: "Port 8501 already in use"
```bash
streamlit run xer_assistant.py --server.port 8502
```

### Slow Performance
- Use smaller model: `claude-3-haiku-20240307`
- Reduce `max_tokens` to 2048
- Limit data sent (only relevant tables)

### Out of Memory
- Process files one at a time
- Reduce JSON data size
- Use pagination for large datasets

---

## 🚀 Advanced Features

### 1. Add File Comparison

```python
if len(uploaded_files) > 1:
    st.subheader("📊 File Comparison")
    comparison_query = "Compare these project versions and highlight changes"
    response = analyze_with_claude(comparison_query, report)
    st.markdown(response)
```

### 2. Export to Excel

```python
import pandas as pd

# Convert to DataFrame
df = pd.DataFrame(report['files'][0]['wbs_summary'])

# Download button
st.download_button(
    "📥 Download as Excel",
    df.to_csv(index=False).encode('utf-8'),
    "xer_analysis.csv",
    "text/csv"
)
```

### 3. Scheduled Reports

```python
import schedule
import time

def automated_analysis():
    files = list(Path('.').glob('*.xer'))
    report = generate_report(files)
    analysis = analyze_with_claude("Generate weekly status report", report)
    # Email or save

schedule.every().monday.at("09:00").do(automated_analysis)
```

---

## 📚 Next Steps

1. ✅ Set up the basic assistant
2. 🔧 Customize for your needs
3. 📊 Add custom analysis functions
4. 🎨 Brand it with your company theme
5. 🚀 Deploy to cloud (Streamlit Cloud, AWS, Azure)

---

## 🆘 Support

- **Claude Documentation:** https://docs.anthropic.com
- **Streamlit Docs:** https://docs.streamlit.io
- **Primavera P6 Forum:** https://community.oracle.com/customerconnect/categories/primavera_p6

---

**Ready to start?** Just run:
```bash
streamlit run xer_assistant.py
```

🎉 Happy analyzing!
