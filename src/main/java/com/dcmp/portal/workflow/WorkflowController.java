package com.dcmp.portal.workflow;

import com.dcmp.portal.device.Device;
import com.dcmp.portal.device.DeviceRepository;
import com.dcmp.portal.user.AppUser;
import com.dcmp.portal.user.LoginController;
import javax.servlet.http.HttpSession;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.server.ResponseStatusException;

@Controller
public class WorkflowController {

    private final DeviceRepository devices;
    private final WorkflowService workflow;

    public WorkflowController(DeviceRepository devices, WorkflowService workflow) {
        this.devices = devices;
        this.workflow = workflow;
    }

    @PostMapping("/devices/{id}/status")
    public String changeStatus(@PathVariable Long id, @RequestParam String to, HttpSession session) {
        AppUser user = (AppUser) session.getAttribute(LoginController.SESSION_USER);
        Device device = devices.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Device not found"));
        try {
            workflow.transition(device, to, user);
        } catch (IllegalStateException e) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, e.getMessage());
        }
        return "redirect:/devices/" + id;
    }
}
