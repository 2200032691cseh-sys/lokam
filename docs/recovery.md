# Backup and recovery

Target daily encrypted PostgreSQL custom-format backups and object manifests with checksums to an independent destination. Use consistent DB snapshots and retain corresponding object versions while a snapshot remains recoverable. Separate backup credentials and encryption keys; verify age, checksum, coverage and retention daily. Propose 30 days subject to legal and quota review.

On incident stop writes/jobs, isolate credentials, choose the last verified recovery point, restore DB and objects into a fresh restricted environment, apply erasure markers before opening requests, rotate credentials and invalidate old sessions. Verify row/object counts, sampled hashes, ownership, privacy, reference integrity, worker deduplication and smoke flows. Record measured RPO ≤24h and RTO ≤4h. Drill schema rollback, provider migration and interrupted workers. The Neon restore window alone does not establish these targets.
