package com.dcmp.portal.selenium;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;

/** Critical user journeys (see docs/09-selenium-test-plan.md). */
class UserJourneysIT extends BaseSeleniumIT {

    // J1 - authentication
    @Test
    void j1_invalidLoginIsRejectedAndValidLoginReachesDeviceList() {
        login("admin", "wrong-password");
        assertTrue(driver.findElement(By.id("login-error")).getText().contains("Invalid"));

        login("admin", "admin123");
        assertTrue(driver.getCurrentUrl().endsWith("/devices"), "expected device list, was " + driver.getCurrentUrl());
        assertTrue(driver.findElement(By.id("who")).getText().contains("ADMIN"));
    }

    // J2 - register a device and see its compliance result
    @Test
    void j2_registerCompliantDeviceShowsCompliantOnDetails() {
        login("admin", "admin123");
        String name = createDevice("J2", true, true, true);
        assertEquals(name, driver.findElement(By.id("device-name")).getText());
        assertEquals("COMPLIANT", driver.findElement(By.id("compliance")).getText());
    }

    @Test
    void j2_registerDeviceWithMissingControlsIsNonCompliant() {
        login("admin", "admin123");
        createDevice("J2b", true, false, false);
        assertEquals("NON_COMPLIANT", driver.findElement(By.id("compliance")).getText());
    }

    // J3 - search
    @Test
    void j3_searchFindsRegisteredDeviceAndHidesOthers() {
        login("admin", "admin123");
        String name = createDevice("J3", true, true, true);

        search(name);
        String table = driver.findElement(By.tagName("table")).getText();
        assertTrue(table.contains(name));

        search("no-such-device-xyz");
        assertTrue(driver.findElement(By.tagName("table")).getText().contains("No devices found"));
    }

    // J4 - role-based workflow
    @Test
    void j4_technicianCanMoveToUnderReviewAndHistoryIsRecorded() {
        login("admin", "admin123");
        createDevice("J4", true, true, true);
        String detailsUrl = driver.getCurrentUrl();
        open("/devices");
        clickAndWait(By.id("logout"));

        login("tech", "tech123");
        driver.get(detailsUrl);
        clickAndWait(By.id("to-UNDER_REVIEW"));
        assertEquals("UNDER_REVIEW", driver.findElement(By.id("status")).getText());
        assertTrue(driver.findElement(By.xpath("//table//td[text()='tech']")).isDisplayed());
        assertTrue(driver.findElements(By.id("to-CLOSED")).isEmpty(), "technician must not see Close");
    }

    // J5 - dashboard
    @Test
    void j5_dashboardShowsSummaryCounts() {
        login("admin", "admin123");
        createDevice("J5", false, false, false);
        open("/dashboard");
        int total = Integer.parseInt(driver.findElement(By.id("total")).getText());
        int compliant = Integer.parseInt(driver.findElement(By.id("compliant")).getText());
        int non = Integer.parseInt(driver.findElement(By.id("non-compliant")).getText());
        assertTrue(total >= 1);
        assertEquals(total, compliant + non);
    }
}
