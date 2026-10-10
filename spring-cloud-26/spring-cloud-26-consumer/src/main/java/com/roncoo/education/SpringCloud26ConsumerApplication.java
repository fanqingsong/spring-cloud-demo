package com.roncoo.education;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients(basePackages = "com.roncoo.education.feign")
@EnableDiscoveryClient
@SpringBootApplication
public class SpringCloud26ConsumerApplication {

	public static void main(String[] args) {
		SpringApplication.run(SpringCloud26ConsumerApplication.class, args);
	}

}
