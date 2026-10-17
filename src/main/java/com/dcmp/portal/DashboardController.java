package com.dcmp.portal;

import com.dcmp.portal.device.Device;
import com.dcmp.portal.device.DeviceRepository;
import java.util.List;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class DashboardController {

    private final DeviceRepository repository;

    public DashboardController(DeviceRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/dashboard")
    public String dashboard(Model model) {
        List<Device> all = repository.findAll();
        long compliant = all.stream().filter(Device::isCompliant).count();
        model.addAttribute("total", all.size());
        model.addAttribute("compliant", compliant);
        model.addAttribute("nonCompliant", all.size() - compliant);
        model.addAttribute("reported", repository.countByWorkflowStatus("REPORTED"));
        model.addAttribute("underReview", repository.countByWorkflowStatus("UNDER_REVIEW"));
        model.addAttribute("remediated", repository.countByWorkflowStatus("REMEDIATED"));
        model.addAttribute("closed", repository.countByWorkflowStatus("CLOSED"));
        return "dashboard";
    }
}
