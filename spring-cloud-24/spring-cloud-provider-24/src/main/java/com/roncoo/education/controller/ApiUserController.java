package com.roncoo.education.controller;

import java.util.Date;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.roncoo.education.bean.User;
import com.roncoo.education.config.DemoConfigProperties;

@RestController
@RequestMapping("/api/user")
public class ApiUserController {

	private static final Logger log = LoggerFactory.getLogger(ApiUserController.class);

	private final DemoConfigProperties demoConfigProperties;

	public ApiUserController(DemoConfigProperties demoConfigProperties) {
		this.demoConfigProperties = demoConfigProperties;
	}

	@GetMapping("/{id}")
	public User find(@PathVariable int id) {
		User user = new User();
		user.setId(id);
		user.setName("无境-24");
		user.setCreateTime(new Date());
		log.info("provider find id={}", id);
		return user;
	}

	@GetMapping("/config/demo")
	public Map<String, String> configDemo() {
		return Map.of(
				"welcome", demoConfigProperties.getWelcome(),
				"sharedMessage", demoConfigProperties.getSharedMessage());
	}
}
