package com.roncoo.education.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/user")
public class UserController {

	private static final String PROVIDER_URL = "http://spring-cloud-nacos-provider/api/user/{id}";

	private final RestTemplate restTemplate;

	public UserController(RestTemplate restTemplate) {
		this.restTemplate = restTemplate;
	}

	@GetMapping("/{id}")
	public String get(@PathVariable int id) {
		return restTemplate.getForObject(PROVIDER_URL, String.class, id);
	}

}
