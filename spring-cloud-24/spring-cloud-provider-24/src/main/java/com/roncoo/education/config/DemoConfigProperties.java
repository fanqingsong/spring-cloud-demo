package com.roncoo.education.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.stereotype.Component;

@Component
@RefreshScope
@ConfigurationProperties(prefix = "demo")
public class DemoConfigProperties {

	private String welcome = "local-default";
	private String sharedMessage = "local-shared";

	public String getWelcome() {
		return welcome;
	}

	public void setWelcome(String welcome) {
		this.welcome = welcome;
	}

	public String getSharedMessage() {
		return sharedMessage;
	}

	public void setSharedMessage(String sharedMessage) {
		this.sharedMessage = sharedMessage;
	}
}
