package com.dcmp.portal.workflow;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StatusHistoryRepository extends JpaRepository<StatusHistory, Long> {

    List<StatusHistory> findByDeviceIdOrderByChangedAtDesc(Long deviceId);
}
