# Views Analysis: SDUI vs Static UI

Analysis of the 6 screens in `views/` to determine what to build as SDUI (runtime JSON-driven) vs static/traditional React UI.

---

## Screen Overview

| Screen | File | Flow |
|--------|------|------|
| 1 | screen-1-show-me-pending-referral.png | Dashboard / Home — greeting, alerts, suggested actions |
| 2 | screen-2-show-and-select-form-not-legible.png | Referral form preview — AI says form not legible, user selects reason |
| 3 | screen-3-send-mail.png | Send mail — AI-generated message to clinic, action icons |
| 4 | screen-4-email-confirmation-pending-referral.png | Email sent confirmation — success message, next action |
| 5 | screen-5-mail-sent-show-appointment.png | Post-email — "Show appointments" prompt, workflow transition |
| 6 | sacreen-6-scheduler-calender-view.png | Scheduler — weekly/daily view, appointment cards grid |

---

## Global Pattern: App Shell (Static)

**Same across all screens — build once, keep static:**

| Element | Location | Notes |
|---------|----------|-------|
| Logo (webpt) | Header left | Brand, static |
| Global search bar | Header center | Component static; suggestions could be SDUI later |
| Utility icons | Header right | Grid, filter, notifications, chat |
| User profile | Header right | John Doe, Santa Clara Street — layout static, data injected |
| Bottom search/ask bar | Footer | "Search or ask: patient status, eligibility..." |
| Navigation icons | Footer | History, 12 Tasks, 5 Activities — structure static, counts dynamic |
| Day's Summary bar | Footer | Structure can be SDUI; see below |

---

## Screen-by-Screen Breakdown

### Screen 1: Dashboard / Pending Referrals

| Area | SDUI? | Components | Rationale |
|------|-------|-------------|-----------|
| Greeting | ✅ SDUI | Text | "Good Morning John" — personalized, time-based |
| Appointment summary | ✅ SDUI | Text | "28 Appointments... sent reminders" — dynamic count |
| Pending referrals alert | ✅ SDUI | Alert/Banner | Conditional; "2 referrals" — dynamic; visibility + content |
| "Show Me Pending Referrals" button | ✅ SDUI | Button | Conditional; action = navigate |
| "Or Shall I help you with" | ✅ SDUI | Text | Optional conditional |
| Suggested action buttons | ✅ SDUI | Row + Buttons | "Review Completed Tasks", "Quick Patient Intake", "Scheduling" — labels + actions dynamic |
| Illustration (right) | ❌ Static | Image | Decorative, fixed |

**SDUI components needed:** Text, Alert/Banner, Button, Row

---

### Screen 2: Form Not Legible — Select Reason

| Area | SDUI? | Components | Rationale |
|------|-------|-------------|-----------|
| AI message | ✅ SDUI | Message/Card | "I am unable to read the referral form" — dynamic, highlighted |
| Form preview (image) | ❌ Static | Image | Document viewer; content is data, not UI structure |
| Download / expand icons | ❌ Static | IconButton | Fixed actions |
| "Request Revised Form" + dropdown | ✅ SDUI | Button, Dropdown | Options: "Information missing", "Form not legible", "Send custom message" — server-driven |
| "Complete Registration" | ✅ SDUI | Button | Visibility + action dynamic |
| Day's Summary | ✅ SDUI | SummaryStat / Row | Dynamic counts |

**SDUI components needed:** Message, Button, Dropdown, Text

---

### Screen 3: Send Mail

| Area | SDUI? | Components | Rationale |
|------|-------|-------------|-----------|
| Instructional text | ✅ SDUI | Text | "Here is your message for Dr. Chris David's clinic..." |
| Message bubble content | ✅ SDUI | Message/Card | Email body — dynamic, context-specific |
| Action icons (mail, chat, document) | ✅ SDUI | Row + IconButton | Presence, actions dynamic |
| "Request Revised Form" / "Complete Registration" | ✅ SDUI | Button | Same as Screen 2 |
| Day's Summary | ✅ SDUI | SummaryStat | Dynamic |

**SDUI components needed:** Text, Message, Card, IconButton, Row

---

### Screen 4: Email Confirmation

| Area | SDUI? | Components | Rationale |
|------|-------|-------------|-----------|
| Referral form snippet card | ✅ SDUI | Card | Structure + buttons |
| Message bubbles | ✅ SDUI | Message | Timestamps, content, action icons |
| Success message | ✅ SDUI | StatusMessage | "Email successfully sent..." — icon + text + color |
| "Next Pending Referral" button | ✅ SDUI | Button | Visibility + action |
| Day's Summary | ✅ SDUI | SummaryStat | Dynamic |

**SDUI components needed:** Card, Message, StatusMessage, Button

---

### Screen 5: Mail Sent — Show Appointments

| Area | SDUI? | Components | Rationale |
|------|-------|-------------|-----------|
| Status update | ✅ SDUI | StatusMessage | "Email sent. You have successfully resolved..." |
| "Next: Schedules to Review" | ✅ SDUI | Text | Dynamic prompt |
| Referral summary | ✅ SDUI | Text | "Out of 20 referrals I have scheduled 15..." — numbers dynamic |
| "Yes, Show These Appointments" | ✅ SDUI | Button | Action = navigate to scheduler |
| Request Revised / Complete Registration | ✅ SDUI | Button | Same pattern |
| Day's Summary | ✅ SDUI | SummaryStat | Dynamic |

**SDUI components needed:** StatusMessage, Text, Button

---

### Screen 6: Scheduler / Calendar View

| Area | SDUI? | Components | Rationale |
|------|-------|-------------|-----------|
| Alert banners | ✅ SDUI | AlertBanner | "Copay not collected...", "Claim rejected..." — content, type, visibility |
| Summary text | ✅ SDUI | Text | "15 appointments scheduled out of 20 referrals" |
| View toggle | ✅ SDUI | SegmentedControl | "Weekly View | Daily View" — active state, actions |
| "View Detailed Schedules" | ✅ SDUI | Button | Action dynamic |
| Weekly grouping headers | ✅ SDUI | WeeklyHeader | "26 Feb - 01 Mar 2026 (7)" — dateRange, count |
| Appointment cards grid | ✅ SDUI | AppointmentCard | Patient, doctor, insurance, time, status — **primary SDUI** |
| Status indicators on cards | ✅ SDUI | (part of AppointmentCard) | Valid, Expiring, High No-Show, Invalid — conditional styling |
| Day's Summary | ✅ SDUI | SummaryStat | Dynamic |

**SDUI components needed:** AlertBanner, Text, SegmentedControl, Button, WeeklyHeader, AppointmentCard

**Note:** Calendar engine (grid, dates, drag-drop) stays **static**. SDUI configures it (view, grouping) and renders the appointment cards within it.

---

## Consolidated Component List

### SDUI Components (Register in Renderer)

| Component | Used In | Props / Data |
|-----------|--------|--------------|
| **Text** | All screens | value, variant, style |
| **Button** | All screens | label, variant, action |
| **Alert / Banner** | 1, 6 | message, type (warning/error), visible |
| **Card** | 2, 3, 4 | children, elevation, style |
| **Message** | 2, 3, 4, 5 | content, timestamp, actions |
| **StatusMessage** | 4, 5 | text, icon, color (success/error) |
| **Dropdown** | 2 | options, label, action |
| **Row / Column** | All | children, layout |
| **IconButton** | 2, 3, 4 | icon, action |
| **SummaryStat** | All (Day's Summary) | items: [{ label, value, action? }] |
| **SegmentedControl** | 6 | options, activeIndex, onChange |
| **WeeklyHeader** | 6 | dateRange, count |
| **AppointmentCard** | 6 | patient, doctor, insurance, datetime, status |
| **CalendarScheduler** | 6 | view, grouping, actions (wrapper) |

### Static UI (Normal React)

| Element | Notes |
|--------|-------|
| App shell | Header, footer, nav |
| Logo | Brand |
| Search bar (structure) | Input component |
| Document viewer | Form preview image container |
| Calendar engine | FullCalendar or custom grid — dates, slots |
| Illustrations | Decorative images |

---

## Data Injection Mapping

| SDUI Component | dataSource Example | Injected Fields |
|----------------|-------------------|-----------------|
| Text (greeting) | userContext | name, timeOfDay |
| Text (summary) | /api/dashboard/summary | appointmentCount, referralCount |
| Alert | /api/alerts | message, type |
| SummaryStat | /api/day-summary | appointments, authorizations, benefits, copays |
| AppointmentCard | /api/appointments | patient, doctor, insurance, datetime, status |
| Message | conversationContext | content, timestamp |

---

## Recommendation Summary

| Build As | Scope |
|----------|-------|
| **SDUI** | Main content area of each screen: greetings, alerts, messages, action buttons, Day's Summary, scheduler controls, appointment cards |
| **Static** | App shell (header, footer), logo, search bar structure, document viewer container, calendar grid engine |
| **Hybrid** | Shell is static; main content area = `<SDUIRenderer spec={spec} />` |

This aligns with the existing architecture: SDUI for dynamic, role/context-driven content; static for performance-critical and fixed structure.
