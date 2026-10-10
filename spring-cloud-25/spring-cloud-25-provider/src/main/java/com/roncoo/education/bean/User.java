package com.roncoo.education.bean;

import java.util.Date;

public class User {

	private int id;

	private String name;

	private Date createTime;

	private String greeting;

	private String instanceTag;

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Date getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}

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
