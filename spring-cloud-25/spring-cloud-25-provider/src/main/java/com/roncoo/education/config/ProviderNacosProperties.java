package com.roncoo.education.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cloud.context.config.annotation.RefreshScope;

@RefreshScope
@ConfigurationProperties(prefix = "provider")
public class ProviderNacosProperties {

	private String greeting = "默认问候（本地 fallback）";

	private String instanceTag = "default";

	public String getGreeting() {
		return greeting;
	}

	public void setGreeting(String greeting) {
		this.greeting = greeting;
	}

	public String getInstanceTag() {
		return instanceTag;
	}

	public void setInstanceTag(String instanceTag) {
		this.instanceTag = instanceTag;
	}

}
