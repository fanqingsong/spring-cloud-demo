package com.roncoo.education;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(properties = {
		"spring.cloud.nacos.config.enabled=false",
		"spring.cloud.nacos.discovery.enabled=false",
		"spring.config.import=",
})
class SpringCloud25ConsumerApplicationTests {

	@Test
	void contextLoads() {
	}

}
