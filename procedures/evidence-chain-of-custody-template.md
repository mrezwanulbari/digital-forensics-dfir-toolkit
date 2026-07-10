# Evidence Chain of Custody Template & Procedure

Documentation template and handling discipline for maintaining a defensible chain of custody, from initial acquisition through final disposition.

## Chain of Custody Log Template

```markdown
## Evidence Item: [Unique Evidence ID]

**Description:** [e.g., "Dell Latitude laptop, S/N XXXXX, believed compromised host"]
**Source:** [Where/how the evidence was obtained — location, system, user]
**Acquired by:** [Name, role]
**Acquisition date/time:** [Timestamp, timezone specified]
**Acquisition method:** [e.g., "Live memory capture via [tool], followed by forensic disk image via write-blocker"]
**Original hash (SHA-256):** [Hash of the acquired image, computed immediately after acquisition]

### Custody Transfer Log

| Date/Time | From | To | Purpose | Hash Verified? |
|---|---|---|---|---|
| [timestamp] | [name] | [name] | [e.g., "Transfer to analysis workstation"] | [Y/N — record verification hash match] |

### Storage Location
[Physical/digital storage location, access controls in place]

### Disposition
[Final outcome — retained, returned, destroyed per policy — with date and authorizing party]
```

## Handling Discipline

1. **Hash immediately after acquisition, before anything else touches the evidence.** This hash is the baseline every future verification compares against — computing it late means you can't prove nothing changed in the gap.
2. **Every custody transfer gets a log entry, no exceptions.** A gap in the log — even an innocent one, like handing a drive to a colleague to walk it to another room — is a gap an opposing party can use to challenge the evidence's integrity in any subsequent legal or HR proceeding.
3. **Work from copies, never originals.** The original evidence, once acquired and hashed, goes into controlled storage and is not touched again except to create additional verified copies if needed. All analysis happens on a working copy.
4. **Verify hash on every access, not just at transfer.** Before starting analysis on a stored image, re-verify its hash matches the original acquisition hash — this catches storage corruption or unauthorized access, not just intentional tampering.
5. **Document the "why," not just the "what."** A custody log that says "moved to analyst workstation" is weaker than one that says "moved to analyst workstation for timeline analysis per [investigation reference]." Purpose context matters if the log is ever reviewed months later.

## Common Failure Points

- **Verbal handoffs** — "I gave it to him in the hallway" is not a chain of custody entry. If it's not written down with a timestamp, it didn't happen for evidentiary purposes.
- **Shared/generic storage locations** — evidence stored in a general-access shared drive or unlocked cabinet undermines the custody claim regardless of how good the paper log is; the physical/digital control has to match the documentation.
- **Retroactive logging** — reconstructing custody log entries after the fact from memory is far weaker than contemporaneous logging, and can be identified as such under scrutiny (metadata timestamps on the log file itself matter).

---
*Part of the [digital-forensics-dfir-toolkit](../README.md) repository.*
