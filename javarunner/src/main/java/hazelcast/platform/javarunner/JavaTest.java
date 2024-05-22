package hazelcast.platform.javarunner;

import java.util.Map;

public interface JavaTest {
    public void init(Map<String,String> testProps);

    public Object prepareNext();

    public void runTest(Object t);

}
