package com.dcmp.portal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.dcmp.portal.device.Device;
import com.dcmp.portal.device.DeviceRepository;
import com.dcmp.portal.user.AppUser;
import com.dcmp.portal.workflow.StatusHistoryRepository;
import com.dcmp.portal.workflow.WorkflowService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = "spring.datasource.url=jdbc:h2:mem:workflowdb")
@AutoConfigureMockMvc
class WorkflowTests {

    @Autowired
    MockMvc mvc;
    @Autowired
    DeviceRepository devices;
    @Autowired
    StatusHistoryRepository history;

    private MockHttpSession as(String role) {
        MockHttpSession s = new MockHttpSession();
        s.setAttribute("user", new AppUser(role.toLowerCase(), "x", role));
        return s;
    }

    private Device newDevice(String serial) {
        Device d = new Device();
        d.setName("W-" + serial);
        d.setOwner("o");
        d.setSerialNo(serial);
        d.setOs("Linux");
        return devices.save(d);
    }

    @Test
    void rulesPerRole() {
        assertTrue(WorkflowService.isAllowed("TECHNICIAN", "REPORTED", "UNDER_REVIEW"));
        assertFalse(WorkflowService.isAllowed("TECHNICIAN", "REMEDIATED", "CLOSED"));
        assertTrue(WorkflowService.isAllowed("AUDITOR", "REMEDIATED", "CLOSED"));
        assertFalse(WorkflowService.isAllowed("AUDITOR", "REPORTED", "UNDER_REVIEW"));
        assertFalse(WorkflowService.isAllowed("ADMIN", "REPORTED", "CLOSED"));
    }

    @Test
    void technicianTransitionIsRecordedInHistory() throws Exception {
        Device d = newDevice("W-1");
        mvc.perform(post("/devices/" + d.getId() + "/status").session(as("TECHNICIAN")).param("to", "UNDER_REVIEW"))
                .andExpect(status().is3xxRedirection());
        assertEquals("UNDER_REVIEW", devices.findById(d.getId()).get().getWorkflowStatus());
        assertEquals(1, history.findByDeviceIdOrderByChangedAtDesc(d.getId()).size());
    }

    @Test
    void forbiddenTransitionIsRejected() throws Exception {
        Device d = newDevice("W-2");
        mvc.perform(post("/devices/" + d.getId() + "/status").session(as("AUDITOR")).param("to", "CLOSED"))
                .andExpect(status().isForbidden());
    }
}
