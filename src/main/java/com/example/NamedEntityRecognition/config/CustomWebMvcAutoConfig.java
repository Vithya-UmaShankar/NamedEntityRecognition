package com.example.NamedEntityRecognition.config;

import com.example.NamedEntityRecognition.controller.MainController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.AutoConfigureAfter;
import org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.resource.PathResourceResolver;

@Configuration()
@AutoConfigureAfter(DispatcherServletAutoConfiguration.class)
public class CustomWebMvcAutoConfig implements WebMvcConfigurer {

    @Autowired
    MainController mainController;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String imagePath = "file://" + mainController.APP_PATH + "Images/";

        registry.addResourceHandler("/Images/**")
                .addResourceLocations(imagePath)
                .setCachePeriod(3600)
                .resourceChain(true)
                .addResolver(new PathResourceResolver());


    }
}
