package com.roncoo.education.controller;

import org.springframework.cloud.stream.function.StreamBridge;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MessageController {

	private final StreamBridge streamBridge;

	public MessageController(StreamBridge streamBridge) {
		this.streamBridge = streamBridge;
	}

	@PostMapping("/messages")
	public String publish(@RequestParam(defaultValue = "hello-stream") String body) {
		boolean sent = streamBridge.send("demo-topic-out-0", body);
		return sent ? "sent:" + body : "failed";
	}
}
