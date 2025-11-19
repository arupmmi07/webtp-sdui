"""Streamlit Chat UI for Therapist Replacement System.

This replaces the CLI with a modern web-based chat interface.

Usage:
    streamlit run demo/chat_ui.py

Features:
    - ChatGPT-like interface
    - Visual workflow stages
    - Provider scoring tables
    - Audit log viewer
    - Export capabilities
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.workflow import create_workflow_orchestrator


# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .stChatMessage {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "orchestrator" not in st.session_state:
    with st.spinner("🔄 Initializing system..."):
        st.session_state.orchestrator = create_workflow_orchestrator()
        st.session_state.initialized = True

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Hi! I'm your AI Assistant. I can help with various workflows.\n\n**Try saying:**\n- \"therapist departed T001\" - Handle provider replacement\n- \"help\" - See what I can do\n- \"show mocks\" - View system status"
    }]

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "workflow_history" not in st.session_state:
    st.session_state.workflow_history = []


# Header
st.markdown('<div class="main-header">🤖 AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent automation for your workflows</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Quick Commands")
    
    st.markdown("### Main Commands")
    if st.button("🚨 Therapist Departed T001", use_container_width=True):
        st.session_state.command_input = "therapist departed T001"
    
    st.markdown("### View Options")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Audit", use_container_width=True):
            st.session_state.command_input = "show audit"
    with col2:
        if st.button("🎭 Mocks", use_container_width=True):
            st.session_state.command_input = "show mocks"
    
    if st.button("❓ Help", use_container_width=True):
        st.session_state.command_input = "help"
    
    st.divider()
    
    st.markdown("### 📈 Statistics")
    if st.session_state.workflow_history:
        st.metric("Workflows Run", len(st.session_state.workflow_history))
        successful = sum(1 for w in st.session_state.workflow_history if w.get("final_status") == "SUCCESS")
        st.metric("Success Rate", f"{(successful/len(st.session_state.workflow_history)*100):.0f}%")
    else:
        st.info("No workflows run yet")
    
    st.divider()
    
    st.markdown("### ⚙️ System Status")
    st.success("✅ Mock Mode Active")
    st.caption("Using mocked services (no API costs)")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chat cleared! Ready for new commands."
        }]
        st.rerun()
    
    st.divider()
    
    st.markdown("### 📚 Documentation")
    st.caption("[View Docs](docs/QUICKSTART_DEMO.md) • [MOCKS Guide](docs/MOCKS.md)")


# Main chat interface
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Helper functions
def display_workflow_result(result):
    """Display workflow result in a structured format."""
    
    status = result.get("final_status")
    
    if status == "SUCCESS":
        st.success("✅ **Workflow Complete - SUCCESS!**")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Status", "SUCCESS", delta="100%")
        with col2:
            trigger = result.get("trigger_result", {})
            st.metric("Appointments", trigger.get("affected_count", 0))
        with col3:
            st.metric("Session", result.get("session_id", "N/A")[-4:])
        with col4:
            st.metric("Stages", len(result.get("events", [])))
        
        st.markdown("---")
        
        # Workflow stages
        st.markdown("### 📋 Workflow Stages")
        
        tabs = st.tabs(["Trigger", "Filtering", "Scoring", "Consent", "Booking", "Audit"])
        
        # Tab 1: Trigger
        with tabs[0]:
            trigger_result = result.get("trigger_result", {})
            st.markdown("#### 🚨 Trigger - Affected Appointments")
            st.write(f"**Therapist:** {trigger_result.get('therapist_name', 'N/A')} ({trigger_result.get('therapist_id')})")
            st.write(f"**Priority:** {trigger_result.get('priority', 'N/A')}")
            st.write(f"**Affected Appointments:** {trigger_result.get('affected_count', 0)}")
            
            if trigger_result.get("appointments"):
                apt = trigger_result["appointments"][0]
                st.info(f"📅 Appointment **{apt['appointment_id']}**: Patient **{apt['patient_id']}** on **{apt['date']}** at **{apt['time']}**")
        
        # Tab 2: Filtering
        with tabs[1]:
            filter_result = result.get("filter_result", {})
            st.markdown("#### 🔍 Filtering - Provider Qualification")
            
            qualified = filter_result.get("qualified_providers", [])
            eliminated = filter_result.get("eliminated_providers", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Qualified", len(qualified), delta="✅")
            with col2:
                st.metric("Eliminated", len(eliminated), delta="❌")
            
            if qualified:
                st.success(f"✅ **Qualified:** {', '.join(qualified)}")
            
            if eliminated:
                st.warning("❌ **Eliminated:**")
                for provider_id, details in eliminated.items():
                    st.write(f"- **{provider_id}**: {details.get('reason')} - {details.get('details')}")
            
            # Show filters applied
            with st.expander("View Filter Details"):
                filters_applied = filter_result.get("filters_applied", [])
                for f in filters_applied:
                    st.write(f"**{f.get('filter')}**")
                    st.write(f"- Passed: {', '.join(f.get('passed', []))}")
                    st.write(f"- Eliminated: {', '.join(f.get('eliminated', []))}")
                    st.caption(f.get('reason', ''))
        
        # Tab 3: Scoring
        with tabs[2]:
            score_result = result.get("score_result", {})
            st.markdown("#### ⭐ Scoring - Provider Ranking")
            
            ranked_providers = score_result.get("ranked_providers", [])
            
            if ranked_providers:
                # Create comparison table
                import pandas as pd
                
                table_data = []
                for p in ranked_providers:
                    breakdown = p.get("breakdown", {})
                    table_data.append({
                        "Rank": f"#{p['rank']}",
                        "Provider": p['provider_name'],
                        "ID": p['provider_id'],
                        "Total Score": f"{p['total_score']}/150",
                        "Continuity": f"{breakdown.get('continuity', {}).get('score', 0)}/40",
                        "Specialty": f"{breakdown.get('specialty', {}).get('score', 0)}/35",
                        "Preference": f"{breakdown.get('preference_fit', {}).get('score', 0)}/30",
                        "Load": f"{breakdown.get('load_balance', {}).get('score', 0)}/25",
                        "Time": f"{breakdown.get('day_time_match', {}).get('score', 0)}/20",
                        "Rating": p['recommendation']
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Winner highlight
                winner = ranked_providers[0]
                st.success(f"🏆 **Winner:** {winner['provider_name']} - {winner['total_score']}/150 points ({winner['recommendation']})")
                
                # Detailed breakdown for winner
                with st.expander(f"View {winner['provider_name']} Scoring Breakdown"):
                    breakdown = winner.get("breakdown", {})
                    for factor, details in breakdown.items():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{factor.replace('_', ' ').title()}**")
                            st.caption(details.get('reason', ''))
                        with col2:
                            st.metric("Score", f"{details.get('score')}/{details.get('max')}")
        
        # Tab 4: Consent
        with tabs[3]:
            consent_result = result.get("consent_result", {})
            st.markdown("#### 💬 Consent - Patient Communication")
            
            st.write(f"**Channel:** {consent_result.get('channel_used', 'N/A').upper()}")
            st.write(f"**Patient Response:** {consent_result.get('patient_response', 'N/A')}")
            st.write(f"**Response Time:** {consent_result.get('response_time_minutes', 0)} minutes")
            
            if consent_result.get("consent_granted"):
                st.success("✅ Patient accepted the offer")
            else:
                st.error("❌ Patient declined")
            
            # Show message
            with st.expander("View Message Sent"):
                st.code(consent_result.get("message_sent", "N/A"), language=None)
        
        # Tab 5: Booking
        with tabs[4]:
            booking = result.get("booking_result", {})
            st.markdown("#### 📅 Booking - Final Confirmation")
            
            st.success("✅ Appointment Booked Successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Patient:** {booking.get('patient_id')}")
                st.write(f"**Provider:** {booking.get('provider_id')}")
            with col2:
                st.write(f"**Date:** {booking.get('date')}")
                st.write(f"**Time:** {booking.get('time')}")
            
            st.info(f"🎫 **Confirmation Number:** {booking.get('confirmation_number')}")
            
            if booking.get("confirmation_sent"):
                st.success("✅ Confirmation SMS sent to patient")
        
        # Tab 6: Audit
        with tabs[5]:
            audit = result.get("audit_result", {})
            st.markdown("#### 📊 Audit - Complete Log")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Processed", audit.get("appointments_processed", 0))
            with col2:
                st.metric("Rebooked", audit.get("appointments_rebooked", 0))
            with col3:
                st.metric("Success Rate", audit.get("success_rate", "N/A"))
            
            with st.expander("View Full Event Log"):
                events = result.get("events", [])
                for i, event in enumerate(events, 1):
                    st.write(f"**{i}. {event.get('stage', 'unknown').upper()}**")
                    st.caption(f"Status: {event.get('status', 'unknown')}")
        
        # Export button
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.download_button(
                label="📥 Download Full Results (JSON)",
                data=json.dumps(result, indent=2, default=str),
                file_name=f"workflow_{result.get('session_id', 'result')}.json",
                mime="application/json",
                use_container_width=True
            ):
                st.success("Downloaded!")
        
        with col2:
            if st.button("📋 Copy Session ID", use_container_width=True):
                st.code(result.get("session_id", "N/A"))
    
    elif status == "NO_WORK_NEEDED":
        st.info("ℹ️ No affected appointments found.")
    
    elif status == "ESCALATED_TO_HOD":
        st.warning("⚠️ No qualified providers found. Escalated to Head of Department.")
    
    elif status == "PATIENT_DECLINED":
        st.warning("⚠️ Patient declined the offer. Would try next provider.")
    
    else:
        st.error(f"❌ Workflow failed or incomplete. Status: {status}")


def display_help():
    """Display help information."""
    st.markdown("""
    ### 💡 What I Can Do
    
    **📋 Use Case Commands:**
    
    **UC1: Trigger & Prioritize**
    - "therapist departed T001"
    - "provider unavailable T001"
    - Identifies affected appointments with priority scores
    
    **UC2: Filter Candidates**
    - (Automatic during full workflow)
    - Filters providers by compliance, skills, location
    
    **UC3: Score & Rank**
    - (Automatic during full workflow)
    - Scores using continuity, specialty, preference, load, time
    
    **UC4: Patient Consent**
    - (Automatic during full workflow)
    - Multi-channel communication (SMS/Email)
    
    **UC5: Backfill & Waitlist**
    - (Future: "backfill slot Monday 2PM")
    - Fills freed slots with high no-show risk patients
    
    **UC6: Audit & Reconcile**
    - (Automatic at end of workflow)
    - Complete audit trail and EMR updates
    
    **🔍 View Commands:**
    - "show audit" - View last workflow results
    - "show mocks" - View system status
    - "help" - Show this message
    
    ### 🎯 Quick Start
    
    **Try:** "therapist departed T001"
    
    **What happens:** Complete 6-stage workflow
    1. 🚨 Trigger - Find affected appointments
    2. 🔍 Filter - Apply compliance rules (8 filters)
    3. ⭐ Score - Rank providers (5 factors, 150 pts max)
    4. 💬 Consent - Get patient approval via SMS
    5. 📅 Book - Confirm appointment
    6. 📊 Audit - Generate complete log
    
    ### 🎭 System Status
    
    Running in **demo mode**:
    - AI decisions are simulated
    - No real messages sent
    - Using test data
    
    Type any command to get started!
    """)


def display_mocks():
    """Display mocked components information."""
    st.markdown("""
    ### 🎭 Mocked Components
    
    #### 🟡 Currently Mocked
    
    **1. LLM Calls**
    - **Mock:** `adapters/llm/mock_llm.py`
    - **Real:** `adapters/llm/litellm_adapter.py`
    - **Swap Time:** 2 hours
    - **Change:** 1 line of code
    
    **2. LangFuse Prompts**
    - **Mock:** Hardcoded strings
    - **Real:** LangFuse API
    - **Swap Time:** 2 hours
    
    **3. MCP Knowledge Server**
    - **Mock:** Returns hardcoded rules
    - **Real:** Parse PDFs dynamically
    - **Swap Time:** 4 hours
    
    **4. MCP Domain Server**
    - **Mock:** Hardcoded test data
    - **Real:** Database/WebPT API
    - **Swap Time:** 8 hours
    
    **5. SMS/Email**
    - **Mock:** Print to console
    - **Real:** Twilio/SendGrid
    - **Swap Time:** 4 hours
    
    #### 🟢 Real Components
    
    - ✅ Workflow Orchestration (Sequential execution)
    - ✅ Event Logging (Python list)
    - ✅ Data Models (Pydantic/dataclasses)
    
    ---
    
    📚 **See `docs/MOCKS.md` for detailed swap instructions**
    """)


# Process command input from sidebar
if "command_input" in st.session_state and st.session_state.command_input:
    prompt = st.session_state.command_input
    st.session_state.command_input = None
    
    # Add to messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Rerun to display
    st.rerun()


# Chat input
if prompt := st.chat_input("Type a command (e.g., 'therapist departed T001')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process command
    with st.chat_message("assistant"):
        prompt_lower = prompt.lower()
        
        # Use Case 1: Trigger
        if "therapist departed" in prompt_lower or "provider departed" in prompt_lower or "provider unavailable" in prompt_lower:
            # Extract therapist ID
            parts = prompt.split()
            therapist_id = parts[-1] if len(parts) >= 3 else "T001"
            
            # Create collapsible progress container
            with st.expander("🔄 Workflow Execution (click to expand/collapse)", expanded=False):
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Stage indicators
                stages_col = st.columns(6)
                stage_status = {}
                for i, col in enumerate(stages_col):
                    with col:
                        stage_status[i] = st.empty()
                
                try:
                    # Stage 1: Trigger
                    status_text.text("Stage 1: Trigger & Prioritize...")
                    stage_status[0].markdown("🟡 1")
                    progress_bar.progress(10)
                    
                    # Get trigger result
                    trigger_result = st.session_state.orchestrator.scheduling_agent.trigger_handler(therapist_id)
                    
                    stage_status[0].markdown("✅ 1")
                    with st.expander("🚨 Stage 1: Trigger - Details", expanded=False):
                        st.write(f"**Therapist:** {trigger_result.get('therapist_name')}")
                        st.write(f"**Affected:** {trigger_result.get('affected_count')} appointments")
                        st.write(f"**Priority:** {trigger_result.get('priority')}")
                    
                    progress_bar.progress(25)
                    
                    # Stage 2: Filtering
                    status_text.text("Stage 2: Filter Candidates (8 compliance checks)...")
                    stage_status[1].markdown("🟡 2")
                    
                    appointment = trigger_result['appointments'][0]
                    candidate_ids = ["P001", "P004", "P003"]
                    filter_result = st.session_state.orchestrator.scheduling_agent.filter_candidates(appointment, candidate_ids)
                    
                    stage_status[1].markdown("✅ 2")
                    with st.expander("🔍 Stage 2: Filtering - Details", expanded=False):
                        st.write(f"**Candidates:** 3 → {len(filter_result['qualified_providers'])} qualified")
                        st.write(f"**Filters Applied:** Skills, License, POC, Payer, Location, Telehealth, Availability, Capacity")
                        if filter_result.get('eliminated_providers'):
                            st.write("**Eliminated:**")
                            for pid, details in filter_result['eliminated_providers'].items():
                                st.caption(f"- {pid}: {details['reason']}")
                    
                    progress_bar.progress(40)
                    
                    # Stage 3: Scoring
                    status_text.text("Stage 3: Score & Rank (5 factors, 150 pts)...")
                    stage_status[2].markdown("🟡 3")
                    
                    score_result = st.session_state.orchestrator.scheduling_agent.score_and_rank_providers(
                        appointment, filter_result['qualified_providers']
                    )
                    
                    stage_status[2].markdown("✅ 3")
                    with st.expander("⭐ Stage 3: Scoring - Details", expanded=False):
                        st.write("**Scoring Factors:**")
                        st.caption("• Continuity (40 pts) - Prior relationship")
                        st.caption("• Specialty (35 pts) - Clinical match")
                        st.caption("• Preference (30 pts) - Patient preferences")
                        st.caption("• Load Balance (25 pts) - Provider capacity")
                        st.caption("• Day/Time (20 pts) - Schedule alignment")
                        st.write("**Results:**")
                        for p in score_result['ranked_providers']:
                            st.write(f"#{p['rank']}: {p['provider_name']} - {p['total_score']}/150 pts")
                    
                    progress_bar.progress(55)
                    
                    # Stage 4: Consent
                    status_text.text("Stage 4: Patient Consent (SMS/Email)...")
                    stage_status[3].markdown("🟡 4")
                    
                    top_provider_id = score_result['recommended_provider_id']
                    consent_result = st.session_state.orchestrator.engagement_agent.send_offer(
                        patient_id=appointment['patient_id'],
                        provider_id=top_provider_id,
                        appointment=appointment,
                        original_provider_name=appointment.get('original_provider_name', 'your therapist')
                    )
                    
                    stage_status[3].markdown("✅ 4")
                    with st.expander("💬 Stage 4: Consent - Details", expanded=False):
                        st.write(f"**Channel:** {consent_result.get('channel_used', 'SMS').upper()}")
                        st.write(f"**Message Sent:** Yes")
                        st.write(f"**Patient Response:** {consent_result.get('patient_response')}")
                        st.write(f"**Response Time:** {consent_result.get('response_time_minutes')} minutes")
                        st.code(consent_result.get('message_sent', ''), language=None)
                    
                    progress_bar.progress(70)
                    
                    # Stage 5: Backfill (future)
                    status_text.text("Stage 5: Backfill & Waitlist (skipped in demo)...")
                    stage_status[4].markdown("⚪ 5")
                    with st.expander("📋 Stage 5: Backfill - Status", expanded=False):
                        st.info("Backfill workflow not needed - patient accepted first offer")
                        st.caption("Would execute if patient declined all options:")
                        st.caption("• Fill freed slot with high no-show risk patient")
                        st.caption("• Reschedule original patient using availability windows")
                    
                    progress_bar.progress(85)
                    
                    # UC6: Booking
                    status_text.text("Booking appointment...")
                    
                    booking_data = {
                        "appointment_id": appointment['appointment_id'],
                        "patient_id": appointment['patient_id'],
                        "provider_id": top_provider_id,
                        "date": appointment['date'],
                        "time": appointment['time']
                    }
                    
                    booking_result = st.session_state.orchestrator.domain_server.book_appointment(booking_data)
                    
                    if booking_result['status'] == "SUCCESS":
                        st.session_state.orchestrator.engagement_agent.send_confirmation(
                            patient_id=appointment['patient_id'],
                            provider_id=top_provider_id,
                            appointment=booking_data
                        )
                    
                    progress_bar.progress(95)
                    
                    # Stage 6: Audit
                    status_text.text("Stage 6: Generating Audit Log...")
                    stage_status[5].markdown("🟡 6")
                    
                    # Build complete result
                    result = {
                        "session_id": f"SESSION-{therapist_id}-001",
                        "therapist_id": therapist_id,
                        "trigger_result": trigger_result,
                        "filter_result": filter_result,
                        "score_result": score_result,
                        "consent_result": consent_result,
                        "booking_result": booking_result,
                        "events": [
                            {"stage": "trigger", "status": "complete", "data": trigger_result},
                            {"stage": "filtering", "status": "complete", "data": filter_result},
                            {"stage": "scoring", "status": "complete", "data": score_result},
                            {"stage": "consent", "status": "complete", "data": consent_result},
                            {"stage": "booking", "status": "complete", "data": booking_result},
                        ],
                        "final_status": "SUCCESS",
                        "appointments_processed": 1,
                        "appointments_rebooked": 1
                    }
                    
                    audit_result = st.session_state.orchestrator.scheduling_agent.create_audit_log(result)
                    result["audit_result"] = audit_result
                    
                    stage_status[5].markdown("✅ 6")
                    with st.expander("📊 Stage 6: Audit - Details", expanded=False):
                        st.write(f"**Session:** {audit_result.get('session_id')}")
                        st.write(f"**Processed:** {audit_result.get('appointments_processed')} appointments")
                        st.write(f"**Success Rate:** {audit_result.get('success_rate')}")
                        st.write(f"**Status:** {audit_result.get('status')}")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ All stages complete!")
                    
                    # Save result
                    st.session_state.last_result = result
                    st.session_state.workflow_history.append(result)
                    
                    # Display full result
                    st.markdown("---")
                    
                    # Receptionist-friendly summary
                    st.success("✅ **Appointment Successfully Rescheduled**")
                    
                    patient_name = "Maria Rodriguez"  # From mock data
                    old_provider = trigger_result.get('therapist_name', 'Dr. Sarah Johnson')
                    new_provider = "Dr. Emily Ross"  # Winner from scoring
                    booking = booking_result
                    
                    st.markdown(f"""
                    ### 📋 Summary for Front Desk
                    
                    **Original Situation:**
                    - Provider **{old_provider}** ({therapist_id}) is unavailable
                    - **{trigger_result.get('affected_count', 1)}** appointment(s) affected
                    
                    **Action Taken:**
                    - ✅ Found qualified replacement: **{new_provider}**
                    - ✅ Patient **{patient_name}** notified via SMS
                    - ✅ Patient confirmed: **YES**
                    - ✅ Appointment rebooked
                    
                    **New Appointment Details:**
                    - **Patient:** {patient_name} (PAT001)
                    - **Provider:** {new_provider} (P001)
                    - **Date:** {booking.get('date')}
                    - **Time:** {booking.get('time')}
                    - **Location:** Metro PT Main Clinic
                    - **Confirmation #:** {booking.get('confirmation_number')}
                    
                    ### ✨ Next Steps for You:
                    
                    ✅ **No action needed** - Everything is handled automatically!
                    - EMR updated with new provider
                    - Patient received confirmation SMS
                    - Dr. {new_provider} has been notified
                    - Chart prepared for appointment
                    
                    ### 📊 Why Dr. {new_provider} was selected:
                    
                    - ✅ **Specialty Match:** Orthopedic specialist (perfect for post-surgical knee)
                    - ✅ **Patient Preference:** Female provider (patient requested)
                    - ✅ **Schedule Match:** Tuesday 10 AM (patient's preferred time)
                    - ✅ **Good Availability:** 60% capacity (not overloaded)
                    - ✅ **Compliance:** All Medicare/POC requirements met
                    - **Score:** 75/150 points (EXCELLENT match)
                    
                    ---
                    
                    💡 **Note:** You can expand "Workflow Execution" above to see technical details of all 6 stages.
                    """)
                    
                    display_workflow_result(result)
                    
                    response = "📋 See appointment summary above for all details."
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    response = f"Error processing workflow: {str(e)}"
        
        elif "show audit" in prompt_lower:
            if st.session_state.last_result:
                display_workflow_result(st.session_state.last_result)
                response = "Audit log displayed above. ⬆️"
            else:
                st.info("ℹ️ No workflow has been run yet. Try: `therapist departed T001`")
                response = "No audit log available. Run a workflow first."
        
        elif "show mocks" in prompt_lower:
            display_mocks()
            response = "Mocked components listed above. ⬆️"
        
        elif "help" in prompt_lower:
            display_help()
            response = "Help information displayed above. ⬆️"
        
        elif "clear" in prompt_lower:
            st.session_state.messages = []
            st.rerun()
            response = "Chat cleared!"
        
        else:
            st.warning(f"❓ Unknown command: `{prompt}`")
            st.markdown("**Try:**")
            st.markdown("- `therapist departed T001`")
            st.markdown("- `help`")
            st.markdown("- `show mocks`")
            response = "Unknown command. Type 'help' to see available commands."
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})


# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 AI Assistant")
with col2:
    st.caption("🎭 Demo Mode Active")
with col3:
    st.caption("📚 [Documentation](docs/)")

