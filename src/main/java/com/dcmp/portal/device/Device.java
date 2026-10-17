package com.dcmp.portal.device;

import java.time.LocalDateTime;
import javax.persistence.*;
import javax.validation.constraints.NotBlank;

@Entity
public class Device {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Name is required")
    private String name;

    @NotBlank(message = "Owner is required")
    private String owner;

    @NotBlank(message = "Serial number is required")
    @Column(unique = true)
    private String serialNo;

    @NotBlank(message = "Operating system is required")
    private String os;

    private boolean antivirusEnabled;
    private boolean diskEncrypted;
    private boolean firewallEnabled;

    private String workflowStatus = "REPORTED";
    private LocalDateTime createdAt = LocalDateTime.now();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getOwner() { return owner; }
    public void setOwner(String owner) { this.owner = owner; }
    public String getSerialNo() { return serialNo; }
    public void setSerialNo(String serialNo) { this.serialNo = serialNo; }
    public String getOs() { return os; }
    public void setOs(String os) { this.os = os; }
    public boolean isAntivirusEnabled() { return antivirusEnabled; }
    public void setAntivirusEnabled(boolean v) { this.antivirusEnabled = v; }
    public boolean isDiskEncrypted() { return diskEncrypted; }
    public void setDiskEncrypted(boolean v) { this.diskEncrypted = v; }
    public boolean isFirewallEnabled() { return firewallEnabled; }
    public void setFirewallEnabled(boolean v) { this.firewallEnabled = v; }
    public String getWorkflowStatus() { return workflowStatus; }
    public void setWorkflowStatus(String s) { this.workflowStatus = s; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime t) { this.createdAt = t; }

    public boolean isCompliant() {
        return antivirusEnabled && diskEncrypted && firewallEnabled;
    }
}
