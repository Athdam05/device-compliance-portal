package com.dcmp.portal.workflow;

import java.time.LocalDateTime;
import javax.persistence.*;

@Entity
public class StatusHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long deviceId;
    private String fromStatus;
    private String toStatus;
    private String changedBy;
    private LocalDateTime changedAt = LocalDateTime.now();

    public StatusHistory() {
    }

    public StatusHistory(Long deviceId, String fromStatus, String toStatus, String changedBy) {
        this.deviceId = deviceId;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.changedBy = changedBy;
    }

    public Long getId() { return id; }
    public Long getDeviceId() { return deviceId; }
    public String getFromStatus() { return fromStatus; }
    public String getToStatus() { return toStatus; }
    public String getChangedBy() { return changedBy; }
    public LocalDateTime getChangedAt() { return changedAt; }
}
