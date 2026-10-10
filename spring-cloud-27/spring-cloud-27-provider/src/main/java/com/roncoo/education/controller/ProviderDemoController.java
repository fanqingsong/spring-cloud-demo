package com.roncoo.education.controller;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class ProviderDemoController {

	@Value("${provider.instance-label:unknown}")
	private String instanceLabel;

	@Value("${spring.cloud.nacos.discovery.weight:1}")
	private int nacosWeight;

	@GetMapping("/instance-label")
	public String instanceLabel() {
		return instanceLabel;
	}

	@GetMapping("/user/{id}")
	public Map<String, Object> user(@PathVariable int id) {
		Map<String, Object> body = new LinkedHashMap<>();
		body.put("id", id);
		body.put("instanceLabel", instanceLabel);
		body.put("nacosWeight", nacosWeight);
		return body;
	}

}
