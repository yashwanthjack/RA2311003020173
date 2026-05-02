# Campus Notifications System Design

## Stage 1

### 1. Core Actions Identified
Based on the requirement to display real-time updates regarding Placements, Events, and Results to logged-in students, the following core actions are necessary:
- **Fetch Notifications:** Retrieve a paginated list of notifications for the user (can filter by read/unread or type).
- **Mark as Read (Single):** Mark a specific notification as read once the user clicks it.
- **Mark as Read (All):** Provide a bulk action to clear the unread badge.
- **Real-time Delivery:** Push new notifications to the client instantly without requiring a page refresh.

---

### 2. REST API Endpoints & Contracts

#### Base Headers (Applicable to all requests)
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### A. Fetch Notifications
Retrieves notifications for the authenticated student.

- **Endpoint:** `GET /api/v1/notifications`
- **Query Parameters:**
  - `status` (optional): `unread` | `read` | `all` (default: `all`)
  - `type` (optional): `Event` | `Result` | `Placement`
  - `page` (optional): integer (default: 1)
  - `limit` (optional): integer (default: 20)
- **Request Body:** None
- **Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "total": 45,
    "page": 1,
    "notifications": [
      {
        "id": "d146095a-0d86-4a34-9e69-3900a14576bc",
        "type": "Result",
        "message": "mid-sem results are published",
        "isRead": false,
        "createdAt": "2026-04-22T17:51:30Z"
      },
      {
        "id": "8a7412bd-6065-4d09-8501-a37f11cc848b",
        "type": "Placement",
        "message": "Advanced Micro Devices Inc. hiring",
        "isRead": true,
        "createdAt": "2026-04-22T17:49:42Z"
      }
    ]
  }
}
```

#### B. Mark a Single Notification as Read
Updates the `isRead` flag for a specific notification.

- **Endpoint:** `PATCH /api/v1/notifications/{notification_id}/read`
- **Request Body:** None
- **Response (200 OK):**
```json
{
  "status": "success",
  "message": "Notification marked as read"
}
```

#### C. Mark All Notifications as Read
Clears the unread queue for the authenticated student.

- **Endpoint:** `PATCH /api/v1/notifications/read-all`
- **Request Body:** None
- **Response (200 OK):**
```json
{
  "status": "success",
  "message": "All notifications marked as read"
}
```

---

### 3. JSON Schemas (Data Models)

**Notification Object Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Notification",
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "studentId": { "type": "string" },
    "type": { 
      "type": "string", 
      "enum": ["Event", "Result", "Placement"] 
    },
    "message": { "type": "string" },
    "isRead": { "type": "boolean" },
    "createdAt": { "type": "string", "format": "date-time" }
  },
  "required": ["id", "studentId", "type", "message", "isRead", "createdAt"]
}
```

---

### 4. Real-Time Notification Mechanism

To achieve real-time delivery without overwhelming the backend with continuous polling from clients, we will use **Server-Sent Events (SSE)**.

**Why SSE over WebSockets?**
- **One-Way Traffic:** Notifications are inherently a push mechanism (Server -> Client). SSE is specifically designed for this uni-directional data flow, making it significantly lighter on server resources than establishing bi-directional WebSockets.
- **Native Browser Support:** SSE uses standard HTTP and is supported natively by the `EventSource` API in browsers, allowing for seamless integration.
- **Built-in Reconnection:** SSE automatically handles reconnections if the client drops offline briefly, which reduces boilerplate code on the frontend.

**Implementation Flow:**
1. The client establishes an SSE connection via `GET /api/v1/notifications/stream`.
2. The server holds the connection open.
3. When an HR/Admin triggers a placement or result notification, the backend saves it to the database and immediately pushes an event payload through the open SSE stream to the target student's `studentId` channel.
4. The client's `EventSource` listener catches the event and updates the UI instantly (e.g., popping up a toast notification and incrementing the unread counter).

---

## Stage 2

### 1. Persistent Storage Choice: SQLite
For this microservice, **SQLite** is suggested as the persistent storage engine. 
**Explanation:** 
- **Simplicity & Speed:** It requires zero configuration, has no separate server process, and data is stored in a single cross-platform file. 
- **Microservice Fit:** By enabling Write-Ahead Logging (WAL mode), SQLite handles concurrent reads and sequential writes extremely fast, making it highly suitable for a microservice environment before it hits enterprise-scale traffic.
- **Portability:** It integrates natively with Python and makes local testing and CI/CD pipelines significantly easier.

### 2. Database Schema
```sql
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    studentId TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Event', 'Result', 'Placement')),
    message TEXT NOT NULL,
    isRead BOOLEAN NOT NULL DEFAULT 0,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes to optimize the core REST APIs
CREATE INDEX idx_student_status_time ON notifications(studentId, isRead, createdAt DESC);
CREATE INDEX idx_student_time ON notifications(studentId, createdAt DESC);
```

### 3. Scaling Problems & Solutions

**Problems as data volume increases:**
1. **Write Contention:** Even with WAL mode, SQLite handles writes sequentially. A mass "Notify All" event (50,000+ rows) could cause write locks and queueing, slowing down the API.
2. **Unbounded File Growth:** Millions of historical notifications will bloat the single SQLite `.db` file, leading to slower sequential scans and larger, cumbersome backups.
3. **Pagination Degradation:** Using traditional `OFFSET` for pagination becomes exponentially slower as the offset grows, because the database must scan through all skipped rows.

**Proposed Solutions:**
1. **Message Queuing & Batch Inserts:** Introduce a queue (like Redis or RabbitMQ) to absorb the massive spike of "Notify All" requests and batch insert them into SQLite (e.g., 500 rows per transaction) to eliminate write locking.
2. **Data Archival Strategy (TTL):** Implement a cron job that runs nightly to archive or hard-delete notifications older than 30 or 60 days, keeping the active SQLite table small and extremely fast.
3. **Cursor-Based Pagination:** Replace `OFFSET/LIMIT` in the API with cursor-based pagination (e.g., `WHERE studentId = ? AND createdAt < last_seen_timestamp LIMIT 20`). This leverages the index immediately regardless of how deep into history the user scrolls.
4. **Future Migration:** If the microservice heavily outgrows the single-node architecture, the schema seamlessly transitions to PostgreSQL.

### 4. SQL Queries (Mapping to Stage 1 REST APIs)

**A. Fetch Notifications (Unread only, Paginated)**
```sql
-- Using standard Offset/Limit for V1
SELECT id, type, message, isRead, createdAt 
FROM notifications 
WHERE studentId = ? AND isRead = 0
ORDER BY createdAt DESC 
LIMIT 20 OFFSET 0;
```

**B. Mark Single Notification as Read**
```sql
UPDATE notifications 
SET isRead = 1 
WHERE id = ? AND studentId = ?;
```

**C. Mark All Notifications as Read**
```sql
UPDATE notifications 
SET isRead = 1 
WHERE studentId = ? AND isRead = 0;
```

---

## Stage 3

### 1. Analysis of the Slow SQL Query
**Provided Query:**
```sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```
**Is this query accurate?** 
Functionally, yes, but it is flawed for production:
- Using `SELECT *` forces the database to read and transfer every single column (including massive text payloads), which consumes unnecessary memory and network bandwidth.
- `1042` is treated as an integer, but `studentID` might be a string. This causes implicit type casting, which can bypass index usage entirely.

**Why is it slow?**
The database has grown to 5,000,000 rows. Without a specific composite index covering `studentID`, `isRead`, and `createdAt`, the database is forced to perform a **Full Table Scan** to find the rows, followed by an expensive **Filesort** in memory to order the results by date.

**What to change and computation cost:**
- **Change:** Replace `SELECT *` with specific columns (`SELECT id, type, message, createdAt`). Ensure `studentID` is properly quoted if it's a string. Create a composite index: `CREATE INDEX idx_student_unread ON notifications(studentID, isRead, createdAt DESC);`
- **Cost:** With the composite index, the computation cost drops from `O(N)` (scanning 5 million rows) to `O(log N + K)` where `K` is the small number of unread notifications for that specific student. The database fetches the pre-sorted rows directly from the B-Tree index.

### 2. Is adding indexes on every column effective?
**No, this is terrible advice.** 
While adding indexes speeds up `SELECT` queries, it severely slows down `INSERT`, `UPDATE`, and `DELETE` operations because the database must recalculate and write to every single index tree whenever data changes. In a notification system with high write-throughput (e.g., massive "Notify All" bursts), over-indexing will crash the database's write performance. You should only index columns frequently used together in `WHERE`, `JOIN`, or `ORDER BY` clauses.

### 3. Query for Recent Placements
```sql
SELECT DISTINCT studentId 
FROM notifications 
WHERE type = 'Placement' 
  AND createdAt >= date('now', '-7 days');
```

---

## Stage 4

### Performance Improvement Strategies
Fetching notifications on every single page load overwhelms the database. To improve performance and UX, we must decouple page loads from database reads.

1. **Caching the Unread Count (Redis):**
   - **Solution:** Instead of querying the database for `COUNT(*)` on every page load, store the student's unread count in an in-memory cache like Redis. When a new notification is generated, increment the Redis key. When the user reads it, decrement it.
   - **Tradeoff:** Extremely fast page loads (O(1) memory read), but introduces cache invalidation complexity (the cache might drift from the true DB state if not managed perfectly).

2. **Client-Side State Management:**
   - **Solution:** The frontend (e.g., using Redux, React Context) should fetch the notification payload exactly once when the user logs in. Navigating between pages should read from this local memory, avoiding the network entirely.
   - **Tradeoff:** Zero backend load for navigation, but if the user has multiple tabs open, the state might desync across tabs without a mechanism to share state.

3. **Real-time Push (SSE/WebSockets):**
   - **Solution:** Rely exclusively on the Server-Sent Events (SSE) mechanism defined in Stage 1 to push updates. The client only updates its local state when the server explicitly pushes a new notification event.
   - **Tradeoff:** Requires holding open connections on the server, which consumes server memory/ports, but completely eliminates unnecessary HTTP polling.

---

## Stage 5

### Reliability and Scaling (Notify All Redesign)

**Shortcomings of the proposed pseudocode:**
1. **Synchronous Blocking:** The `for` loop executes sequentially. If the `send_email` API takes 1 second per user, notifying 50,000 students will take almost 14 hours!
2. **Coupled Failures:** Because `send_email` and `save_to_db` are in the same synchronous block, an external failure in the Email API crashes the script. As indicated by the logs, failing midway means the remaining 49,800 students never get their DB insert or in-app push.
3. **Missing DB Transactions:** Saving to the DB shouldn't wait for a network request (email) to finish.

**Should DB save and email send happen together?**
**No.** They operate on entirely different latency scales. Database inserts are fast, internal, and reliable. Email APIs (like SendGrid/AWS) are slow, external, and prone to rate-limiting or network timeouts. They must be decoupled using an Asynchronous Message Queue.

### Revised Pseudocode (Event-Driven Architecture)
```python
function notify_all(student_ids: array, message: string):
  # 1. Fast, internal DB operations (Batch Insert)
  batch_save_to_db(student_ids, message)
  
  for student_id in student_ids:
    # 2. Instantly push to connected clients via SSE
    push_to_app(student_id, message) 
    
    # 3. Fire-and-forget: Send the email task to a Message Queue (e.g., RabbitMQ, Celery, SQS)
    enqueue_task("email_queue", student_id, message)

# This runs on separate Background Worker servers
function process_email_queue_task(student_id: string, message: string):
  try:
    send_email(student_id, message)
  except TemporaryAPIError:
    # If the email API fails, push it back to the queue to try again later
    retry_task_later()
  except PermanentError:
    # Send to a Dead Letter Queue for engineering review
    log_to_dead_letter_queue(student_id, message)
```
