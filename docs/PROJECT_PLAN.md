# FriendTask API

A collaborative task-sharing API using Django and Django REST Framework.

---

## 📦 Project Structure

Entities:
- **User**
- **Session** (between 2 users)
- **Task** (linked to a session)

---

## Data Models

### User
- id: string
- username: string
- email: string
- created_at: timestamp

### Task
- id: string
- session_id: string
- text: string
- is_done: boolean
- created_at: timestamp
- updated_at: timestamp

### Session
- id: string
- user1_id: string
- user2_id: string
- tasks: Task[]
- created_at: timestamp

## Mock API Endpoints

### Authentication
- POST /api/auth/register
- POST /api/auth/login

### Sessions
- POST /api/sessions/create -> Creates new session, returns session ID
- GET /api/sessions/{id} -> Get session details (e.g., user1, user2 and created at)
- GET /api/sessions -> List user's sessions

### Tasks
- GET /api/sessions/{id}/tasks -> Get all tasks in session
- POST /api/sessions/{id}/tasks/add -> Add new task
- PUT /api/sessions/{id}/tasks/{taskId} -> Update task status
- DELETE /api/sessions/{id}/tasks/{taskId} -> Delete task