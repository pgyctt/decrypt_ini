#!/usr/bin/env python3
"""
对称字节变换工具
编码算法: (byte ^ 0x36) >> 3 | ((byte ^ 0x36) & 0x07) << 5
解码算法: ((byte << 3) | (byte >> 5)) ^ 0x36
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
try:
    from tkinter import ttk
except ImportError:
    ttk = None

# 尝试导入 tkinterdnd2 用于拖拽支持
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

def encode_byte(b: int) -> int:
    """编码单个字节（将原文转换为密文）"""
    b &= 0xFF
    temp = b ^ 0x36
    result = ((temp >> 3) | ((temp & 0x07) << 5)) & 0xFF
    return result

def decode_byte(b: int) -> int:
    """解码单个字节（将密文还原为原文）"""
    b &= 0xFF
    result = ((b << 3) | (b >> 5)) & 0xFF
    result ^= 0x36
    return result

def encode_bytes(data: bytes) -> bytes:
    """对字节数据进行编码"""
    return bytes(encode_byte(b) for b in data)

def decode_bytes(data: bytes) -> bytes:
    """对字节数据进行解码"""
    return bytes(decode_byte(b) for b in data)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("对称字节变换工具")
        self.root.geometry("750x620")
        self.root.resizable(True, True)
        self.decoded_content = ""
        self.last_transformed = b""
        self.last_operation = None

        if ttk:
            self.style = ttk.Style()
            self.style.theme_use('clam')

        self._create_styles()
        self._create_widgets()
        
        # 测试算法正确性
        self._test_algorithm()
        
        # 设置拖拽功能
        self._setup_drag_drop()

    def _test_algorithm(self):
        """测试编码解码算法的正确性"""
        test_bytes = [0x00, 0x31, 0x41, 0x61, 0xFF]  # 测试几个关键值
        all_pass = True
        for b in test_bytes:
            encoded = encode_byte(b)
            decoded = decode_byte(encoded)
            if b != decoded:
                all_pass = False
                print(f"警告: 字节 0x{b:02x} 编码后 0x{encoded:02x} 解码后 0x{decoded:02x} 不匹配")
            else:
                print(f"✓ 0x{b:02x} ({chr(b) if 32 <= b <= 126 else '?'}) -> 0x{encoded:02x} -> 0x{decoded:02x}")
        
        if all_pass:
            print("✓ 算法测试通过")
        else:
            print("✗ 算法测试失败")

    def _setup_drag_drop(self):
        """设置文件拖拽功能"""
        if HAS_DND:
            # 使用 tkinterdnd2 库实现拖拽
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_file_drop)
            
            # 在界面上显示拖拽提示
            drop_hint = tk.Label(self.root, text="💡 可以将文件拖拽到此处",
                               font=("Microsoft YaHei", 9),
                               fg="#7f8c8d", bg="#ecf0f1")
            drop_hint.pack(side=tk.BOTTOM, pady=5)
        else:
            # 如果没有 tkinterdnd2，显示提示信息
            drop_hint = tk.Label(self.root, text="💡 提示: 安装 tkinterdnd2 可启用拖拽功能 (pip install tkinterdnd2)",
                               font=("Microsoft YaHei", 8),
                               fg="#95a5a6", bg="#ecf0f1")
            drop_hint.pack(side=tk.BOTTOM, pady=5)
    
    def _on_file_drop(self, event):
        """处理文件拖拽事件"""
        try:
            # 获取拖拽的文件路径
            file_path = event.data
            
            # tkinterdnd2 返回的路径可能包含花括号，需要清理
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            
            # 更新文件输入框
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, file_path)
            
            # 显示提示信息
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, f"已加载文件: {file_path}\n")
            self.text_result.insert(tk.END, "请选择编码或解码操作\n")
            
        except Exception as e:
            messagebox.showerror("错误", f"拖拽文件失败: {e}")

    def _create_styles(self):
        if not ttk:
            return

        self.style.configure("Title.TLabel", font=("Microsoft YaHei", 18, "bold"), foreground="#2c3e50")
        self.style.configure("Section.TLabel", font=("Microsoft YaHei", 11, "bold"), foreground="#34495e")
        self.style.configure("Flat.TButton", font=("Microsoft YaHei", 10), padding=6)
        self.style.configure("Primary.TButton", font=("Microsoft YaHei", 10, "bold"), padding=8)
        self.style.map("Primary.TButton", background=[("active", "#2980b9")])

    def _create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # 标题
        title_label = tk.Label(main_frame, text="对称字节变换工具",
                               font=("Microsoft YaHei", 16, "bold"),
                               fg="#2c3e50", bg="#ecf0f1")
        title_label.pack(pady=(0, 2))

        # 算法说明
        algo_frame = tk.Frame(main_frame, bg="#ecf0f1")
        algo_frame.pack(fill=tk.X, pady=(0, 8))
        
        encode_algo = tk.Label(algo_frame, 
                               text="编码: (byte ^ 0x36) >> 3 | ((byte ^ 0x36) & 0x07) << 5",
                               font=("Consolas", 9),
                               fg="#e67e22", bg="#ecf0f1")
        encode_algo.pack(side=tk.LEFT, padx=(0, 20))
        
        decode_algo = tk.Label(algo_frame, 
                               text="解码: ((byte << 3) | (byte >> 5)) ^ 0x36",
                               font=("Consolas", 9),
                               fg="#27ae60", bg="#ecf0f1")
        decode_algo.pack(side=tk.LEFT)

        # 使用说明
        info_frame = tk.Frame(main_frame, bg="#e8f5e9", relief=tk.RIDGE, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """使用说明：
1. 编码：选择原始文件 → 点击"编码" → 保存加密文件
2. 解码：选择加密文件 → 点击"解码" → 保存还原文件"""
        
        info_label = tk.Label(info_frame, text=info_text,
                              font=("Microsoft YaHei", 9),
                              fg="#2e7d32", bg="#e8f5e9",
                              justify=tk.LEFT)
        info_label.pack(padx=10, pady=8)

        # 文件选择区域
        file_frame = tk.Frame(main_frame, bg="#ecf0f1")
        file_frame.pack(fill=tk.X, pady=5)

        if ttk:
            tk.Label(file_frame, text="选择文件:", font=("Microsoft YaHei", 10),
                     fg="#34495e", bg="#ecf0f1").pack(side=tk.LEFT, padx=(0, 10))

            self.entry_file = ttk.Entry(file_frame, width=55, font=("Microsoft YaHei", 10))
            self.entry_file.pack(side=tk.LEFT, padx=5)

            btn_browse = ttk.Button(file_frame, text="浏览", command=self.browse_file, style="Flat.TButton")
            btn_browse.pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(file_frame, text="选择文件:", font=("Microsoft YaHei", 10),
                     fg="#34495e", bg="#ecf0f1").pack(side=tk.LEFT, padx=(0, 10))

            self.entry_file = tk.Entry(file_frame, width=55, font=("Microsoft YaHei", 10))
            self.entry_file.pack(side=tk.LEFT, padx=5)

            btn_browse = tk.Button(file_frame, text="浏览", command=self.browse_file,
                                   bg="#3498db", fg="white", font=("Microsoft YaHei", 9),
                                   relief=tk.FLAT, padx=15, pady=5)
            btn_browse.pack(side=tk.LEFT, padx=5)

        # 按钮区域
        btn_frame = tk.Frame(main_frame, bg="#ecf0f1")
        btn_frame.pack(pady=10)

        if ttk:
            self.btn_encode = ttk.Button(btn_frame, text="🔒 编码", command=self.encode, style="Primary.TButton")
            self.btn_encode.pack(side=tk.LEFT, padx=10)

            self.btn_decode = ttk.Button(btn_frame, text="🔓 解码", command=self.decode, style="Primary.TButton")
            self.btn_decode.pack(side=tk.LEFT, padx=10)
        else:
            self.btn_encode = tk.Button(btn_frame, text="🔒 编码", command=self.encode,
                                        bg="#e67e22", fg="white", font=("Microsoft YaHei", 10, "bold"),
                                        relief=tk.FLAT, padx=20, pady=5)
            self.btn_encode.pack(side=tk.LEFT, padx=10)

            self.btn_decode = tk.Button(btn_frame, text="🔓 解码", command=self.decode,
                                        bg="#27ae60", fg="white", font=("Microsoft YaHei", 10, "bold"),
                                        relief=tk.FLAT, padx=20, pady=5)
            self.btn_decode.pack(side=tk.LEFT, padx=10)

        # 结果显示区域
        result_frame = tk.Frame(main_frame, bg="#ecf0f1")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        if ttk:
            tk.Label(result_frame, text="处理结果:", font=("Microsoft YaHei", 11, "bold"),
                     fg="#34495e", bg="#ecf0f1").pack(anchor='w', pady=(0, 5))

            text_frame = tk.Frame(result_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)

            self.text_result = scrolledtext.ScrolledText(
                text_frame, height=15, width=80,
                font=("Consolas", 10),
                bg="#2c3e50", fg="#ecf0f1",
                insertbackground="white",
                relief=tk.FLAT,
                padx=10, pady=10
            )
            self.text_result.pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(result_frame, text="处理结果:", font=("Microsoft YaHei", 11, "bold"),
                     fg="#34495e", bg="#ecf0f1").pack(anchor='w', pady=(0, 5))

            text_frame = tk.Frame(result_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)

            self.text_result = scrolledtext.ScrolledText(
                text_frame, height=15, width=80,
                font=("Consolas", 10),
                bg="white", fg="#2c3e50",
                insertbackground="#2c3e50",
                relief=tk.SOLID, borderwidth=1,
                padx=10, pady=10
            )
            self.text_result.pack(fill=tk.BOTH, expand=True)

        # 保存按钮区域
        save_frame = tk.Frame(main_frame, bg="#ecf0f1")
        save_frame.pack(pady=8)

        if ttk:
            self.btn_save = ttk.Button(save_frame, text="💾 保存到文件", command=self.save_to_file, style="Flat.TButton")
            self.btn_save.pack()
        else:
            self.btn_save = tk.Button(save_frame, text="💾 保存到文件", command=self.save_to_file,
                                      bg="#3498db", fg="white", font=("Microsoft YaHei", 10, "bold"),
                                      relief=tk.FLAT, padx=30, pady=8)
            self.btn_save.pack()

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("所有文件", "*.*"), ("INI文件", "*.ini"), ("文本文件", "*.txt")])
        if filename:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, filename)

    def encode(self):
        """编码：将原文转换为密文"""
        filepath = self.entry_file.get().strip()
        if not filepath:
            messagebox.showwarning("警告", "请先选择文件")
            return
        if not os.path.exists(filepath):
            messagebox.showerror("错误", "文件不存在")
            return
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            transformed = encode_bytes(data)
            self.last_transformed = transformed
            self.last_operation = 'encode'
            
            # 编码后的数据是二进制，用十六进制显示
            hex_display = ' '.join(f'{b:02x}' for b in transformed[:256])
            if len(transformed) > 256:
                hex_display += f'\n\n... (共 {len(transformed)} 字节，仅显示前256字节)'
            
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, f"【编码完成】\n")
            self.text_result.insert(tk.END, f"原始大小: {len(data)} 字节\n")
            self.text_result.insert(tk.END, f"编码后大小: {len(transformed)} 字节\n\n")
            self.text_result.insert(tk.END, f"十六进制预览:\n{hex_display}\n\n")
            self.text_result.insert(tk.END, "提示：请点击\"保存到文件\"保存编码后的文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {e}")

    def decode(self):
        """解码：将密文还原为原文"""
        filepath = self.entry_file.get().strip()
        if not filepath:
            messagebox.showwarning("警告", "请先选择文件")
            return
        if not os.path.exists(filepath):
            messagebox.showerror("错误", "文件不存在")
            return
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            transformed = decode_bytes(data)
            self.last_transformed = transformed
            self.last_operation = 'decode'
            
            # 尝试将解码后的数据解析为文本
            try:
                self.decoded_content = transformed.decode('utf-8')
                encoding_used = 'UTF-8'
            except UnicodeDecodeError:                
                # 如果还是失败，显示十六进制
                hex_display = ' '.join(f'{b:02x}' for b in transformed[:256])
                if len(transformed) > 256:
                    hex_display += f'\n\n... (共 {len(transformed)} 字节，仅显示前256字节)'
                self.decoded_content = f"[非文本文件，无法用文本显示]\n\n十六进制预览:\n{hex_display}"
                encoding_used = '无'
            
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, f"【解码完成】\n")
            self.text_result.insert(tk.END, f"原始大小: {len(data)} 字节\n")
            self.text_result.insert(tk.END, f"解码后大小: {len(transformed)} 字节\n")
            
            if encoding_used != '无':
                self.text_result.insert(tk.END, f"文本编码: {encoding_used}\n")
            
            self.text_result.insert(tk.END, f"\n{'='*50}\n\n")
            self.text_result.insert(tk.END, self.decoded_content)
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {e}")

    def save_to_file(self):
        """保存文件（统一保存为二进制格式）"""
        if not self.last_transformed:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        # 根据操作类型设置默认文件名
        if self.last_operation == 'encode':
            default_name = "encoded.ini"
            filetypes = [("加密文件", "*.ini"), ("所有文件", "*.*")]
        elif self.last_operation == 'decode':
            default_name = "decoded.txt"
            filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        else:
            default_name = "output.bin"
            filetypes = [("所有文件", "*.*")]
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".bin",
            initialfile=default_name,
            filetypes=filetypes
        )
        
        if filepath:
            try:
                with open(filepath, 'wb') as f:
                    f.write(self.last_transformed)
                messagebox.showinfo("成功", f"文件已保存到:\n{filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

if __name__ == "__main__":
    if HAS_DND:
        # 使用支持拖拽的 TkinterDnD.Tk()
        root = TkinterDnD.Tk()
    else:
        # 使用普通 Tk()
        root = tk.Tk()
    
    app = App(root)
    root.mainloop()