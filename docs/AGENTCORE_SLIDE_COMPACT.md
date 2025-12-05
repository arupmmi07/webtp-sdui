# AWS AgentCore Architecture - Compact One Slide

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  TRIGGERS: EHR │ Calendar │ Admin Portal │ Patient API  →  AWS API Gateway              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                    AMAZON BEDROCK AGENTCORE RUNTIME                                          │
│                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │              SUPERVISOR ORCHESTRATOR AGENT                                           │   │
│  │  Prompts: LangFuse (A/B Testing) │ Memory: AgentCore (Short/Long-term)             │   │
│  │                                                                                       │   │
│  │  Workflow: Trigger → Filter → Score → QA → Consent → Book → Audit                 │   │
│  │                                                                                       │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │   │
│  │  │   Smart     │ │   Patient   │ │   Backfill  │ │   Quality   │ │   Audit    │ │   │
│  │  │ Scheduling  │ │ Engagement  │ │   Agent     │ │  Assurance  │ │   Agent    │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                                         │
│                                    ↓                                                         │
│                    ┌───────────────────────────────────────┐                               │
│                    │   AGENTCORE GATEWAY (MCP)             │                               │
│                    │   REST APIs → MCP Tools (Zero Code Changes)                         │
│                    └───────────────┬───────────────────────┘                               │
└────────────────────────────────────┼─────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  EXISTING APIS: Provider │ Patient │ Appointment │ Notification │ Waitlist │ Knowledge     │
│  (No Code Changes Required - Gateway Handles Integration)                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  OBSERVABILITY: AgentCore (CloudWatch) │ LangFuse (Prompts/Analytics) │ Custom Dashboards│
│  A/B Testing │ Quality Gates │ Evaluations │ Alerting (PagerDuty/Slack)                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

KEY DECISIONS:
• Orchestrator: AgentCore Runtime (Fully-Managed, 8-Hour Sessions)
• Prompts: LangFuse (Versioned, A/B Testable)
• APIs: AgentCore Gateway (REST → MCP, Zero Code Changes)
• Scale: 27K Doctors, 500K Patients, Auto-Scaling
• Security: HIPAA/SOC 2, Session Isolation
```

---

## Even More Compact Version (For Tight Slides)

```
TRIGGERS → API Gateway → AgentCore Runtime
                              │
                    ┌─────────┴─────────┐
                    │ Supervisor Agent  │ (LangFuse Prompts, AgentCore Memory)
                    │  6-Stage Workflow │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    [Smart] [Patient] [Backfill] [QA] [Audit] Agents
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    AgentCore Gateway (MCP)
                              │
        Existing APIs (Provider│Patient│Appointment│Notification│Waitlist│Knowledge)
                              │
                    Observability (AgentCore│LangFuse│Custom)
                              
Features: A/B Testing │ Quality Gates │ Evaluations │ Auto-Scaling │ HIPAA/SOC 2
Scale: 27K Doctors, 500K Patients
```

