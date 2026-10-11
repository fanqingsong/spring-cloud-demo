//package com.roncoo.education.configuration;
//
//import org.springframework.cloud.loadbalancer.annotation.LoadBalancerClient;
//import org.springframework.context.annotation.Configuration;
//
///**
// * 为 spring-cloud-provider 挂上自定义负载均衡规则。
// * <p>
// * 原课程用 @RibbonClient + *.ribbon.NFLoadBalancerRuleClassName；
// * 现改为 @LoadBalancerClient（Spring Cloud LoadBalancer）。
// * <p>
// * 本课重点是 OpenFeign；自定义规则见第 09 课。需要演示时取消本文件注释即可。
// */
//@Configuration
//@LoadBalancerClient(name = "spring-cloud-provider", configuration = RoncooCustomRuleConfig.class)
//public class ProviderConfiguration {
//
//}
