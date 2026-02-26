import java.util.*;
import java.lang.reflect.*;

print('Hello World')

class Main {
    public static void main(String[] args) {
        try {
            Solution sol = new Solution();
            Object[] methodArgs = new Object[1];
            methodArgs[0] = "A man, a plan, a canal: Panama";
            Method method = null;
            for (Method m : sol.getClass().getDeclaredMethods()) {
                if (m.getName().equals("solution")) {
                    method = m;
                    break;
                }
            }
            
            if (method == null) {
                System.err.println("Method 'solution' not found");
                return;
            }
            
            Object result = method.invoke(sol, methodArgs);
            
            // Handle void return type (assume in-place modification of first arg)
            if (method.getReturnType().equals(Void.TYPE)) {
                if (methodArgs.length > 0) {
                    printResult(methodArgs[0]);
                } else {
                    System.out.println("null");
                }
            } else {
                printResult(result);
            }
        
        } catch (IllegalArgumentException e) {
            System.err.println("Runtime Error: Argument Mismatch. Check input types.");
            e.printStackTrace(System.err);
            System.exit(1);
        } catch (Exception e) {
            System.err.println("Runtime Error: " + e.getMessage());
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }

    static void printResult(Object result) {
        if (result == null) {
            System.out.println("null");
        } else if (result instanceof int[]) {
            System.out.print("[");
            int[] arr = (int[]) result;
            for (int i = 0; i < arr.length; i++) {
                System.out.print(arr[i]);
                if (i < arr.length - 1) System.out.print(", ");
            }
            System.out.println("]");
        } else if (result instanceof char[]) {
            System.out.print("[");
            char[] arr = (char[]) result;
            for (int i = 0; i < arr.length; i++) {
                System.out.print("\"" + arr[i] + "\"");
                if (i < arr.length - 1) System.out.print(", ");
            }
            System.out.println("]");
        } else if (result instanceof Boolean) {
            System.out.println(((Boolean) result).toString().toLowerCase());
        } else {
            System.out.println(result);
        }
    }
}
