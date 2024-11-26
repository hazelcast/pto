package hazelcast.platform.javarunner;

import java.util.Map;

public class NullTest extends JavaTest {
    @Override
    public void init(Map<String, String> testProps) {

    }

    @Override
    public Object prepareNext() {
        return null;
    }

    @Override
    public void runTest(Object t) {
    }

}
