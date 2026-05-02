# Campus Notifications Microservice Deliverables

## Overview
You are a backend developer working on a campus notification platform where students receive real-time updates regarding Placements, Events, and Results.
- Incrementally solve different tasks across stages.
- Commit and push deliverables to the **same GitHub Repository** that was created while implementing the Logging Middleware.
- Revise submissions for previous stages as you progress. Evaluated both individually and cumulatively.

## Strict Rules
- Ensure **Name** or any mention of **Affordmed** is entirely absent from Repository Name, README, and all commit messages.
- Submit comprehensive solutions (architecture design, complete code, clear output screenshots).
- Commit and push to GitHub regularly at logical milestones.
- Adhere to production-grade coding standards (naming conventions, organized folder structure, appropriate comments).
- For Backend track: select any Backend Framework without utilizing external libraries for algorithms.
- Capture output screenshots from API clients (Insomnia/Postman) displaying **request body, response and response time**. Screenshots must be of API calls to your app, not the test server.

## Repository Structure Requirements
For Backend track, create the following inside the repository:
- `logging_middleware` folder
- `vehicle_maintence_scheduler` folder
- `notification_system_design.md` (as markdown file)
- `notification_app_be` folder
- `.gitignore` (add node_modules if js/ts is used)

## Stage 1
Assume a front-end developer colleague asked for REST API design, contract, and structure to display notifications to users when logged in.
- Identify core actions.
- Present REST API endpoints along with JSON request, response, and headers structures using an appropriate format.
- Define clear, consistent endpoints using predictable naming conventions.
- Design JSON schemas with essential fields.
- Design a mechanism for real-time notifications.
- Submit response as a markdown file called `notification_system_design.md` in the repo.
- Label response with **"Stage 1"** as heading.

## Stage 2
Based on the APIs and contract created in Stage 1, store them reliably.
- Suggest a persistent storage (DB) and explain the choice.
- Write applicable DB schema.
- Identify problems that could arise as data volume increases.
- Propose solutions to such problems.
- Write SQL or NoSQL queries based on DB schema and REST APIs from Stage 1.
- Submit response in a new section labeled **"Stage 2"** by expanding the same `notification_system_design.md` file.

## Stage 3
An earlier developer chose a relational database (MySQL or PostgreSQL). The database has grown to 50,000 students and 5,000,000 notifications. The developer wrote a query to fetch all unread notifications of a student, which is now performing slowly:
```sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```
Task is to optimize this query.

## Registration
Register with Test Server to obtain unique **Client ID** and **Client Secret**.
**Registration API (POST):**
`http://20.207.122.201/evaluation-service/register`

**Request Body:**
```json
{
  "email": "ramkrishna@abc.edu",
  "name": "Ram Krishna",
  "mobileNo": "9999999999",
  "githubUsername": "github",
  "rollNo": "aa1bb",
  "accessCode": "xgAsNC"
}
```
- Email and Roll Number must align with university/college.
- GitHub Repository link submitted in Google Form must match `githubUsername`.
- Use the `accessCode` shared via email.

**Registration Response:**
- You can register only once. Save `clientID` and `clientSecret`.
```json
{
  "email": "ramkrishna@abc.edu",
  "name": "ram krishna",
  "rollNo": "aa1bb",
  "accessCode": "xgAsNC",
  "clientID": "d9cbb699-6a27-44a5-8d59-8b1befa816da",
  "clientSecret": "tVJaaaRBSexCRXeM"
}
```

## Authentication
After registration, obtain an Authorization Token to access Test Server APIs.

**Authorization Token API (POST):**
`http://20.207.122.201/evaluation-service/auth`

**Request Body:**
```json
{
  "email": "ramkrishna@abc.edu",
  "name": "ram krishna",
  "rollNo": "aa1bb",
  "accessCode": "xgAsNC",
  "clientID": "d9cbb699-6a27-44a5-8d59-8b1befa816da",
  "clientSecret": "tVJaaaRBSexCRXeM"
}
```

**Response (Status Code: 200):**
```json
{
  "token_type": "Bearer",
  "access_token": "ey...",
  "expires_in": 1743574344
}
```

## Develop Logging Middleware
- Critical component for robust/observable applications.
- Capture entire lifecycle (warnings, info, debugging) not just errors.
- **Requirement:** Must be a reusable package. If Full Stack track, develop in TypeScript/JavaScript for Frontend consumption.
- Write a reusable function `Log(stack, level, package, message)` that calls the Test Server API.
- Example calls:
  - `Log("backend", "error", "handler", "received string, expected bool")`
  - `Log("backend", "fatal", "db", "Critical database connection failure.")`
- Integrate strategically throughout the codebase.

### Log API (POST)
`http://20.207.122.201/evaluation-service/logs`

**Constraints:**
- Protected Route (requires auth token).
- `stack`, `level`, and `package` accept only lowercase values.

**Allowed Values:**
- **Stack:** `backend`, `frontend`
- **Level:** `debug`, `info`, `warn`, `error`, `fatal`
- **Package:**
  - Backend only: `cache`, `controller`, `cron_job`, `db`, `domain`, `handler`, `repository`, `route`, `service`
  - Frontend only: `api`, `component`, `hook`, `page`, `state`, `style`
  - Both: `auth`, `config`, `middleware`, `utils`

**Request Body:**
```json
{
  "stack": "backend",
  "level": "error",
  "package": "handler",
  "message": "received string, expected bool"
}
```

**Response (Status Code: 200):**
```json
{
  "logID": "a4aad02e-19d0-4153-86d9-58bf55d7c402",
  "message": "log created successfully"
}
```

## Evaluation Considerations
- **Time Limit:** 3 Hours (No extra time for pushing to GitHub)
- **Pre-Test Setup:** Must complete all steps in Pre-Test Setup before working on the test.
- **Mandatory Logging Integration:** You MUST extensively use the Logging Middleware you created. Use of inbuilt language loggers or console logging is NOT allowed.
- **Authentication:** Assume users accessing your app are pre-authorised. Your application must NOT require user registration or login mechanisms for access.

## Stage 3 (Continued)
In addition to optimizing the slow query:
- Answer: Is this query accurate? Why is it slow? What would you change and what is the likely computation cost?
- Another developer suggests adding indexes on every column to be safe. Is this effective? Why/Why not?
- Write a query to find all students who got a placement notification in the last 7 days. (Table has `notificationType` column accepting enum values "Event", "Result", "Placement").
- Submit in section labeled "Stage 3" by expanding the same `notification_system_design.md` file.

## Stage 4
- Problem: Notifications are fetched on each page load for every student, overwhelming the DB and causing bad UX.
- Suggest a solution to improve performance. Elaborate on the tradeoffs of each strategy.
- Submit in section labeled "Stage 4" by expanding the same `notification_system_design.md` file.

## Stage 5
- Scenario: Placement season. HR clicks "Notify All", 50,000 students should get email and in-app notification simultaneously.
- Proposed pseudocode:
```python
function notify_all(student_ids: array, message: string):
  for student_id in student_ids:
    send_email(student_id, message) # calls Email API
    save_to_db(student_id, message) # DB insert
    push_to_app(student_id, message) # implementation based on Stage 1
```
- Answer: What shortcomings do you observe? Logs indicate `send_email` failed for 200 students midway. What now? How would you redesign this to be reliable and fast? Should DB save and email send happen together? Why or why not?
- Submit revised pseudocode and answers in section labeled "Stage 5".

## Stage 6
- Feature: Priority Inbox displaying top 'n' most important unread notifications first (n=10, 15, 20 etc. user choice).
- Priority based on combination of weight (placement > result > event) and recency.
- Implement approach in a functioning code file (not pseudo-code) in Go, Rust, Python, TS, JS, Java, etc. Write code only to find top 10 notifications (DB query not expected).
- Upload screenshots of output displaying priority notifications.
- Push code and screenshots to the GitHub repo.
- Answer: New notifications keep coming in. How will you maintain the top 10 efficiently? Explain approach in section labeled "Stage 6" of `notification_system_design.md`.
- **Note:** Do NOT store notifications in DB or hardcode them. Use the Notification API to fetch them.

### Notification API (GET)
`http://20.207.122.201/evaluation-service/notifications`

**Constraints:**
- API is a protected Route (requires auth token).

**Response (Status Code: 200):**
```json
{
  "notifications": [
    {
      "ID": "d146095a-0d86-4a34-9e69-3900a14576bc",
      "Type": "Result",
      "Message": "mid-sem",
      "Timestamp": "2026-04-22 17:51:30"
    },
    {
      "ID": "b283218f-ea5a-4b7c-93a9-1f2f240d64b0",
      "Type": "Placement",
      "Message": "CSX Corporation hiring",
      "Timestamp": "2026-04-22 17:51:18"
    },
    {
      "ID": "81589ada-0ad3-4f77-9554-f52fb558e09d",
      "Type": "Event",
      "Message": "farewell",
      "Timestamp": "2026-04-22 17:51:06"
    },
    {
      "ID": "cf2885a6-45ac-4ba0-b548-6e9e9d4c52c8",
      "Type": "Result",
      "Message": "project-review",
      "Timestamp": "2026-04-22 17:49:54"
    },
    {
      "ID": "8a7412bd-6065-4d09-8501-a37f11cc848b",
      "Type": "Placement",
      "Message": "Advanced Micro Devices Inc. hiring",
      "Timestamp": "2026-04-22 17:49:42"
    }
  ]
}
```
