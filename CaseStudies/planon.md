# CASE STUDY: PLANON

## 1. Platform Overview

### 1.1 Platform Name

Planon

### 1.2 Company

Planon

### 1.3 Domain

Facility, asset and maintenance management.

### 1.4 Authors

Kasinadh

## 2. Problem Statement

### 2.1 Existing Problem

Hostels often handle complaints through messages, calls or registers.
This can make complaints easy to miss and difficult to track.

### 2.2 Target Users

-   Students/residents
-   Hostel administrators
-   Maintenance staff
-   Supervisors

### 2.3 Platform's Approach

Planon centralizes service requests and maintenance work. Users can
submit requests, while staff can assign, track and complete the related
work orders. citeturn0search0turn0search3

## 3. Features & Internal Architecture

### 3.1 Complaint / Service Requests

#### Purpose

Lets users report a maintenance problem and follow its progress.

#### Components

Request form, request record, status and user details.

#### Internal Working

A request is collected and processed through configured workflows before
being handled by the responsible team. citeturn0search4

#### Data Flow

``` text
Student → Complaint Form → Workflow → Maintenance Staff → Status Update
```

### 3.2 Work Order Management

#### Purpose

Turns reported problems into organized maintenance tasks.

#### Components

Work order, priority, assigned staff, time and materials.

#### Internal Working

Work can be assigned according to configured rules, skills and
availability. citeturn0search0

#### Data Flow

``` text
Complaint → Work Order → Assignment → Repair → Completion
```

### 3.3 Preventive Maintenance

#### Purpose

Helps prevent repeated or predictable equipment problems.

#### Components

Maintenance schedules, activities and assets.

#### Internal Working

Planned maintenance activities can generate work orders before equipment
fails. citeturn0search6

#### Data Flow

``` text
Asset → Schedule → Planned Activity → Work Order → Maintenance
```

### 3.4 Asset Management

#### Purpose

Keeps information about equipment and its maintenance history.

#### Components

Asset details, location, condition and repair history.

#### Internal Working

Planon connects asset information with maintenance activities and work
orders. citeturn0search8

#### Data Flow

``` text
Asset → Observation/Issue → Maintenance Action → Updated Record
```

### 3.5 Mobile Field Services

#### Purpose

Allows maintenance staff to manage work while they are on-site.

#### Components

Mobile app, work assignments, assets and orders.

#### Internal Working

Technicians can view and update assigned work orders from a mobile
device. citeturn0search14

### 3.6 Overall Architecture

``` text
Student / Staff
      ↓
Request Interface
      ↓
Workflow & Business Rules
      ↓
Complaint / Work Order / Asset Records
      ↓
Maintenance Team
      ↓
Status, Reports & Feedback
```

The exact proprietary database and internal service implementation of
Planon is not publicly documented in the sources reviewed.

## 4. Features Applicable to Our Project

### 4.1 Adopt

-   Online complaint submission
-   Complaint status tracking
-   Work-order assignment
-   Priority-based handling
-   Basic reports

### 4.2 Adapt

Planon's large facility-management workflow can be simplified for a
hostel. Our system can focus only on rooms, hostel facilities, students,
complaints and maintenance staff.

### 4.3 Future Possibilities

-   Preventive maintenance
-   Mobile access for workers
-   QR-based asset identification
-   Analytics and performance dashboards

## 5. Limitations, Trade-offs & Lessons

### 5.1 Observed Limitations

Planon is designed for broad enterprise facility management, so it
contains many capabilities that a small hostel system would not need.
This can make a similar system unnecessarily complex.

### 5.2 Architectural Lessons

A centralized complaint record, clear status flow and assignment system
are useful patterns for our project.

### 5.3 Things We Should Avoid

We should avoid copying enterprise-level complexity. The hostel system
should stay simple, fast and easy for students and staff to use.

## 6. Key Findings

-   Centralized complaints reduce dependence on paper or scattered
    messages.
-   Status tracking makes the process more transparent.
-   Work orders connect complaints with actual maintenance work.
-   Asset records can help identify repeated problems.
-   Preventive maintenance can reduce recurring complaints.
-   Our project should use the useful ideas while keeping the system
    hostel-specific.

## 7. Conclusion

Planon shows how maintenance requests can be connected to workflows,
staff assignments, assets and work orders. For our Hostel Complaint
Management System, the main lesson is to keep the same organized flow
but simplify it for students, wardens and maintenance staff.

## 8. References

1.  Planon --- Operations Command Center:
    https://planonsoftware.com/us/software/field-services/operations-command-center/
2.  Planon --- Asset & Maintenance Management:
    https://planonsoftware.com/us/software/iwms/asset-maintenance-management/
3.  Planon --- Customer Management:
    https://planonsoftware.com/us/software/field-services/customer-management/
4.  Planon --- Asset Lifecycle Management:
    https://planonsoftware.com/us/modules/asset-lifecycle-management/
5.  Planon --- Planon App:
    https://suppconf.planonsoftware.com/Planon%20Live/PlanonApp_2_PL_OS.html