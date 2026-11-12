# -*- coding: utf-8 -*-
"""
좌표/색상/폰트 설정 파일
=========================
Figma Dev Mode에서 실측한 값(폰트/크기/굵기/색상/자간)을 그대로 반영했습니다.

두 줄로 나뉘는 텍스트(타입/평형, 취소선/할인가, 50,000/선착순 할인 적용)는
더 이상 손으로 맞춘 Y좌표(offset)를 쓰지 않고, "두 줄 사이 간격(GAP)"만
지정하면 렌더러가 두 줄 전체 블록의 높이를 계산해서 칸 정중앙에 자동으로
배치합니다 (가로는 자간까지 반영한 실제 글자 폭 기준으로 중앙 정렬).

좌표를 눈으로 보면서 조절하고 싶다면 `python3 test_render.py --grid` 로
50px 간격의 눈금(그리드)이 그려진 이미지를 생성해서 좌표를 가늠할 수 있습니다.
"""

import os

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

TEMPLATE_1 = os.path.join(ASSETS_DIR, "1번.png")  # 헤더 (단지명 + 타임특가 + 프리미엄 표 헤더)
TEMPLATE_2 = os.path.join(ASSETS_DIR, "2번.png")  # 프리미엄 반복 행
TEMPLATE_3 = os.path.join(ASSETS_DIR, "3번.png")  # 실속결합 표 헤더
TEMPLATE_4 = os.path.join(ASSETS_DIR, "4번.png")  # 실속결합 반복 행
TEMPLATE_5 = os.path.join(ASSETS_DIR, "5번.png")  # 푸터 (주의사항 + 부가서비스)
TEMPLATE_5_ENDED = os.path.join(ASSETS_DIR, "5번_이벤트종료.png")  # 이벤트 종료 ver 푸터 ('선착순 할인 제공' 삭제)

# ------------------------------------------------------------------
# 폰트: Pretendard (외부 OTF). assets/fonts/ 에 없으면 시스템 기본
# 한글 폰트(Noto Sans CJK KR)로 자동 대체됩니다.
# Figma font-weight 숫자 -> Pretendard 파일명 매핑:
#   100 Thin / 200 ExtraLight / 300 Light / 400 Regular / 500 Medium /
#   600 SemiBold / 700 Bold / 800 ExtraBold / 900 Black
# ------------------------------------------------------------------
FONT_FILES = {
    "black": os.path.join(FONTS_DIR, "Pretendard-Black.otf"),
    "extrabold": os.path.join(FONTS_DIR, "Pretendard-ExtraBold.otf"),
    "bold": os.path.join(FONTS_DIR, "Pretendard-Bold.otf"),
    "semibold": os.path.join(FONTS_DIR, "Pretendard-SemiBold.otf"),
    "medium": os.path.join(FONTS_DIR, "Pretendard-Medium.otf"),
    "regular": os.path.join(FONTS_DIR, "Pretendard-Regular.otf"),
    "light": os.path.join(FONTS_DIR, "Pretendard-Light.otf"),
    "extralight": os.path.join(FONTS_DIR, "Pretendard-ExtraLight.otf"),
    "thin": os.path.join(FONTS_DIR, "Pretendard-Thin.otf"),
}

# 시스템 폴백 폰트 (Pretendard 파일이 없을 경우에만 사용됨)
FALLBACK_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FALLBACK_FONT_PATH_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FALLBACK_FONT_INDEX_KR = 2

# ------------------------------------------------------------------
# 색상: Figma에서 준 값 + 원본 이미지 픽셀 샘플링으로 검증 완료
# ------------------------------------------------------------------
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)                # 타입/평형, 실속결합 사전/사후점검 숫자
COLOR_GRAY60 = (102, 102, 102)         # rgba(0,0,0,0.6) - 정가/취소선 등 보조 텍스트
COLOR_RED = (254, 80, 81)              # #FE5051 - '선착순 할인 적용'
COLOR_ORANGE = (255, 85, 48)           # #FF5530 - 프리미엄 사전점검 메인 할인가
COLOR_BLUE = (0, 100, 255)             # 실속결합 프로모션 최종가

# ------------------------------------------------------------------
# 1번.png (808 x 727) : 단지명 삽입 위치
# Figma 실측: font-size 70 / weight 700(Bold) / letter-spacing -2.8 / color #FFF
# ------------------------------------------------------------------
COMPLEX_NAME_POS = (404, 230)     # 중앙 정렬 기준점 (x=중앙, y=텍스트 중심) - '타임특가'와 가깝게 조정
COMPLEX_NAME_FONT_SIZE = 75         # 기본(최대) 크기 - 이름이 길면 아래 MAX_WIDTH에 맞춰 자동으로 줄어듦
COMPLEX_NAME_MIN_FONT_SIZE = 43     # 아무리 길어도 이 크기 밑으로는 줄이지 않음
COMPLEX_NAME_MAX_WIDTH = 680       # 이 폭(px)을 넘으면 폰트 크기를 자동으로 줄임 (808 캔버스에서 좌우 여백 고려)
COMPLEX_NAME_FONT = "bold"
COMPLEX_NAME_LETTER_SPACING = -2.8
COMPLEX_NAME_COLOR = COLOR_WHITE

# ------------------------------------------------------------------
# 2번.png (808 x 100) : 프리미엄 반복 행 - 4개 컬럼 중심 x좌표
# 검은 표 실제 폭: x=63~743 (칸마다 170px) / 하단 테두리: 검정 3px (실속결합과 동일)
# ------------------------------------------------------------------
ROW1_COL_X = [148, 318, 488, 658]  # 타입 / 정가 / 접수대행 / 사전점검
ROW1_CENTER_Y = 48                 # 행 높이 100의 정중앙

# 타입/평형: Figma 실측 - '51m²' size32/weight500(Medium)/letter-spacing-1.28
#            '(20평)' size24/weight300(Light)/letter-spacing-0.96, 둘 다 색상 #000
ROW1_TYPE_MAIN_FONT_SIZE = 32
ROW1_TYPE_MAIN_FONT = "medium"
ROW1_TYPE_MAIN_LETTER_SPACING = -1.28
ROW1_TYPE_SUB_FONT_SIZE = 24
ROW1_TYPE_SUB_FONT = "light"
ROW1_TYPE_SUB_LETTER_SPACING = -0.96
ROW1_TYPE_COLOR = COLOR_BLACK
ROW1_TYPE_GAP = 7                  # 두 줄 사이 간격(px) - 이 값만 조절하면 붙는 정도가 바뀜

# 정가: Figma 실측 - size32 / weight400(Regular) / color rgba(0,0,0,0.6)
ROW1_PRICE_FONT_SIZE = 32
ROW1_PRICE_FONT = "regular"
ROW1_PRICE_COLOR = COLOR_GRAY60

# 접수대행(고정): '50,000' 취소선 - size30/weight400/letter-spacing-1.2/color gray60
#                '선착순 할인 적용' - size16/weight700(Bold)/letter-spacing-0.64/color red
ROW1_FIXED_TOP_FONT_SIZE = 30
ROW1_FIXED_TOP_FONT = "regular"
ROW1_FIXED_TOP_LETTER_SPACING = -1.2
ROW1_FIXED_TOP_STRIKE_WIDTH = 2
ROW1_FIXED_BOTTOM_FONT_SIZE = 16
ROW1_FIXED_BOTTOM_FONT = "bold"
ROW1_FIXED_BOTTOM_LETTER_SPACING = -0.64
ROW1_FIXED_GAP = 2

# 사전점검: 취소선(예:241,000) - size28/weight400/letter-spacing-1.12/color gray60
#          할인가(예:191,000) - size38/weight700(Bold)/letter-spacing-1.52/color orange
ROW1_STRIKE_FONT_SIZE = 28
ROW1_STRIKE_FONT = "regular"
ROW1_STRIKE_LETTER_SPACING = -1.12
ROW1_STRIKE_WIDTH = 3                # 취소선 두께(px)
ROW1_STRIKE_COLOR = COLOR_GRAY60

ROW1_DISCOUNT_FONT_SIZE = 38
ROW1_DISCOUNT_FONT = "bold"
ROW1_DISCOUNT_LETTER_SPACING = -1.52
ROW1_DISCOUNT_COLOR = COLOR_ORANGE
ROW1_DISCOUNT_GAP = 2

# ------------------------------------------------------------------
# 4번.png (808 x 100) : 실속결합 반복 행 - 6개 컬럼 중심 x좌표
# 검은 표 실제 폭: x=42~766 (5칸은 111px, '프로모션' 칸만 170px)
# 타입/접수대행/사전·사후점검 4개 레이어는 Figma 실측값, '프로모션' 최종가만
# 스펙을 받지 못해 폭이 같은 프리미엄 '사전점검' 칸 크기를 그대로 재사용함.
# ------------------------------------------------------------------
ROW2_COL_X = [97, 207, 318, 429, 540, 681]
# 타입 / 사전점검 / 사전점검접수대행 / 사후점검 / 사후점검접수대행 / 프로모션
ROW2_CENTER_Y = 48                 # 행 높이 100의 정중앙

# 타입/평형: Figma 실측 결과 프리미엄 행과 완전히 동일한 스펙 (32px/24px)
ROW2_TYPE_MAIN_FONT_SIZE = 32
ROW2_TYPE_MAIN_FONT = "medium"
ROW2_TYPE_MAIN_LETTER_SPACING = -1.28
ROW2_TYPE_SUB_FONT_SIZE = 24
ROW2_TYPE_SUB_FONT = "light"
ROW2_TYPE_SUB_LETTER_SPACING = -0.96
ROW2_TYPE_COLOR = COLOR_BLACK
ROW2_TYPE_GAP = 7

# 사전점검 / 사후점검: Figma 실측 - size28/weight400(Regular)/letter-spacing-1.12/color gray60
ROW2_PRICE_FONT_SIZE = 28
ROW2_PRICE_FONT = "regular"
ROW2_PRICE_LETTER_SPACING = -1.12
ROW2_PRICE_COLOR = COLOR_GRAY60

# 접수대행(고정): '50,000' 취소선 - size28/weight400/letter-spacing-1.12/color gray60
#                '선착순 할인 적용' - size16/weight700(Bold)/letter-spacing-0.64/color red (프리미엄과 동일)
ROW2_FIXED_TOP_FONT_SIZE = 28
ROW2_FIXED_TOP_FONT = "regular"
ROW2_FIXED_TOP_LETTER_SPACING = -1.12
ROW2_FIXED_TOP_STRIKE_WIDTH = 2
ROW2_FIXED_BOTTOM_FONT_SIZE = 16
ROW2_FIXED_BOTTOM_FONT = "bold"
ROW2_FIXED_BOTTOM_LETTER_SPACING = -0.64
ROW2_FIXED_GAP = 2

# 프로모션: 취소선(예:376,000) - size30/weight400/letter-spacing-1.2/color gray60 (Figma 실측)
#          최종가(예:276,000) - 스펙 미제공, 폭이 같은 프리미엄 '사전점검' 할인가 크기 재사용
ROW2_STRIKE_FONT_SIZE = 30
ROW2_STRIKE_FONT = "regular"
ROW2_STRIKE_LETTER_SPACING = -1.2
ROW2_STRIKE_WIDTH = 3
ROW2_STRIKE_COLOR = COLOR_GRAY60

ROW2_PROMO_FONT_SIZE = 38
ROW2_PROMO_FONT = "bold"
ROW2_PROMO_LETTER_SPACING = -1.52
ROW2_PROMO_COLOR = COLOR_BLUE
ROW2_PROMO_GAP = 2

# ------------------------------------------------------------------
# 고정 텍스트 (매 행 동일)
# ------------------------------------------------------------------
FIXED_RECEIPT_TOP = "50,000"
FIXED_RECEIPT_BOTTOM = "선착순 할인 적용"
FIXED_AFTERCHECK = "85,000"
FIXED_COMBO_BOTTOM = "결합 할인 적용"   # 이벤트 종료 ver: 실속결합 사후점검 접수대행 칸 아래 문구

# ------------------------------------------------------------------
# 구글시트 컬럼(A,B,C...) -> 실제 사용하는 컬럼 인덱스 (0=A, 1=B, ...)
# 사용자가 시트 구성을 바꾸면 이 숫자만 수정하면 됩니다.
# ------------------------------------------------------------------
COL_IDX = {
    "단지명": 0,       # A열
    "평형": 3,          # D열 (예: 20, 24, 29...)
    "전용면적": 4,       # E열 (예: 51, 59, 74... -> m²)
    "정가": 6,          # G열
    "타임특가": 8,       # I열 (프리미엄 사전점검 할인가 / 실속결합 사전점검)
    "전체총합": 9,       # J열 (실속결합 프로모션 취소선 값)
    "프로모션최종가": 12,  # M열 (실속결합 프로모션 최종 할인가)
}

RECEIPT_FEE = 50000  # 사전점검 취소선 = 타임특가 + 5만원
