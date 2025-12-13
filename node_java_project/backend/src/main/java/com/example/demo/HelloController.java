package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

  @GetMapping("/api/greeting")
  public Greeting greet() {
    return new Greeting("Hello from the Java backend!");
  }

  public record Greeting(String message) {}
}

