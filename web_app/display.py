
import textwrap

def print_summary(summary_text: str):
    """
    格式化并美观地打印视频摘要。

    Args:
        summary_text: 摘要的字符串文本。
    """
    print("\n" + "="*60)
    print(" " * 24 + "视频摘要结果")
    print("="*60)

    # 使用 textwrap 自动换行，使长文本在终端中更易读
    # width=60 匹配上面的分割线长度
    wrapped_text = textwrap.fill(summary_text, width=60)
    
    # 打印时左右留出一些边距
    for line in wrapped_text.split('\n'):
        print(f"  {line}")

    print("\n" + "="*60)

if __name__ == '__main__':
    # 用于直接测试 display.py 模块
    test_summary = "这是一个用于测试显示模块的摘要文本。它演示了如何将一段可能很长的文本进行格式化，使其在标准的终端窗口中能够美观、清晰地显示出来，通过自动换行和添加标题，提升了最终结果的可读性。"
    print("--- 开始测试显示模块 ---")
    print_summary(test_summary)
    print("--- 测试结束 ---")
