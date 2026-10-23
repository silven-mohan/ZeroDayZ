# ZeroDayZ
This is the source code for the *Centralized Hostel Complaint Management and Maintenance System*.

## Database Schema

The following Mermaid ER diagram documents the supplied MySQL schema. `rooms` is
included as a referenced dependency because `complaints.room_id` has a foreign
key to it, although its `CREATE TABLE` definition was not included in the
schema block.

```mermaid
erDiagram
	USERS {
		INT id PK
		ENUM role
		VARCHAR identifier
		VARCHAR password_hash
		VARCHAR name
		BOOLEAN is_active
		TIMESTAMP created_at
		TIMESTAMP updated_at
	}

	ROOMS {
		INT id PK
	}

	COMPLAINTS {
		INT id PK
		INT student_id FK
		INT assigned_staff_id FK
		INT room_id FK
		ENUM category
		VARCHAR location_details
		VARCHAR description
		ENUM status
		ENUM priority
		TIMESTAMP created_at
		TIMESTAMP updated_at
		TIMESTAMP resolved_at
	}

	COMPLAINT_ASSIGNMENTS {
		INT id PK
		INT complaint_id FK
		INT staff_id FK
		INT assigned_by FK
		TIMESTAMP assigned_at
		TIMESTAMP ended_at
		VARCHAR notes
	}

	COMPLAINT_HISTORY {
		INT id PK
		INT complaint_id FK
		INT actor_id FK
		ENUM old_status
		ENUM new_status
		VARCHAR note
		TIMESTAMP created_at
	}

	COMPLAINT_COMMENTS {
		INT id PK
		INT complaint_id FK
		INT author_id FK
		VARCHAR comment
		TIMESTAMP created_at
	}

	COMPLAINT_ATTACHMENTS {
		INT id PK
		INT complaint_id FK
		INT uploaded_by FK
		VARCHAR file_path
		VARCHAR original_filename
		VARCHAR mime_type
		INT file_size_bytes
		TIMESTAMP created_at
	}

	FEEDBACK {
		INT id PK
		INT complaint_id FK
		INT student_id FK
		TINYINT rating
		BOOLEAN solved
		VARCHAR comment
		TIMESTAMP created_at
	}

	SUGGESTIONS {
		INT id PK
		INT student_id FK
		ENUM topic
		VARCHAR title
		VARCHAR suggestion
		BOOLEAN anonymous
		TIMESTAMP created_at
	}

	COMPLAINT_ACTIONS {
		INT id PK
		INT complaint_id FK
		INT staff_id FK
		ENUM action
		VARCHAR note
		TIMESTAMP created_at
	}

	USERS ||--o{ COMPLAINTS : submits
	USERS o|--o{ COMPLAINTS : assigned_staff
	ROOMS o|--o{ COMPLAINTS : contains
	COMPLAINTS ||--o{ COMPLAINT_ASSIGNMENTS : has
	USERS ||--o{ COMPLAINT_ASSIGNMENTS : staff_member
	USERS o|--o{ COMPLAINT_ASSIGNMENTS : assigns
	COMPLAINTS ||--o{ COMPLAINT_HISTORY : tracks
	USERS o|--o{ COMPLAINT_HISTORY : acts
	COMPLAINTS ||--o{ COMPLAINT_COMMENTS : discusses
	USERS ||--o{ COMPLAINT_COMMENTS : writes
	COMPLAINTS ||--o{ COMPLAINT_ATTACHMENTS : includes
	USERS ||--o{ COMPLAINT_ATTACHMENTS : uploads
	COMPLAINTS ||--o{ FEEDBACK : receives
	USERS ||--o{ FEEDBACK : submits
	USERS o|--o{ SUGGESTIONS : submits
	COMPLAINTS ||--o{ COMPLAINT_ACTIONS : has
	USERS ||--o{ COMPLAINT_ACTIONS : decides
```

### Relationship Notes

- A user can submit many complaints, feedback records, comments, attachments, and suggestions.
- A complaint can be assigned to staff, tracked through status history, discussed, attached to files, and acted on by staff.
- Each feedback record belongs to one complaint and one student. The schema permits one feedback record per complaint/student pair.
- Suggestions may be anonymous. Anonymous suggestions store `student_id` as `NULL` and set `anonymous` to `TRUE`.
- Deleting referenced users, complaints, or rooms is restricted unless the foreign key explicitly uses `ON DELETE SET NULL`.



## 🔀 Branch Structure:

* **main** -> Contains production ready code.

* **develop** -> This is the integration branch for all other branches.

* **feature/X** -> In this branch a feature X may be bulit.

* **fix/X3** -> In this a bug X3 may be fixed.

----

### 📝 LICENSE:

Check [LICENSE.md](./LICENSE) for more details.

----

<p align = "center"> Made with 🩵 </p>