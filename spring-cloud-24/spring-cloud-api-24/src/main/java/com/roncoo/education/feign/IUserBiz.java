package com.roncoo.education.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import com.roncoo.education.bean.User;
import com.roncoo.education.service.UserService;

@FeignClient(name = "spring-cloud-provider")
public interface IUserBiz extends UserService {

	@Override
	@GetMapping("/api/user/{id}")
	User find(@PathVariable("id") int id);
}
