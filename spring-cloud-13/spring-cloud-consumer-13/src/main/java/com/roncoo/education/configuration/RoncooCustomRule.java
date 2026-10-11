package com.roncoo.education.configuration;

import java.util.List;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.cloud.client.ServiceInstance;
import org.springframework.cloud.client.loadbalancer.DefaultResponse;
import org.springframework.cloud.client.loadbalancer.EmptyResponse;
import org.springframework.cloud.client.loadbalancer.Request;
import org.springframework.cloud.client.loadbalancer.Response;
import org.springframework.cloud.loadbalancer.core.NoopServiceInstanceListSupplier;
import org.springframework.cloud.loadbalancer.core.ReactorServiceInstanceLoadBalancer;
import org.springframework.cloud.loadbalancer.core.ServiceInstanceListSupplier;

import reactor.core.publisher.Mono;

/**
 * 自定义负载均衡策略（Spring Cloud LoadBalancer）。
 * <p>
 * 原课程基于 Netflix Ribbon 的 AbstractLoadBalancerRule；
 * 本仓库已升级到 Spring Cloud 2024，改为实现 ReactorServiceInstanceLoadBalancer。
 */
public class RoncooCustomRule implements ReactorServiceInstanceLoadBalancer {

	private final String serviceId;
	private final ObjectProvider<ServiceInstanceListSupplier> serviceInstanceListSupplierProvider;

	public RoncooCustomRule(ObjectProvider<ServiceInstanceListSupplier> serviceInstanceListSupplierProvider,
			String serviceId) {
		this.serviceId = serviceId;
		this.serviceInstanceListSupplierProvider = serviceInstanceListSupplierProvider;
	}

	@Override
	public Mono<Response<ServiceInstance>> choose(Request request) {
		ServiceInstanceListSupplier supplier = serviceInstanceListSupplierProvider
				.getIfAvailable(NoopServiceInstanceListSupplier::new);
		return supplier.get(request).next().map(this::choose);
	}

	/**
	 * 从可用实例列表中选出端口为 7779 的实例。
	 */
	private Response<ServiceInstance> choose(List<ServiceInstance> instances) {
		if (instances == null || instances.isEmpty()) {
			return new EmptyResponse();
		}

		// 只获取端口为：7779的服务实例
		for (ServiceInstance instance : instances) {
			if (instance.getPort() == 7779) {
				System.out.println("实例IP：" + instance.getHost() + " 端口：" + instance.getPort()
						+ " serviceId=" + serviceId);
				return new DefaultResponse(instance);
			}
		}

		return new EmptyResponse();
	}

}
