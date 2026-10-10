package com.roncoo.education;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@EnableDiscoveryClient
@SpringBootApplication
public class SpringCloud26ProviderApplication {

	public static void main(String[] args) {
		SpringApplication.run(SpringCloud26ProviderApplication.class, args);
	}

}
