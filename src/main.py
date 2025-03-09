import os
import shutil
from pathlib import Path
from datetime import datetime
from draft_manager import DraftManager
from srt_to_bcut import SrtToBcut

class BcutHelper:
    def __init__(self):
        """初始化"""
        self.workspace = Path(__file__).parent.parent
        self.input_dir = self.workspace / 'input'
        self.backup_dir = self.workspace / 'backup'
        self.completed_dir = self.workspace / 'completed'
        self.draft_manager = DraftManager()
        
        # 确保目录存在
        self.input_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.completed_dir.mkdir(exist_ok=True)

    def get_latest_srt(self) -> Path:
        """获取input目录下最新的srt文件"""
        srt_files = list(self.input_dir.glob('*.srt'))
        if not srt_files:
            raise FileNotFoundError("input目录下没有找到srt文件")
        return max(srt_files, key=lambda f: f.stat().st_mtime)

    def select_draft(self):
        """让用户选择草稿"""
        print("\n=== 可用的草稿列表 ===")
        drafts = self.draft_manager.list_drafts()
        if not drafts:
            raise FileNotFoundError("未找到任何草稿")
        
        # 显示草稿列表
        for i, draft in enumerate(drafts, 1):
            print(f"[{i}] {self.draft_manager.format_draft_info(draft)}")
        
        # 用户选择
        while True:
            try:
                choice = input("\n请选择要导入字幕的草稿编号（输入q退出）: ")
                if choice.lower() == 'q':
                    return None
                index = int(choice) - 1
                if 0 <= index < len(drafts):
                    return drafts[index]
                print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")

    def backup_json(self, json_path: Path) -> Path:
        """备份JSON文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"{json_path.stem}_{timestamp}.json"
        shutil.copy2(json_path, backup_path)
        return backup_path

    def process(self):
        """主处理流程"""
        try:
            # 1. 获取最新的srt文件
            srt_file = self.get_latest_srt()
            print(f"\n找到字幕文件: {srt_file.name}")
            
            # 2. 选择草稿
            selected_draft = self.select_draft()
            if not selected_draft:
                print("用户取消操作")
                return
            
            # 3. 获取最新的JSON文件
            json_path = self.draft_manager.get_latest_json_file(selected_draft['id'])
            if not json_path:
                raise FileNotFoundError(f"未找到草稿的JSON文件")
            
            # 4. 备份JSON文件
            backup_path = self.backup_json(json_path)
            print(f"\nJSON文件已备份: {backup_path.name}")
            
            # 5. 执行转换
            converter = SrtToBcut(str(json_path), str(srt_file))
            output_file = converter.convert()
            print(f"字幕导入完成: {output_file}")
            
            # 6. 移动处理完的srt文件到completed目录
            completed_path = self.completed_dir / srt_file.name
            if completed_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                completed_path = self.completed_dir / f"{srt_file.stem}_{timestamp}{srt_file.suffix}"
            shutil.move(str(srt_file), str(completed_path))
            print(f"字幕文件已移动到: {completed_path.name}")
            
        except Exception as e:
            print(f"\n处理失败: {str(e)}")
            return False
        
        return True

def main():
    """主函数"""
    helper = BcutHelper()
    helper.process()

if __name__ == "__main__":
    main() 