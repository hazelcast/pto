package hazelcast.platform.javarunner;

import java.util.Map;

public abstract class JavaTest {
    private  String testName;
    public  void init(String testName, Map<String,String> testProps){
        this.testName = testName;
    }

    public abstract void init( Map<String,String> testProps);

    public abstract Object prepareNext();

    public abstract void runTest(Object t);

    public String getTestName() {
        return testName;
    }
}
