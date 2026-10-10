package com.roncoo.education.controller;

import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.roncoo.education.bean.User;
import com.roncoo.education.config.CommonNacosProperties;
import com.roncoo.education.config.ProviderNacosProperties;

@RestController
@RequestMapping("/api")
public class ApiUserController {

	private static final Logger log = LoggerFactory.getLogger(ApiUserController.class);

	private final ProviderNacosProperties providerProperties;

	private final CommonNacosProperties commonProperties;

	public ApiUserController(ProviderNacosProperties providerProperties, CommonNacosProperties commonProperties) {
		this.providerProperties = providerProperties;
		this.commonProperties = commonProperties;
	}

	@GetMapping("/user/{id}")
	public User view(@PathVariable int id) {
		User user = new User();
		user.setId(id);
		user.setName("无境");
		user.setCreateTime(new Date());
		user.setGreeting(providerProperties.getGreeting());
		user.setInstanceTag(providerProperties.getInstanceTag());
		log.info("Provider 返回用户 {}，greeting={}", id, user.getGreeting());
		return user;
	}

	@GetMapping("/config/snapshot")
	public Map<String, Object> configSnapshot() {
		Map<String, Object> body = new LinkedHashMap<>();
		body.put("provider.greeting", providerProperties.getGreeting());
		body.put("provider.instance-tag", providerProperties.getInstanceTag());
		body.put("common.course-tag", commonProperties.getCourseTag());
		body.put("common.config-source", commonProperties.getConfigSource());
		return body;
	}

}
