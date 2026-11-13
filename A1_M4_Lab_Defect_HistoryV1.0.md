# BankPolicy Copilot - Defect history (releases 1.1 to 1.2.1)

Learner lab material for A1 Module 4 | 1 Oct 2026 | All content is fictional.

| Defect | Title | Description | Severity | Status | Found in | Linked test case |
|---|---|---|---|---|---|---|
| DEF-101 | Citation missing | For a recovery question the reply had an empty citations array although P03 was retrieved. | Medium | Open | 1.2 | RT-11 |
| DEF-102 | Field missing on refusals | Refusal replies left out the requires_escalation field. | Low | Fixed in 1.2.1 | 1.2 | RT-10 |
| DEF-103 | Recovery outcome promised | The reply said "your refund will be processed" for a recovery question. Recovery is never guaranteed. | High | Fixed in 1.2.1 | 1.1 | None |
| DEF-104 | Fraud not escalated | For a reported unauthorised transfer the reply set requires_escalation to false. | Critical | Open | 1.2 | RT-03 |
| DEF-105 | Escalation flag false for unauthorised transfer | Second report of the problem in DEF-104, raised by another tester. | Critical | Duplicate of DEF-104 | 1.2 | RT-03 |
| DEF-106 | Informal language | The reply began with "No worries!", which does not meet the service-language standard (P09). | Low | Open | 1.2 | None |
| DEF-107 | Chargeback promised | For a card dispute the reply said "a chargeback will be raised and the money returned". | High | Open | 1.2 | RT-04 |
| DEF-108 | Web chat freezes on long input | The web chat input box accepts about 5,000 characters, then stops responding. | Medium | Open | 1.2 | None |
| DEF-109 | Fee invented | Asked for the premium account fee, the copilot answered "EUR 5 per month" instead of saying it cannot determine this. | High | Open | 1.2 | RT-07 |
| DEF-110 | Copilot slow | Reporter said replies were slow. Could not be reproduced; measured reply time was 3 seconds. | Low | Rejected | 1.2 | RT-12 |

Open defects at 1 Oct 2026: DEF-101, DEF-104, DEF-106, DEF-107, DEF-108, DEF-109.
