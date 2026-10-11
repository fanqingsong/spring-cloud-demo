package com.roncoo.education.configuration;

import org.springframework.cloud.loadbalancer.annotation.LoadBalancerClient;
import org.springframework.context.annotation.Configuration;

/**
 * 为 spring-cloud-provider 挂上自定义负载均衡规则。
 * <p>
 * 原课程用 @RibbonClient + *.ribbon.NFLoadBalancerRuleClassName；
 * 现改为 @LoadBalancerClient（Spring Cloud LoadBalancer）。
 */
@Configuration
@LoadBalancerClient(name = "spring-cloud-provider", configuration = RoncooCustomRuleConfig.class)
public class ProviderConfiguration {

}
