import json
import re
from datetime import datetime
import copy
from pathlib import Path
from version_adapter import BcutVersionAdapter

class SrtToBcut:
    def __init__(self, json_template_path: str, srt_file_path: str):
        """
        初始化转换器
        :param json_template_path: 必剪JSON模板文件路径
        :param srt_file_path: SRT字幕文件路径
        """
        self.json_template_path = Path(json_template_path)
        self.srt_file_path = Path(srt_file_path)
        self.adapter = BcutVersionAdapter(json_template_path)
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
            content = f.read().strip()  # 去除文件末尾的空白字符

        # 修改正则表达式，使其更准确地匹配SRT格式
        subtitle_pattern = r'(\d+)\r?\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\r?\n((?:.+(?:\r?\n)?)+)'
        subtitles = []
        
        for match in re.finditer(subtitle_pattern, content):
            index = int(match.group(1))
            start_time = self.parse_srt_time(match.group(2))
            end_time = self.parse_srt_time(match.group(3))
            text = match.group(4).strip()
            
            subtitle = {
                'index': index,
                'start': start_time,
                'end': end_time,
                'text': text,
                'duration': end_time - start_time
            }
            subtitles.append(subtitle)
            print(f"解析到字幕: {subtitle}")  # 添加调试信息
        
        print(f"总共解析到 {len(subtitles)} 个字幕")  # 添加调试信息
        return subtitles

    def create_subtitle_clip_template(self) -> dict:
        """
        创建基础字幕片段模板
        :return: 字幕片段模板
        """
        return {
            "1000d": 0,
            "10031": 0,
            "10033": {"B": 1, "L": 0, "R": 1, "T": 0},
            "10035": [-0.47519999742507935, 0.6909000277519226, -0.47519999742507935,
                     0.8291000127792358, 0.47519999742507935, 0.8291000127792358,
                     0.47519999742507935, 0.6909000277519226],
            "10037": [0, -0.7599999904632568],
            "10038": [0.3499999940395355, 1],
            "10040": 0, "10041": 0, "10042": 0, "10043": 100, "10044": 1, "10045": 0,
            "10051": 0, "10052": 0, "10053": 0, "10054": 0, "10055": 0, "10056": 0,
            "10057": 0, "10058": 0, "10059": 0, "10081": "", "10082": -1, "10083": 0,
            "10084": 0, "10085": 0, "10087": 0, "10088": 0, "10089": 0, "10092": 1,
            "10093": -16777216, "10094": 25, "10095": 0, "10096": -16777216,
            "10097": 80, "10098": 2, "10099": 2, "10100": 45, "10101": 0,
            "10102": -16777216, "10103": 40, "10105": "思源黑体 CN",
            "10301": 0, "10302": 0, "10303": 0, "10304": 0, "10306": 0, "10307": 0,
            "10400": 0, "10501": 0,
            "AssetInfo": {
                "assetItemType": 1,
                "audioType": 0,
                "content": "",
                "coverPath": "",
                "displayName": "字幕",
                "duration": 0,
                "fontID": 0,
                "fontSrcPath": "/Applications/BCUT.app/Contents/MacOS/../Resources/Font/Source Han Sans CN Medium.ttf",
                "frameRateDen": -1,
                "frameRateNum": -1,
                "height": -1,
                "itemName": "SubttCaption",
                "originClipType": 260223104,
                "originDuration": 0,
                "originSrcFile": "",
                "realMaterialId": "",
                "shotClipId": "",
                "shotIndex": -1,
                "srcPath": "/Applications/BCUT.app/Contents/MacOS/../Resources/res/subtt/huazi/speech",
                "type": 5,
                "videoType": 0,
                "width": -1
            },
            "BSpeedInfo": {
                "BSpeedType": 1,
                "pointListX": None,
                "pointListY": None,
                "speedCurveTypeName": "",
                "speedRate": 1
            },
            "FreezeImage": False,
            "IsDBVolume": True,
            "MarkPointInfo": None,
            "attachVoiceId": 0,
            "cutInfo": {"bottom": 1, "left": 0, "right": 1, "top": 0},
            "font_id": 0,
            "keyFrameArray": None,
            "network_font_id": 0,
            "srcFontPath": "/Applications/BCUT.app/Contents/MacOS/../Resources/Font/Source Han Sans CN Medium.ttf"
        }

    def create_subtitle_track(self) -> dict:
        """
        创建新的字幕轨道
        :return: 字幕轨道配置
        """
        return {
            "BTrackLastSplitPos": 0,
            "BTrackType": 0,
            "MiddleTrack": True,
            "clips": [],
            "mute": False,
            "split": None,
            "trackIndex": 1
        }

    def create_subtitle_clip(self, subtitle: dict) -> dict:
        """
        创建必剪字幕片段
        :param subtitle: 字幕信息
        :return: 必剪字幕片段配置
        """
        if not self.base_clip:
            self.base_clip = self.create_subtitle_clip_template()

        clip = copy.deepcopy(self.base_clip)
        
        # 更新关键信息
        clip['30011'] = subtitle['start']  # 片段在轨道上的起始时间
        clip['30012'] = subtitle['duration']  # 片段持续时间
        clip['30021'] = subtitle['start']  # 片段在轨道上的起始位置
        clip['duration'] = subtitle['duration']  # 片段持续时间
        clip['inPoint'] = subtitle['start']  # 片段内部起始位置
        clip['outPoint'] = subtitle['end']  # 片段内部结束位置
        clip['trimIn'] = 0  # 片段裁剪起始位置（相对于片段开始）
        clip['trimOut'] = subtitle['duration']  # 片段裁剪结束位置（相对于片段开始）
        clip['AssetInfo']['content'] = subtitle['text']
        clip['AssetInfo']['duration'] = subtitle['duration']
        
        # 生成新的唯一ID
        clip['m_id'] = int(datetime.now().timestamp() * 1000) + subtitle['index']
        
        return clip

    def load_template(self):
        """
        加载必剪JSON模板
        """
        self.config = self.adapter.load_config()
        subtitle_track, existing_clips = self.adapter.get_subtitle_track_and_clips()
        
        # 如果有现有字幕片段，使用第一个作为模板
        if existing_clips:
            self.base_clip = existing_clips[0]
        
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
        if self.adapter.is_new_version:
            subtitle_track['captions'] = []
        else:
            subtitle_track['clips'] = []
        
        # 创建新的字幕片段
        for subtitle in subtitles:
            new_clip = self.adapter.create_subtitle_clip(subtitle, self.base_clip)
            if self.adapter.is_new_version:
                subtitle_track['captions'].append(new_clip)
            else:
                subtitle_track['clips'].append(new_clip)
        
        # 保存更新后的配置
        self.adapter.save_config()
        
        return str(self.json_template_path) 