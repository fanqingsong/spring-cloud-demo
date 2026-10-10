package com.roncoo.education;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

import com.roncoo.education.config.CommonNacosProperties;
import com.roncoo.education.config.ProviderNacosProperties;

@EnableDiscoveryClient
@EnableConfigurationProperties({ ProviderNacosProperties.class, CommonNacosProperties.class })
@SpringBootApplication
public class SpringCloud25ProviderApplication {

	public static void main(String[] args) {
		SpringApplication.run(SpringCloud25ProviderApplication.class, args);
	}

}
