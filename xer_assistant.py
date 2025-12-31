#!/usr/bin/env python3
"""
XER Assistant - Custom LLM Assistant for Primavera P6 Project Analysis
Powered by Opencoders
"""

import streamlit as st
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from xer_parser import XERParser, generate_report

# Load environment variables
load_dotenv()

# Configuration - Choose your AI provider
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # Options: "claude", "gemini", "openai"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def analyze_with_ai(query, xer_data):
    """Send XER data to AI for analysis"""

    # Prepare context
    context = f"""You are an expert Primavera P6 project management analyst.

Here's the XER project data:
{json.dumps(xer_data, indent=2)[:10000]}  # Limit to avoid token limits

User's question: {query}

Please provide a detailed, professional analysis."""

    if AI_PROVIDER == "claude":
        return analyze_with_claude(context)
    elif AI_PROVIDER == "gemini":
        return analyze_with_gemini(context)
    elif AI_PROVIDER == "openai":
        return analyze_with_openai(context)
    else:
        return "Error: Invalid AI provider configured"


def analyze_with_claude(context):
    """Use Claude API"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": context}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Claude Error: {str(e)}\n\nTip: Add API credits at https://console.anthropic.com/settings/billing"


def analyze_with_gemini(context):
    """Use Google Gemini API (FREE tier available!)"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(context)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}\n\nTip: Get free API key at https://makersuite.google.com/app/apikey"


def analyze_with_openai(context):
    """Use OpenAI GPT-4o mini"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": context}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}"


def main():
    st.set_page_config(
        page_title="XER Project Assistant",
        page_icon="",
        layout="wide"
    )

    st.title("XER Assistant")
    st.markdown("*upload xer & ask questions about your Primavera P6 projects*")

    # Sidebar - File upload
    with st.sidebar:
        st.header("Upload XER Files")
        uploaded_files = st.file_uploader(
            "Choose XER files",
            type=['xer'],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) loaded")

            # Save temporarily
            xer_paths = []
            for uploaded_file in uploaded_files:
                temp_path = Path(f"temp_{uploaded_file.name}")
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.read())
                xer_paths.append(temp_path)

    # Main area - Analysis
    if uploaded_files:
        # Parse XER files
        with st.spinner("Parsing XER files..."):
            report = generate_report(xer_paths)

        # Display quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Files", len(report['files']))
        with col2:
            total_tasks = sum(f['task_count'] for f in report['files'])
            st.metric("Total Tasks", f"{total_tasks:,}")
        with col3:
            total_wbs = sum(f['wbs_count'] for f in report['files'])
            st.metric("WBS Items", f"{total_wbs:,}")
        with col4:
            st.metric("Resources", report['files'][0]['table_statistics'].get('RSRC', 0))

        # Query interface
        st.markdown("---")
        st.subheader("Ask Questions About Your Project")

        # Predefined queries
        quick_questions = [
            "What's the current project status and schedule health?",
            "Identify the critical path and schedule risks",
            "Analyze resource utilization and potential conflicts",
            "Compare the baseline vs current schedule",
            "What are the top 10 most critical activities?",
            "Calculate the schedule variance and delay causes"
        ]

        selected_question = st.selectbox("Quick Questions:", ["Custom question..."] + quick_questions)

        if selected_question == "Custom question...":
            query = st.text_area("Ask anything about your project:", height=100)
        else:
            query = st.text_area("Question:", value=selected_question, height=100)

        if st.button("🔍 Analyze", type="primary"):
            if query:
                with st.spinner(f"let me look into that..."):
                    try:
                        response = analyze_with_ai(query, report)

                        st.markdown("### 📊 Analysis Results")
                        st.markdown(response)

                        # Download option
                        st.download_button(
                            "📥 Download Analysis",
                            response,
                            file_name="xer_analysis.md",
                            mime="text/markdown"
                        )

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("💡 Make sure to set your Anthropic API key in the code!")
            else:
                st.warning("Please enter a question")

        # Show raw data option
        with st.expander("📋 View Raw Parsed Data"):
            st.json(report)

        # Cleanup temp files
        for path in xer_paths:
            if path.exists():
                path.unlink()

    else:
        # Welcome screen
        st.info("👈 Upload your XER files in the sidebar to get started")

        # st.markdown("""
        # ### What can this assistant do?

        # - 📊 **Analyze project schedules** - Get insights on timeline, delays, and progress
        # - 🎯 **Identify critical paths** - Find activities driving your end date
        # - 👥 **Resource analysis** - Check utilization and conflicts
        # - 📈 **Variance analysis** - Compare baseline vs actual performance
        # - 🔍 **Custom queries** - Ask anything about your project data

        # ### Supported Files
        # - Primavera P6 XER files (all versions)
        # - Multiple files for comparison

        # ### Getting Started
        # 1. Upload your XER file(s) in the sidebar
        # 2. Choose a quick question or write your own
        # 3. Click "Analyze" to get AI-powered insights
        # """)


if __name__ == "__main__":
    main()
