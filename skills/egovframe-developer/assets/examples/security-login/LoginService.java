package org.example.egov.login.service;

import org.example.egov.login.web.LoginRequest;
import org.example.egov.login.web.LoginResponse;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Service;

@Service
public class LoginService {
    private final AuthenticationManager authenticationManager;

    public LoginService(AuthenticationManager authenticationManager) {
        this.authenticationManager = authenticationManager;
    }

    public LoginResponse login(LoginRequest request) {
        var token = new UsernamePasswordAuthenticationToken(request.userId(), request.password());
        var authentication = authenticationManager.authenticate(token);
        return new LoginResponse(authentication.getName());
    }
}
