import os
import base64
import re
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
from dotenv import load_dotenv
import json

load_dotenv()

# 영상 다운로드 및 분석 결과 저장 디렉토리
VIDEO_DIR = Path("downloaded_videos")
VIDEO_DIR.mkdir(exist_ok=True)
VIDEO_ANALYSIS_DIR = Path("video_analysis")
VIDEO_ANALYSIS_DIR.mkdir(exist_ok=True)

@tool
def download_youtube_video(youtube_url: str) -> str:
    """
    유튜브 영상을 다운로드합니다.
    
    Args:
        youtube_url: 유튜브 영상 URL
    
    Returns:
        다운로드된 영상 파일 경로
    """
    try:
        import yt_dlp
        
        # 유튜브 URL 검증
        youtube_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_pattern, youtube_url)
        if not match:
            return f"유효하지 않은 유튜브 URL입니다: {youtube_url}"
        
        video_id = match.group(1)
        
        # 다운로드 옵션 설정
        ydl_opts = {
            'format': 'best[height<=360]',  # 360p로 제한 (용량 및 속도 최적화, 내용 분석에는 충분)
            'outtmpl': str(VIDEO_DIR / f'{video_id}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 영상 정보 가져오기
            info = ydl.extract_info(youtube_url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # 영상 다운로드
            ydl.download([youtube_url])
            
            # 다운로드된 파일 찾기
            video_files = list(VIDEO_DIR.glob(f"{video_id}.*"))
            if not video_files:
                return f"영상 다운로드 실패: {youtube_url}"
            
            video_path = video_files[0]
            
            return f"""영상 다운로드 완료!
제목: {title}
길이: {duration // 60}분 {duration % 60}초
파일 경로: {video_path}
"""
    
    except ImportError:
        return "yt-dlp 패키지가 설치되지 않았습니다. 'pip install yt-dlp'를 실행하세요."
    except Exception as e:
        return f"영상 다운로드 중 오류 발생: {str(e)}"

@tool
def summarize_youtube_video(youtube_url: str) -> str:
    """
    유튜브 영상을 다운로드하고 Gemini를 사용하여 요약합니다.
    
    Args:
        youtube_url: 유튜브 영상 URL
    
    Returns:
        영상 요약 텍스트
    """
    try:
        import yt_dlp
        
        # 유튜브 URL에서 비디오 ID 추출
        youtube_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_pattern, youtube_url)
        if not match:
            return f"유효하지 않은 유튜브 URL입니다: {youtube_url}"
        
        video_id = match.group(1)
        
        # 이미 다운로드된 영상이 있는지 확인
        video_files = list(VIDEO_DIR.glob(f"{video_id}.*"))
        if not video_files:
            # 영상 다운로드
            ydl_opts = {
                'format': 'best[height<=360]',  # 360p로 제한 (용량 및 속도 최적화)
                'outtmpl': str(VIDEO_DIR / f'{video_id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                ydl.download([youtube_url])
            
            video_files = list(VIDEO_DIR.glob(f"{video_id}.*"))
            if not video_files:
                return f"영상 다운로드 실패: {youtube_url}"
        
        video_path = video_files[0]
        
        # 영상 파일 읽기
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()
        
        # 파일 크기 확인 및 경고 (Gemini는 실제로 더 큰 파일도 처리 가능하지만, 안정성을 위해 50MB로 제한)
        file_size_mb = len(video_data) / (1024 * 1024)
        if file_size_mb > 50:
            return f"영상 파일이 너무 큽니다 ({file_size_mb:.2f}MB). 50MB 이하의 영상만 처리할 수 있습니다. 영상이 길다면 화질을 더 낮추거나 영상을 분할해서 처리해주세요."
        
        # 30MB 이상이면 경고 메시지 추가
        size_warning = ""
        if file_size_mb > 30:
            size_warning = f"\n⚠️ 주의: 영상이 큽니다 ({file_size_mb:.2f}MB). 처리 시간이 오래 걸릴 수 있습니다."
        
        # MIME 타입 결정
        video_ext = video_path.suffix.lower()
        mime_types = {
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".mkv": "video/x-matroska"
        }
        mime_type = mime_types.get(video_ext, "video/mp4")
        
        # 영상 정보 가져오기
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            title = info.get('title', 'Unknown')
            description = info.get('description', '')[:500]  # 처음 500자만
        
        # Gemini API 직접 호출
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 프롬프트 구성
        prompt = f"""다음 유튜브 영상을 분석하고 요약해주세요.

영상 제목: {title}
영상 설명: {description}

영상의 주요 내용을 다음 형식으로 요약해주세요:
1. 영상 주제 및 목적
2. 주요 내용 요약 (3-5개 포인트)
3. 핵심 메시지
4. 추천 대상

한국어로 자세하고 구체적으로 작성해주세요."""
        
        # 영상 파일 업로드 및 요약
        try:
            response = model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": video_data
                },
                prompt
            ])
            
            result = response.text
            if size_warning:
                result = size_warning + "\n\n" + result
            
            return result
        
        except Exception as e:
            error_msg = str(e)
            # 파일 크기 관련 에러인지 확인
            if "file size" in error_msg.lower() or "too large" in error_msg.lower() or "size limit" in error_msg.lower():
                return f"영상 파일이 너무 큽니다 ({file_size_mb:.2f}MB). Gemini API 제한을 초과했습니다. 영상을 더 낮은 화질로 다운로드하거나, 영상을 분할해서 처리해주세요."
            return f"영상 요약 생성 중 오류 발생: {str(e)}"
    
    except ImportError:
        return "필요한 패키지가 설치되지 않았습니다. 'pip install yt-dlp google-generativeai'를 실행하세요."
    except Exception as e:
        return f"영상 요약 중 오류 발생: {str(e)}"

@tool
def answer_youtube_question(question: str, youtube_url: str) -> str:
    """
    유튜브 영상에 대한 질문에 답변합니다.
    
    Args:
        question: 사용자의 질문
        youtube_url: 유튜브 영상 URL
    
    Returns:
        질문에 대한 답변
    """
    try:
        # 먼저 영상 요약 생성
        summary = summarize_youtube_video.invoke({"youtube_url": youtube_url})
        
        if "오류" in summary or "실패" in summary:
            return summary
        
        # Gemini로 질문 답변
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        prompt = f"""다음은 유튜브 영상의 요약입니다:

{summary}

위 영상 요약을 바탕으로 다음 질문에 답변해주세요:
{question}

답변은 요약 내용에 근거하여 정확하고 구체적으로 작성해주세요."""
        
        response = llm.invoke(prompt)
        return response.content
    
    except Exception as e:
        return f"질문 답변 생성 중 오류 발생: {str(e)}"

# 도구 리스트
video_tools = [download_youtube_video, summarize_youtube_video, answer_youtube_question]
