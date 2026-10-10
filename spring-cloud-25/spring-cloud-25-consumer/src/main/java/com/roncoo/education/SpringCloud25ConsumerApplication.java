package com.roncoo.education;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

import com.roncoo.education.config.CommonNacosProperties;
import com.roncoo.education.config.ConsumerNacosProperties;

@EnableDiscoveryClient
@EnableConfigurationProperties({ ConsumerNacosProperties.class, CommonNacosProperties.class })
@SpringBootApplication
public class SpringCloud25ConsumerApplication {

	@Bean
	@LoadBalanced
	RestTemplate restTemplate() {
		return new RestTemplate();
	}

	public static void main(String[] args) {
		SpringApplication.run(SpringCloud25ConsumerApplication.class, args);
	}

}
