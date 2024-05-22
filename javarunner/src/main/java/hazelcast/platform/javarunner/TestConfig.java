package hazelcast.platform.javarunner;

import java.util.Map;

public class TestConfig {
    private String testName;
    private String testClass;
    private int threads;
    private int requestsPerSecondPerThread;

    private int durationSeconds;

    private int warmupSeconds;
    private Map<String, String> testProperties;

    @Override
    public String toString() {
        return "TestConfig{" +
                "testName='" + testName + '\'' +
                ", testClass='" + testClass + '\'' +
                ", threads=" + threads +
                ", requestsPerSecondPerThread=" + requestsPerSecondPerThread +
                ", durationSeconds=" + durationSeconds +
                ", warmupSeconds=" + warmupSeconds +
                ", testProperties=" + testProperties +
                '}';
    }

    public String getTestName() {
        return testName;
    }

    public void setTestName(String testName) {
        this.testName = testName;
    }

    public String getTestClass() {
        return testClass;
    }

    public void setTestClass(String testClass) {
        this.testClass = testClass;
    }

    public int getThreads() {
        return threads;
    }

    public void setThreads(int threads) {
        this.threads = threads;
    }

    public int getRequestsPerSecondPerThread() {
        return requestsPerSecondPerThread;
    }

    public void setRequestsPerSecondPerThread(int requestsPerSecondPerThread) {
        this.requestsPerSecondPerThread = requestsPerSecondPerThread;
    }

    public int getDurationSeconds() {
        return durationSeconds;
    }

    public void setDurationSeconds(int durationSeconds) {
        this.durationSeconds = durationSeconds;
    }

    public int getWarmupSeconds() {
        return warmupSeconds;
    }

    public void setWarmupSeconds(int warmupSeconds) {
        this.warmupSeconds = warmupSeconds;
    }

    public Map<String, String> getTestProperties() {
        return testProperties;
    }

    public void setTestProperties(Map<String, String> testProperties) {
        this.testProperties = testProperties;
    }
}
