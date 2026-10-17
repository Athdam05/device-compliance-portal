package com.dcmp.portal.device;

import javax.validation.Valid;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@Controller
@RequestMapping("/devices")
public class DeviceController {

    private final DeviceRepository repository;

    public DeviceController(DeviceRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public String list(@RequestParam(required = false) String q,
                       @RequestParam(required = false) String status, Model model) {
        String query = (q == null || q.trim().isEmpty()) ? null : q.trim();
        String st = (status == null || status.trim().isEmpty()) ? null : status.trim();
        model.addAttribute("devices", repository.search(query, st));
        model.addAttribute("q", q);
        model.addAttribute("status", status);
        return "devices/list";
    }

    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("device", new Device());
        return "devices/form";
    }

    @PostMapping
    public String create(@Valid @ModelAttribute Device device, BindingResult result) {
        if (result.hasErrors()) {
            return "devices/form";
        }
        try {
            repository.save(device);
        } catch (DataIntegrityViolationException e) {
            result.rejectValue("serialNo", "duplicate", "Serial number already exists");
            return "devices/form";
        }
        return "redirect:/devices/" + device.getId();
    }

    @GetMapping("/{id}")
    public String details(@PathVariable Long id, Model model) {
        model.addAttribute("device", find(id));
        return "devices/details";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("device", find(id));
        return "devices/form";
    }

    @PostMapping("/{id}")
    public String update(@PathVariable Long id, @Valid @ModelAttribute Device device, BindingResult result) {
        Device existing = find(id);
        if (result.hasErrors()) {
            return "devices/form";
        }
        existing.setName(device.getName());
        existing.setOwner(device.getOwner());
        existing.setSerialNo(device.getSerialNo());
        existing.setOs(device.getOs());
        existing.setAntivirusEnabled(device.isAntivirusEnabled());
        existing.setDiskEncrypted(device.isDiskEncrypted());
        existing.setFirewallEnabled(device.isFirewallEnabled());
        try {
            repository.saveAndFlush(existing);
        } catch (DataIntegrityViolationException e) {
            result.rejectValue("serialNo", "duplicate", "Serial number already exists");
            return "devices/form";
        }
        return "redirect:/devices/" + id;
    }

    private Device find(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Device not found"));
    }
}
