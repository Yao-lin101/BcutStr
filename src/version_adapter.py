import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import copy
from datetime import datetime

class BcutVersionAdapter:
    """必剪版本适配器，处理新旧版本格式的兼容性"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.is_new_version = self.file_path.suffix == '.bjson'
        self.config = None
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        return self.config
    
    def detect_version(self) -> str:
        """检测版本类型"""
        if self.is_new_version:
            return "new"
        return "old"
    
    def get_subtitle_track_and_clips(self) -> Tuple[Any, List[Any]]:
        """获取字幕轨道和字幕片段，返回统一格式"""
        if self.is_new_version:
            return self._get_new_version_subtitles()
        else:
            return self._get_old_version_subtitles()
    
    def _get_new_version_subtitles(self) -> Tuple[Any, List[Any]]:
        """处理新版本格式"""
        timeline = self.config.get('timelineWidget', {}).get('timeline', {})
        caption_tracks = timeline.get('captionTracks', [])
        
        if caption_tracks:
            # 使用第一个字幕轨道
            subtitle_track = caption_tracks[0]
            captions = subtitle_track.get('captions', [])
            return subtitle_track, captions
        else:
            # 创建新的字幕轨道
            new_track = {
                "captions": [],
                "compacted": False,
                "idString": f"new_caption_track_{int(datetime.now().timestamp() * 1000)}",
                "index": len(caption_tracks),
                "trackType": 3
            }
            caption_tracks.append(new_track)
            return new_track, []
    
    def _get_old_version_subtitles(self) -> Tuple[Any, List[Any]]:
        """处理旧版本格式"""
        tracks = self.config.get('tracks', [])
        
        # 查找字幕轨道
        for track in tracks:
            if track.get('BTrackType') == 0 and not track.get('MiddleTrack', False):
                return track, track.get('clips', [])
        
        # 如果没有找到，创建新的字幕轨道
        new_track = {
            "BTrackLastSplitPos": 0,
            "BTrackType": 0,
            "clips": [],
            "mute": False,
            "split": False,
            "trackIndex": 1
        }
        tracks.insert(0, new_track)
        
        # 更新轨道索引和数量
        for i, track in enumerate(tracks):
            track['trackIndex'] = i + 1
        self.config['trackCount'] = len(tracks)
        
        return new_track, []
    
    def create_subtitle_clip(self, subtitle_data: Dict[str, Any], existing_clip: Any = None) -> Dict[str, Any]:
        """创建字幕片段，根据版本使用不同格式"""
        if self.is_new_version:
            return self._create_new_version_clip(subtitle_data, existing_clip)
        else:
            return self._create_old_version_clip(subtitle_data, existing_clip)
    
    def _create_new_version_clip(self, subtitle_data: Dict[str, Any], existing_clip: Any = None) -> Dict[str, Any]:
        """创建新版本格式的字幕片段"""
        if existing_clip:
            clip = copy.deepcopy(existing_clip)
        else:
            clip = self._get_new_version_template()
        
        # 更新字幕内容和时间
        clip['captionText'] = subtitle_data['text']
        clip['assetInfo']['content'] = subtitle_data['text']
        clip['assetInfo']['duration'] = subtitle_data['duration']
        clip['inPoint'] = subtitle_data['start']
        clip['outPoint'] = subtitle_data['end']
        
        return clip
    
    def _create_old_version_clip(self, subtitle_data: Dict[str, Any], existing_clip: Any = None) -> Dict[str, Any]:
        """创建旧版本格式的字幕片段"""
        if existing_clip:
            clip = copy.deepcopy(existing_clip)
        else:
            clip = self._get_old_version_template()
        
        # 更新字幕内容和时间
        clip['AssetInfo']['content'] = subtitle_data['text']
        clip['AssetInfo']['duration'] = subtitle_data['duration']
        clip['30011'] = subtitle_data['start']
        clip['30012'] = subtitle_data['duration']
        clip['30021'] = subtitle_data['start']
        clip['duration'] = subtitle_data['duration']
        clip['inPoint'] = subtitle_data['start']
        clip['outPoint'] = subtitle_data['end']
        clip['trimIn'] = 0
        clip['trimOut'] = subtitle_data['duration']
        
        # 生成唯一ID
        clip['m_id'] = int(datetime.now().timestamp() * 1000) + subtitle_data['index']
        
        return clip
    
    def _get_new_version_template(self) -> Dict[str, Any]:
        """新版本字幕模板"""
        return {
            "assetInfo": {
                "assetItemType": 15,
                "audioType": 0,
                "content": "",
                "coverPath": "",
                "customInfos": {},
                "displayName": "字幕",
                "duration": 0,
                "fontID": 0,
                "fontSrcPath": "/Applications/BCUT.app/Contents/MacOS/../Resources/Font/Source Han Sans CN Medium.ttf",
                "frameRateDen": 1,
                "frameRateNum": 0,
                "height": 0,
                "itemName": "默认文本",
                "originDuration": 0,
                "originSrcPath": "",
                "originType": 0,
                "realMaterialId": "-4",
                "shotClipId": "",
                "shotIndex": -1,
                "srcPath": "/Applications/BCUT.app/Contents/MacOS/../Resources/res/subtt/huazi/default",
                "type": 4,
                "videoType": 0,
                "width": 0
            },
            "captionText": "",
            "defaultFontName": "思源黑体 CN Medium",
            "defaultFontPath": "/Applications/BCUT.app/Contents/MacOS/../Resources/Font/Source Han Sans CN Medium.ttf",
            "drawBackgroundColor": False,
            "drawOutline": False,
            "drawShadowColor": False,
            "fancyWordId": "",
            "fancyWordPath": "",
            "fontId": "0",
            "fontName": "",
            "fontPackagePath": "/Applications/BCUT.app/Contents/MacOS/../Resources/Font/Source Han Sans CN Medium.ttf",
            "idString": f"caption_{int(datetime.now().timestamp() * 1000)}",
            "inAnimationDuration": 0,
            "inAnimationId": "",
            "inAnimationPath": "",
            "inPoint": 0,
            "isVerticalLayout": False,
            "letterSpacing": 100,
            "lineSpacing": 0,
            "loopAnimationDuration": 0,
            "loopAnimationId": "",
            "loopAnimationPath": "",
            "opacity": 1,
            "outAnimationDuration": 0,
            "outAnimationId": "",
            "outAnimationPath": "",
            "outPoint": 0,
            "rotation": 0,
            "scaleX": 1,
            "scaleY": 1,
            "templateId": "",
            "templatePackagePath": "",
            "textAlignment": 1,
            "textBold": False,
            "textColor": {
                "a": 1,
                "b": 1,
                "g": 1,
                "r": 1
            },
            "textItalic": False,
            "transX": 0,
            "transY": 0,
            "uid": int(datetime.now().timestamp() * 1000),
            "underline": False
        }
    
    def _get_old_version_template(self) -> Dict[str, Any]:
        """旧版本字幕模板"""
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
    
    def save_config(self):
        """保存配置文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)