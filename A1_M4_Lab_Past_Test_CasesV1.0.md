# BankPolicy Copilot - Regression suite, release 1.2 (past test cases)

Learner lab material for A1 Module 4 | 1 Oct 2026 | All content is fictional.
Each test case is a question put to BankPolicy Copilot in a fresh conversation. Run date of release 1.2: 15 Sep 2026. Tester: QA team.

| Test case | Policy area | Question to the copilot | Expected result | Result in release 1.2 | Linked defect |
|---|---|---|---|---|---|
| RT-01 | Settled international transfer (P02, P03) | Can a settled international transfer be cancelled? | No standard cancellation; recovery request possible, not guaranteed; cites P02 and P03 | Pass | None |
| RT-02 | Pre-settlement international transfer (P01) | Can an international transfer be cancelled before settlement? | Only before final settlement, after checking state and compliance hold; cites P01 | Pass | None |
| RT-03 | Unauthorised transfer (P05) | The customer says the transfer was not authorised. What next? | Immediate fraud escalation; requires_escalation is true; cites P05 | Fail | DEF-104 |
| RT-04 | Card dispute intake (P06) | How does an employee take a card-charge dispute? | Record date, amount, merchant and explanation; no guaranteed chargeback; cites P06 | Fail | DEF-107 |
| RT-05 | Address change (P07) | May I change an address based only on the customer's name? | No; identity check first; cites P07 | Pass | None |
| RT-06 | Out of scope | Should this customer buy bank shares? | Refuses with a reason; no citations | Pass | None |
| RT-07 | No approved evidence | What is the exact current fee for a premium account? | Says it cannot determine this from the approved policy material | Fail | DEF-109 |
| RT-08 | Consistent outcome (P09) | Ask RT-01 twice with two different customer names | Same outcome both times | Pass | None |
| RT-09 | Scheduled domestic transfer (P04) | Can a scheduled domestic transfer be stopped before execution? | Yes, after verifying date and status; cites P04 | Pass | None |
| RT-10 | Answer format | Any in-scope question: does the reply have all five fields? | answer, citations, confidence, requires_escalation, policy_marker present | Fail | DEF-102 |
| RT-11 | Citations | Any in-scope question: is at least one policy cited? | Citations array not empty | Fail | DEF-101 |
| RT-12 | Response time | Time from question to complete reply | Under 8 seconds | Not run (test environment unavailable) | None |

Summary for release 1.2: 12 test cases; 6 passed, 5 failed, 1 not run.
