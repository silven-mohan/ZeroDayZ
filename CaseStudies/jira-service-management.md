# CASE STUDY: JIRA SERVICE MANAGEMENT

## 1. Platform Overview

### 1.1 Platform Name
Jira Service Management

### 1.2 Company
Atlassian

### 1.3 Domain
IT service management, service requests, incident management, and workflow management.

### 1.4 Author
Silven Mohan 

## 2. Problem Statement

### 2.1 Existing Problem
Hostel complaints are often handled through messages, calls, or paper records, making them difficult to track.  
A centralized system is needed to record complaints, assign maintenance work, and monitor their progress.

### 2.2 Target Users
- Hostel students/residents
- Hostel wardens
- Maintenance staff
- Administrators
- Supervisors

### 2.3 Platform's Approach
Jira Service Management provides a centralized service-request system where users can submit requests and track their status.  
Requests can be organized into workflows so that responsible staff can handle, update, and resolve them systematically.

## 3. Features & Internal Architecture

### 3.1 Service Request Management

#### Purpose
Allows users to raise maintenance complaints through a structured service interface.

#### Components
- Request forms
- Service portal
- Request records
- Status tracking

#### Internal Working
A user submits a complaint, which becomes a service request that can be processed by the responsible team.

#### Data Flow
```text
Student Complaint
       ↓
Service Portal
       ↓
Request Created
       ↓
Maintenance Team
       ↓
Status Updated
       ↓
Complaint Resolved
```

### 3.2 Workflow Management

#### Purpose
Provides a defined process for moving complaints from submission to resolution.

#### Components
- Statuses
- Workflow transitions
- Assignees
- Resolution states

#### Internal Working
A complaint moves through predefined stages such as Open, In Progress, and Resolved.

#### Data Flow
```text
Open
 ↓
Assigned
 ↓
In Progress
 ↓
Resolved
 ↓
Closed
```

### 3.3 Assignment and Team Handling

#### Purpose
Helps ensure that complaints reach the appropriate maintenance personnel.

#### Components
- Service teams
- Assignees
- Queues
- Request details

#### Internal Working
Submitted requests can be organized and assigned so that maintenance staff know which issues require attention.

#### Data Flow
```text
New Request
     ↓
Request Queue
     ↓
Assigned Staff
     ↓
Maintenance Action
     ↓
Resolution
```

### 3.4 Notifications and Status Updates

#### Purpose
Keeps users informed about changes to their complaints.

#### Components
- Request updates
- Notifications
- Status changes
- Comments

#### Internal Working
When a complaint changes state or receives an update, relevant users can be informed through the service workflow.

#### Data Flow
```text
Complaint Update
      ↓
Status/Comment Change
      ↓
Notification
      ↓
Student / Staff
```

### 3.5 Overall Architecture

The publicly documented logical model can be represented as:

```text
Student / Staff
      ↓
Service Portal
      ↓
Request & Workflow
      ↓
Assignment / Processing
      ↓
Service Data
      ↓
Status / Notification / Resolution
```

The vendor does not publicly document every proprietary internal implementation detail, so specific databases, internal services, or algorithms should not be assumed.

## 4. Features Applicable to Our Project

### 4.1 Adopt

| Platform Capability | Relevance | Proposed Use |
|---|---|---|
| Complaint submission | High | Allow students to report hostel issues |
| Request tracking | High | Let students check complaint progress |
| Workflow management | High | Move complaints through defined stages |
| Assignment | High | Allocate complaints to maintenance staff |
| Notifications | Medium | Inform students about updates |
| Reporting | Medium | Monitor unresolved and completed complaints |

### 4.2 Adapt
The project can simplify Jira Service Management's service-request approach for hostel use.  
Only hostel-specific categories such as electrical, plumbing, cleaning, furniture, and room maintenance need to be included.

### 4.3 Future Possibilities
Future versions could include maintenance analytics, priority-based assignment, mobile access, escalation rules, and automated notifications.

## 5. Limitations, Trade-offs & Lessons

### 5.1 Observed Limitations
A large enterprise service-management platform can provide more configuration than a small hostel system actually needs.  
Complex workflows and administration should therefore be avoided unless they solve a real hostel-management requirement.

### 5.2 Architectural Lessons
The project should keep complaints, users, assignments, statuses, and resolutions as clearly connected entities.  
A simple workflow and clean separation between student requests and staff processing can make the system easier to maintain.

### 5.3 Things We Should Avoid
- Unnecessary workflow complexity
- Too many complaint categories
- Duplicate complaint records
- Excessive administrative configuration
- Features unrelated to hostel maintenance

## 6. Key Findings

1. A centralized complaint portal reduces dependence on informal communication.
2. Each complaint should have a clear status from submission to resolution.
3. Assignment helps ensure that maintenance issues reach responsible staff.
4. Notifications can keep students informed without repeated follow-up.
5. Complaint categories can make requests easier to organize and process.
6. Reporting can help administrators identify recurring maintenance problems.
7. The hostel system should retain useful service-management ideas while remaining simple.

## 7. Conclusion

Jira Service Management provides useful concepts for organizing service requests, workflows, assignments, and status tracking.  
For the hostel project, these ideas can be adapted into a simpler system focused specifically on maintenance complaints and student needs.

## 8. References

1. Atlassian — Jira Service Management documentation and product resources.
2. Atlassian — Jira Service Management workflow and request-management documentation.
3. Platform Case Study Research Skill provided for this project.
