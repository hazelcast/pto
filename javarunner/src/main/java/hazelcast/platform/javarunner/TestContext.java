package hazelcast.platform.javarunner;

import io.prometheus.metrics.core.metrics.Counter;
import io.prometheus.metrics.core.metrics.Gauge;
import io.prometheus.metrics.core.metrics.Histogram;

import java.lang.reflect.InvocationTargetException;
import java.util.concurrent.atomic.AtomicBoolean;

/*
 * Encapsulates the information that is shared between tests
 */
public class TestContext {
    private String testName;
    JavaTest test;
    int rate;
    Counter requestCount;
    Histogram requestLatency;
    Gauge workerSleepTimeMs;
    AtomicBoolean stopped;

    TestContext(TestConfig config) throws NoSuchMethodException, InvocationTargetException,
            InstantiationException, IllegalAccessException, ClassNotFoundException {
        this.testName = config.getTestName();
        Class<?> testClass = Class.forName(config.getTestClass());
        this.test = (JavaTest) testClass.getDeclaredConstructor().newInstance();
        this.test.init(config.getTestProperties());
        this.rate = config.getRequestsPerSecondPerThread();

        this.requestCount = Counter.builder()
                .name("request_count")
                .help("number of tests requests submitted")
                .labelNames("test_name")
                .register();

        this.requestLatency = Histogram.builder()
                .name("response_time_s")
                .help("time, in seconds, for the request to return")
                .labelNames("test_name")
                .nativeOnly()
                .register();

        this.workerSleepTimeMs = Gauge.builder().name("test_worker_sleep_ms")
                .help("the amount of time (in ms) the test worker threads rest between invocations - less than or equal to 0 means this thread cannot keep up")
                .labelNames("test_name", "thread_name")
                .register();

        this.stopped = new AtomicBoolean(false);
    }

}
