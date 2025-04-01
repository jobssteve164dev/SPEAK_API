"""
Edge TTS SDK - 简单易用的文字转语音SDK
"""

from .tts_sdk import (
    TTSClient,
    SyncTTSClient,
    text_to_speech,
    async_text_to_speech
)

__version__ = "0.1.0"
__all__ = ["TTSClient", "SyncTTSClient", "text_to_speech", "async_text_to_speech"] 