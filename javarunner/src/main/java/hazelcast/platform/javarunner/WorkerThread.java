package hazelcast.platform.javarunner;

import java.time.Duration;

public class WorkerThread extends Thread {
    private static final long MAXIMUM_LATE_NANOS = 5_000_000_000L;  // 5 seconds
    public WorkerThread(JavaTest test, int rate, JavaRunnerController controller) {
        this.test = test;
        this.rate = rate;
        this.controller = controller;
    }

    private final JavaTest test;
    private final int rate;

    private final  JavaRunnerController controller;

    public void run(){
        long interval = 1_000_000_000L / rate;

        long now = System.nanoTime();
        long nextRun = now;
        while(!controller.isStopped()){
            long sleep = nextRun - System.nanoTime();
            controller.recordWorkerSleepTime((double) sleep / (double) 1_000_000_000L);
            if (sleep <= -MAXIMUM_LATE_NANOS){
                controller.stopAll(JavaRunnerController.Status.STOPPED_TOO_SLOW);
                System.out.println("Stopping test thread because it can not maintain the required rate");
                continue;
            }
            if (sleep > 0){
                try {
                    Thread.sleep(sleep/1_000_000L, (int) (sleep % 1_000_000));
                } catch(InterruptedException ix){
                    System.out.println("Worker interrupted");
                    break;
                }
            }

            Object testCase = test.prepareNext();

            controller.recordLatency(() -> test.runTest(testCase));
            controller.incrementRequestCount();

            nextRun += interval;
        }
    }
}
