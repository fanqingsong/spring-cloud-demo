package com.roncoo.education.feign.fallback;

import org.springframework.stereotype.Component;

import com.roncoo.education.feign.IUserBiz;

@Component
public class UserFeignFallback implements IUserBiz {

	@Override
	public String view(int id) {
		return "{\"id\":" + id + ",\"fallback\":true,\"message\":\"Provider 不可用，走 Feign 降级\"}";
	}

}
