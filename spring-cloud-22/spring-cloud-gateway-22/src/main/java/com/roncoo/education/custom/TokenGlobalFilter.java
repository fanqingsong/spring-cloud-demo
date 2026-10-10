package com.roncoo.education.custom;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;

import reactor.core.publisher.Mono;

@Component
@ConditionalOnProperty(name = "gateway.token-filter.enabled", havingValue = "true")
public class TokenGlobalFilter implements GlobalFilter, Ordered {

	@Override
	public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
		String token = exchange.getRequest().getHeaders().getFirst("token");
		if (!"roncoo".equals(token)) {
			exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
			return exchange.getResponse()
					.writeWith(Mono.just(exchange.getResponse().bufferFactory().wrap("token is error".getBytes())));
		}
		System.out.println("请求路径为：" + exchange.getRequest().getURI().getPath());
		return chain.filter(exchange);
	}

	@Override
	public int getOrder() {
		return 1;
	}
}
