package com.roncoo.education.controller;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/demo")
public class WeightDemoController {

	private static final String LABEL_URL = "http://spring-cloud-27-provider/api/instance-label";

	private final RestTemplate restTemplate;

	public WeightDemoController(RestTemplate restTemplate) {
		this.restTemplate = restTemplate;
	}

	@GetMapping("/weight")
	public Map<String, Object> weightStats(@RequestParam(name = "times", defaultValue = "100") int times) {
		if (times < 1) {
			times = 1;
		}
		if (times > 500) {
			times = 500;
		}
		Map<String, Integer> hits = new TreeMap<>();
		for (int i = 0; i < times; i++) {
			String label = restTemplate.getForObject(LABEL_URL, String.class);
			String key = label == null ? "null" : label;
			hits.merge(key, 1, Integer::sum);
		}
		Map<String, Object> result = new LinkedHashMap<>();
		result.put("times", times);
		result.put("hitsByInstanceLabel", hits);
		result.put("hint", "默认 Compose：weight-high(100) 与 weight-low(1)，high 命中应明显多于 low");
		return result;
	}

}
