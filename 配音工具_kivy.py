#!/usr/bin/env python3
"""
🌸  配音工具 (Kivy 移动版)
适配 Kivy 2.3+ / KivyMD 1.2+ / Python 3.12
Word 文本 → edge-tts 智能配音 | 14 中文音色 | 场景预设 | 试听

运行: python 配音工具_kivy.py
"""

import os, re, sys, json, hashlib, asyncio, subprocess, threading, time, tempfile, traceback
from pathlib import Path
from datetime import datetime

# ── 崩溃日志（写入外部存储，方便排查）──
CRASH_LOG = None
try:
    from kivy.utils import platform as _kivy_platform
    if _kivy_platform == 'android':
        CRASH_LOG = Path('/storage/emulated/0/配音工具/crash.log')
        CRASH_LOG.parent.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

def _log_crash(msg):
    """记录启动日志"""
    try:
        if CRASH_LOG:
            with open(CRASH_LOG, 'a', encoding='utf-8') as f:
                f.write(f'[{datetime.now().isoformat()}] {msg}\n')
    except Exception:
        pass

_log_crash('=== App 启动 ===')
_log_crash(f'Python: {sys.version}')
_log_crash(f'Platform: {_kivy_platform if "_kivy_platform" in dir() else "unknown"}')

# ── Android: 设置 asyncio 事件循环策略 ──
try:
    if _kivy_platform == 'android':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        _log_crash('asyncio event loop policy set')
except Exception as e:
    _log_crash(f'asyncio setup: {e}')

# ── Kivy / KivyMD (1.x API) ──
from kivy.config import Config
Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '800')
Config.set('kivy', 'log_level', 'warning')
Config.set('kivy', 'keyboard_mode', 'systemandmulti')  # Android 软键盘适配
Config.set('kivy', 'log_enable', 1)
# 开启 Kivy 日志文件
if _kivy_platform == 'android':
    Config.set('kivy', 'log_dir', '/storage/emulated/0/配音工具')
    Config.set('kivy', 'log_maxfiles', 5)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.slider import MDSlider
from kivymd.uix.spinner import MDSpinner

# ═══════════════ Android 权限 ─══════════════
ANDROID_PERMISSIONS = []
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission, check_permission
        ANDROID_PERMISSIONS = [
            Permission.INTERNET,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_MEDIA_AUDIO,
        ]
    except ImportError:
        pass

# ═══════════════ 全局配置 ═══════════════

# Android: 优先使用应用内部目录（私有存储），支持导出到外部
if platform == 'android':
    try:
        from android.storage import app_storage_path, primary_external_storage_path
        APP_DIR = Path(app_storage_path()) / '配音工具'
        EXPORT_DIR = Path(primary_external_storage_path()) / '配音工具'
    except Exception:
        APP_DIR = Path('/data/data/com.dubbing.tool/files/配音工具')
        EXPORT_DIR = Path('/storage/emulated/0/配音工具')
    BASE_DIR = APP_DIR  # 生成的音频存应用内部
    TTS_CACHE = APP_DIR / 'cache'
    # 确保导出目录也存在
    EXPORT_DIR.mkdir(exist_ok=True, parents=True)
else:
    BASE_DIR = Path(os.environ.get('USERPROFILE', '.')) / 'Desktop' / '视频剪辑'
    TTS_CACHE = BASE_DIR / 'cache'

BASE_DIR.mkdir(exist_ok=True, parents=True)
TTS_CACHE.mkdir(exist_ok=True, parents=True)

# FFmpeg 路径（Windows桌面 / Android 默认）
if platform == 'win32':
    _ffdir = Path(os.environ.get('LOCALAPPDATA', '.')) / 'Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin'
    FFMPEG = str(_ffdir / 'ffmpeg.exe')
    FFPROBE = str(_ffdir / 'ffprobe.exe')
    FFPLAY  = str(_ffdir / 'ffplay.exe')
else:
    FFMPEG  = 'ffmpeg'
    FFPROBE = 'ffprobe'
    FFPLAY  = 'ffplay'

# GPT-SoVITS
API_URL = 'http://127.0.0.1:9880/tts'
API_TIMEOUT = 3600

# ═══════════════ 配色 (粉色薄荷绿) ═══════════════
def rgba(r, g, b, a=1):
    return (r/255, g/255, b/255, a)

CLR = {
    'bg':           rgba(250,229,229),
    'card':         rgba(255,255,255),
    'card_border':  rgba(245,208,208),
    'pink':         rgba(250,175,175),
    'pink_light':   rgba(253,237,237),
    'mint':         rgba(175,225,200),
    'mint_light':   rgba(230,247,238),
    'text':         rgba(93,64,55),
    'text_light':   rgba(184,155,149),
    'text_title':   rgba(232,138,138),
    'tag_mint_fg':  rgba(109,189,149),
    'input_bg':     rgba(255,245,245),
    'accent_yellow':rgba(255,243,205),
}

# ═══════════════ 音色库 ═══════════════
VOICES = {
    '🎬 纪录片/旁白': [
        ('zh-CN-YunyangNeural', '男声·BBC动物世界', '-18%', '-8Hz'),
        ('zh-CN-YunyangNeural', '男声·大国工程', '-12%', '-5Hz'),
        ('zh-CN-YunyangNeural', '男声·新闻档案', '-5%', '-2Hz'),
        ('zh-CN-YunxiNeural',   '男声·探索发现', '-5%', '-2Hz'),
        ('zh-CN-YunxiNeural',   '男声·诗词朗诵', '-35%', '-3Hz'),
        ('zh-CN-XiaoxiaoNeural','女声·蓝色星球', '-15%', '-3Hz'),
        ('zh-CN-XiaoxiaoNeural','女声·深夜电台', '-20%', '-5Hz'),
        ('zh-CN-XiaoxiaoNeural','女声·诗词吟诵', '-38%', '-5Hz'),
        ('zh-TW-YunJheNeural',  '男声·历史档案', '-10%', '-8Hz'),
    ],
    '🎙 热血/广告': [
        ('zh-CN-YunjianNeural', '男声·体育解说', '+8%', '+8Hz'),
        ('zh-CN-YunjianNeural', '男声·预告大片', '+5%', '+5Hz'),
        ('zh-TW-HsiaoYuNeural', '女声·综艺旁白', '+10%', '+10Hz'),
        ('zh-TW-HsiaoYuNeural', '女声·快嘴种草', '+15%', '+5Hz'),
    ],
    '🌟 青春/生活': [
        ('zh-CN-YunxiaNeural',  '男声·少年游记', '+5%', '+5Hz'),
        ('zh-CN-YunxiaNeural',  '男声·游戏解说', '+12%', '+8Hz'),
        ('zh-CN-XiaoyiNeural',  '女声·美食探店', '+5%', '+3Hz'),
        ('zh-CN-XiaoyiNeural',  '女声·童趣故事', '-10%', '+8Hz'),
        ('zh-TW-HsiaoChenNeural','女声·日系治愈', '-8%', '+2Hz'),
    ],
    '🇭🇰 粤语': [
        ('zh-HK-HiuGaaiNeural', '女声·港风日常', '+0%', '+0Hz'),
        ('zh-HK-HiuMaanNeural', '女声·粤语文艺', '-10%', '-3Hz'),
        ('zh-HK-WanLungNeural', '男声·港闻播报', '-5%', '-2Hz'),
    ],
    '🏘 方言': [
        ('zh-CN-liaoning-XiaobeiNeural', '东北话·欢乐喜剧', '+5%', '+5Hz'),
        ('zh-CN-shaanxi-XiaoniNeural',   '陕西话·人文纪录', '-8%', '+0Hz'),
    ],
}

SCENE_PRESETS = {
    '诗词朗诵': {'rate_val': 0.65, 'desc': '慢速深情'},
    '纪录片旁白': {'rate_val': 0.82, 'desc': '沉稳大气'},
    '带货口播':   {'rate_val': 1.12, 'desc': '快节奏'},
    '新闻播报':   {'rate_val': 0.97, 'desc': '标准语速'},
}

# ═══════════════ 引擎 ═══════════════

def _run_safe(cmd, **kwargs):
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('encoding', 'utf-8')
    kwargs.setdefault('errors', 'replace')
    if platform == 'win32':
        kwargs.setdefault('creationflags', 0x08000000)
    return subprocess.run(cmd, **kwargs)

def _safe_thread_run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def clean_text(text):
    import unicodedata
    result = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat[0] in ('L', 'N', 'P'): result.append(ch)
        elif cat in ('Zs',): result.append(' ')
        elif ch in '\n\r\t': result.append('\n' if ch == '\n' else ' ')
    text = ''.join(result)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

class VoiceGenerator:
    def __init__(self, d): self.out = Path(d)
    async def _g(self, text, voice, filename, rate='-5%', pitch='+0Hz'):
        import edge_tts
        comm = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await comm.save(str(self.out / f'{filename}.mp3'))
    def generate(self, text, voice, filename, rate='-5%', pitch='+0Hz'):
        _safe_thread_run(self._g(text, voice, filename, rate, pitch))


# ═══════════════ KivyMD App ═══════════════

class TtsApp(MDApp):
    def build(self):
        try:
            return self._build_safe()
        except Exception as e:
            _log_crash('build() crash: ' + type(e).__name__ + ': ' + str(e))
            _log_crash(traceback.format_exc())
            from kivy.uix.label import Label as _ErrLbl
            from kivy.uix.scrollview import ScrollView as _ErrSV
            sv = _ErrSV()
            sv.add_widget(_ErrLbl(
                text='Init Failed\n\n' + type(e).__name__ + '\n' + str(e)[:500] +
                     '\n\nLog: ' + str(CRASH_LOG),
                font_size='14sp', halign='left', valign='top',
                text_size=(380, None), size_hint_y=None, height=1200))
            return sv

    def _build_safe(self):
        self.theme_cls.primary_palette = 'Pink'
        self.theme_cls.theme_style = 'Light'
        self.title = '🌸 配音工具'
        self.icon = '🌸'

        # ── Android 权限申请 ──
        if platform == 'android' and ANDROID_PERMISSIONS:
            try:
                request_permissions(ANDROID_PERMISSIONS)
            except Exception:
                pass

        # ── 软键盘适配：键盘弹出时调整布局 ──
        Window.softinput_mode = 'resize'

        # 状态
        self.doc_text = ''
        self.selected_voice_id = ''
        self.selected_voice_label = '未选择'
        self.selected_rate = '-5%'
        self.selected_pitch = '+0Hz'
        self.speed_override_val = 1.0
        self.is_generating = False

        # ── 主布局（FloatLayout 支持遮罩叠加） ──
        root = FloatLayout()

        # 主内容层
        main_layer = BoxLayout(orientation='vertical')

        # 顶栏
        header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(52),
            padding=[dp(14), dp(8)]
        )
        with header.canvas.before:
            Color(*CLR['pink_light'])
            self._header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda o, v: setattr(self._header_rect, 'pos', v))
        header.bind(size=lambda o, v: setattr(self._header_rect, 'size', v))

        header.add_widget(Label(
            text='🌸 配音工具', font_size=sp(18), bold=True,
            color=CLR['text_title'], size_hint_x=0.7, halign='left'
        ))
        header.add_widget(Label(
            text='移动版', font_size=sp(12),
            color=CLR['text_light'], size_hint_x=0.3, halign='right'
        ))
        main_layer.add_widget(header)

        # 滚动区
        scroll = ScrollView(do_scroll_x=False)
        self.content = BoxLayout(
            orientation='vertical', spacing=dp(10), padding=[dp(12), dp(8)],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        main_layer.add_widget(scroll)

        # 底栏
        self.status_bar = Label(
            text='💤 就绪', font_size=sp(12),
            color=CLR['text_light'], size_hint_y=None, height=dp(32),
            halign='left', valign='middle'
        )
        with self.status_bar.canvas.before:
            Color(*CLR['card'])
            self._bar_rect = Rectangle(pos=self.status_bar.pos, size=self.status_bar.size)
        self.status_bar.bind(pos=lambda o, v: setattr(self._bar_rect, 'pos', v))
        self.status_bar.bind(size=lambda o, v: setattr(self._bar_rect, 'size', v))
        self.status_bar.bind(texture_size=self.status_bar.setter('texture_size'))
        main_layer.add_widget(self.status_bar)

        root.add_widget(main_layer)

        # ── 加载遮罩层 ──
        self.loading_overlay = FloatLayout(opacity=0, size_hint=(1, 1))
        with self.loading_overlay.canvas.before:
            Color(0, 0, 0, 0.45)
            self._overlay_rect = Rectangle(size=root.size)
        self.loading_overlay.bind(size=lambda o, v: setattr(self._overlay_rect, 'size', v))
        self.loading_spinner = MDSpinner(
            size_hint=(None, None), size=(dp(48), dp(48)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            line_width=dp(4), active=True,
            palette=[[0.686, 0.882, 0.784, 1], [0.980, 0.686, 0.686, 1], [0.427, 0.741, 0.584, 1]]
        )
        self.loading_overlay.add_widget(self.loading_spinner)
        self.loading_label = Label(
            text='', font_size=sp(14), bold=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.42},
            size_hint_y=None, height=dp(30)
        )
        self.loading_overlay.add_widget(self.loading_label)
        root.add_widget(self.loading_overlay)

        # 构建模块
        self._build_text_input()
        self._build_voice_selector()
        self._build_speed_control()
        self._build_scene_presets()
        self._build_generate_button()
        self._build_audio_list()

        # 所有 Canvas rect 绑定尺寸
        for card_widget in self.content.children:
            if isinstance(card_widget, BoxLayout):
                for child in card_widget.children:
                    if hasattr(child, 'canvas') and hasattr(child, '_row_rect_prepare'):
                        child.bind(pos=lambda o, v: setattr(o._row_rect, 'pos', v))
                        child.bind(size=lambda o, v: setattr(o._row_rect, 'size', v))

        return root

    # ── 加载动画控制 ──
    def _show_loading(self, msg='加载中...'):
        self.loading_label.text = msg
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self.loading_overlay)
        self.loading_spinner.active = True

    def _hide_loading(self):
        anim = Animation(opacity=0, duration=0.2)
        anim.start(self.loading_overlay)
        self.loading_spinner.active = False

    # ── 卡片工厂 ──
    def _card(self, title):
        card = BoxLayout(
            orientation='vertical', spacing=dp(4),
            padding=[dp(14), dp(10)],
            size_hint_y=None, height=dp(10)  # adaptive later
        )
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*CLR['card'])
            self._card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=lambda o, v: setattr(self._card_rect, 'pos', v))
        card.bind(size=lambda o, v: setattr(self._card_rect, 'size', v))

        card.add_widget(Label(
            text=title, font_size=sp(15), bold=True,
            color=CLR['text_title'], size_hint_y=None, height=dp(30),
            halign='left', valign='middle'
        ))
        return card

    # ── 模块 1: 文本输入 ──
    def _build_text_input(self):
        card = self._card('📥 文本输入')
        self.text_input = TextInput(
            hint_text='输入配音文本…支持 [停顿1s] 标记控制节奏',
            multiline=True, size_hint_y=None, height=dp(120),
            background_color=CLR['input_bg'],
            foreground_color=CLR['text'],
            cursor_color=CLR['pink'],
            font_size=sp(14), padding=[dp(10), dp(10)]
        )
        self.text_input.bind(text=self._on_text_changed)
        card.add_widget(self.text_input)

        btn_row = BoxLayout(orientation='horizontal', spacing=dp(6),
                          size_hint_y=None, height=dp(44), padding=[0, dp(4)])
        btn_row.add_widget(self._mint_btn('📄 导入文档', self._pick_doc))
        btn_row.add_widget(self._outline_btn('📋 粘贴', self._paste_clipboard))
        card.add_widget(btn_row)

        self.word_count_lbl = Label(
            text='字数: 0 · 预估时长: 0秒', font_size=sp(11),
            color=CLR['tag_mint_fg'], size_hint_y=None, height=dp(20),
            halign='left', valign='middle'
        )
        card.add_widget(self.word_count_lbl)
        self.content.add_widget(card)

    def _on_text_changed(self, instance, value):
        chars = len(re.sub(r'\s', '', value))
        secs = max(1, chars / 4)
        mins, sec = divmod(int(secs), 60)
        dur = f'{mins}分{sec}秒' if mins else f'{sec}秒'
        self.word_count_lbl.text = f'字数: {chars} · 预估时长: ~{dur}'
        self.doc_text = value

    def _pick_doc(self, *args):
        if platform == 'android':
            try:
                from plyer import filechooser
                filechooser.open_file(
                    on_selection=lambda sel: self._load_file(sel[0] if sel else None),
                    filters=['*.docx', '*.txt'])
            except Exception:
                self._toast('文件选择器不可用')
        else:
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk(); root.withdraw()
                p = filedialog.askopenfilename(
                    title='选择文件', filetypes=[('Documents', '*.docx;*.txt')])
                root.destroy()
                if p: self._load_file(p)
            except Exception as e:
                self._toast(f'文件对话框失败: {e}')

    def _load_file(self, path):
        if not path: return
        path = Path(path)
        try:
            if path.suffix.lower() == '.docx':
                from docx import Document
                doc = Document(str(path))
                text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
            else:
                text = path.read_text(encoding='utf-8')
            cleaned = clean_text(text)
            self.doc_text = cleaned
            self.text_input.text = cleaned
            self.status_bar.text = f'📄 已加载 {len(cleaned)} 字'
        except Exception as e:
            self._toast(f'加载失败: {e}')

    def _paste_clipboard(self, *args):
        try:
            from kivy.core.clipboard import Clipboard
            text = Clipboard.paste()
            if text:
                self.text_input.text = text
                self.status_bar.text = '📋 已粘贴剪贴板内容'
        except Exception:
            self._toast('无法访问剪贴板')

    # ── 模块 2: 音色选择 ──
    def _build_voice_selector(self):
        card = self._card('🎤 配音音色')
        cat_row = BoxLayout(orientation='horizontal', spacing=dp(6),
                          size_hint_y=None, height=dp(44))
        self.cat_spinner = Spinner(
            text='🎬 纪录片/旁白', values=list(VOICES.keys()),
            size_hint=(0.45, 1), background_color=CLR['input_bg'],
            color=CLR['text'], font_size=sp(13)
        )
        self.cat_spinner.bind(text=self._on_cat_changed)
        cat_row.add_widget(self.cat_spinner)

        self.voice_spinner = Spinner(
            text='选择音色', values=[],
            size_hint=(0.55, 1), background_color=CLR['input_bg'],
            color=CLR['text'], font_size=sp(13)
        )
        self.voice_spinner.bind(text=self._on_voice_changed)
        cat_row.add_widget(self.voice_spinner)
        card.add_widget(cat_row)

        self.voice_info = Label(
            text='未选择音色', font_size=sp(11),
            color=CLR['text_light'], size_hint_y=None, height=dp(20),
            halign='left', valign='middle'
        )
        card.add_widget(self.voice_info)
        self._on_cat_changed(self.cat_spinner, self.cat_spinner.text)
        self.content.add_widget(card)

    def _on_cat_changed(self, spinner, text):
        voices = VOICES.get(text, [])
        labels = [v[1] for v in voices]
        self.voice_spinner.values = labels
        if labels:
            self.voice_spinner.text = labels[0]

    def _on_voice_changed(self, spinner, text):
        for cat, vlist in VOICES.items():
            for v in vlist:
                if v[1] == text:
                    self.selected_voice_id = v[0]
                    self.selected_voice_label = v[1]
                    self.selected_rate = v[2]
                    self.selected_pitch = v[3]
                    self.voice_info.text = f'默认语速{v[2]} 语调{v[3]}'
                    return

    # ── 模块 3: 语速调节 ──
    def _build_speed_control(self):
        card = self._card('⚡ 语速调节 (0.5x ~ 3.0x)')

        slider_row = BoxLayout(orientation='horizontal', spacing=dp(8),
                             size_hint_y=None, height=dp(48))
        self.speed_slider = Slider(
            min=0.5, max=3.0, value=1.0, step=0.02,
            size_hint_x=0.65, cursor_size=(dp(20), dp(20))
        )
        self.speed_slider.bind(value=self._on_speed_changed)
        slider_row.add_widget(self.speed_slider)

        self.speed_lbl = Label(
            text='1.00x', font_size=sp(14),
            color=CLR['text'], size_hint_x=0.15
        )
        slider_row.add_widget(self.speed_lbl)

        btn_box = BoxLayout(orientation='horizontal', spacing=dp(2), size_hint_x=0.2)
        btn_box.add_widget(self._mini_btn('−', lambda x: self._adj_speed(-0.05)))
        btn_box.add_widget(self._mini_btn('+', lambda x: self._adj_speed(0.05)))
        slider_row.add_widget(btn_box)
        card.add_widget(slider_row)

        card.add_widget(self._outline_btn('🔊 试听当前语速', self._preview_speed))
        self.content.add_widget(card)

    def _on_speed_changed(self, instance, value):
        self.speed_override_val = value
        self.speed_lbl.text = f'{value:.2f}x'

    def _adj_speed(self, delta):
        new = max(0.5, min(3.0, self.speed_slider.value + delta))
        self.speed_slider.value = new

    # ── 模块 4: 场景预设 ──
    def _build_scene_presets(self):
        card = self._card('🎬 场景预设')
        grid = GridLayout(cols=3, spacing=dp(6), size_hint_y=None, height=dp(90), padding=[0, dp(4)])

        for name, info in SCENE_PRESETS.items():
            btn = Button(
                text=f'{name}\n{info["desc"]}', font_size=sp(11),
                color=CLR['text_light'],
                background_normal='', background_color=CLR['tag_mint_fg'][:3] + (0.2,),
                size_hint_y=None, height=dp(40), halign='center', valign='middle'
            )
            btn.bind(on_release=lambda x, n=name, v=info['rate_val']: self._apply_preset(n, v))
            grid.add_widget(btn)

        default_btn = Button(
            text='默认\n音色自带', font_size=sp(11),
            color=CLR['text_light'],
            background_normal='', background_color=CLR['input_bg'],
            size_hint_y=None, height=dp(40), halign='center', valign='middle'
        )
        default_btn.bind(on_release=lambda x: self._apply_preset('默认', 1.0))
        grid.add_widget(default_btn)
        card.add_widget(grid)
        self.content.add_widget(card)

    def _apply_preset(self, name, rate_val):
        self.speed_slider.value = rate_val
        self.speed_override_val = rate_val
        self.status_bar.text = f'🎬 已套用「{name}」预设'

    # ── 模块 5: 生成按钮 ──
    def _build_generate_button(self):
        card = self._card('✨ 生成配音')
        gen_btn = Button(
            text='🎬 生成配音', font_size=sp(18), bold=True,
            color=(0.23, 0.44, 0.31, 1),
            background_normal='', background_color=CLR['mint'],
            size_hint_y=None, height=dp(56)
        )
        gen_btn.bind(on_release=self._generate)
        card.add_widget(gen_btn)

        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(6))
        self.progress.opacity = 0
        card.add_widget(self.progress)

        self.gen_status = Label(
            text='', font_size=sp(11), color=CLR['text_light'],
            size_hint_y=None, height=dp(20)
        )
        card.add_widget(self.gen_status)
        self.content.add_widget(card)

    # ── 模块 6: 音频列表 ──
    def _build_audio_list(self):
        card = self._card('📂 已生成音频')
        self.audio_list_container = BoxLayout(
            orientation='vertical', spacing=dp(3), size_hint_y=None, height=dp(40)
        )
        card.add_widget(self.audio_list_container)
        self._refresh_audio_list()
        self.content.add_widget(card)

    def _refresh_audio_list(self):
        self.audio_list_container.clear_widgets()
        mp3s = sorted(BASE_DIR.glob('*.mp3'), key=os.path.getmtime, reverse=True)[:10]
        if not mp3s:
            self.audio_list_container.height = dp(24)
            self.audio_list_container.add_widget(Label(
                text='暂无生成记录', font_size=sp(11), color=CLR['text_light'],
                size_hint_y=None, height=dp(24)
            ))
            return
        self.audio_list_container.height = min(len(mp3s) * dp(40), dp(400))
        for mp3 in mp3s:
            row = BoxLayout(orientation='horizontal', spacing=dp(4),
                          size_hint_y=None, height=dp(38), padding=[dp(6), dp(2)])
            with row.canvas.before:
                Color(*CLR['mint_light'])
                row._row_rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
            row.bind(pos=lambda o, v: setattr(o._row_rect, 'pos', v))
            row.bind(size=lambda o, v: setattr(o._row_rect, 'size', v))
            row._row_rect_prepare = True  # marker for binding in build()

            size_mb = os.path.getsize(mp3) / 1024 / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(mp3)).strftime('%m-%d %H:%M')
            row.add_widget(Label(
                text=f'{mp3.stem[:18]}', font_size=sp(11),
                color=CLR['text'], size_hint_x=0.38, halign='left', valign='middle'
            ))
            row.add_widget(Label(
                text=f'{size_mb:.1f}MB', font_size=sp(9),
                color=CLR['text_light'], size_hint_x=0.2, halign='center', valign='middle'
            ))
            play_btn = Button(
                text='▶ 播放', font_size=sp(10),
                color=CLR['tag_mint_fg'],
                background_normal='', background_color=(0,0,0,0),
                size_hint_x=0.22
            )
            play_btn.bind(on_release=lambda x, p=str(mp3): self._play_audio(p))
            row.add_widget(play_btn)

            export_btn = Button(
                text='📤', font_size=sp(14),
                color=CLR['text_light'],
                background_normal='', background_color=(0,0,0,0),
                size_hint_x=0.2
            )
            export_btn.bind(on_release=lambda x, p=str(mp3): self._export_audio(p))
            row.add_widget(export_btn)
            self.audio_list_container.add_widget(row)

    def _export_audio(self, path):
        """导出音频到共享存储（Android）或打开文件夹（桌面）"""
        if platform == 'android':
            try:
                import shutil
                dest = EXPORT_DIR / Path(path).name
                shutil.copy2(path, str(dest))
                self._show_dialog('📤 导出成功',
                    f'文件已复制到:\n{dest}\n\n可在文件管理器中找到')
            except Exception as e:
                self._show_dialog('导出失败', str(e))
        else:
            try:
                os.startfile(os.path.dirname(path))
            except Exception:
                subprocess.Popen(['explorer', os.path.dirname(path)])

    # ═══════════════ 核心生成 ═══════════════

    def _generate(self, *args):
        if self.is_generating: return
        if not self.doc_text.strip():
            self._show_dialog('提示', '请先输入配音文本'); return
        if not self.selected_voice_id:
            self._show_dialog('提示', '请先选择音色'); return

        self.is_generating = True
        rate = f'{(self.speed_override_val-1)*100:+.0f}%'
        pitch = self.selected_pitch
        text = self.doc_text
        vid = self.selected_voice_id
        fname = re.sub(r'[^\w\-]', '_', self.selected_voice_label) \
                + '_' + datetime.now().strftime('%Y%m%d_%H%M%S')

        self._show_loading(f'正在生成配音…\n{self.selected_voice_label} · 语速{rate}')
        self.progress.opacity = 1
        self.progress.value = 0
        self.gen_status.text = ''
        self.status_bar.text = f'⏳ 正在生成: {self.selected_voice_label}'

        def task():
            try:
                gen = VoiceGenerator(BASE_DIR)
                gen.generate(text, vid, fname, rate=rate, pitch=pitch)
                Clock.schedule_once(lambda dt: self._on_gen_done(fname), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt, e=e: self._on_gen_fail(str(e)), 0)

        threading.Thread(target=task, daemon=True).start()

    def _on_gen_done(self, fname):
        self.is_generating = False
        self._hide_loading()
        self.progress.value = 100
        self.progress.opacity = 0
        mp3_path = BASE_DIR / f'{fname}.mp3'
        size_mb = os.path.getsize(mp3_path) / 1024 / 1024 if mp3_path.exists() else 0
        self.gen_status.text = f'✅ 生成成功 · {size_mb:.1f}MB'
        self.status_bar.text = f'✅ {fname} · {size_mb:.1f}MB'
        self._refresh_audio_list()
        self._play_audio(str(mp3_path))
        # 成功弹窗
        self._show_dialog('✅ 生成成功',
            f'文件: {fname}.mp3\n大小: {size_mb:.1f}MB\n\n'
            f'已保存至应用目录，可在下方列表播放')

    def _on_gen_fail(self, msg):
        self.is_generating = False
        self._hide_loading()
        self.progress.value = 0
        self.progress.opacity = 0
        self.gen_status.text = f'❌ {msg[:60]}'
        self.status_bar.text = f'❌ 生成失败: {msg[:60]}'
        self._show_dialog('❌ 生成失败',
            f'{msg}\n\n💡 请检查:\n'
            f'1. 网络连接是否正常\n'
            f'2. 音色ID是否有效\n'
            f'3. Python依赖是否完整 (edge-tts)')

    def _preview_speed(self, *args):
        if not self.selected_voice_id:
            self._toast('请先选择音色'); return
        rate = f'{(self.speed_override_val-1)*100:+.0f}%'
        vid = self.selected_voice_id
        sample_path = str(TTS_CACHE / f'{vid}_preview.wav')
        try: os.remove(sample_path)
        except OSError: pass

        self.status_bar.text = f'⏳ 试听中... 语速{rate}'

        def task():
            try:
                import edge_tts
                comm = edge_tts.Communicate(
                    '欢迎使用配音工具。这是语速试听效果。', vid, rate=rate)
                _safe_thread_run(comm.save(sample_path))
                self._play_audio(sample_path)
                Clock.schedule_once(
                    lambda dt: setattr(self.status_bar, 'text', '✅ 试听完毕'), 3)
            except Exception as e:
                Clock.schedule_once(
                    lambda dt, e=e: setattr(self.status_bar, 'text', f'❌ 试听失败: {e}'), 0)

        threading.Thread(target=task, daemon=True).start()

    def _play_audio(self, path):
        if not os.path.exists(path):
            self._toast('文件不存在')
            return
        self.status_bar.text = f'🔊 正在播放: {Path(path).name[:30]}'
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.fromFile(File(path)), 'audio/*')
                PythonActivity.mActivity.startActivity(intent)
            except Exception:
                try:
                    from jnius import autoclass
                    MediaPlayer = autoclass('android.media.MediaPlayer')
                    FileInputStream = autoclass('java.io.FileInputStream')
                    player = MediaPlayer()
                    fis = FileInputStream(path)
                    player.setDataSource(fis.getFD())
                    player.prepare()
                    player.start()
                except Exception as e:
                    self._toast(f'播放失败: {e}')
        else:
            try:
                subprocess.Popen(
                    [FFPLAY, '-nodisp', '-autoexit', '-loglevel', 'quiet', path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                try:
                    os.startfile(path)
                except Exception:
                    self._toast('无法播放音频')

    # ═══════════════ 组件工厂 ═══════════════

    def _mint_btn(self, text, callback):
        btn = Button(
            text=text, font_size=sp(14), bold=True,
            color=(0.29, 0.55, 0.41, 1),
            background_normal='', background_color=CLR['mint'],
            size_hint_y=None, height=dp(44)
        )
        btn.bind(on_release=callback)
        return btn

    def _outline_btn(self, text, callback):
        btn = Button(
            text=text, font_size=sp(13),
            color=CLR['text_light'],
            background_normal='', background_color=(0,0,0,0),
            size_hint_y=None, height=dp(44)
        )
        btn.bind(on_release=callback)
        return btn

    def _mini_btn(self, text, callback):
        btn = Button(
            text=text, font_size=sp(13),
            color=CLR['text_light'],
            background_normal='', background_color=(0,0,0,0),
            size_hint=(None, None), size=(dp(36), dp(36))
        )
        btn.bind(on_release=callback)
        return btn

    def _show_dialog(self, title, msg):
        """Android 风格弹窗提示"""
        self.status_bar.text = msg[:60]
        try:
            content = BoxLayout(orientation='vertical', padding=[dp(16), dp(12)], spacing=dp(8))
            content.add_widget(Label(
                text=msg, font_size=sp(14),
                color=CLR['text'], halign='left', valign='top',
                size_hint_y=None, height=dp(min(200, 20 * msg.count('\n') + 60))
            ))
            content.add_widget(Button(
                text='确定', font_size=sp(15),
                color=CLR['text_title'],
                background_normal='', background_color=CLR['pink_light'],
                size_hint_y=None, height=dp(44)
            ))
            popup = Popup(
                title=title, content=content,
                size_hint=(0.85, None), height=dp(min(280, 160 + 20 * msg.count('\n'))),
                background_color=CLR['card'],
                title_color=CLR['text_title'],
                title_size=sp(16),
                separator_color=CLR['card_border']
            )
            content.children[-1].bind(on_release=popup.dismiss)
            popup.open()
        except Exception:
            pass

    def _toast(self, msg):
        """简短提示（状态栏）"""
        self.status_bar.text = msg


# ═══════════════ 入口 ═══════════════
if __name__ == '__main__':
    try:
        _log_crash('TtsApp().run() starting')
        TtsApp().run()
    except Exception as e:
        _log_crash('FATAL: ' + type(e).__name__ + ': ' + str(e))
        _log_crash(traceback.format_exc())
        try:
            from kivy.app import App as _CrashApp
            from kivy.uix.label import Label as _CrashLabel
            from kivy.uix.scrollview import ScrollView as _CrashScroll
            class _CrashWrapper(_CrashApp):
                def build(self):
                    sv = _CrashScroll()
                    sv.add_widget(_CrashLabel(
                        text='App crashed\n\n' + type(e).__name__ + ': ' + str(e) +
                             '\n\nLog: ' + str(CRASH_LOG),
                        font_size='14sp', halign='left', valign='top',
                        text_size=(380, None), size_hint_y=None, height=800))
                    return sv
            _CrashWrapper().run()
        except Exception:
            pass
        raise
