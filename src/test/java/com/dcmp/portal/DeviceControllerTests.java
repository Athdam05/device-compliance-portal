package com.dcmp.portal;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.dcmp.portal.user.AppUser;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = "spring.datasource.url=jdbc:h2:mem:testdb")
@AutoConfigureMockMvc
class DeviceControllerTests {

    @Autowired
    MockMvc mvc;

    private MockHttpSession admin() {
        MockHttpSession session = new MockHttpSession();
        session.setAttribute("user", new AppUser("admin", "x", "ADMIN"));
        return session;
    }

    @Test
    void listPageLoads() throws Exception {
        mvc.perform(get("/devices").session(admin())).andExpect(status().isOk());
    }

    @Test
    void anonymousIsRedirectedToLogin() throws Exception {
        mvc.perform(get("/devices")).andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/login"));
    }

    @Test
    void createRedirectsToDetails() throws Exception {
        mvc.perform(post("/devices").session(admin()).param("name", "Lab-PC-1").param("owner", "Asha")
                .param("serialNo", "SN-T1").param("os", "Windows 11")
                .param("antivirusEnabled", "true"))
                .andExpect(status().is3xxRedirection());
    }

    @Test
    void createWithMissingNameShowsForm() throws Exception {
        mvc.perform(post("/devices").session(admin()).param("owner", "Asha")
                .param("serialNo", "SN-T2").param("os", "Linux"))
                .andExpect(status().isOk())
                .andExpect(view().name("devices/form"));
    }
}
