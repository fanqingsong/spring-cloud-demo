package com.roncoo.education;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(properties = {
		"spring.cloud.nacos.discovery.enabled=false",
		"spring.cloud.openfeign.circuitbreaker.enabled=false",
})
class SpringCloud26ConsumerApplicationTests {

	@Test
	void contextLoads() {
	}

}
