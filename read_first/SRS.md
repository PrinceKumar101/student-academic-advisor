# Student Academic Advisor

## Complete Project Specification & Implementation Plan

**Project Type:** AI-Assisted Full-Stack Academic Performance Analysis System  
**Primary Language:** Python  
**Frontend:** React + TypeScript  
**Backend:** FastAPI  
**Database:** SQLite + SQLAlchemy  
**AI:** OpenAI API  
**Charts:** Recharts  
**Styling:** Tailwind CSS

---

# 1. Project Overview

## 1.1 Project Name

**Student Academic Advisor**

## 1.2 One-Line Description

Student Academic Advisor is a full-stack application that analyzes a student's academic information, identifies potential academic risks, explains the reasons behind those risks, and uses an AI API to provide personalized recommendations and study plans.

## 1.3 Problem Statement

Students often receive academic information in separate places: attendance records, internal marks, assignments, quizzes, previous examination results, and other academic activities.

Because this information is scattered, students may not realize that their academic performance is declining until examinations are approaching.

Teachers also have difficulty manually monitoring every student's academic progress, especially when dealing with large classes.

The proposed system combines academic data into one platform and provides:

- Academic performance analysis
- Risk assessment
- Performance trend detection
- Identification of weak areas
- Explanation of risk factors
- Personalized recommendations
- AI-generated study plans
- What-if simulations
- Teacher/class-level analytics
- Intervention tracking

The system should act as an **academic decision-support and advisory system**, not as a replacement for teachers.

---

# 2. Important Project Principle

The system should NOT falsely claim that an AI model has been trained to predict student performance.

The project will use a **Python-based academic risk scoring algorithm** for quantitative risk assessment.

The AI API will be used for:

- Understanding the student's situation
- Generating explanations
- Generating personalized recommendations
- Creating study plans
- Answering academic questions using the student's available context

Therefore:

**Python = calculation, analysis and business logic**

**AI API = intelligent interpretation and personalized assistance**

This makes the architecture technically honest and feasible for a college project.

---

# 3. Main Objectives

The system should:

1. Store student academic information.
2. Calculate an academic risk score.
3. Categorize students into Low, Medium, and High risk.
4. Track performance over time.
5. Identify declining performance.
6. Identify major contributing factors.
7. Explain why a student has a particular risk level.
8. Generate personalized recommendations using an AI API.
9. Generate personalized study plans.
10. Allow students to perform what-if simulations.
11. Allow teachers to monitor students.
12. Allow teachers to create interventions.
13. Track whether student performance improves after intervention.
14. Present all important information through a clean dashboard.

---

# 4. User Roles

The application should have two primary roles.

## 4.1 Student

A student should be able to:

- Create/login to an account
- View personal academic information
- View current risk level
- View risk score
- View performance trends
- View weak areas
- Ask the AI academic assistant questions
- Generate a personalized study plan
- Use the what-if simulator
- View recommendations
- View previous recommendations
- View assigned interventions
- Track improvement

## 4.2 Teacher

A teacher should be able to:

- Login to the teacher dashboard
- View class statistics
- View students
- Filter students by risk level
- View individual student performance
- View performance trends
- Identify high-risk students
- View reasons for risk
- Create interventions
- Track intervention progress
- View class-level trends
- Generate reports

---

# 5. Core Features

## Feature 1 — Student Profile

Store basic non-sensitive academic information.

Example:

- Student ID
- Name
- Email
- Department
- Semester
- Section
- Subjects

Avoid storing unnecessary personal information.

---

# 6. Feature 2 — Academic Data Management

The system should allow academic records to be stored.

Possible data:

### Attendance

- Subject
- Total classes
- Classes attended
- Attendance percentage

### Internal Assessment

- Subject
- Test name
- Maximum marks
- Obtained marks

### Assignments

- Subject
- Assignment name
- Maximum marks
- Obtained marks
- Submission status

### Quizzes

- Subject
- Quiz name
- Maximum marks
- Obtained marks

### Previous Performance

- Semester
- GPA/percentage
- Overall result

### Study Habits

Optional fields:

- Average study hours per day
- Assignment completion rate
- Self-reported confidence

The system should support historical records rather than storing only the latest values.

---

# 7. Feature 3 — Academic Risk Score

The system should calculate an academic risk score from 0 to 100.

Example interpretation:

```text
0–30    = Low Risk
31–60   = Medium Risk
61–100  = High Risk

```

The score should be generated using a transparent weighted algorithm.

Suggested initial weighting:

```text
Attendance          25%
Internal Marks      25%
Assignment          15%
Quiz Performance    15%
Previous Performance 10%
Study Habits        10%

```

These values are initial assumptions and should be configurable.

The algorithm must normalize different metrics before calculating the final score.

Example:

```text
Attendance Risk = function of attendance percentage
Academic Risk = function of marks
Assignment Risk = function of completion/performance
Quiz Risk = function of quiz performance
Historical Risk = function of previous performance
Study Risk = function of study habits

```

The final score should be calculated deterministically.

Do NOT use arbitrary random values.

---

# 8. Feature 4 — Risk Factor Explanation

The application should not only display:

```text
HIGH RISK

```

It should explain why.

Example:

```text
Risk Score: 78/100
Risk Level: HIGH

Major contributing factors:

1. Attendance — High concern
2. Internal marks — High concern
3. Quiz performance — Moderate concern
4. Assignment completion — Moderate concern

```

The system should show the quantitative contribution where possible.

Example:

```text
Attendance       ██████████
Internal Marks   ████████
Quiz             █████
Assignments      ████
Study Habits     ███

```

The quantitative calculation should come from Python.

The natural-language explanation can be generated by the AI API.

---

# 9. Feature 5 — Performance Trend Analysis

The system should store historical academic records.

Instead of looking only at current marks, calculate trends.

Examples:

```text
Internal Marks

Test 1 → 72
Test 2 → 68
Test 3 → 61
Test 4 → 54

```

The system should identify:

- Improvement
- Decline
- Stable performance
- Sudden drop

Example output:

> Your internal assessment performance has declined consistently over the last three assessments.

The trend detection itself should primarily use Python/statistical calculations.

AI may be used to explain the trend in natural language.

---

# 10. Feature 6 — Subject-Level Analysis

The system should calculate performance separately for each subject.

Example:

```text
Data Structures       48%   HIGH CONCERN
DBMS                  62%   MODERATE
Operating Systems     74%   GOOD
Computer Networks     81%   GOOD

```

This allows the application to determine where the student should spend more time.

---

# 11. Feature 7 — AI Academic Advisor

This is the primary AI feature.

The system should send relevant student information to the AI API.

Example context:

```text
Student academic summary:

Attendance: 68%
Average internal marks: 52%
Assignment completion: 61%
Average quiz score: 48%
Previous GPA: 6.2
Average study time: 1.5 hours/day

Risk score: 76
Risk level: High

Weak subjects:
- Data Structures
- DBMS

Recent trend:
- Internal marks declining
- Attendance declining

```

The AI should then generate:

- Main concerns
- Possible reasons
- Recommended actions
- Short-term improvement plan
- Study priorities

The AI response should NOT invent academic data.

The prompt must explicitly instruct the AI to use only supplied information and clearly identify assumptions.

---

# 12. Feature 8 — AI Study Planner

Students should be able to generate a study plan.

Inputs:

- Subjects
- Weak subjects
- Exam date
- Available hours per day
- Current performance
- Preferred study schedule
- Existing commitments

Example:

```text
Exam Date: 30 days away
Available Study Time: 2 hours/day

Weak subjects:
1. Data Structures
2. DBMS

Strong subjects:
1. Operating Systems
2. Computer Networks

```

The AI should generate a realistic plan.

The output should contain:

- Date/day
- Subject
- Topic
- Duration
- Suggested activity
- Priority

The plan should be returned in structured JSON so that the frontend can display it properly.

---

# 13. Feature 9 — What-If Simulator

This should be one of the project's standout features.

The student can modify hypothetical values and see how the risk score changes.

Example:

```text
Current:

Attendance: 64%
Internal: 48%
Assignments: 55%
Quiz: 42%

Risk Score: 82
Risk Level: HIGH

```

Student changes:

```text
Attendance → 80%
Internal → 60%

```

The system recalculates:

```text
New Risk Score: 63
Risk Level: MEDIUM

```

The simulation must use the same Python risk calculation algorithm.

The AI API is not required for the calculation.

Optionally, AI can explain:

> Improving attendance has the largest impact on your current risk score.

---

# 14. Feature 10 — AI Academic Chat Assistant

Provide a chat interface for students.

Possible questions:

- Why am I at high risk?
- Which subject should I focus on?
- How can I improve my internal marks?
- Make a 7-day study plan.
- I have two hours today. What should I study?
- Explain my performance trend.
- What should I prioritize before my next test?

The AI should receive relevant academic context.

The assistant must not pretend to be a teacher or medical/psychological professional.

It should provide educational guidance and recommend contacting a teacher when appropriate.

---

# 15. Feature 11 — Early Warning Detection

The system should detect significant negative changes.

Examples:

```text
Attendance:
82% → 67%

Internal:
72 → 54

Quiz:
76 → 48

```

The system can generate:

```text
⚠ Performance deterioration detected

Attendance decreased by 15 percentage points.
Internal performance decreased by 18 points.

```

Possible triggers:

- Significant drop in marks
- Significant attendance decline
- Repeated missed assignments
- Multiple poor quizzes
- Overall risk score increasing

Thresholds should be configurable.

---

# 16. Feature 12 — Teacher Dashboard

Teacher dashboard should provide a class overview.

Example:

```text
Total Students: 60

Low Risk:       38
Medium Risk:    15
High Risk:       7

```

The teacher should be able to:

- Search students
- Filter by risk
- Sort by risk score
- View individual student profiles
- View performance trends
- View weak subjects
- View intervention history

---

# 17. Feature 13 — Intervention System

Teachers should be able to create interventions.

Example:

```text
Student: Rahul

Intervention:
Attend additional tutorial sessions

Priority:
High

Deadline:
20 September

Notes:
Focus on Data Structures.

```

Student sees:

```text
Assigned Intervention

✓ Attend tutorial
○ Complete practice set
○ Meet teacher

```

The student can update completion status.

---

# 18. Feature 14 — Intervention Effectiveness

This feature makes the project more meaningful.

Before intervention:

```text
Risk Score: 84

```

After intervention:

```text
Risk Score: 62

```

The system should display:

```text
Risk decreased by 22 points.

```

It should also compare:

- Attendance
- Marks
- Assignment completion
- Quiz performance

This demonstrates that the system is not just identifying problems but also tracking improvement.

Do not claim that the intervention caused the improvement scientifically. The system can report an association/comparison, but not causal proof.

---

# 19. Feature 15 — Class Analytics

Teachers should have charts for:

- Average attendance
- Average marks
- Risk distribution
- Subject performance
- Performance trends
- Assignment completion
- Quiz performance

Example:

```text
Subject Performance

DSA       ███████
DBMS      ████████
OS        █████████
CN        █████████

```

---

# 20. AI API Design

Use the AI API only where it adds meaningful value.

Do NOT send every calculation to the AI.

Python should handle:

- Percentages
- Averages
- Risk calculations
- Trends
- Comparisons
- Thresholds
- Database operations

AI should handle:

- Natural-language explanations
- Recommendations
- Study plans
- Conversational assistance
- Summaries

This reduces cost and improves reliability.

---

# 21. Structured AI Responses

AI responses should preferably use structured JSON.

Example:

```json
{
  "summary": "The student is currently at high academic risk.",
  "main_concerns": [
    {
      "factor": "Attendance",
      "severity": "high",
      "explanation": "Attendance is significantly below the configured threshold."
    }
  ],
  "recommendations": [
    "Improve attendance",
    "Focus on weak subjects",
    "Complete pending assignments"
  ],
  "priority": "high"
}

```

Do not directly trust arbitrary AI text for database operations.

Validate AI output before displaying/storing it.

---

# 22. Database Design

Use SQLite initially.

Use SQLAlchemy ORM.

Suggested tables:

## users

```text
id
name
email
password_hash
role
created_at

```

## students

```text
id
user_id
student_id
department
semester
section

```

## subjects

```text
id
name
code
semester

```

## enrollments

```text
id
student_id
subject_id

```

## attendance

```text
id
student_id
subject_id
total_classes
classes_attended
percentage
date

```

## assessments

```text
id
student_id
subject_id
type
name
maximum_marks
obtained_marks
date

```

Assessment types:

```text
internal
quiz
assignment
exam

```

## study_habits

```text
id
student_id
study_hours
assignment_completion
recorded_at

```

## risk_assessments

```text
id
student_id
risk_score
risk_level
attendance_component
academic_component
assignment_component
quiz_component
historical_component
study_component
created_at

```

## interventions

```text
id
student_id
teacher_id
title
description
priority
status
due_date
created_at
completed_at

```

## ai_advice

```text
id
student_id
type
content
created_at

```

## study_plans

```text
id
student_id
title
start_date
end_date
created_at

```

## study_plan_items

```text
id
study_plan_id
date
subject
topic
duration
priority
completed

```

---

# 23. Backend Architecture

Use FastAPI.

Recommended structure:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── academics.py
│   │   ├── risk.py
│   │   ├── ai.py
│   │   ├── study_plans.py
│   │   ├── interventions.py
│   │   └── analytics.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── risk_engine.py
│   │   ├── trend_engine.py
│   │   ├── analytics_service.py
│   │   └── ai_service.py
│   │
│   ├── database/
│   └── core/
│
├── tests/
├── requirements.txt
└── .env.example

```

---

# 24. Risk Engine

Create a dedicated Python service:

```text
risk_engine.py

```

It should contain functions such as:

```python
calculate_attendance_risk()
calculate_academic_risk()
calculate_assignment_risk()
calculate_quiz_risk()
calculate_historical_risk()
calculate_study_habit_risk()
calculate_total_risk()
get_risk_level()

```

Keep this logic independent from FastAPI routes.

This will make testing much easier.

---

# 25. Frontend Architecture

Use:

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Recharts

Suggested structure:

```text
frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── hooks/
│   ├── types/
│   ├── utils/
│   └── App.tsx

```

---

# 26. Initial Pages

Do NOT spend significant time polishing these pages initially.

Build functional versions first.

### Authentication

- Login
- Register

### Student

- Dashboard
- Academic Performance
- Risk Analysis
- Subject Analysis
- What-If Simulator
- AI Advisor
- Study Planner
- Interventions
- Profile

### Teacher

- Dashboard
- Students
- Student Details
- Class Analytics
- Interventions

---

# 27. Authentication

Implement:

```text
Register
   ↓
Hash password
   ↓
Store user
   ↓
Login
   ↓
JWT token
   ↓
Authenticated API requests

```

Passwords must never be stored as plain text.

Use secure password hashing.

Role-based authorization should prevent students from accessing teacher-only functionality.

---

# 28. API Endpoints

Initial API design:

## Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me

```

## Students

```text
GET /students/me
GET /students/{id}
PUT /students/{id}

```

## Academic Data

```text
GET /students/{id}/attendance
POST /students/{id}/attendance

GET /students/{id}/assessments
POST /students/{id}/assessments

```

## Risk

```text
GET /students/{id}/risk
POST /students/{id}/risk/recalculate

```

## Trends

```text
GET /students/{id}/trends

```

## AI

```text
POST /ai/analyze-performance
POST /ai/generate-study-plan
POST /ai/chat

```

## What-If

```text
POST /students/{id}/what-if

```

## Interventions

```text
GET /students/{id}/interventions
POST /students/{id}/interventions
PUT /interventions/{id}

```

## Analytics

```text
GET /teacher/dashboard
GET /teacher/students
GET /teacher/analytics

```

---

# 29. Security Requirements

The project should include basic security.

1. Never hardcode API keys.
2. Store secrets in `.env`.
3. Add `.env` to `.gitignore`.
4. Never expose the AI API key to the React frontend.
5. AI requests must go through FastAPI.
6. Hash user passwords.
7. Validate API inputs.
8. Implement role-based access.
9. Students should only access their own academic data.
10. Teachers should only access students/classes they are authorized to manage.

---

# 30. AI Privacy Requirements

Do not send unnecessary personal information to the AI API.

The AI generally only needs academic context such as:

```text
Attendance: 68%
Average marks: 54%
Risk score: 72
Weak subjects: DSA, DBMS
Trend: declining

```

Avoid sending:

- Passwords
- Personal identifiers
- Unnecessary contact information
- Sensitive personal information

For demonstrations, use synthetic student data.

---

# 31. Data Strategy

The application needs realistic academic data for demonstration.

Do not depend on real student data.

Create a synthetic dataset with realistic variation.

Example:

```text
100 students
5 subjects
Multiple assessments
Attendance records
Assignment records
Quiz records
Historical performance

```

The synthetic dataset should intentionally contain different student profiles:

### High-performing student

High attendance + high marks.

### Struggling student

Low attendance + low marks.

### Improving student

Initially poor but improving.

### Declining student

Initially good but gradually declining.

### Inconsistent student

Highly variable results.

This will allow the dashboard and trend features to demonstrate meaningful scenarios.

---

# 32. Seed Data

Create a database seeding script.

Example:

```text
scripts/
    seed_database.py

```

It should generate:

- Teachers
- Students
- Subjects
- Academic records
- Historical assessments
- Attendance
- Assignments
- Quizzes

The project should be runnable with one command to populate demo data.

---

# 33. Testing Strategy

Testing should happen BEFORE UI polishing.

## Unit tests

Test:

- Attendance calculations
- Marks calculations
- Risk calculation
- Risk categories
- Trend detection
- What-if calculations

Example:

```text
Given:
Attendance = 90
Marks = 90

Expected:
Low Risk

```

## API tests

Test:

- Login
- Authentication
- Student endpoints
- Teacher endpoints
- Risk endpoints
- AI endpoints

## Security tests

Check:

- Student cannot access another student's data.
- Student cannot access teacher endpoints.
- Invalid tokens are rejected.

---

# 34. AI Failure Handling

The application must continue functioning if the AI API is unavailable.

For example:

```text
AI unavailable.

Your calculated risk score is still available.

Risk Level: HIGH
Risk Score: 78

Please try AI recommendations again later.

```

Never make the entire application dependent on the AI API.

---

# 35. AI Cost Control

Do not call the AI API for:

- Simple calculations
- Percentages
- Risk scores
- Charts
- Sorting
- Filtering

Only call it for tasks where natural-language intelligence is useful.

Potential AI calls:

```text
Performance explanation
Study plan generation
Academic chat
Personalized recommendations

```

---

# 36. Development Phases

The project must be developed in phases.

Do NOT begin by spending significant time on visual design.

---

## PHASE 1 — Requirements & Project Setup

Tasks:

1. Finalize requirements.
2. Finalize user roles.
3. Finalize technology stack.
4. Create project repository.
5. Create frontend and backend directories.
6. Configure Git.
7. Configure `.gitignore`.
8. Create `.env.example`.
9. Create Python virtual environment.
10. Configure React/Vite.
11. Configure FastAPI.

### Deliverable

A clean project skeleton that runs locally.

---

# PHASE 2 — Database Design

Tasks:

1. Design database schema.
2. Create SQLAlchemy models.
3. Configure SQLite.
4. Create database initialization.
5. Create migrations if required.
6. Create seed-data generator.
7. Generate realistic demo data.

### Deliverable

Working database containing realistic academic data.

---

# PHASE 3 — Authentication & Authorization

Tasks:

1. Implement registration.
2. Implement login.
3. Hash passwords.
4. Implement JWT authentication.
5. Implement role-based access.
6. Protect student endpoints.
7. Protect teacher endpoints.

### Deliverable

Secure basic authentication system.

---

# PHASE 4 — Academic Data Backend

Implement:

- Student profiles
- Subjects
- Attendance
- Assessments
- Assignments
- Quizzes
- Historical performance
- Study habits

Create APIs for reading and updating this information.

### Deliverable

Complete backend academic data management.

---

# PHASE 5 — Academic Risk Engine

Implement the Python risk calculation system.

Tasks:

1. Normalize metrics.
2. Calculate individual risk components.
3. Calculate total score.
4. Categorize risk.
5. Identify major risk factors.
6. Implement configurable thresholds.
7. Add unit tests.

### Deliverable

Reliable deterministic academic risk engine.

---

# PHASE 6 — Trend & Analytics Engine

Implement:

- Performance trends
- Subject-level analysis
- Attendance trends
- Mark trends
- Assignment trends
- Risk-score trends
- Early-warning detection

### Deliverable

Backend analytics system capable of explaining performance changes.

---

# PHASE 7 — What-If Simulation

Implement a simulation API.

Input:

```text
Current academic data
+
Hypothetical changes

```

Output:

```text
Current score
New score
Current risk level
New risk level
Changed factors

```

The simulation must NOT modify the actual student record.

### Deliverable

Functional academic what-if simulator.

---

# PHASE 8 — AI Integration

Implement an isolated AI service.

Create:

```text
ai_service.py

```

Functions:

```python
analyze_student_performance()
generate_recommendations()
generate_study_plan()
answer_student_question()

```

Tasks:

1. Configure API key through environment variables.
2. Create reusable AI client.
3. Create prompts.
4. Request structured outputs.
5. Validate AI responses.
6. Handle API errors.
7. Add timeout handling.
8. Prevent unnecessary API calls.

### Deliverable

Working AI-assisted academic advisor.

---

# PHASE 9 — AI Study Planner

Implement:

1. Student input form.
2. Academic context generation.
3. AI request.
4. Structured study plan response.
5. Validation.
6. Storage in database.
7. Display of study plan.
8. Completion tracking.

### Deliverable

Personalized AI study planner.

---

# PHASE 10 — AI Chat Assistant

Implement:

1. Chat API.
2. Student academic context.
3. Conversation handling.
4. AI response generation.
5. Basic conversation history.
6. Error handling.

The assistant should have strict instructions not to fabricate academic data.

### Deliverable

Functional AI academic assistant.

---

# PHASE 11 — Teacher Features

Implement:

1. Teacher dashboard APIs.
2. Student listing.
3. Risk filtering.
4. Student details.
5. Class statistics.
6. Class analytics.
7. Intervention creation.
8. Intervention tracking.

### Deliverable

Functional teacher-side system.

---

# PHASE 12 — Intervention Tracking

Implement:

1. Create intervention.
2. Assign intervention to student.
3. Student sees intervention.
4. Student updates status.
5. Store completion date.
6. Compare before/after academic metrics.
7. Show improvement.

### Deliverable

Complete intervention workflow.

---

# PHASE 13 — Frontend Functional UI

Only after backend functionality is stable.

Create functional pages:

Student:

```text
Dashboard
Performance
Risk Analysis
Subjects
What-If
AI Advisor
Study Planner
Interventions

```

Teacher:

```text
Dashboard
Students
Student Details
Analytics
Interventions

```

At this stage prioritize functionality over visual perfection.

### Deliverable

Entire application usable from the browser.

---

# PHASE 14 — Integration Testing

Test the complete user journeys.

## Student Journey

```text
Login
 ↓
Dashboard
 ↓
View performance
 ↓
View risk
 ↓
Understand risk
 ↓
Use what-if simulator
 ↓
Ask AI advisor
 ↓
Generate study plan
 ↓
Complete intervention
 ↓
View improvement

```

## Teacher Journey

```text
Login
 ↓
Teacher dashboard
 ↓
Identify high-risk students
 ↓
Open student
 ↓
Analyze performance
 ↓
Create intervention
 ↓
Monitor improvement

```

### Deliverable

End-to-end working system.

---

# PHASE 15 — UI Design & Visual Polish

This MUST be one of the final phases.

Only after functionality is stable.

Tasks:

1. Establish visual design system.
2. Improve typography.
3. Improve spacing.
4. Improve dashboard layout.
5. Add meaningful icons.
6. Improve charts.
7. Improve cards.
8. Add loading states.
9. Add empty states.
10. Add error states.
11. Improve forms.
12. Improve responsive design.
13. Improve navigation.
14. Improve accessibility.
15. Add subtle animations only where useful.

Avoid excessive animations or decorative elements.

The interface should look like a professional academic analytics product.

---

# 37. Suggested UI Design Direction

The design should feel:

**Modern + Academic + Professional + Data-focused**

Avoid making it look like:

- A generic AI chatbot
- A gaming dashboard
- A template-heavy admin panel

The dashboard should prioritize information hierarchy.

Example:

```text
Student Dashboard

Good morning, Rahul

┌────────────┐ ┌────────────┐ ┌────────────┐
│ Risk Score │ │ Attendance │ │ Avg Marks  │
│    62      │ │    78%     │ │    68%     │
└────────────┘ └────────────┘ └────────────┘

Performance Trend
────────────────────────────
             ╱──╲
        ╱───╯    ╲
   ────╯

Areas Requiring Attention
────────────────────────────
DSA                 High
DBMS                Medium

AI Recommendation
────────────────────────────
"Focus on DSA for the next..."

```

---

# 38. Dashboard Design Principle

Do not show every piece of information at once.

The student should immediately understand:

1. Am I doing well?
2. What is my current risk?
3. Why?
4. What should I do next?

The teacher should immediately understand:

1. How is the class performing?
2. Which students need attention?
3. Why do they need attention?
4. What interventions are active?

---

# 39. Error & Loading States

Every asynchronous operation should have:

### Loading

```text
Analyzing your performance...

```

### Success

```text
Analysis completed.

```

### Error

```text
Unable to generate AI recommendations.
Your academic analysis is still available.

```

Never leave blank screens.

---

# 40. Project Demo Scenario

The final demonstration should use a prepared student.

Example:

```text
Student: Rahul

```

Initial situation:

```text
Attendance: 64%
Internal: 48%
Assignments: 55%
Quiz: 42%
Previous GPA: 6.1

```

System calculates:

```text
Risk Score: 82
Risk Level: HIGH

```

Then demonstrate:

### Step 1

Show why Rahul is at risk.

### Step 2

Show performance decline.

### Step 3

Ask AI:

> Why am I at high risk?

### Step 4

Generate personalized study plan.

### Step 5

Use what-if:

```text
Attendance: 64% → 80%
Internal: 48 → 60

```

Show new risk.

### Step 6

Teacher creates intervention.

### Step 7

Update academic data.

### Step 8

Show improvement.

This creates a complete story rather than demonstrating disconnected features.

---

# 41. Project Evaluation / Viva Talking Points

The project should demonstrate the following concepts:

### Python

- Functions
- Classes
- Exception handling
- File handling
- Pandas
- NumPy
- Data processing
- Statistical calculations
- API integration

### Backend

- REST APIs
- Authentication
- Authorization
- Database interaction
- Validation

### Frontend

- React
- TypeScript
- API integration
- State management
- Charts
- Responsive UI

### AI

- LLM API integration
- Prompt engineering
- Structured AI responses
- Context-aware recommendations
- AI error handling

### Database

- Relational schema
- Relationships
- CRUD operations
- Historical data

---

# 42. What NOT to Build

To keep the project manageable:

Do NOT initially build:

- Mobile application
- Custom-trained ML model
- Computer vision
- Voice assistant
- Complex microservices
- Kubernetes
- Real-time messaging
- Complex recommendation algorithms
- Payment system

These add complexity without necessarily improving the academic value of the project.

---

# 43. Future Scope

These features can be mentioned as future improvements rather than implemented initially:

- Machine-learning-based prediction
- Mobile application
- Integration with college ERP
- Automatic attendance import
- LMS integration
- Email notifications
- Parent dashboard
- Advanced predictive analytics
- More sophisticated recommendation algorithms
- Multi-college deployment

---

# 44. Definition of Done

The project should not be considered complete until:

- Student authentication works.
- Teacher authentication works.
- Role-based authorization works.
- Database works.
- Student academic records work.
- Risk calculation works.
- Risk explanation works.
- Performance trends work.
- Subject analysis works.
- What-if simulation works.
- AI recommendations work.
- AI study planner works.
- AI chat works.
- Teacher dashboard works.
- Interventions work.
- Intervention tracking works.
- Error handling works.
- Tests pass.
- Seed/demo data works.
- Complete student workflow works.
- Complete teacher workflow works.
- UI is polished.
- README is complete.
- Environment setup is documented.

---

# 45. Instructions to Cursor

Treat this document as the **single source of truth** for the project.

Implementation rules:

1. Do not build the entire project in one step.
2. Work phase-by-phase.
3. Complete and test each phase before moving to the next.
4. Do not skip backend architecture in favor of UI.
5. Do not hardcode academic data.
6. Do not hardcode API keys.
7. Keep AI integration isolated from core business logic.
8. Keep risk calculations deterministic.
9. Write reusable services instead of putting all logic inside API routes.
10. Use type-safe frontend code.
11. Validate API inputs.
12. Handle API failures gracefully.
13. Write tests for important calculations.
14. Do not over-engineer the application.
15. Keep the project understandable enough for a college student to explain during a viva.
16. Do not polish the UI until the core functionality and integration are complete.
17. When implementing a phase, explain what files are being created/changed and why.
18. Do not silently introduce major technologies or architectural changes without documenting the reason.
19. Prefer simple solutions over unnecessary complexity.
20. Maintain a `README.md` containing setup, architecture, environment variables, database setup, and run instructions.

---

# 46. Recommended Development Order

The exact implementation order should be:

```text
Requirements
    ↓
Project Setup
    ↓
Database
    ↓
Authentication
    ↓
Academic Data
    ↓
Risk Engine
    ↓
Trend Engine
    ↓
What-If Simulator
    ↓
AI Integration
    ↓
Study Planner
    ↓
AI Assistant
    ↓
Teacher Dashboard
    ↓
Interventions
    ↓
Frontend Integration
    ↓
Testing
    ↓
UI Design
    ↓
UI Polish
    ↓
Documentation
    ↓
Final Demo

```

---

# 47. Final Product Vision

The final product should feel like:

> **A smart academic advisor that helps students understand where they stand academically, why they may be struggling, what they should focus on next, and how their choices could affect their academic risk. Teachers can use the same system to identify students who need attention and track their progress over time.**

The application should be useful even when the AI service is unavailable because the core academic analysis is performed by the Python backend.

AI should enhance the product, not become a dependency for basic functionality.

---

# 48. Initial Stack Summary

```text
Frontend
React
TypeScript
Vite
Tailwind CSS
Recharts

Backend
Python
FastAPI
Pydantic

Database
SQLite
SQLAlchemy

AI
OpenAI API

Authentication
JWT
Password hashing

Data Processing
Pandas
NumPy

Testing
Pytest
FastAPI TestClient

Version Control
Git / GitHub

```

Start with SQLite because this is a college project. PostgreSQL can be introduced later if deployment requirements justify it.

---

# 49. First Task for Cursor

Do NOT start implementing all features.

Start with **PHASE 1 — Requirements & Project Setup**.

Before writing application code:

1. Create the project structure.
2. Initialize frontend.
3. Initialize backend.
4. Configure environment variables.
5. Configure Git.
6. Create initial README.
7. Verify that the React frontend runs.
8. Verify that the FastAPI backend runs.
9. Create a basic health-check endpoint.
10. Document how to start both services.

After that phase is complete, stop and report:

- Files created
- Technologies configured
- Commands required to run the project
- Any assumptions made
- Any unresolved decisions

Then proceed to PHASE 2 only after verification.

---

# 50. Important Open Decisions

The following decisions can be finalized during implementation if necessary:

1. Exact risk-score weights
2. Exact thresholds for Low/Medium/High risk
3. Exact AI model/API configuration
4. Whether teachers can edit student academic records
5. Whether students can manually enter academic data or only teachers can enter it
6. Whether CSV import should be implemented
7. Whether notifications should be included
8. Whether the final deployment requires PostgreSQL

Do not let these unresolved decisions block the initial project setup.

Use sensible defaults, document them, and keep them configurable where practical.