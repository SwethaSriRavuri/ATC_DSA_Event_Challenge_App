# Contest Reference Solutions

Here are the correct solutions for all 10 problems in both Python and Java.
Use these to test your system.

---

## 1. Two Sum (Easy)
**Python**
```python
def solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Java**
```java
import java.util.HashMap;
import java.util.Map;

class Solution {
    public int[] solution(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            map.put(nums[i], i);
        }
        return new int[]{};
    }
}
```

---

## 2. Reverse String (Easy)
**Python**
```python
def solution(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
    return s
```

**Java**
```java
class Solution {
    public void solution(char[] s) {
        int left = 0;
        int right = s.length - 1;
        while (left < right) {
            char temp = s[left];
            s[left] = s[right];
            s[right] = temp;
            left++;
            right--;
        }
    }
}
```

---

## 3. Valid Palindrome (Easy)
**Python**
```python
def solution(s):
    filtered = [c.lower() for c in s if c.isalnum()]
    return filtered == filtered[::-1]
```

**Java**
```java
class Solution {
    public boolean solution(String s) {
        if (s.isEmpty()) return true;
        int head = 0, tail = s.length() - 1;
        while(head <= tail) {
            char cHead = s.charAt(head);
            char cTail = s.charAt(tail);
            if (!Character.isLetterOrDigit(cHead)) {
                head++;
            } else if(!Character.isLetterOrDigit(cTail)) {
                tail--;
            } else {
                if (Character.toLowerCase(cHead) != Character.toLowerCase(cTail)) {
                    return false;
                }
                head++;
                tail--;
            }
        }
        return true;
    }
}
```

---

## 4. Binary Search (Medium)
**Python**
```python
def solution(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Java**
```java
class Solution {
    public int solution(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            if (nums[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }
}
```

---

## 5. Maximum Subarray (Medium)
**Python**
```python
def solution(nums):
    current_sum = nums[0]
    max_sum = nums[0]
    for i in range(1, len(nums)):
        current_sum = max(nums[i], current_sum + nums[i])
        max_sum = max(max_sum, current_sum)
    return max_sum
```

**Java**
```java
class Solution {
    public int solution(int[] nums) {
        int maxSoFar = nums[0], maxEndingHere = nums[0];
        for (int i = 1; i < nums.length; ++i) {
            maxEndingHere = Math.max(nums[i], maxEndingHere + nums[i]);
            maxSoFar = Math.max(maxSoFar, maxEndingHere);
        }
        return maxSoFar;
    }
}
```

---

## 6. Longest Substring Without Repeating Characters (Medium)
**Python**
```python
def solution(s):
    char_map = {}
    left = 0
    max_len = 0
    for right in range(len(s)):
        if s[right] in char_map:
            left = max(left, char_map[s[right]] + 1)
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Java**
```java
import java.util.HashMap;
import java.util.Map;

class Solution {
    public int solution(String s) {
        if (s.length() == 0) return 0;
        Map<Character, Integer> map = new HashMap<>();
        int maxLen = 0;
        int left = 0;
        for (int i = 0; i < s.length(); i++) {
            if (map.containsKey(s.charAt(i))) {
                left = Math.max(left, map.get(s.charAt(i)) + 1);
            }
            map.put(s.charAt(i), i);
            maxLen = Math.max(maxLen, i - left + 1);
        }
        return maxLen;
    }
}
```

---

## 7. Trapping Rain Water (Hard)
**Python**
```python
def solution(height):
    if not height: return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water
```

**Java**
```java
class Solution {
    public int solution(int[] height) {
        if (height == null || height.length == 0) return 0;
        int left = 0, right = height.length - 1;
        int leftMax = 0, rightMax = 0;
        int water = 0;
        while (left < right) {
            if (height[left] < height[right]) {
                if (height[left] >= leftMax) leftMax = height[left];
                else water += leftMax - height[left];
                left++;
            } else {
                if (height[right] >= rightMax) rightMax = height[right];
                else water += rightMax - height[right];
                right--;
            }
        }
        return water;
    }
}
```

---

## 8. Edit Distance (Hard)
**Python**
```python
def solution(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]
```

**Java**
```java
class Solution {
    public int solution(String word1, String word2) {
        int m = word1.length();
        int n = word2.length();
        int[][] dp = new int[m + 1][n + 1];
        for (int i = 0; i <= m; i++) dp[i][0] = i;
        for (int j = 0; j <= n; j++) dp[0][j] = j;
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i - 1][j], dp[i][j - 1]));
                }
            }
        }
        return dp[m][n];
    }
}
```

---

## 9. Merge k Sorted Lists (Hard)
**Python**
```python
import heapq

def solution(lists):
    # Flatten and sort provided list of lists
    merged = []
    for sublist in lists:
        for item in sublist:
            merged.append(item)
    merged.sort()
    return merged
```

**Java**
```java
import java.util.*;

class Solution {
    public int[] solution(int[][] lists) {
        List<Integer> merged = new ArrayList<>();
        for (int[] list : lists) {
            for (int val : list) {
                merged.add(val);
            }
        }
        Collections.sort(merged);
        int[] result = new int[merged.size()];
        for (int i = 0; i < merged.size(); i++) {
            result[i] = merged.get(i);
        }
        return result;
    }
}
```

---

## 10. Sliding Window Maximum (Hard)
**Python**
```python
from collections import deque

def solution(nums, k):
    q = deque()
    result = []
    for i in range(len(nums)):
        while q and nums[q[-1]] <= nums[i]:
            q.pop()
        q.append(i)
        if q[0] == i - k:
            q.popleft()
        if i >= k - 1:
            result.append(nums[q[0]])
    return result
```

**Java**
```java
import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int[] solution(int[] nums, int k) {
        if (nums == null || k <= 0) return new int[0];
        int n = nums.length;
        int[] result = new int[n - k + 1];
        int ri = 0;
        Deque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < nums.length; i++) {
            while (!q.isEmpty() && q.peek() < i - k + 1) {
                q.poll();
            }
            while (!q.isEmpty() && nums[q.peekLast()] < nums[i]) {
                q.pollLast();
            }
            q.offer(i);
            if (i >= k - 1) {
                result[ri++] = nums[q.peek()];
            }
        }
        return result;
    }
}
```
