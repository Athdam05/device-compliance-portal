package com.dcmp.portal.selenium;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.junit.jupiter.api.extension.TestExecutionExceptionHandler;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.openqa.selenium.By;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriverException;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;

/**
 * Base class for browser tests. The application under test is addressed by the
 * {@code base.url} system property (default: the Tomcat deployment from step 8).
 * A screenshot is written to target/screenshots/ whenever a test fails.
 */
abstract class BaseSeleniumIT {

    static final String BASE_URL = System.getProperty("base.url", "http://localhost:8081/dcmp");

    protected WebDriver driver;

    /** Runs while the browser is still open (before @AfterEach), so the failure screenshot shows the real page. */
    @RegisterExtension
    final TestExecutionExceptionHandler screenshotOnFailure = new TestExecutionExceptionHandler() {
        @Override
        public void handleTestExecutionException(ExtensionContext context, Throwable throwable) throws Throwable {
            saveScreenshot(context.getRequiredTestClass().getSimpleName() + "_" + context.getRequiredTestMethod().getName());
            throw throwable;
        }
    };

    @BeforeEach
    void startBrowser() {
        EdgeOptions options = new EdgeOptions();
        if (!"false".equals(System.getProperty("headless", "true"))) {
            options.addArguments("--headless=new");
        }
        options.addArguments("--window-size=1280,900", "--no-sandbox", "--remote-allow-origins=*");
        driver = new EdgeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
    }

    @AfterEach
    void stopBrowser() {
        if (driver != null) {
            driver.quit();
        }
    }

    protected void open(String path) {
        driver.get(BASE_URL + path);
    }

    /** Clicks an element and waits until the resulting page navigation has replaced it. */
    protected void clickAndWait(By locator) {
        WebElement element = driver.findElement(locator);
        element.click();
        new WebDriverWait(driver, Duration.ofSeconds(10)).until(d -> isDetached(element));
    }

    /**
     * True once the element belongs to a page that has been replaced. Edge may report this either as a
     * StaleElementReferenceException or as a generic WebDriverException ("Node with given id does not
     * belong to the document"), so both count.
     */
    private static boolean isDetached(WebElement element) {
        try {
            element.isEnabled();
            return false;
        } catch (StaleElementReferenceException e) {
            return true;
        } catch (WebDriverException e) {
            return e.getMessage() != null && e.getMessage().contains("does not belong to the document");
        }
    }

    protected void login(String username, String password) {
        open("/login");
        driver.findElement(By.id("username")).sendKeys(username);
        driver.findElement(By.id("password")).sendKeys(password);
        clickAndWait(By.id("login"));
    }

    protected void search(String text) {
        open("/devices");
        driver.findElement(By.id("q")).sendKeys(text);
        clickAndWait(By.id("search"));
    }

    protected void saveScreenshot(String name) {
        if (driver == null) {
            return;
        }
        try {
            byte[] png = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
            Path dir = Paths.get("target", "screenshots");
            Files.createDirectories(dir);
            Files.write(dir.resolve(name + ".png"), png);
        } catch (IOException | RuntimeException e) {
            System.err.println("Could not save screenshot: " + e.getMessage());
        }
    }

    /** Registers a device through the UI and leaves the browser on its details page. */
    protected String createDevice(String namePrefix, boolean antivirus, boolean encrypted, boolean firewall) {
        String serial = "SEL-" + System.nanoTime();
        String name = namePrefix + "-" + serial;
        open("/devices/new");
        driver.findElement(By.id("name")).sendKeys(name);
        driver.findElement(By.id("owner")).sendKeys("Selenium Tester");
        driver.findElement(By.id("serialNo")).sendKeys(serial);
        driver.findElement(By.id("os")).sendKeys("Windows 11");
        if (antivirus) {
            driver.findElement(By.id("antivirusEnabled1")).click();
        }
        if (encrypted) {
            driver.findElement(By.id("diskEncrypted1")).click();
        }
        if (firewall) {
            driver.findElement(By.id("firewallEnabled1")).click();
        }
        clickAndWait(By.id("save"));
        return name;
    }
}
