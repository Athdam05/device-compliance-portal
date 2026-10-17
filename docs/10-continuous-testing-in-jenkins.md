# Step 10 – Continuous Testing in Jenkins
**Student:** Atharva Anand Damale (23102C0004)

## 1. Pipeline design
`Checkout → Build (unit tests) → Package → Selenium Tests → Deploy → Verify`

- **Selenium Tests stage:** starts the freshly built WAR on a private port (8082) with a throw-away in-memory H2 database,
  waits for `/actuator/health`, runs `mvn failsafe:integration-test failsafe:verify -Pselenium -Dbase.url=http://localhost:8082`,
  then **always** stops the test instance (`post { always }`).
- **Reports:** JUnit results (`target/surefire-reports` and `target/failsafe-reports`) are published in Jenkins;
  failure screenshots (`target/screenshots/*.png`) are archived as build artefacts.
- **Gate:** the stage fails the build on any test failure, so Jenkins marks `Deploy` and `Verify` as *skipped due to earlier failure(s)*.
  Broken builds never reach Tomcat.

## 2. Deliberately introduced defect and its correction
| Run | Commit | Result |
|---|---|---|
| #3 | `9cc7492` *feat: relax compliance rule (DELIBERATE DEFECT)* – `isCompliant()` changed from `&&` to `\|\|` | Unit tests 11/11 pass (they do not cover the rule). **Selenium J2 fails:** `expected: <NON_COMPLIANT> but was: <COMPLIANT>`. Deploy + Verify skipped. Pipeline FAILURE. Screenshot archived: `UserJourneysIT_j2_registerDeviceWithMissingControlsIsNonCompliant.png` |
| #4 | `a1cfb33` *fix: compliance requires all three controls* | Unit 11/11, **Selenium 6/6**, Deploy and Verify pass. Pipeline SUCCESS. Deployed app confirmed: device with only antivirus → NON_COMPLIANT |

This shows why UI-level tests matter: the defect passed every unit test and was caught only by the browser journey.

## 3. Other findings during integration
| Run | Problem | Resolution |
|---|---|---|
| #2 | J3 failed in `login` with `WebDriverException: Node with given id does not belong to the document` | Edge reports a replaced page this way instead of `StaleElementReferenceException`. `clickAndWait` now treats both as "page changed" (commit `eb4e69e`). Suite then passed 2/2 local runs and Jenkins #4. |

## 4. Evidence checklist
- Jenkins test report: `dcmp-pipeline` → build → **Tests**
- Failed pipeline: build **#3** (Selenium stage red, Deploy/Verify skipped)
- Defect correction commit: `a1cfb33`
- Successful rerun: build **#4**

## 5. Known limitations
- Jenkins SCM polling for the pipeline job kept watching the previously configured branch after the branch was changed,
  so builds #3 and #4 were started manually ("Build with Parameters"). The freestyle job `dcmp-ci` polls correctly.
- Tests use Microsoft Edge with a manually installed msedgedriver (`C:\Users\damal\tools\edgedriver`), because Selenium Manager could not fetch it.
