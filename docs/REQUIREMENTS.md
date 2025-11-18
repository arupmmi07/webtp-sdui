# System Requirements

## Functional Requirements

### FR1: Trigger Detection & Prioritization
- **FR1.1:** System MUST detect therapist unavailability within 30 seconds
- **FR1.2:** System MUST identify all affected appointments
- **FR1.3:** System MUST calculate no-show risk for each patient
- **FR1.4:** System MUST calculate POC urgency for each appointment
- **FR1.5:** System MUST prioritize appointments using weighted scoring algorithm
- **FR1.6:** System MUST emit `trigger_detected` event with prioritized list

### FR2: Provider Filtering & Compliance
- **FR2.1:** System MUST apply 8 hard constraint filters in sequence
- **FR2.2:** System MUST validate required skills/certifications
- **FR2.3:** System MUST validate active license status
- **FR2.4:** System MUST validate POC authorization
- **FR2.5:** System MUST validate payer compliance rules
- **FR2.6:** System MUST validate location constraints
- **FR2.7:** System MUST validate telehealth vs. in-person availability
- **FR2.8:** System MUST validate provider availability
- **FR2.9:** System MUST validate provider capacity limits
- **FR2.10:** System MUST emit `candidates_filtered` event with qualified providers

### FR3: Provider Scoring & Ranking
- **FR3.1:** System MUST apply 5 scoring factors to qualified providers
- **FR3.2:** System MUST score continuity (0-40 points)
- **FR3.3:** System MUST score specialty match (0-35 points)
- **FR3.4:** System MUST score patient preference fit (0-30 points)
- **FR3.5:** System MUST score schedule load balance (0-25 points)
- **FR3.6:** System MUST score day/time match (0-20 points)
- **FR3.7:** System MUST rank providers by total score
- **FR3.8:** System MUST generate human-readable explanation for each score
- **FR3.9:** System MUST emit `candidates_scored` event with ranked list

### FR4: Patient Consent & Communication
- **FR4.1:** System MUST retrieve patient communication preferences
- **FR4.2:** System MUST support SMS, Email, and IVR channels
- **FR4.3:** System MUST send personalized offer message
- **FR4.4:** System MUST wait for patient response with configurable timeout (default 24h)
- **FR4.5:** System MUST handle YES response → book appointment
- **FR4.6:** System MUST handle NO response → offer next candidate
- **FR4.7:** System MUST handle INFO request → send detailed provider info
- **FR4.8:** System MUST handle timeout → send reminder via secondary channel
- **FR4.9:** System MUST retry up to 3 candidates before declaring failure
- **FR4.10:** System MUST emit `appointment_booked` or `consent_declined_all` event

### FR5: Waitlist & Backfill Automation
- **FR5.1:** System MUST add freed slot to intelligent waitlist
- **FR5.2:** System MUST query high no-show risk patients (risk >=0.6)
- **FR5.3:** System MUST prioritize waitlist patients by no-show risk score
- **FR5.4:** System MUST offer freed slot to high-risk patients
- **FR5.5:** System MUST retrieve original patient's availability windows
- **FR5.6:** System MUST search for alternative slots matching availability
- **FR5.7:** System MUST auto-propose alternative appointment
- **FR5.8:** System MUST assign to HOD if no match found
- **FR5.9:** System MUST flag for manual review when HOD assigned
- **FR5.10:** System MUST schedule extra reminders for high-risk patients
- **FR5.11:** System MUST emit `backfill_completed` or `manual_review_needed` event

### FR6: Audit & Reconciliation
- **FR6.1:** System MUST log all events with timestamps
- **FR6.2:** System MUST aggregate events into session-level audit log
- **FR6.3:** System MUST update EMR with all appointment changes
- **FR6.4:** System MUST generate reports for stakeholders
- **FR6.5:** System MUST notify all affected parties (patients, providers, staff)
- **FR6.6:** System MUST calculate session metrics (success rate, revenue impact)
- **FR6.7:** System MUST archive audit logs for 7 years (HIPAA)
- **FR6.8:** System MUST verify zero compliance violations
- **FR6.9:** System MUST emit `session_complete` event

## Non-Functional Requirements

### NFR1: Performance
- **NFR1.1:** Trigger detection MUST complete within 30 seconds
- **NFR1.2:** Filtering + Scoring MUST complete within 15 seconds per appointment
- **NFR1.3:** System MUST handle 15-50 appointments concurrently (MVP)
- **NFR1.4:** System MUST scale to 500+ appointments concurrently (Production)
- **NFR1.5:** MCP API calls MUST complete within 2 seconds
- **NFR1.6:** Average resolution time MUST be <8 hours (MVP), <4 hours (Production)

### NFR2: Reliability
- **NFR2.1:** System uptime MUST be >=95% (MVP), >=99.5% (Production)
- **NFR2.2:** System MUST handle transient failures with retry logic
- **NFR2.3:** System MUST gracefully degrade if external services unavailable
- **NFR2.4:** System MUST preserve state across restarts
- **NFR2.5:** No data loss allowed - all events MUST be logged

### NFR3: Scalability
- **NFR3.1:** System MUST support pluggable event queue (memory → Redis → Kafka)
- **NFR3.2:** System MUST support horizontal scaling of agents
- **NFR3.3:** System MUST support distributed deployment
- **NFR3.4:** Knowledge documents MUST be hot-reloadable without restart

### NFR4: Maintainability
- **NFR4.1:** System MUST use vendor-agnostic interfaces
- **NFR4.2:** LLM provider MUST be swappable via configuration
- **NFR4.3:** API backend MUST be swappable via configuration
- **NFR4.4:** Code MUST have >80% test coverage
- **NFR4.5:** All components MUST have unit tests
- **NFR4.6:** Critical workflows MUST have integration tests
- **NFR4.7:** Documentation MUST be kept up-to-date

### NFR5: Security & Compliance
- **NFR5.1:** System MUST be HIPAA compliant
- **NFR5.2:** All PHI MUST be encrypted in transit (TLS)
- **NFR5.3:** All PHI MUST be encrypted at rest (AES-256)
- **NFR5.4:** Audit logs MUST be tamper-proof
- **NFR5.5:** Access to patient data MUST be logged
- **NFR5.6:** System MUST support role-based access control (RBAC)
- **NFR5.7:** Audit logs MUST be retained for 7 years

### NFR6: Usability
- **NFR6.1:** CLI demo MUST provide real-time progress feedback
- **NFR6.2:** Error messages MUST be human-readable
- **NFR6.3:** Audit logs MUST be human-readable
- **NFR6.4:** Setup MUST complete in <15 minutes
- **NFR6.5:** Documentation MUST include setup guide, architecture, and examples

### NFR7: Extensibility
- **NFR7.1:** Adding new agent MUST NOT require changes to orchestrator
- **NFR7.2:** Adding new LLM provider MUST require only adapter + config change
- **NFR7.3:** Adding new API backend MUST require only adapter + config change
- **NFR7.4:** Adding new workflow MUST require only knowledge document update
- **NFR7.5:** System MUST support dynamic workflow creation from knowledge docs

## Data Requirements

### DR1: Patient Data
- Patient ID, Name, Age, Gender
- Contact: Phone, Email, Communication Preference
- Insurance: Type, Plan, Payer Rules
- Clinical: Condition, POC Status, POC Expiration
- History: Prior appointments, No-show count, No-show rate
- Preferences: Gender preference, Day/time preference, Location preference

### DR2: Provider Data
- Provider ID, Name, Gender, Age
- License: Status, Number, States
- Skills: Certifications, Specializations
- Capacity: Current load, Max capacity
- Availability: Schedule, Open slots
- Location: Clinic(s), Telehealth capability
- Payer: Accepted insurances, NPI registration

### DR3: Appointment Data
- Appointment ID
- Patient ID, Provider ID
- Date/Time, Duration
- Status: Scheduled, Confirmed, Canceled, Completed
- Clinical: Condition, Treatment type
- Insurance: Authorization status

### DR4: Knowledge Data
- Matching rules (8 filters)
- Scoring weights (5 factors)
- Payer rules (by insurance type)
- POC policies
- Communication policies
- No-show risk model
- Waitlist policies
- Workflow steps

## Integration Requirements

### IR1: MCP Servers
- Knowledge MCP Server MUST expose knowledge documents as resources
- Knowledge MCP Server MUST provide search capability
- Domain API MCP Server MUST expose Provider, Patient, Appointment, Notification, Waitlist APIs
- All MCP tools MUST follow MCP protocol specification
- MCP servers MUST be independently testable

### IR2: External Systems (Future)
- System SHOULD support WebPT API integration
- System SHOULD support Athena API integration
- System SHOULD support Twilio for SMS
- System SHOULD support SendGrid for Email
- System SHOULD support generic REST API backends

### IR3: Event System
- Events MUST include: event_type, timestamp, appointment_id, data
- Events MUST be serializable (JSON)
- Event bus MUST support pub/sub pattern
- Event bus MUST support at-least-once delivery

## Acceptance Criteria

### AC1: Use Case Coverage
- ✅ All 6 use cases implemented and tested
- ✅ All 8 filters working correctly
- ✅ All 5 scoring factors working correctly
- ✅ Multi-channel communication working (SMS/Email/IVR)
- ✅ Waitlist backfill working with high-risk targeting
- ✅ HOD assignment working as fallback
- ✅ Complete audit trail generated

### AC2: Demo Success
- ✅ CLI demo runs without errors
- ✅ Demo processes 15 appointments end-to-end
- ✅ All 6 stages visible in real-time
- ✅ Audit log generated and readable
- ✅ Metrics calculated correctly
- ✅ All 5 personas validated

### AC3: Quality Gates
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Test coverage >80%
- ✅ No linter errors
- ✅ Documentation complete
- ✅ Setup guide tested and working

### AC4: Flexibility
- ✅ LLM provider swap working
- ✅ API backend swap working
- ✅ Knowledge document changes reflected in behavior
- ✅ New workflow creatable without code changes

## Out of Scope (Post-MVP)

- Web UI (CLI only for MVP)
- Real-time dashboard
- Machine learning for no-show prediction
- Integration with actual EMR systems
- Mobile app
- Multi-tenant support
- Advanced analytics
- Automated capacity planning
- Provider recommendation engine
- Patient journey optimization

