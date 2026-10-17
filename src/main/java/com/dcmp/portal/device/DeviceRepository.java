package com.dcmp.portal.device;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface DeviceRepository extends JpaRepository<Device, Long> {

    @Query("select d from Device d where "
            + "(:q is null or lower(d.name) like lower(concat('%', :q, '%')) "
            + "or lower(d.owner) like lower(concat('%', :q, '%'))) "
            + "and (:status is null or d.workflowStatus = :status) order by d.id")
    List<Device> search(@Param("q") String q, @Param("status") String status);

    long countByWorkflowStatus(String workflowStatus);
}
