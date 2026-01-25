import subprocess
import os
import tempfile
import json
import config
import time

class CodeExecutor:
    """Base class for code execution"""
    
    def __init__(self, timeout=config.EXECUTION_TIMEOUT):
        self.timeout = timeout
    
    def execute(self, code, test_input):
        """Execute code with given input. To be implemented by subclasses."""
        raise NotImplementedError


class PythonExecutor(CodeExecutor):
    """Execute Python code"""
    
    def execute(self, code, test_input):
        """
        Execute Python code with test input
        Returns: (success, output, error, execution_time)
        """
        start_time = time.time()
        temp_file = None
        
        try:
            # Check syntax first for clean error messages
            import ast
            try:
                ast.parse(code)
            except SyntaxError as e:
                return False, '', f"Syntax Error: {e.msg} (Line {e.lineno})", 0.0

            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                temp_file = f.name
                
                # Write user code and test invocation
                f.write(code + '\n\n')
                f.write('# Test execution\n')
                f.write('import json\n')
                f.write('import sys\n')
                f.write(f'test_input = {json.dumps(test_input)}\n')
                f.write('try:\n')
                f.write('    result = solution(**test_input)\n')
                f.write('    print(json.dumps(result), file=sys.stdout)\n')  # Only print result
                f.write('except Exception as e:\n')
                f.write('    print(str(e), file=sys.stderr)\n')
                f.write('    sys.exit(1)\n')
            
            # Execute Python code
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=config.TEMP_DIR
            )
            
            execution_time = time.time() - start_time
            
            # Clean up
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, result.stdout.strip(), '', execution_time
            else:
                return False, '', result.stderr.strip(), execution_time
                
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return False, '', 'Time Limit Exceeded', execution_time
            
        except Exception as e:
            execution_time = time.time() - start_time
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return False, '', str(e), execution_time


class JavaExecutor(CodeExecutor):
    """Execute Java code"""
    
    def execute(self, code, test_input):
        """
        Execute Java code with test input
        Returns: (success, output, error, execution_time)
        """
        start_time = time.time()
        temp_dir = None
        
        try:
            # Check if javac is available
            javac_cmd = 'javac'
            try:
                subprocess.run(
                    [javac_cmd, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            except FileNotFoundError:
                # Try specific detected path
                fallback_javac = r"C:\Program Files\Java\jdk-1.8\bin\javac.exe"
                if os.path.exists(fallback_javac):
                    javac_cmd = fallback_javac
                else:
                    execution_time = time.time() - start_time
                if 'javac' in str(e):
                    hint = "Java Compiler (javac) not found. If on Cloud, ensure Docker is used."
                elif 'java' in str(e):
                    hint = "Java Runtime (java) not found. If on Cloud, ensure Docker is used."
                else:
                    hint = "Check JDK installation."
                
                error_msg = (
                    f"Java execution failed: {str(e)}\\n\\n"
                    f"Hint: {hint}\\n"
                    "Please contact the organizer."
                )
                return False, '', error_msg, execution_time
            
            # Create temporary directory for Java files
            temp_dir = tempfile.mkdtemp(dir=config.TEMP_DIR)
            java_file = os.path.join(temp_dir, 'Solution.java')
            
            # Generate test harness based on input parameters
            test_harness = self._generate_test_harness(test_input)
            
            # Write complete Java program with proper newlines
            with open(java_file, 'w', encoding='utf-8') as f:
                f.write('import java.util.*;\n')
                f.write('import java.lang.reflect.*;\n\n')
                f.write(code + '\n\n')
                f.write(test_harness)
            
            # Compile Java code (Limit compiler memory to 128m)
            compile_result = subprocess.run(
                [javac_cmd, '-J-Xmx128m', 'Solution.java'],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=temp_dir
            )
            
            if compile_result.returncode != 0:
                execution_time = time.time() - start_time
                self._cleanup(temp_dir)
                return False, '', f'Compilation Error:\n{compile_result.stderr}', execution_time
            
            # Execute Java code (Limit runtime memory to 64m)
            run_result = subprocess.run(
                ['java', '-Xmx64m', 'Main'],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=temp_dir
            )
            
            execution_time = time.time() - start_time
            
            # Clean up
            self._cleanup(temp_dir)
            
            if run_result.returncode == 0:
                return True, run_result.stdout.strip(), '', execution_time
            else:
                return False, '', run_result.stderr.strip(), execution_time
                
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self._cleanup(temp_dir)
            return False, '', 'Time Limit Exceeded', execution_time
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._cleanup(temp_dir)
            return False, '', str(e), execution_time
    
    def _generate_test_harness(self, test_input):
        """Generate Java test harness based on input parameters"""
        harness = 'class Main {\n'
        harness += '    public static void main(String[] args) {\n'
        harness += '        try {\n'
        harness += '            Solution sol = new Solution();\n'
        
        # Prepare arguments
        params = list(test_input.keys())
        harness += f'            Object[] methodArgs = new Object[{len(params)}];\n'
        
        for i, param in enumerate(params):
            val = self._python_to_java(test_input[param])
            harness += f'            methodArgs[{i}] = {val};\n'
            
        # Find and invoke method using reflection
        harness += '            Method method = null;\n'
        harness += '            for (Method m : sol.getClass().getDeclaredMethods()) {\n'
        harness += '                if (m.getName().equals("solution")) {\n'
        harness += '                    method = m;\n'
        harness += '                    break;\n'
        harness += '                }\n'
        harness += '            }\n'
        harness += '            \n'
        harness += '            if (method == null) {\n'
        harness += '                System.err.println("Method \'solution\' not found");\n'
        harness += '                return;\n'
        harness += '            }\n'
        harness += '            \n'
        harness += '            Object result = method.invoke(sol, methodArgs);\n'
        harness += '            \n'
        harness += '            // Handle void return type (assume in-place modification of first arg)\n'
        harness += '            if (method.getReturnType().equals(Void.TYPE)) {\n'
        harness += '                if (methodArgs.length > 0) {\n'
        harness += '                    printResult(methodArgs[0]);\n'
        harness += '                } else {\n'
        harness += '                    System.out.println("null");\n'
        harness += '                }\n'
        harness += '            } else {\n'
        harness += '                printResult(result);\n'
        harness += '            }\n'
        
        harness += '        } catch (Exception e) {\n'
        harness += '            System.err.println("Runtime Error: " + e.getMessage());\n'
        harness += '            e.printStackTrace(System.err);\n'
        harness += '            System.exit(1);\n'
        harness += '        }\n'
        harness += '    }\n\n'
        
        # Add helper method to print results
        harness += '    static void printResult(Object result) {\n'
        harness += '        if (result == null) {\n'
        harness += '            System.out.println("null");\n'
        harness += '        } else if (result instanceof int[]) {\n'
        harness += '            System.out.print("[");\n'
        harness += '            int[] arr = (int[]) result;\n'
        harness += '            for (int i = 0; i < arr.length; i++) {\n'
        harness += '                System.out.print(arr[i]);\n'
        harness += '                if (i < arr.length - 1) System.out.print(", ");\n'
        harness += '            }\n'
        harness += '            System.out.println("]");\n'
        harness += '        } else if (result instanceof char[]) {\n'
        harness += '            System.out.print("[");\n'
        harness += '            char[] arr = (char[]) result;\n'
        harness += '            for (int i = 0; i < arr.length; i++) {\n'
        harness += '                System.out.print("\\"" + arr[i] + "\\"");\n'
        harness += '                if (i < arr.length - 1) System.out.print(", ");\n'
        harness += '            }\n'
        harness += '            System.out.println("]");\n'
        harness += '        } else if (result instanceof Boolean) {\n'
        harness += '            System.out.println(((Boolean) result).toString().toLowerCase());\n'
        harness += '        } else {\n'
        harness += '            System.out.println(result);\n'
        harness += '        }\n'
        harness += '    }\n'
        harness += '}\n'
        
        return harness
    
    def _python_to_java(self, value):
        """Convert Python value to Java code string"""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            if len(value) == 0:
                return 'new int[0]'
            elif isinstance(value[0], str):
                # char array
                chars = ', '.join([f"'{c}'" for c in value])
                return f'new char[] {{{chars}}}'
            else:
                # int array
                nums = ', '.join([str(v) for v in value])
                return f'new int[] {{{nums}}}'
        return str(value)
    
    def _cleanup(self, temp_dir):
        """Clean up temporary directory"""
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


def get_executor(language):
    """Factory method to get appropriate executor"""
    if language.lower() == 'python':
        return PythonExecutor()
    elif language.lower() == 'java':
        return JavaExecutor()
    else:
        raise ValueError(f"Unsupported language: {language}")
