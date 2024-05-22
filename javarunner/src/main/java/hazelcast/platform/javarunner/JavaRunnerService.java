package hazelcast.platform.javarunner;

import io.prometheus.metrics.exporter.httpserver.HTTPServer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

import java.io.IOException;

@SpringBootApplication
@ComponentScan(basePackages = "hazelcast.platform.javarunner")
public class JavaRunnerService {

    public static void main(String []args){
        SpringApplication.run(JavaRunnerService.class, args);

        try {
            HTTPServer server = HTTPServer.builder().port(8008).buildAndStart();
            Runtime.getRuntime().addShutdownHook(new Thread(server::close));
        } catch(IOException iox){
            iox.printStackTrace(System.err);
            System.exit(1);
        }

    }
}
