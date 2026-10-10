package com.roncoo.education.controller;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.roncoo.education.config.CommonNacosProperties;
import com.roncoo.education.config.ConsumerNacosProperties;

@RestController
@RequestMapping("/config")
public class ConfigDemoController {

	private static final String PROVIDER_CONFIG_URL = "http://spring-cloud-nacos-provider/api/config/snapshot";

	private final ConsumerNacosProperties consumerProperties;

	private final CommonNacosProperties commonProperties;

	private final RestTemplate restTemplate;

	public ConfigDemoController(ConsumerNacosProperties consumerProperties, CommonNacosProperties commonProperties,
			RestTemplate restTemplate) {
		this.consumerProperties = consumerProperties;
		this.commonProperties = commonProperties;
		this.restTemplate = restTemplate;
	}

	@GetMapping("/local")
	public Map<String, Object> localConfig() {
		Map<String, Object> body = new LinkedHashMap<>();
		body.put("consumer.hint", consumerProperties.getHint());
		body.put("common.course-tag", commonProperties.getCourseTag());
		body.put("common.config-source", commonProperties.getConfigSource());
		return body;
	}

	@GetMapping("/via-provider")
	@SuppressWarnings("unchecked")
	public Map<String, Object> viaProvider() {
		return restTemplate.getForObject(PROVIDER_CONFIG_URL, Map.class);
	}

}
