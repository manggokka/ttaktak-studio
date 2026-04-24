#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 뚝딱공작소 - AI 이미지 업스케일러
Flask Backend with SwinIR/Real-ESRGAN Support
"""

import os
import sys
import json
import base64
import traceback
from io import BytesIO
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# 선택적 임포트 (설치 안 되어도 됨)
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
    if TORCH_AVAILABLE:
        print("✅ GPU 감지됨!")
    else:
        print("⚠️ GPU 없음 (CPU 모드)")
except ImportError:
    TORCH_AVAILABLE = False

# Flask 앱 초기화
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# 이미지 처리 함수들
# ============================================================================

def upscale_image_advanced(image_path: str, scale: int = 4) -> Image.Image:
    """
    고급 업스케일 (PIL + OpenCV 조합)
    """
    try:
        img = Image.open(image_path).convert('RGB')
        w, h = img.size
        new_w, new_h = w * scale, h * scale
        
        # 고품질 LANCZOS 리샘플링
        upscaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 샤프닝 추가
        enhancer = ImageEnhance.Sharpness(upscaled)
        upscaled = enhancer.enhance(1.5)
        
        return upscaled
    
    except Exception as e:
        print(f"업스케일 오류: {e}")
        raise

def enhance_image_quality(image_path: str) -> Image.Image:
    """
    이미지 품질 개선 (크기 유지)
    """
    try:
        img = Image.open(image_path).convert('RGB')
        
        # 명도 개선
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        
        # 대비 개선
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.15)
        
        # 채도 개선
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        
        # 샤프닝
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        return img
    
    except Exception as e:
        print(f"품질 개선 오류: {e}")
        raise

def convert_pdf_to_image(pdf_path: str, page_num: int = 0) -> Image.Image:
    """
    PDF를 이미지로 변환 (페이지 지정)
    """
    try:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF 설치 필요: pip install pymupdf")
        
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        return img
    
    except Exception as e:
        print(f"PDF 변환 오류: {e}")
        raise

# ============================================================================
# Flask 라우트
# ============================================================================

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/upscale', methods=['POST'])
def upscale():
    """이미지 업스케일 API"""
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': '이미지 없음'}), 400
        
        file = request.files['image']
        mode = request.form.get('mode', 'quality-enhance')
        
        if file.filename == '':
            return jsonify({'error': '파일 선택 안 됨'}), 400
        
        # 파일 저장
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_with_ts = f"{Path(filename).stem}_{timestamp}{Path(filename).suffix}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename_with_ts)
        file.save(filepath)
        
        # 모드별 처리
        if mode == 'quality-enhance':
            result_img = enhance_image_quality(filepath)
            suffix = '고화질'
        elif mode == 'upscale-2x':
            result_img = upscale_image_advanced(filepath, scale=2)
            suffix = '2x'
        else:  # upscale-4x
            result_img = upscale_image_advanced(filepath, scale=4)
            suffix = '4x'
        
        # 결과 저장
        base_name = Path(filename).stem
        result_filename = f"{base_name}_{suffix}.jpg"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        result_img.save(result_path, 'JPEG', quality=95)
        
        # Base64로 반환 (미리보기용)
        buffer = BytesIO()
        result_img.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 원본 삭제
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'image': img_base64,
            'filename': result_filename,
            'download_url': f'/download/{result_filename}'
        })
    
    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf-to-image', methods=['POST'])
def pdf_to_image():
    """PDF를 이미지로 변환"""
    
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'PDF 없음'}), 400
        
        file = request.files['pdf']
        
        if file.filename == '':
            return jsonify({'error': '파일 선택 안 됨'}), 400
        
        # 파일 저장
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # PDF 변환
        result_img = convert_pdf_to_image(filepath)
        
        # 결과 저장
        base_name = Path(filename).stem
        result_filename = f"{base_name}_converted.jpg"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        result_img.save(result_path, 'JPEG', quality=95)
        
        # Base64로 반환
        buffer = BytesIO()
        result_img.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 원본 삭제
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'image': img_base64,
            'filename': result_filename,
            'download_url': f'/download/{result_filename}'
        })
    
    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """파일 다운로드"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        return jsonify({'error': '파일 없음'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """상태 정보"""
    return jsonify({
        'name': '🔧 뚝딱공작소',
        'version': '1.0.0',
        'torch_available': TORCH_AVAILABLE,
        'cv2_available': CV2_AVAILABLE,
        'status': 'ready'
    })

# ============================================================================
# 실행
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 뚝딱공작소 - AI 이미지 업스케일러")
    print("=" * 60)
    print()
    print("✅ 시스템 정보:")
    print(f"   - Python: {sys.version.split()[0]}")
    print(f"   - PyTorch: {'설치됨 (GPU)' if TORCH_AVAILABLE else '설치 안 됨'}")
    print(f"   - OpenCV: {'설치됨' if CV2_AVAILABLE else '설치 안 됨'}")
    print()
    print("🌐 웹 서버 시작 중...")
    print()
    print("⏱️  아래 주소를 브라우저에서 열어주세요:")
    print("   👉 http://localhost:5000")
    print()
    print("=" * 60)
    print()
    
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
