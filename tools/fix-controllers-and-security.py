#!/usr/bin/env python3
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent

SECURITY = """package com.roncoo.education;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class EurekaSecurityConfiguration {

	@Bean
	SecurityFilterChain eurekaSecurityFilterChain(HttpSecurity http) throws Exception {
		http.csrf(csrf -> csrf.disable())
				.authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
				.httpBasic(Customizer.withDefaults());
		return http.build();
	}
}
"""

for f in root.rglob("UserController.java"):
    t = f.read_text()
    t = re.sub(r"import com\.netflix\.hystrix[^\n]*\n", "", t)
    t = re.sub(
        r"@HystrixCommand\([^\)]*\)\n(\s*//@CircuitBreaker[^\n]*\n)?",
        '@CircuitBreaker(name = "getUser", fallbackMethod = "getFallback")\n',
        t,
    )
    t = re.sub(r"\s*// @HystrixCommand[^\n]*\n", "", t)
    if "@CircuitBreaker" in t and "resilience4j" not in t:
        t = t.replace(
            "import org.springframework.web.client.RestTemplate;\n",
            "import org.springframework.web.client.RestTemplate;\n\n"
            "import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;\n",
        )
    f.write_text(t)

for pom in root.rglob("pom.xml"):
    if "spring-cloud-starter-netflix-eureka-server" not in pom.read_text():
        continue
    app = pom.parent / "src/main/java/com/roncoo/education/ServiceApplication.java"
    if not app.exists():
        continue
    sec = app.parent / "EurekaSecurityConfiguration.java"
    if not sec.exists():
        sec.write_text(SECURITY)
