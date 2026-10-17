package com.dcmp.portal.user;

import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

/** Seeds one demo user per role on first start. Demo credentials are listed in the README. */
@Component
public class DataSeeder implements CommandLineRunner {

    private final UserRepository users;

    public DataSeeder(UserRepository users) {
        this.users = users;
    }

    @Override
    public void run(String... args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        seed(encoder, "admin", "admin123", "ADMIN");
        seed(encoder, "auditor", "auditor123", "AUDITOR");
        seed(encoder, "tech", "tech123", "TECHNICIAN");
    }

    private void seed(BCryptPasswordEncoder encoder, String username, String password, String role) {
        if (!users.findByUsername(username).isPresent()) {
            users.save(new AppUser(username, encoder.encode(password), role));
        }
    }
}
