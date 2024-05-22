package hazelcast.platform.javarunner;

import io.prometheus.metrics.core.metrics.Counter;
import io.prometheus.metrics.core.metrics.Gauge;
import io.prometheus.metrics.core.metrics.Histogram;
import jakarta.annotation.PostConstruct;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.lang.reflect.InvocationTargetException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

@RestController
public class JavaRunnerController {

    private ScheduledExecutorService executorService;
    private volatile Counter requestCount;
    private volatile Histogram requestLatency;

    private Gauge workerSleepTimeMs;

//    private Counter successCount;
//    private Counter failCount;

    private volatile JavaTest currentTest;

    private Thread []workers;

    private AtomicBoolean stopped;

    @PostConstruct
    public void init(){
        executorService = Executors.newSingleThreadScheduledExecutor();

        requestCount = Counter.builder()
                .name("request_count")
                .help("number of tests requests submitted")
                .labelNames("test_name")
                .register();

//        successCount = Counter.builder()
//                .name("success_count")
//                .help("number of tests requests that completed successfully")
//                .labelNames("test_name")
//                .register();
//
//        failCount = Counter.builder()
//                .name("failure_count")
//                .help("number of tests requests that failed")
//                .labelNames("test_name")
//                .register();

        requestLatency = Histogram.builder()
                .name("response_time")
                .help("time, in milliseconds, for the request to return")
                .labelNames("test_name")
                .register();

        workerSleepTimeMs = Gauge.builder().name("test_worker_sleep_ms")
                .help("the amount of time (in ms) the test worker threads rest between invocations - less than or equal to 0 means this thread cannot keep up")
                .labelNames("test_name", "thread_name")
                .register();
    }

    @PostMapping("/start")
    public synchronized ResponseEntity<String> startTest(@RequestBody TestConfig config){
        if (currentTest == null){
            try {
                stopped = new AtomicBoolean(false);
                // build the test instance
                Class<?> testClass = Class.forName(config.getTestClass());
                currentTest = (JavaTest) testClass.getDeclaredConstructor().newInstance();
                currentTest.init(config.getTestProperties());

                int threadCount = config.getThreads();
                int rate = config.getRequestsPerSecondPerThread();

                workers = new Thread[threadCount];
                for(int i=0;i< threadCount; ++i){
                    workers[i] = new WorkerThread(
                            config.getTestName(),
                            currentTest,
                            rate,
                            requestCount,
                            requestLatency,
                            workerSleepTimeMs,
                            stopped);
                    workers[i].start();
                }

                Stopper stopper = new Stopper();
                executorService.schedule(new Thread(stopper::run), config.getDurationSeconds(), TimeUnit.SECONDS );
                // start the loop
            } catch (ClassNotFoundException | InstantiationException | IllegalAccessException |
                     NoSuchMethodException | InvocationTargetException e) {
                return new ResponseEntity<>("TEST CLASS " + config.getTestClass() +  " COULD NOT BE INSTANTIATED VIA NO-ARG CTOR", HttpStatus.INTERNAL_SERVER_ERROR);
            }
            return new ResponseEntity<>("TEST " + config.getTestClass() + " STARTED", HttpStatus.OK);
        } else {
            return new ResponseEntity<>("TEST ALREADY IN PROGRESS", HttpStatus.LOCKED);
        }
    }

    private class Stopper {
        public void run(){
            stopped.set(true);
            for (Thread t: workers) {
                try {
                    t.join(2000);
                } catch(InterruptedException ix){
                    break;
                }
            }
            currentTest = null;
        }
    }
}
