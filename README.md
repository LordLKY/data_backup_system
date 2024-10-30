# virtual_file_system
虚拟文件管理系统

![VFS](https://github.com/LordLKY/virtual_file_system/blob/main/asset/3.jpg)

## About

本项目是一个虚拟文件管理系统，使用Python实现，并拥有命令行界面和基于PyQt的前端界面。包括以下功能：

- 文件的备份与恢复
- 文件的压缩/解压、加密/解密以及打包/解包
- 文件目录查看与比对

本项目的合作者还有：（待补充），非常感谢他们的贡献。

## Usage

### Requirement

- Python 3.8+

### Build

```bash
git clone https://github.com/LordLKY/virtual_file_system.git
cd virtual_file_system
pip install -r requirements.txt
```

### Run

```bash
python cmd.py
python ui.py
```

其中cmd.py是一个命令行风格的界面；ui.py为图形界面。运行ui.py出现以下界面则表示运行成功：

![Main Window of VFS](https://github.com/LordLKY/virtual_file_system/blob/main/asset/2.png)

## Features

### File System

（待补充）

### File Processing

该部分代码位于[该目录](https://github.com/LordLKY/virtual_file_system/tree/main/file_process)，实现了文件压缩/解压、加密/解密以及打包/解包功能。以下是各个功能的简要介绍：

#### zip/unzip

采用了基于哈夫曼编码的压缩算法。根据文件字符频率生成哈夫曼树，依据哈夫曼树进行编码。生成的哈夫曼编码表保存在压缩文件的开头，以便解压时使用。

#### encrypt/decrypt

在简单的异或加密的基础上增加了全排列加密的技巧。由八位密码生成一个64位排列，并根据该排列打乱原文件内容，之后与密码进行异或。

#### pack/unpack

按先序DFS遍历目录下的文件并记录文件信息，将文件信息与文件内容一起打包。解包时根据文件信息重建目录结构。

## Notice

- 本项目中的文件备份/恢复以及目录比对/查看功能需要在完成根目录与用户设置后才能使用
- 本项目中的压缩/加密/打包算法较为简单，仅支持文本文件
- 本项目采用了延迟保存修改的方式，即用户在进行文件备份后，不会立即修改，而是等到用户关闭程序时才提交修改。这提高了程序的运行效率。