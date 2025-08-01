import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import platform


class DraftManager:
    def __init__(self):
        """初始化草稿管理器"""
        system = platform.system()
        if system == 'Windows':
            self.drafts_dir = Path(os.path.expanduser("~/Documents/Bcut Drafts"))
        elif system == 'Darwin':
            self.drafts_dir = Path(os.path.expanduser("~/Movies/Bcut Drafts"))
        else:
            print("未找到草稿目录，请手动指定草稿目录")
            self.drafts_dir = Path(input("请输入草稿目录路径: "))
        
        self.draft_info_path = self.drafts_dir / "draftInfo.json"
        self.drafts = []
        self._load_drafts()

    def _load_drafts(self):
        """加载草稿信息"""
        if not self.drafts_dir.exists():
            raise FileNotFoundError(f"未找到必剪草稿目录: {self.drafts_dir}\n请确保已安装必剪(Bcut)并创建过项目")
            
        if not self.draft_info_path.exists():
            raise FileNotFoundError(f"未找到草稿信息文件: {self.draft_info_path}\n请确保已使用必剪(Bcut)创建过项目")
            
        try:
            with open(self.draft_info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 按修改时间降序排序
                self.drafts = sorted(
                    data.get('draftInfos', []),
                    key=lambda x: x.get('modifyTime', 0),
                    reverse=True
                )
                
            if not self.drafts:
                raise ValueError("草稿列表为空，请先在必剪(Bcut)中创建项目")
                
        except json.JSONDecodeError:
            raise ValueError(f"草稿信息文件格式错误: {self.draft_info_path}")

    def list_drafts(self) -> List[Dict]:
        """列出所有草稿"""
        return self.drafts

    def get_draft_by_id(self, draft_id: str) -> Optional[Dict]:
        """根据ID获取草稿信息"""
        for draft in self.drafts:
            if draft.get('id') == draft_id:
                return draft
        return None

    def get_latest_json_file(self, draft_id: str) -> Optional[Path]:
        """获取指定草稿的最新JSON/BJSON文件"""
        draft_dir = self.drafts_dir / draft_id
        if not draft_dir.exists():
            raise FileNotFoundError(f"草稿目录不存在: {draft_dir}")

        # 获取目录下所有的json和bjson文件
        json_files = list(draft_dir.glob("*.json"))
        bjson_files = list(draft_dir.glob("*.bjson"))
        all_files = json_files + bjson_files
        
        if not all_files:
            raise FileNotFoundError(f"未找到JSON/BJSON文件: {draft_dir}")

        # 按文件修改时间排序，返回最新的
        latest_file = max(all_files, key=lambda f: f.stat().st_mtime)
        return latest_file

    def format_draft_info(self, draft: Dict) -> str:
        """格式化草稿信息用于显示"""
        modify_time = datetime.fromtimestamp(draft['modifyTime'] / 1000).strftime('%m-%d %H:%M')
        return f"{draft['name']} ({modify_time})"

def main():
    """测试函数"""
    manager = DraftManager()
    print("=== 可用的草稿列表 ===")
    for draft in manager.list_drafts():
        print("\n" + manager.format_draft_info(draft))
        latest_json = manager.get_latest_json_file(draft['id'])
        if latest_json:
            print(f"最新配置文件: {latest_json}")
        print("-" * 50)

if __name__ == "__main__":
    main()