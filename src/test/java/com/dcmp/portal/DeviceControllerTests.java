package com.dcmp.portal;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = "spring.datasource.url=jdbc:h2:mem:testdb")
@AutoConfigureMockMvc
class DeviceControllerTests {

    @Autowired
    MockMvc mvc;

    @Test
    void listPageLoads() throws Exception {
        mvc.perform(get("/devices")).andExpect(status().isOk());
    }

    @Test
    void createRedirectsToDetails() throws Exception {
        mvc.perform(post("/devices").param("name", "Lab-PC-1").param("owner", "Asha")
                .param("serialNo", "SN-T1").param("os", "Windows 11")
                .param("antivirusEnabled", "true"))
                .andExpect(status().is3xxRedirection());
    }

    @Test
    void createWithMissingNameShowsForm() throws Exception {
        mvc.perform(post("/devices").param("owner", "Asha").param("serialNo", "SN-T2").param("os", "Linux"))
                .andExpect(status().isOk())
                .andExpect(view().name("devices/form"));
    }
}
