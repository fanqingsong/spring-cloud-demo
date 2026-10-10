package com.roncoo.education.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import com.roncoo.education.feign.fallback.UserFeignFallback;

@FeignClient(value = "spring-cloud-26-provider", fallback = UserFeignFallback.class)
public interface IUserBiz {

	@GetMapping("/api/user/{id}")
	String view(@PathVariable("id") int id);

}
