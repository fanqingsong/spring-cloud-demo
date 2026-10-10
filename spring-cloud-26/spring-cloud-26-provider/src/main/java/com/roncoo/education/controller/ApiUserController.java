package com.roncoo.education.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
public class ApiUserController {

	private static final Logger log = LoggerFactory.getLogger(ApiUserController.class);

	@GetMapping("/{id}")
	public String view(@PathVariable int id) {
		String body = "{\"id\":" + id + ",\"name\":\"无境\",\"via\":\"spring-cloud-26-provider\"}";
		log.info("Provider 响应: {}", body);
		return body;
	}

}
