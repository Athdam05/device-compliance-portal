package com.dcmp.portal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.dcmp.portal.device.Device;
import com.dcmp.portal.device.DeviceRepository;
import com.dcmp.portal.user.AppUser;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = "spring.datasource.url=jdbc:h2:mem:searchdb")
@AutoConfigureMockMvc
class SearchUpdateDashboardTests {

    @Autowired
    MockMvc mvc;
    @Autowired
    DeviceRepository repository;

    private MockHttpSession admin() {
        MockHttpSession s = new MockHttpSession();
        s.setAttribute("user", new AppUser("admin", "x", "ADMIN"));
        return s;
    }

    private Device save(String name, String owner, String serial) {
        Device d = new Device();
        d.setName(name);
        d.setOwner(owner);
        d.setSerialNo(serial);
        d.setOs("Linux");
        return repository.save(d);
    }

    @Test
    void searchMatchesNameOrOwnerCaseInsensitive() {
        save("Alpha-Server", "Ravi", "S-1");
        save("Beta-Laptop", "Meena", "S-2");
        assertEquals(1, repository.search("alpha", null).size());
        assertEquals(1, repository.search("MEENA", null).size());
        assertEquals(0, repository.search("zzz", null).size());
    }

    @Test
    void updatePersistsChanges() throws Exception {
        Device d = save("Old-Name", "Ravi", "S-3");
        mvc.perform(post("/devices/" + d.getId()).session(admin()).param("name", "New-Name").param("owner", "Ravi")
                .param("serialNo", "S-3").param("os", "Linux").param("firewallEnabled", "true"))
                .andExpect(status().is3xxRedirection());
        assertEquals("New-Name", repository.findById(d.getId()).get().getName());
    }

    @Test
    void dashboardLoads() throws Exception {
        mvc.perform(get("/dashboard").session(admin())).andExpect(status().isOk())
                .andExpect(model().attributeExists("total", "compliant", "nonCompliant"));
    }
}
