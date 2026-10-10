package com.roncoo.education.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/hello")
public class HelloController {

	private static final String PROVIDER_URL = "http://spring-cloud-provider/api/hello";

	@Autowired
	private RestTemplate restTemplate;

	@GetMapping
	public String hello() {
		return restTemplate.getForObject(PROVIDER_URL, String.class);
	}

}
