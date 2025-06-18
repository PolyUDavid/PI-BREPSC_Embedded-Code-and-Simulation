#!/usr/bin/env python3

if __name__ == "__main__":
    import sys
    import os
    
    # 设置输出不缓冲，确保实时显示
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except AttributeError:
        pass  # 忽略某些环境下的缓冲设置失败
    
    print("--- 最终审查门控激活 ---", flush=True)
    print()
    
    while True:
        try:
            print("系统已完成主要操作。等待您的审查或进一步的子指令。", flush=True)
            print("请输入子指令，或输入以下命令之一: 'TASK_COMPLETE', 'Done', 'Quit', 'q' 来表示完成。", flush=True)
            print()
            
            # 下面这行是关键 - 系统将"监听"此行
            # 用户不需要解析这个，但这对用户可见性很好。
            print("REVIEW_GATE_AWAITING_INPUT:", end="", flush=True)
            
            try:
                user_input = input().strip()
                
                if user_input.lower() in ['task_complete', 'done', 'quit', 'q']:
                    print(f"--- 审查门控: 收到完成信号 '{user_input}' ---", flush=True)
                    print("--- 最终审查门控脚本退出 ---", flush=True)
                    break
                elif user_input:
                    print(f"--- 审查门控: 收到子指令 '{user_input}' ---", flush=True)
                    print("请等待系统处理您的指令...", flush=True)
                    print()
                    # 这是关键行 - 系统将"监听"此行。
                    print(f"USER_SUB_PROMPT: {user_input}", flush=True)
                    break
                else:
                    # 如果用户只是按了回车，循环继续，
                    # "REVIEW_GATE_AWAITING_INPUT:" 将再次打印。
                    pass
                    
            except EOFError:
                print("\n--- 审查门控: 输入流结束 ---", flush=True)
                break
                
        except KeyboardInterrupt:
            print("\n--- 审查门控: 会话被用户中断 (KeyboardInterrupt) ---", flush=True)
            break
        except Exception as e:
            print(f"\n--- 审查门控: 意外错误: {e} ---", flush=True)
            break
    
    print("--- 最终审查门控脚本退出 ---", flush=True) 