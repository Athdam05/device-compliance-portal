# Step 9 – Selenium Test Design and Local Execution
**Student:** Atharva Anand Damale (23102C0004)

## 1. Critical user journeys
| ID | Journey | Why it is critical |
|---|---|---|
| J1 | Invalid login is rejected; valid login reaches the device list | Gate to the whole application |
| J2 | Register a device; details page shows COMPLIANT / NON_COMPLIANT | Core feature + compliance rule |
| J3 | Search finds a registered device and shows "No devices found" for a miss | Core feature (US4) |
| J4 | Technician moves a device to UNDER_REVIEW; history row recorded; no "Close" option | Role-based workflow (US7, US8) |
| J5 | Dashboard totals are consistent (total = compliant + non-compliant) | Management summary (US9) |

## 2. Test data
Each test creates its own device with a unique serial (`SEL-<nanoTime>`), so tests are independent and repeatable.
Demo users (seeded): `admin/admin123`, `tech/tech123`.

## 3. Test cases
| Test | Steps | Assertion |
|---|---|---|
| `j1_invalidLoginIsRejected…` | login with wrong password; login admin/admin123 | `#login-error` contains "Invalid"; URL ends with `/devices`; `#who` shows ADMIN |
| `j2_registerCompliantDevice…` | create device with all 3 controls ticked | `#device-name` equals name; `#compliance` = COMPLIANT |
| `j2_registerDeviceWithMissingControls…` | create device with only antivirus | `#compliance` = NON_COMPLIANT |
| `j3_searchFinds…` | create device; search by name; search for nonsense | table contains name; table contains "No devices found" |
| `j4_technicianCanMove…` | admin creates device; logout; tech moves to UNDER_REVIEW | `#status` = UNDER_REVIEW; history row by `tech`; no `#to-CLOSED` |
| `j5_dashboardShowsSummaryCounts` | create non-compliant device; open dashboard | total ≥ 1; total = compliant + non-compliant |

## 4. Failure screenshot mechanism
`BaseSeleniumIT` registers a JUnit 5 `TestExecutionExceptionHandler`. When any test throws, it saves
`target/screenshots/<TestClass>_<testMethod>.png` **before** the browser is closed, then rethrows the failure.
(An earlier version used `TestWatcher`, which runs after `@AfterEach` has closed the browser and produced no
screenshots — this was found and fixed during development.)

## 5. How to run locally through Maven
Selenium tests are named `*IT.java` and run by the Maven Failsafe plugin only in the `selenium` profile, so the normal
`mvn package` build does not need a browser.
```
mvn verify -Pselenium -Dbase.url=http://localhost:8081/dcmp -Dwebdriver.edge.driver=C:\Users\damal\tools\edgedriver\msedgedriver.exe
```
Properties: `base.url` (application under test, default = Tomcat deployment), `headless` (default true; `-Dheadless=false` to watch).
Browser: Microsoft Edge 155 with matching msedgedriver 155.

## 6. Result of local run
`UserJourneysIT`: Tests run: 6, Failures: 0, Errors: 0 – BUILD SUCCESS (Failsafe report in `target/failsafe-reports`).

### Issues found while building the suite (and fixes)
| Issue | Cause | Fix |
|---|---|---|
| Wrong Selenium version (4.1.4) used | Spring Boot dependency management overrides `selenium.version` | Set `<selenium.version>4.21.0</selenium.version>` in the pom |
| Edge driver not found | Selenium Manager could not fetch driver | Downloaded matching msedgedriver, passed `-Dwebdriver.edge.driver` |
| DevTools websocket connection refused | Chromium 111+ rejects unknown origins | Added `--remote-allow-origins=*` |
| Random "no such element" / stale element | `click()` returns before the next page loads | `clickAndWait()` helper waits for the old element to go stale + 10 s implicit wait |
| No failure screenshots | `TestWatcher` runs after the browser was closed | Switched to `TestExecutionExceptionHandler` |
