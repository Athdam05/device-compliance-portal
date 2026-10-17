package com.dcmp.portal.user;

import javax.servlet.http.HttpSession;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class LoginController {

    public static final String SESSION_USER = "user";

    private final UserRepository users;
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    public LoginController(UserRepository users) {
        this.users = users;
    }

    @GetMapping("/login")
    public String loginForm() {
        return "login";
    }

    @PostMapping("/login")
    public String login(@RequestParam String username, @RequestParam String password,
                        HttpSession session, Model model) {
        AppUser user = users.findByUsername(username).orElse(null);
        if (user == null || !encoder.matches(password, user.getPasswordHash())) {
            model.addAttribute("error", "Invalid username or password");
            return "login";
        }
        session.setAttribute(SESSION_USER, user);
        return "redirect:/devices";
    }

    @PostMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }
}
