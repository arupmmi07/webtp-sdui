"""Test Script: Upload and Verify LangFuse Prompts.

This script:
1. Connects to LangFuse
2. Creates the 3 core prompts
3. Verifies they were created successfully
4. Tests retrieving them back
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("❌ LangFuse not installed. Run: pip install langfuse")
    sys.exit(1)


# LangFuse credentials from .env
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")


def check_credentials():
    """Check if LangFuse credentials are configured."""
    print("\n" + "=" * 70)
    print("STEP 1: Checking LangFuse Credentials")
    print("=" * 70)
    
    if not LANGFUSE_PUBLIC_KEY:
        print("❌ LANGFUSE_PUBLIC_KEY not found in .env")
        return False
    
    if not LANGFUSE_SECRET_KEY:
        print("❌ LANGFUSE_SECRET_KEY not found in .env")
        return False
    
    print(f"✅ Public Key: {LANGFUSE_PUBLIC_KEY[:10]}...{LANGFUSE_PUBLIC_KEY[-4:]}")
    print(f"✅ Secret Key: {LANGFUSE_SECRET_KEY[:10]}...{LANGFUSE_SECRET_KEY[-4:]}")
    print(f"✅ Host: {LANGFUSE_HOST}")
    
    return True


def connect_to_langfuse():
    """Connect to LangFuse."""
    print("\n" + "=" * 70)
    print("STEP 2: Connecting to LangFuse")
    print("=" * 70)
    
    try:
        client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST
        )
        print("✅ Connected to LangFuse successfully!")
        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def create_chat_router_prompt(client):
    """Create healthcare-chat-router prompt."""
    print("\n" + "=" * 70)
    print("STEP 3: Creating Chat Router Prompt")
    print("=" * 70)
    
    prompt_name = "healthcare-chat-router"
    
    system_prompt = """You are an AI assistant for a healthcare clinic's scheduling system.

Your role is to interpret receptionist messages and extract structured information.

# INTENTS YOU CAN DETECT:

1. THERAPIST_UNAVAILABLE
   - Provider calls in sick, on leave, or departed
   - Examples: "T001 is sick", "Sarah called out", "Dr. Johnson unavailable"

2. PATIENT_DECLINED
   - Patient declines appointment offer
   - Examples: "Maria declined", "Patient doesn't want Dr. Ross"

3. QUERY_WAITLIST
   - Check waitlist status
   - Examples: "show waitlist", "who's on the waitlist?"

4. QUERY_APPOINTMENTS
   - Check appointment status
   - Examples: "show appointments for T001", "what's Maria's appointment?"

5. GENERAL_QUESTION
   - Non-scheduling questions
   - Examples: "how does this work?", "what can you do?"

# OUTPUT FORMAT (JSON):

{
  "intent": "THERAPIST_UNAVAILABLE",
  "confidence": 0.95,
  "entities": {
    "provider_id": "T001",
    "provider_name": "Dr. Sarah Johnson",
    "reason": "sick",
    "date": "2025-11-20"
  },
  "action": "process_therapist_departure",
  "clarification_needed": false,
  "response_to_user": "I understand Dr. Sarah Johnson (T001) is unavailable. Let me check affected appointments..."
}

# IMPORTANT RULES:

- Always extract provider_id OR provider_name (look up if needed)
- Set clarification_needed=true if ambiguous
- Keep response_to_user conversational and helpful
- If multiple interpretations, ask for clarification
- Handle typos gracefully"""
    
    try:
        prompt = client.create_prompt(
            name=prompt_name,
            prompt=system_prompt,
            labels=["production"]  # LangFuse handles versioning automatically
        )
        print(f"✅ Created prompt: {prompt_name}")
        print(f"   Version: {prompt.version if hasattr(prompt, 'version') else 'N/A'}")
        print(f"   Labels: production")
        return True
    except Exception as e:
        print(f"❌ Failed to create {prompt_name}: {e}")
        return False


def create_provider_scoring_prompt(client):
    """Create provider-scoring-prompt."""
    print("\n" + "=" * 70)
    print("STEP 4: Creating Provider Scoring Prompt")
    print("=" * 70)
    
    prompt_name = "provider-scoring-prompt"
    
    system_prompt = """You are a provider matching expert. Score providers for a patient based on:

SCORING FACTORS (Total: 100 points):

1. Continuity (25 pts)
   - Has patient seen this provider before?
   - Higher score for prior relationship

2. Specialty Match (25 pts)
   - Does specialty match patient condition?
   - Exact match = 25, related = 15, general = 5

3. Location Proximity (20 pts)
   - Same zip = 20 pts
   - Adjacent zip = 15 pts
   - Within 5 miles = 10 pts
   - Within 10 miles = 5 pts

4. Availability/Capacity (15 pts)
   - Lower capacity utilization = higher score
   - 0-50% = 15 pts, 51-75% = 10 pts, 76-90% = 5 pts

5. Patient Preferences (15 pts)
   - Gender preference match = 10 pts
   - Language match = 5 pts

Return JSON with scores and reasoning for each provider.

Example output:
{
  "ranked_providers": [
    {
      "provider_id": "P001",
      "provider_name": "Dr. Emily Ross",
      "total_score": 85,
      "breakdown": {
        "continuity": 0,
        "specialty": 25,
        "location": 20,
        "availability": 15,
        "preferences": 15
      },
      "reasoning": "Excellent specialty match, same zip code, good availability"
    }
  ],
  "recommended_provider_id": "P001"
}"""
    
    try:
        prompt = client.create_prompt(
            name=prompt_name,
            prompt=system_prompt,
            labels=["production"]  # LangFuse handles versioning automatically
        )
        print(f"✅ Created prompt: {prompt_name}")
        print(f"   Version: {prompt.version if hasattr(prompt, 'version') else 'N/A'}")
        print(f"   Labels: production")
        return True
    except Exception as e:
        print(f"❌ Failed to create {prompt_name}: {e}")
        return False


def create_patient_message_prompt(client):
    """Create patient-engagement-message prompt."""
    print("\n" + "=" * 70)
    print("STEP 5: Creating Patient Engagement Message Prompt")
    print("=" * 70)
    
    prompt_name = "patient-engagement-message"
    
    system_prompt = """Generate a friendly, professional message to a patient.

TONE:
- Warm and empathetic
- Clear and concise
- Action-oriented
- Respectful of patient's time

MESSAGE TYPES:

1. APPOINTMENT_OFFER
   - Explain situation (provider unavailable)
   - Offer alternative provider
   - Include provider qualifications
   - Make it easy to accept (click link)

2. APPOINTMENT_CONFIRMATION
   - Confirm new appointment details
   - Include date, time, provider, location
   - Add calendar reminder

3. WAITLIST_NOTIFICATION
   - Explain waitlist status
   - Set expectations for follow-up
   - Provide contact info

Keep messages under 160 characters for SMS, longer for email.

Example output:
{
  "subject": "Appointment Change - Dr. Sarah Unavailable",
  "message": "Hi Maria, Dr. Sarah Johnson is unavailable for your appointment on Nov 20 at 10 AM. We'd like to offer you Dr. Emily Ross, a specialist in post-surgical knee care. Click here to confirm: [link]",
  "channel": "email",
  "tone": "empathetic"
}"""
    
    try:
        prompt = client.create_prompt(
            name=prompt_name,
            prompt=system_prompt,
            labels=["production"]  # LangFuse handles versioning automatically
        )
        print(f"✅ Created prompt: {prompt_name}")
        print(f"   Version: {prompt.version if hasattr(prompt, 'version') else 'N/A'}")
        print(f"   Labels: production")
        return True
    except Exception as e:
        print(f"❌ Failed to create {prompt_name}: {e}")
        return False


def verify_prompts(client):
    """Verify all prompts were created and can be retrieved."""
    print("\n" + "=" * 70)
    print("STEP 6: Verifying Prompts (Production Label)")
    print("=" * 70)
    
    prompts_to_verify = [
        "healthcare-chat-router",
        "provider-scoring-prompt",
        "patient-engagement-message"
    ]
    
    all_verified = True
    
    for prompt_name in prompts_to_verify:
        try:
            # Get prompt with production label (latest production version)
            prompt = client.get_prompt(prompt_name, label="production")
            print(f"✅ Verified: {prompt_name}")
            print(f"   Version: {prompt.version if hasattr(prompt, 'version') else 'N/A'}")
            print(f"   Label: production")
            print(f"   Length: {len(prompt.prompt)} characters")
        except Exception as e:
            print(f"❌ Failed to retrieve {prompt_name}: {e}")
            all_verified = False
    
    return all_verified


def test_prompt_usage(client):
    """Test using a prompt in code."""
    print("\n" + "=" * 70)
    print("STEP 7: Testing Prompt Usage")
    print("=" * 70)
    
    try:
        # Get the chat router prompt with production label
        prompt = client.get_prompt("healthcare-chat-router", label="production")
        
        print(f"✅ Successfully loaded: healthcare-chat-router")
        print(f"   Version: {prompt.version if hasattr(prompt, 'version') else 'N/A'}")
        print(f"   Label: production")
        print(f"\nPrompt Preview (first 200 chars):")
        print(f"{prompt.prompt[:200]}...")
        
        print(f"\n📝 Usage Example:")
        print(f"""
from langfuse import Langfuse

langfuse = Langfuse()

# Get production version of prompt
prompt = langfuse.get_prompt("healthcare-chat-router", label="production")

# Use with LLM
response = llm.generate(
    system=prompt.prompt,
    prompt="therapist departed T001"
)

# LangFuse automatically tracks:
# - Which version was used
# - Performance metrics
# - Cost per prompt
""")
        return True
    except Exception as e:
        print(f"❌ Failed to test prompt usage: {e}")
        return False


def main():
    """Main test flow."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║   🧪 LANGFUSE PROMPT UPLOAD & VERIFICATION TEST                 ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Step 1: Check credentials
    if not check_credentials():
        print("\n❌ Please configure LangFuse credentials in .env file")
        return False
    
    # Step 2: Connect to LangFuse
    client = connect_to_langfuse()
    if not client:
        print("\n❌ Failed to connect to LangFuse")
        return False
    
    # Step 3-5: Create prompts
    results = []
    results.append(create_chat_router_prompt(client))
    results.append(create_provider_scoring_prompt(client))
    results.append(create_patient_message_prompt(client))
    
    # Step 6: Verify prompts
    verified = verify_prompts(client)
    
    # Step 7: Test usage
    test_usage = test_prompt_usage(client)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_prompts = len(results)
    successful_prompts = sum(results)
    
    print(f"\nPrompts Created: {successful_prompts}/{total_prompts}")
    print(f"Verification: {'✅ PASSED' if verified else '❌ FAILED'}")
    print(f"Usage Test: {'✅ PASSED' if test_usage else '❌ FAILED'}")
    
    if successful_prompts == total_prompts and verified and test_usage:
        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print("║                                                                  ║")
        print("║   ✅ ALL PROMPTS SUCCESSFULLY CREATED AND VERIFIED!             ║")
        print("║                                                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        
        print(f"\n📊 View your prompts at:")
        print(f"   {LANGFUSE_HOST}/prompts")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. View prompts in LangFuse dashboard")
        print(f"   2. Update config/langfuse_config.py to use these prompts")
        print(f"   3. Test in your application")
        
        return True
    else:
        print("\n❌ Some prompts failed. Check errors above.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

