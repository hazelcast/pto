package hazelcast.platform.javarunner;

import java.util.Map;
import java.util.Random;

public class DummyTest extends JavaTest {

    private final Random rand = new Random();
    @Override
    public void init(Map<String, String> testProps) {

    }

    @Override
    public Object prepareNext() {
        int a = rand.nextInt(1000000);
        int b = rand.nextInt(1000000);
        return new int[]{a,b};
    }

    @Override
    public void runTest(Object t) {
        int []ab = (int []) t;
        int a = ab[0];
        int b = ab[1];
        int notUsed = 0;
        if (a <= b)
            notUsed = gcd(a,b);
        else
            notUsed = gcd(b,a);
    }

    // assumes a <= b
    private int gcd(int a, int b){
        if (a == 0) {
            return b;
        } else if (b == 0) {
            return a;
        } else {
            int r = b % a;
            return gcd(r, a);
        }
    }
}
