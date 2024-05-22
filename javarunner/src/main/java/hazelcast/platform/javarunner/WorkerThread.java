package hazelcast.platform.javarunner;

import io.prometheus.metrics.core.metrics.Counter;
import io.prometheus.metrics.core.metrics.Gauge;
import io.prometheus.metrics.core.metrics.Histogram;

import java.util.concurrent.atomic.AtomicBoolean;

public class WorkerThread extends Thread {
    public WorkerThread(String testName, JavaTest test, int rate, Counter requestCount, Histogram requestLatency, Gauge workerSleepTime, AtomicBoolean stopped) {
        this.testName = testName;
        this.test = test;
        this.rate = rate;
        this.requestCount = requestCount;
        this.requestLatency = requestLatency;
        this.stopped = stopped;
        this.workerSleepTime = workerSleepTime;
    }

    private String testName;
    private JavaTest test;
    private Counter requestCount;
    private Histogram requestLatency;

    private Gauge workerSleepTime;
    private AtomicBoolean stopped;

    private int rate;

    public void run(){
        int interval = 1000/ rate;

        long now = System.currentTimeMillis();
        long nextRun = now;
        while(!stopped.get()){
            long sleep = nextRun - now;
            workerSleepTime.labelValues(testName, Thread.currentThread().getName()).set(sleep);
            if (sleep > 0){
                try {
                    Thread.sleep(sleep);
                } catch(InterruptedException ix){
                    System.out.println("Worker interrupted");
                    break;
                }
            }

            Object testCase = test.prepareNext();

            requestLatency.labelValues(testName).time( () -> test.runTest(testCase));
            requestCount.labelValues(testName).inc();

            nextRun += rate;
        }
    }
}
