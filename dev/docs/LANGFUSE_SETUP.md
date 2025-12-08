# 📝 LangFuse Prompt Setup Guide

## 🎯 Overview

This guide shows you how to set up the agentic orchestrator prompt in LangFuse so you can modify it without changing code.

---

## 🔧 Step 1: Create Prompt in LangFuse

1. **Go to LangFuse Dashboard**
   - Navigate to: https://cloud.langfuse.com (or your self-hosted instance)
   - Login to your account

2. **Create New Prompt**
   - Click **"Prompts"** in the sidebar
   - Click **"Create Prompt"** button
   - Set the following:
     - **Name**: `healthcare-orchestrator-template`
     - **Label**: `production`
     - **Type**: `Chat` or `Text` (Text is simpler for our use case)

---

## 📋 Step 2: Copy the Prompt Template

Copy the following prompt template into LangFuse:

```
You are an AI Healthcare Operations Orchestrator. Your task is to autonomously reassign patients from an unavailable provider to the best alternative providers using your reasoning capabilities.

SITUATION:
Provider {{provider_name}} (ID: {{provider_id}}) is unavailable on {{date}}.
Total affected appointments: {{total_affected}}

AFFECTED PATIENTS:
{{patients_section}}

AVAILABLE PROVIDERS:
{{providers_section}}
{{continuity_info}}

YOUR TASK:
For each patient, analyze the available providers and autonomously decide the best match. Consider:

1. **Patient Preferences:**
   - Gender preference (if specified)
   - Preferred days of the week
   - Location/proximity (zip code, max distance)
   - Insurance compatibility

2. **Provider Capabilities:**
   - Specialty match for patient's condition
   - Experience level (years of experience)
   - Available days and time slots
   - Current patient load vs capacity

3. **Continuity of Care:**
   - Prior provider relationships (check patient's prior_providers list)
   - Same provider on different day (if continuity slots available)
   - Provider familiarity with patient's condition

4. **Operational Factors:**
   - Provider availability on patient's preferred days
   - Time slot preferences (earlier slots preferred)
   - Load balancing (prefer providers with lower current load)

5. **Decision Quality:**
   - EXCELLENT match: All critical preferences met, strong continuity, specialty match
   - GOOD match: Most preferences met, acceptable alternative
   - ACCEPTABLE match: Basic requirements met, may need patient confirmation
   - POOR match: Significant mismatches, should waitlist for manual review

IMPORTANT RULES:
1. Prioritize continuity (prior provider relationship) when possible
2. Respect patient preferences (gender, day, location) - these are critical
3. Ensure provider capacity is not exceeded
4. If no suitable match exists, assign to waitlist for HOD review
5. Provide clear reasoning for each assignment decision

OUTPUT FORMAT (JSON):
For each patient, provide your autonomous decision with reasoning:

{
  "assignments": [
    {
      "appointment_id": "A001",
      "patient_id": "PAT001",
      "patient_name": "Maria Rodriguez",
      "assigned_to": "P001",
      "assigned_to_name": "Dr. Emily Ross",
      "match_quality": "EXCELLENT",
      "reasoning": "Excellent match: Patient prefers female provider (met), specialty matches (orthopedic), same zip code for convenience, provider has prior relationship with patient, available on patient's preferred day (Monday).",
      "match_factors": {
        "gender_preference_met": true,
        "specialty_match": true,
        "location_match": true,
        "continuity": true,
        "day_preference_met": true,
        "provider_capacity": "low"
      },
      "action": "assign"
    },
    {
      "appointment_id": "A002",
      "patient_id": "PAT002",
      "patient_name": "John Davis",
      "assigned_to": null,
      "assigned_to_name": null,
      "match_quality": "POOR",
      "reasoning": "No suitable provider found. Patient requires weekend appointments but all available providers only work weekdays. Patient has restrictive location preference (8 miles max) and no providers within range meet the day requirement.",
      "match_factors": {
        "day_preference_met": false,
        "location_match": false,
        "specialty_match": true,
        "gender_preference_met": true
      },
      "action": "waitlist"
    }
  ],
  "summary": {
    "total_processed": 2,
    "successful_assignments": 1,
    "waitlist_entries": 1
  }
}

IMPORTANT:
- Use your reasoning to evaluate each patient-provider match
- Provide detailed reasoning explaining WHY you chose each provider
- Include match_factors object showing which criteria were met/not met
- Use match_quality: "EXCELLENT", "GOOD", "ACCEPTABLE", or "POOR"
- If match_quality is "POOR" or no suitable provider exists, use action: "waitlist"

Provide ONLY the JSON output, no additional text.
```

---

## 🔑 Step 3: Available Variables

The following variables are automatically injected by the orchestrator:

### **Basic Context:**
- `{{provider_name}}` - Name of unavailable provider (e.g., "Dr. Sarah Johnson")
- `{{provider_id}}` - ID of unavailable provider (e.g., "T001")
- `{{date}}` - Date of unavailability (e.g., "2025-11-21")
- `{{start_date}}` - Start date of unavailability range
- `{{end_date}}` - End date of unavailability range
- `{{total_affected}}` - Number of affected appointments

### **Formatted Sections:**
- `{{patients_section}}` - Pre-formatted list of all affected patients with their details
- `{{providers_section}}` - Pre-formatted list of all available providers with their details
- `{{continuity_info}}` - Information about continuity options (same provider, different day)

### **Raw Data Arrays** (if you want to use Mustache loops):
- `{{patients}}` - Array of patient objects
- `{{available_providers}}` - Array of provider objects
- `{{continuity_slots}}` - Array of continuity slot objects

### **Reference Data** (optional):
- `{{scoring_rules}}` - Object with scoring rule weights (for reference)
- `{{thresholds}}` - Object with decision thresholds (for reference)

---

## 📝 Step 4: Formatting Sections (Optional)

If you want to customize how patients/providers are formatted, you can use Mustache loops:

### **Example: Custom Patient Formatting**

Replace `{{patients_section}}` with:

```
{{#patients}}
Patient: {{patient.name}} (ID: {{patient.patient_id}})
- Condition: {{patient.condition}}
- Gender Preference: {{patient.gender_preference}}
- Preferred Days: {{patient.preferred_days}}
- Prior Providers: {{patient.prior_providers}}
- Appointment ID: {{appointment_id}}
- Original Time: {{original_time}}

{{/patients}}
```

### **Example: Custom Provider Formatting**

Replace `{{providers_section}}` with:

```
{{#available_providers}}
Provider: {{name}} (ID: {{provider_id}})
- Specialty: {{specialty}}
- Gender: {{gender}}
- Experience: {{years_experience}} years
- Location: {{primary_location}}
- Capacity: {{current_patient_load}}/{{max_patient_capacity}}
- Available Days: {{available_days}}

{{/available_providers}}
```

---

## 🧪 Step 5: Test the Prompt

1. **Save the prompt** in LangFuse
2. **Set environment variables** in your `.env` file:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-...
   LANGFUSE_SECRET_KEY=sk-...
   LANGFUSE_HOST=https://cloud.langfuse.com  # or your self-hosted URL
   ```

3. **Run a test workflow**:
   ```bash
   # Trigger a workflow via API or UI
   curl -X POST http://localhost:8000/api/trigger-workflow \
     -H "Content-Type: application/json" \
     -d '{
       "trigger_type": "provider_unavailable",
       "provider_id": "T001",
       "start_date": "2025-11-21",
       "end_date": "2025-11-21"
     }'
   ```

4. **Check logs** - You should see:
   ```
   [PROMPT] ✅ Compiled from LangFuse
   ```

---

## 🔄 Step 6: Versioning & Labels

LangFuse supports versioning:

- **Production**: Use label `production` (current)
- **Staging**: Create a new version with label `staging`
- **Testing**: Create a new version with label `testing`

To use a different label, modify the code:
```python
prompt_obj = self.langfuse.get_prompt(
    "healthcare-orchestrator-template",
    label="staging"  # Change this
)
```

---

## 💡 Tips for Modifying the Prompt

1. **Keep JSON structure consistent** - The code expects specific fields:
   - `assignments` array
   - Each assignment must have: `appointment_id`, `patient_id`, `action`
   - Optional but recommended: `match_quality`, `reasoning`, `match_factors`

2. **Test changes incrementally** - Use a staging label first

3. **Monitor LLM responses** - Check LangFuse traces to see actual LLM outputs

4. **Use Mustache conditionals** - For optional sections:
   ```
   {{#has_continuity_option}}
   CONTINUITY OPTION:
   {{continuity_info}}
   {{/has_continuity_option}}
   ```

5. **Keep it agentic** - Don't add hard rules or scoring logic. Let the LLM reason!

---

## 🐛 Troubleshooting

### **Prompt not found**
- Check prompt name: `healthcare-orchestrator-template`
- Check label: `production`
- Verify API keys are correct

### **Variables not replacing**
- Check variable names match exactly (case-sensitive)
- Verify metadata is being passed correctly
- Check LangFuse logs for compilation errors

### **Fallback to local template**
- If LangFuse fetch fails, system falls back to local template
- Check logs: `[PROMPT] Warning: LangFuse fetch failed: ...`
- Verify network connectivity and API keys

---

## 📚 Additional Resources

- [LangFuse Documentation](https://langfuse.com/docs)
- [Mustache Templating Guide](https://mustache.github.io/mustache.5.html)
- [Prompt Management Best Practices](https://langfuse.com/docs/prompts)

---

**✅ Once set up, you can modify the prompt in LangFuse UI without touching code!**

