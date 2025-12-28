
import sys
import os

# 模拟 uvicorn 运行环境，当前工作目录在 h:\trae
print(f"Current working directory: {os.getcwd()}")

# 尝试导入 backend.main
try:
    print("Attempting to import backend.main...")
    import backend.main
    print("SUCCESS: backend.main imported successfully. The import fix works.")
except ImportError as e:
    print(f"ERROR: Failed to import backend.main: {e}")
except Exception as e:
    print(f"ERROR: An unexpected error occurred: {e}")
