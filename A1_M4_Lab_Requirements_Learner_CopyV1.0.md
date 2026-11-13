# BankPolicy Copilot - Transfer Business Rules Requirements (learner copy)

Addendum to the BankPolicy Reference Application Book | Learner copy for A1 Modules 4 and 5 | 1 Oct 2026
All rules, amounts and records are fictional and for training use only.

## 1. Scope

These requirements define the business rules for money transfers that BankPolicy Copilot answers questions about. They cover transfer request fields, cancellation and recovery, and transfer status. The rules are published to the copilot's approved policy repository as policies P12 to P15 (section 6).

## 2. Terms

| Term | Meaning |
|---|---|
| Domestic transfer | A transfer where both accounts are held in the same country. |
| International transfer | A transfer where the receiving account is held in another country. |
| Execution | The bank sends the transfer. |
| Settlement | The receiving bank confirms that the funds have arrived. After settlement the transfer is final. |
| Cut-off | The latest time a scheduled transfer can still be cancelled. |
| Compliance check | An extra review by the compliance team for a large international transfer. |
| Recovery request | A request to the receiving bank to return funds after execution. Recovery is not guaranteed (P03). |
| Settlement day | The calendar day on which settlement is confirmed. It counts as day 0. |

## 3. Transfer request fields

| ID | Requirement |
|---|---|
| BR-F01 | A transfer shall have exactly one transfer type: DOMESTIC or INTERNATIONAL. Any other value, or no value, shall be rejected. |
| BR-F02 | A domestic transfer amount shall be in EUR, with no more than two decimal places, from 1.00 to 200,000.00 inclusive. Any other amount shall be rejected. |
| BR-F03 | An international transfer amount shall be in the transfer currency, with no more than two decimal places, from 100.00 to 50,000.00 inclusive. Any other amount shall be rejected. |
| BR-F04 | Large international transfers need an extra check. |
| BR-F05 | An international transfer currency shall be one of the upper-case codes EUR, USD, GBP or INR. Any other code, a lower-case code, or no code shall be rejected. |
| BR-F06 | A scheduled domestic transfer shall have an execution date from today to 90 calendar days after today inclusive. A past date, or a date more than 90 days after today, shall be rejected. International transfers are executed immediately and cannot be scheduled. |
| BR-F07 | A scheduled domestic transfer may be cancelled only while more than 30 minutes remain before its scheduled execution time. When 30 minutes or less remain, cancellation shall be refused. |
| BR-F08 | A recovery request must be raised promptly. |

## 4. Cancellation and recovery rules

| ID | Requirement |
|---|---|
| BR-R01 | If fraud is suspected, the transfer shall be escalated immediately through the fraud-response workflow (P05), whatever its type or status. It shall not be cancelled or recovered through the standard process. |
| BR-R02 | A scheduled domestic transfer, with no suspected fraud, shall be cancelled if the request is made before the cut-off (BR-F07). |
| BR-R03 | A scheduled domestic transfer, with no suspected fraud, shall not be cancelled if the request is made at or after the cut-off. The transfer will execute. |
| BR-R05 | An international transfer that has been executed but not settled, with an amount of 10,000.00 or less and no suspected fraud, may have a cancellation requested after a status check (P01). |
| BR-R06 | An international transfer that has been executed but not settled, with an amount above 10,000.00 and no suspected fraud, may have a cancellation requested after a status check and a compliance check. |
| BR-R07 | A settled international transfer, with no suspected fraud, shall not be cancelled (P02). A recovery request may be raised within the recovery window (P03, BR-F08). |
| BR-R08 | A settled transfer of either type, with no suspected fraud, whose recovery window has ended shall be neither cancelled nor recovered. The customer shall be referred to the branch. |

## 5. Transfer status

### 5.1 States

Draft, Scheduled, Executed, Settled, Cancelled, Recovery requested, Recovered, Recovery failed, Fraud hold.

Cancelled, Recovered and Recovery failed are final states: no event moves a transfer out of them.

### 5.2 Allowed changes

| ID | From | Event | To | Condition |
|---|---|---|---|---|
| BR-S01 | Draft | Submit with a future date (domestic only) | Scheduled | Date valid (BR-F06); amount valid (BR-F02) |
| BR-S02 | Draft | Submit for immediate execution | Executed | Amount valid (BR-F02 or BR-F03); compliance check passed if required (BR-F04) |
| BR-S03 | Scheduled | Cancel | Cancelled | Before the cut-off (BR-F07) |
| BR-S04 | Scheduled | Execution time reached | Executed | None |
| BR-S05 | Executed | Receiving bank confirms | Settled | None |
| BR-S06 | Executed (international, not settled) | Cancel | Cancelled | Status check passed; compliance check passed if amount above 10,000.00 (BR-R05, BR-R06) |
| BR-S07 | Executed (domestic) or Settled | Request recovery | Recovery requested | Within the recovery window (BR-F08) |
| BR-S08 | Recovery requested | Funds returned | Recovered | None |
| BR-S09 | Recovery requested | Receiving bank refuses | Recovery failed | None |
| BR-S10 | Draft, Scheduled, Executed, Settled or Recovery requested | Fraud reported | Fraud hold | Always (BR-R01) |

BR-S11: Any change not listed in BR-S01 to BR-S10 shall be refused.

## 6. Policies to publish in the approved policy repository

| ID | Title | Text |
|---|---|---|
| P12 | Transfer Limits Policy | A domestic transfer must be between EUR 1.00 and EUR 200,000.00. An international transfer must be between 100.00 and 50,000.00 in the transfer currency, which must be EUR, USD, GBP or INR. Amounts have no more than two decimal places. An international transfer above 10,000.00 needs a compliance check before it is sent. Only domestic transfers can be scheduled, from today up to 90 days ahead. |
| P13 | Cancellation Cut-off and Compliance Policy | A scheduled domestic transfer can be cancelled only while more than 30 minutes remain before its execution time. A cancellation request for an unsettled international transfer above 10,000.00 needs a compliance check as well as a status check. |
| P14 | Recovery Window Policy | A recovery request can be raised up to and including day 30 after settlement, where the settlement day is day 0. From day 31, refer the customer to the branch. Recovery is never guaranteed. |
| P15 | Transfer Status Policy | A transfer moves from draft to scheduled or executed, from scheduled to executed or cancelled, from executed to settled or (international, before settlement) cancelled, and from executed or settled to recovery requested, then recovered or recovery failed. Suspected fraud moves any open transfer to fraud hold. Cancelled, recovered and recovery failed are final. |
