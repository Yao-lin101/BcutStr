# BcutStr

一个用于将SRT字幕文件导入到必剪(BCUT)项目的工具。

目前只试用于Mac端，我没有用过Windows的必剪，不知道Window版本的必剪草稿路径，就没有做适配。

## 功能特点

- 支持标准SRT字幕文件格式
- 自动检测并使用必剪项目中已有的字幕样式
- 自动备份原始项目文件
- 自动管理已处理的字幕文件
- 简单的用户交互界面

## 使用方法

1. 将SRT字幕文件放入 `input` 目录
2. 运行转换脚本：
```bash
python src/main.py
```
3. 从列表中选择要导入字幕的必剪项目
4. 等待转换完成

程序会自动：
- 备份原始项目文件到 `backup` 目录
- 将字幕导入到选择的项目中
- 将处理完的SRT文件移动到 `completed` 目录

## 项目结构

```
BcutStr/
├── src/
│   ├── main.py          # 主程序入口
│   ├── srt_to_bcut.py   # 字幕转换核心逻辑
│   └── draft_manager.py # 必剪项目管理器
├── input/               # 存放待处理的SRT文件
├── backup/             # 存放项目文件备份
├── completed/          # 存放已处理的SRT文件
└── README.md
```

所有必需的目录（`input`、`backup`、`completed`）会在程序首次运行时自动创建。

## 工作目录说明

- `input/`: 存放待处理的SRT文件，运行完成后文件会被移动到 `completed` 目录
- `backup/`: 存放项目文件的备份，每次处理都会生成一个带时间戳的备份文件
- `completed/`: 存放已处理的SRT文件，文件名会添加处理时间戳以避免重名

## 注意事项

- 确保SRT文件使用UTF-8编码
- 确保已安装必剪(BCUT)并创建过项目
- 程序会自动使用最新修改的SRT文件
- 如需恢复原始项目，可以从 `backup` 目录找到备份文件
- 已处理的字幕文件会被移动到 `completed` 目录，不会被删除 