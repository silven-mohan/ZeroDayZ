-- Apply this migration once to the existing MySQL database.
-- It preserves all complaint data and makes retries of the submission form safe.

ALTER TABLE complaints
    ADD COLUMN idempotency_key VARCHAR(64) NULL,
    ADD UNIQUE KEY uq_complaints_idempotency_key (idempotency_key);

-- Assignment selection is serialized by application row locks. These indexes
-- keep the locked workload and declined-worker lookups bounded as data grows.
CREATE INDEX ix_complaints_assignment_workload
    ON complaints (assigned_staff_id, status);
CREATE INDEX ix_complaint_actions_assignment_attempt
    ON complaint_actions (complaint_id, staff_id, action);
