package com.roncoo.education;

import java.util.function.Consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class StreamApplication {

	private static final Logger log = LoggerFactory.getLogger(StreamApplication.class);

	public static void main(String[] args) {
		SpringApplication.run(StreamApplication.class, args);
	}

	@Bean
	Consumer<String> demoConsumer() {
		return message -> log.info("Spring Cloud Stream 收到消息: {}", message);
	}
}
