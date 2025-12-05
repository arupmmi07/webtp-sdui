# AWS AgentCore Architecture - One Slide

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  TRIGGERS: EHR │ Calendar │ Admin Portal │ Patient API  →  Event Queue (SQS/EventBridge) │
│  (High Volume: 50K+ events/day)  →  Buffering │ Batching │ Rate Limiting                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
                    ┌───────────────────────────────────────┐
                    │   AWS Lambda                          │
                    │   (SQS Event Source Mapping)          │
                    │   • Auto-scales with queue depth       │
                    │   • Batches up to 10 messages         │
                    │   • Invokes AgentCore Runtime API      │
                    └───────────────┬───────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                    AMAZON BEDROCK AGENTCORE RUNTIME                                          │
│                    (Invoked via Runtime API)                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │              SUPERVISOR ORCHESTRATOR AGENT                                           │   │
│  │  Prompts: LangFuse (A/B Testing) │ Memory: AgentCore (Short/Long-term)            │   │
│  │  Workflow: Trigger → Filter → Score → QA → Consent → Book → Audit                  │   │
│  │  Models: Amazon Bedrock (Claude, Llama, etc.) - Native Integration                 │   │
│  │                                                                                       │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │   │
│  │  │   Smart     │ │   Patient   │ │   Backfill  │ │   Quality   │ │   Audit    │ │   │
│  │  │ Scheduling  │ │ Engagement  │ │   Agent     │ │  Assurance  │ │   Agent    │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                                         │
│                                    ↓                                                         │
│                    ┌───────────────────────────────────────┐                               │
│                    │   AGENTCORE GATEWAY (MCP)              │                               │
│                    │   REST APIs → MCP Tools (Zero Code Changes)                          │
│                    └───────────────┬───────────────────────┘                               │
└────────────────────────────────────┼─────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  EXISTING APIS: Provider │ Patient │ Appointment │ Notification │ Waitlist │ Knowledge     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  OBSERVABILITY: AgentCore (CloudWatch) │ LangFuse (Prompts/Analytics) │ Custom Dashboards│
│  A/B Testing │ Quality Gates │ Evaluations │ Alerting (PagerDuty/Slack)                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

KEY DECISIONS:
• Event Handling: SQS → Lambda (Event Source Mapping) → AgentCore Runtime API (Auto-scaling, batching)
• LLM Models: Amazon Bedrock (Native Integration - Claude, Llama, etc.)
• Orchestrator: AgentCore Runtime (Fully-Managed, 8-Hour Sessions, Auto-Scaling)
• Prompts: LangFuse (Versioned, A/B Testable)
• APIs: AgentCore Gateway (REST → MCP, Zero Code Changes)
• Scale: 27K Doctors, 500K Patients, 50K+ Events/Day
• Security: HIPAA/SOC 2, Session Isolation
• Note: LiteLLM Proxy optional for multi-provider fallbacks (if needed)
```

