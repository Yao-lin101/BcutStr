import json
import re
from datetime import datetime
import copy
from pathlib import Path

class SrtToBcut:
    def __init__(self, json_template_path: str, srt_file_path: str):
        """
        初始化转换器
        :param json_template_path: 必剪JSON模板文件路径
        :param srt_file_path: SRT字幕文件路径
        """
        self.json_template_path = Path(json_template_path)
        self.srt_file_path = Path(srt_file_path)
        self.config = None
        self.base_clip = None

    @staticmethod
    def parse_srt_time(time_str: str) -> int:
        """
        将SRT时间格式转换为毫秒
        :param time_str: HH:MM:SS,mmm 格式的时间字符串
        :return: 毫秒数
        """
        time_obj = datetime.strptime(time_str, '%H:%M:%S,%f')
        return int(time_obj.hour * 3600000 + 
                  time_obj.minute * 60000 + 
                  time_obj.second * 1000 + 
                  time_obj.microsecond / 1000)

    def parse_srt(self) -> list:
        """
        解析SRT文件
        :return: 字幕列表
        """
        with open(self.srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        subtitle_pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.*?\n)*?)(?:\n|$)'
        subtitles = []
        
        for match in re.finditer(subtitle_pattern, content):
            index = int(match.group(1))
            start_time = self.parse_srt_time(match.group(2))
            end_time = self.parse_srt_time(match.group(3))
            text = match.group(4).strip()
            
            subtitles.append({
                'index': index,
                'start': start_time,
                'end': end_time,
                'text': text,
                'duration': end_time - start_time
            })
        
        return subtitles

    def create_subtitle_clip(self, subtitle: dict) -> dict:
        """
        创建必剪字幕片段
        :param subtitle: 字幕信息
        :return: 必剪字幕片段配置
        """
        if not self.base_clip:
            raise ValueError("未初始化基础字幕片段模板")

        clip = copy.deepcopy(self.base_clip)
        
        # 更新关键信息
        clip['30011'] = subtitle['start']  # inPoint
        clip['30012'] = subtitle['duration']  # duration
        clip['30021'] = subtitle['start']  # 起始位置
        clip['duration'] = subtitle['duration']
        clip['inPoint'] = subtitle['start']
        clip['outPoint'] = subtitle['end']
        clip['trimIn'] = 0
        clip['trimOut'] = subtitle['duration']
        clip['AssetInfo']['content'] = subtitle['text']
        clip['AssetInfo']['duration'] = subtitle['duration']
        
        # 生成新的唯一ID
        clip['m_id'] = int(datetime.now().timestamp() * 1000) + subtitle['index']
        
        return clip

    def load_template(self):
        """
        加载必剪JSON模板
        """
        with open(self.json_template_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        # 获取字幕轨道
        subtitle_track = next((track for track in self.config['tracks'] 
                             if track['BTrackType'] == 0), None)
        
        if not subtitle_track or not subtitle_track['clips']:
            raise ValueError("未找到有效的字幕轨道或字幕片段模板")
            
        self.base_clip = subtitle_track['clips'][0]
        return subtitle_track

    def convert(self) -> str:
        """
        执行转换
        :return: 输出文件路径
        """
        # 加载模板并获取字幕轨道
        subtitle_track = self.load_template()
        
        # 解析SRT
        subtitles = self.parse_srt()
        
        # 清空现有字幕
        subtitle_track['clips'] = []
        
        # 创建新的字幕片段
        for subtitle in subtitles:
            new_clip = self.create_subtitle_clip(subtitle)
            subtitle_track['clips'].append(new_clip)
        
        # 生成输出文件路径
        output_file = self.json_template_path.parent / f"{self.json_template_path.stem}_updated.json"
        
        # 保存更新后的配置
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        
        return str(output_file)

def main():
    """
    主函数
    """
    # 设置文件路径
    json_template = "testjson/11-44-04-256--{27b1e7cc-0907-4f15-bfc9-ff77fbf0c586}.json"
    srt_file = "teststr/还活着(1).srt"
    
    try:
        converter = SrtToBcut(json_template, srt_file)
        output_file = converter.convert()
        print(f'转换成功！新配置文件已保存为: {output_file}')
    except Exception as e:
        print(f'转换失败：{str(e)}')

if __name__ == "__main__":
    main() 