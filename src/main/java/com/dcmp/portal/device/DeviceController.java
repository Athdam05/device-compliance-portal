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
    public String list(Model model) {
        model.addAttribute("devices", repository.findAll());
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
        Device device = repository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Device not found"));
        model.addAttribute("device", device);
        return "devices/details";
    }
}
