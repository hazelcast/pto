package hazelcast.platform.javarunner;

import io.prometheus.metrics.core.metrics.Counter;
import io.prometheus.metrics.core.metrics.Gauge;
import io.prometheus.metrics.core.metrics.Histogram;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicBoolean;

public class WorkerThread extends Thread {
    private static final long MAXIMUM_LATE_NANOS = 5_000_000_000L;  // 5 seconds
    public WorkerThread(String testName, JavaTest test, int rate, Counter requestCount, Histogram requestLatency, Gauge workerSleepTime, AtomicBoolean stopped) {
        this.testName = testName;
        this.test = test;
        this.rate = rate;
        this.requestCount = requestCount;
        this.requestLatency = requestLatency;
        this.stopped = stopped;
        this.workerSleepTime = workerSleepTime;
    }

    private final String testName;
    private final JavaTest test;
    private final Counter requestCount;
    private final Histogram requestLatency;

    private final Gauge workerSleepTime;
    private final AtomicBoolean stopped;

    private final int rate;

    public void run(){
        long interval = 1_000_000_000L / rate;

        long now = System.nanoTime();
        long nextRun = now;
        while(!stopped.get()){
            long sleep = nextRun - now;
            workerSleepTime.labelValues(testName, Thread.currentThread().getName()).set((double) sleep / (double) 1_000_000_000L);
            if (sleep <= -MAXIMUM_LATE_NANOS){
                stopped.set(true);
                System.out.println("Stopping test thread because it can not maintain the required rate");
                continue;
            }
            if (sleep > 0){
                try {
                    Thread.sleep(Duration.ofNanos(sleep));
                } catch(InterruptedException ix){
                    System.out.println("Worker interrupted");
                    break;
                }
            }

            Object testCase = test.prepareNext();

            requestLatency.labelValues(testName).time( () -> test.runTest(testCase));
            requestCount.labelValues(testName).inc();

            nextRun += interval;
        }
    }
}
