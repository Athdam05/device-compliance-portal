package com.dcmp.portal.workflow;

import com.dcmp.portal.device.Device;
import com.dcmp.portal.device.DeviceRepository;
import com.dcmp.portal.user.AppUser;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;

/**
 * Status workflow: REPORTED -> UNDER_REVIEW -> REMEDIATED -> CLOSED.
 * TECHNICIAN moves forward up to REMEDIATED, AUDITOR closes or reopens, ADMIN may do both.
 */
@Service
public class WorkflowService {

    private final DeviceRepository devices;
    private final StatusHistoryRepository history;

    public WorkflowService(DeviceRepository devices, StatusHistoryRepository history) {
        this.devices = devices;
        this.history = history;
    }

    public static boolean isAllowed(String role, String from, String to) {
        boolean technicianMove = ("REPORTED".equals(from) && "UNDER_REVIEW".equals(to))
                || ("UNDER_REVIEW".equals(from) && "REMEDIATED".equals(to));
        boolean auditorMove = ("REMEDIATED".equals(from) && "CLOSED".equals(to))
                || ("REMEDIATED".equals(from) && "UNDER_REVIEW".equals(to));
        switch (role) {
            case "TECHNICIAN": return technicianMove;
            case "AUDITOR": return auditorMove;
            case "ADMIN": return technicianMove || auditorMove;
            default: return false;
        }
    }

    public List<String> nextStatuses(String role, String from) {
        List<String> options = new ArrayList<>();
        for (String to : new String[] {"UNDER_REVIEW", "REMEDIATED", "CLOSED"}) {
            if (isAllowed(role, from, to)) {
                options.add(to);
            }
        }
        return options;
    }

    public void transition(Device device, String to, AppUser user) {
        String from = device.getWorkflowStatus();
        if (!isAllowed(user.getRole(), from, to)) {
            throw new IllegalStateException(user.getRole() + " cannot move " + from + " to " + to);
        }
        device.setWorkflowStatus(to);
        devices.save(device);
        history.save(new StatusHistory(device.getId(), from, to, user.getUsername()));
    }
}
