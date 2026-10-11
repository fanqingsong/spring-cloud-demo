//package com.roncoo.education.configuration;
//
//import org.springframework.cloud.loadbalancer.annotation.LoadBalancerClient;
//import org.springframework.context.annotation.Configuration;
//
///**
// * 为 spring-cloud-provider2 指定负载均衡配置（示例，默认不启用）。
// * <p>
// * 原课程为 @RibbonClient + RoundRobinRuleConfig；Ribbon 已移除，需改用 @LoadBalancerClient。
// */
//@Configuration
//@LoadBalancerClient(name = "spring-cloud-provider2", configuration = RoncooCustomRuleConfig.class)
//public class Provider2Configuration {
//
//}
