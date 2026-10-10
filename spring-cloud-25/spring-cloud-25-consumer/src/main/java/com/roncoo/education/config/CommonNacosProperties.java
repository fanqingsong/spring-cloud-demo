package com.roncoo.education.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cloud.context.config.annotation.RefreshScope;

@RefreshScope
@ConfigurationProperties(prefix = "common")
public class CommonNacosProperties {

	private String courseTag = "local-fallback";

	private String configSource = "local";

	public String getCourseTag() {
		return courseTag;
	}

	public void setCourseTag(String courseTag) {
		this.courseTag = courseTag;
	}

	public String getConfigSource() {
		return configSource;
	}

	public void setConfigSource(String configSource) {
		this.configSource = configSource;
	}

}
