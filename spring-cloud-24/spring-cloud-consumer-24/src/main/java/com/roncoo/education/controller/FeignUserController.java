package com.roncoo.education.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.roncoo.education.bean.User;
import com.roncoo.education.feign.IUserBiz;

@RestController
@RequestMapping("/feign/user")
public class FeignUserController {

	private final IUserBiz userBiz;

	public FeignUserController(IUserBiz userBiz) {
		this.userBiz = userBiz;
	}

	@GetMapping("/{id}")
	public User find(@PathVariable int id) {
		return userBiz.find(id);
	}
}
