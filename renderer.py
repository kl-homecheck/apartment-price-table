# -*- coding: utf-8 -*-
"""
1~5번 템플릿 이미지를 세로로 이어 붙이고, 그 위에 시트 데이터를 합성해서
최종 단가표 이미지를 만드는 모듈.

조립 순서: 1번 + (2번 x N) + 3번 + (4번 x N) + 5번   (N = 평형 개수)

- 폰트: assets/fonts/ 안의 Pretendard(otf)를 굵기별로 로드. 없으면 시스템
  기본 한글 폰트(Noto Sans CJK KR)로 자동 대체.
- 자간(letter-spacing): PIL 기본 draw.text는 지원하지 않아 한 글자씩 직접
  그리며 간격을 수동으로 채우는 방식(트래킹)을 사용.
- 두 줄짜리 텍스트(타입/평형, 취소선/할인가 등): 손으로 맞춘 Y좌표 대신,
  실제 렌더링된 글자 높이를 계산해서 칸 정중앙에 자동으로 배치.
"""

import os

from PIL import Image, ImageDraw, ImageFont

import config as C

_FONT_CACHE = {}


def _font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    """weight(예: 'bold','medium','regular','light') + size로 폰트 객체를 캐싱해서 반환."""
    key = (weight, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    path = C.FONT_FILES.get(weight)
    if path and os.path.exists(path):
        font = ImageFont.truetype(path, size)
    else:
        fallback_path = (
            C.FALLBACK_FONT_PATH if weight in ("black", "extrabold", "bold", "semibold")
            else C.FALLBACK_FONT_PATH_REGULAR
        )
        font = ImageFont.truetype(fallback_path, size, index=C.FALLBACK_FONT_INDEX_KR)

    _FONT_CACHE[key] = font
    return font


def _tracked_width(draw: ImageDraw.ImageDraw, text: str, font, tracking: float) -> float:
    """자간(tracking, px)을 적용했을 때 텍스트 전체 폭을 계산."""
    if not text:
        return 0.0
    widths = [font.getlength(ch) for ch in text]
    return sum(widths) + tracking * (len(text) - 1)


def _draw_center_tracked(draw: ImageDraw.ImageDraw, xy, text: str, font, fill, tracking: float = 0):
    """(중심x, 중심y) 기준으로, 글자 사이 간격(tracking, px)을 적용해 한 글자씩 그림.
    반환값: (left_x, right_x) - 실제로 그려진 텍스트 블록의 좌/우 x좌표 (취소선 계산용)
    """
    cx, cy = xy
    total_w = _tracked_width(draw, text, font, tracking)
    x = cx - total_w / 2
    left = x
    for ch in text:
        w = font.getlength(ch)
        draw.text((x + w / 2, cy), ch, font=font, fill=fill, anchor="mm")
        x += w + tracking
    right = x - tracking
    return left, right


def _draw_strike_center_tracked(draw: ImageDraw.ImageDraw, xy, text: str, font, fill, tracking: float = 0, line_width: int = 3):
    """자간을 적용해 중앙 정렬로 그리면서, 실제 텍스트 좌우 끝에 정확히 맞춘 취소선을 함께 그림."""
    cx, cy = xy
    left, right = _draw_center_tracked(draw, xy, text, font, fill, tracking=tracking)
    draw.line([(left, cy), (right, cy)], fill=fill, width=line_width)


def _line_extent(draw: ImageDraw.ImageDraw, text: str, font, tracking: float):
    """텍스트를 y=0 중심(anchor='mm')으로 그렸을 때의 (top, bottom) 오프셋과 높이를 계산.
    두 줄 블록을 정중앙에 배치하기 위한 높이 측정에 사용.
    """
    w = _tracked_width(draw, text, font, tracking)
    # 폭은 트래킹 반영, 높이는 대표 글자 하나의 bbox로 측정(숫자/한글 높이 편차가 크지 않음)
    bbox = draw.textbbox((0, 0), text if text else "0", font=font, anchor="mm")
    top, bottom = bbox[1], bbox[3]
    return top, bottom, bottom - top


def draw_vertical_pair(draw: ImageDraw.ImageDraw, cx: float, center_y: float, gap: float, lines: list):
    """여러 줄(2줄 이상)을 지정된 간격(gap)으로 쌓아, 전체 블록을 center_y 기준
    정중앙에 자동 배치해서 그린다.

    lines: [{"text":str, "font":FreeTypeFont, "fill":color, "tracking":float,
             "strike": bool(optional), "line_width": int(optional)}, ...]
    """
    extents = [_line_extent(draw, ln["text"], ln["font"], ln.get("tracking", 0)) for ln in lines]
    heights = [e[2] for e in extents]
    total_h = sum(heights) + gap * (len(lines) - 1)
    block_top = center_y - total_h / 2

    cursor = block_top
    for ln, (top, bottom, h) in zip(lines, extents):
        y_center = cursor - top
        if ln.get("strike"):
            _draw_strike_center_tracked(
                draw, (cx, y_center), ln["text"], ln["font"], ln["fill"],
                tracking=ln.get("tracking", 0), line_width=ln.get("line_width", 3),
            )
        else:
            _draw_center_tracked(draw, (cx, y_center), ln["text"], ln["font"], ln["fill"], tracking=ln.get("tracking", 0))
        cursor += h + gap


def _money(n: int) -> str:
    return f"{n:,}"


def render_row1(row: dict, event_ended: bool = False) -> Image.Image:
    """2번.png 위에 '프리미엄' 한 줄 데이터를 합성.

    event_ended=True (이벤트 종료 ver):
      - 접수대행 칸: '50,000' 취소선 + '선착순 할인 적용' 제거 → '50,000' 일반 글씨 한 줄
      - 사전점검 칸: 취소선 제거 → 더한 금액(타임특가 + 5만원)을 주황 큰 글씨로만 표시
    """
    img = Image.open(C.TEMPLATE_2).convert("RGBA")
    draw = ImageDraw.Draw(img)
    xs = C.ROW1_COL_X
    y = C.ROW1_CENTER_Y

    # 1) 타입/평형: '51m²'(medium, 위) + '(20평)'(light, 아래) - 칸 정중앙에 자동 배치
    draw_vertical_pair(draw, xs[0], y, C.ROW1_TYPE_GAP, [
        {"text": f"{row['area']}m²", "font": _font(C.ROW1_TYPE_MAIN_FONT, C.ROW1_TYPE_MAIN_FONT_SIZE),
         "fill": C.ROW1_TYPE_COLOR, "tracking": C.ROW1_TYPE_MAIN_LETTER_SPACING},
        {"text": f"({row['pyeong']}평)", "font": _font(C.ROW1_TYPE_SUB_FONT, C.ROW1_TYPE_SUB_FONT_SIZE),
         "fill": C.ROW1_TYPE_COLOR, "tracking": C.ROW1_TYPE_SUB_LETTER_SPACING},
    ])

    # 2) 정가 (※ '정가' 칸에는 G열이 아니라 타임특가/사전점검 할인가와 동일한 값이 들어감)
    _draw_center_tracked(draw, (xs[1], y), _money(row["time_deal"]), _font(C.ROW1_PRICE_FONT, C.ROW1_PRICE_FONT_SIZE), C.ROW1_PRICE_COLOR)

    if event_ended:
        # 3) 접수대행: 할인 표기 없이 '50,000' 일반 글씨 (사전점검 가격 칸과 같은 스타일)
        _draw_center_tracked(draw, (xs[2], y), C.FIXED_RECEIPT_TOP,
                             _font(C.ROW1_PRICE_FONT, C.ROW1_PRICE_FONT_SIZE), C.ROW1_PRICE_COLOR)
        # 4) 사전점검: 더한 금액(타임특가 + 5만원)을 주황 큰 글씨로 한 줄만
        _draw_center_tracked(draw, (xs[3], y), _money(row["receipt_strike"]),
                             _font(C.ROW1_DISCOUNT_FONT, C.ROW1_DISCOUNT_FONT_SIZE), C.ROW1_DISCOUNT_COLOR,
                             tracking=C.ROW1_DISCOUNT_LETTER_SPACING)
        return img

    # 3) 접수대행 (고정) - '50,000'(취소선) + '선착순 할인 적용'(작고 빨강)
    draw_vertical_pair(draw, xs[2], y, C.ROW1_FIXED_GAP, [
        {"text": C.FIXED_RECEIPT_TOP, "font": _font(C.ROW1_FIXED_TOP_FONT, C.ROW1_FIXED_TOP_FONT_SIZE),
         "fill": C.COLOR_GRAY60, "tracking": C.ROW1_FIXED_TOP_LETTER_SPACING,
         "strike": True, "line_width": C.ROW1_FIXED_TOP_STRIKE_WIDTH},
        {"text": C.FIXED_RECEIPT_BOTTOM, "font": _font(C.ROW1_FIXED_BOTTOM_FONT, C.ROW1_FIXED_BOTTOM_FONT_SIZE),
         "fill": C.COLOR_RED, "tracking": C.ROW1_FIXED_BOTTOM_LETTER_SPACING},
    ])

    # 4) 사전점검 = 취소선 정가(작게, 위) + 할인가(굵고 큰 오렌지, 아래)
    draw_vertical_pair(draw, xs[3], y, C.ROW1_DISCOUNT_GAP, [
        {"text": _money(row["receipt_strike"]), "font": _font(C.ROW1_STRIKE_FONT, C.ROW1_STRIKE_FONT_SIZE),
         "fill": C.ROW1_STRIKE_COLOR, "tracking": C.ROW1_STRIKE_LETTER_SPACING,
         "strike": True, "line_width": C.ROW1_STRIKE_WIDTH},
        {"text": _money(row["time_deal"]), "font": _font(C.ROW1_DISCOUNT_FONT, C.ROW1_DISCOUNT_FONT_SIZE),
         "fill": C.ROW1_DISCOUNT_COLOR, "tracking": C.ROW1_DISCOUNT_LETTER_SPACING},
    ])

    return img


def render_row2(row: dict, event_ended: bool = False) -> Image.Image:
    """4번.png 위에 '실속결합' 한 줄 데이터를 합성.

    event_ended=True (이벤트 종료 ver):
      - 사전·사후 접수대행 칸: 취소선/'선착순 할인 적용' 제거 → '50,000' 일반 글씨 한 줄
      - 프로모션 칸: 위 취소선 합산 금액은 그대로, 아래 최종가는 합산 금액 - 5만원
    """
    img = Image.open(C.TEMPLATE_4).convert("RGBA")
    draw = ImageDraw.Draw(img)
    xs = C.ROW2_COL_X
    y = C.ROW2_CENTER_Y

    # 1) 타입/평형
    draw_vertical_pair(draw, xs[0], y, C.ROW2_TYPE_GAP, [
        {"text": f"{row['area']}m²", "font": _font(C.ROW2_TYPE_MAIN_FONT, C.ROW2_TYPE_MAIN_FONT_SIZE),
         "fill": C.ROW2_TYPE_COLOR, "tracking": C.ROW2_TYPE_MAIN_LETTER_SPACING},
        {"text": f"({row['pyeong']}평)", "font": _font(C.ROW2_TYPE_SUB_FONT, C.ROW2_TYPE_SUB_FONT_SIZE),
         "fill": C.ROW2_TYPE_COLOR, "tracking": C.ROW2_TYPE_SUB_LETTER_SPACING},
    ])

    # 2) 사전점검 (타임특가, I열)
    _draw_center_tracked(
        draw, (xs[1], y), _money(row["time_deal"]),
        _font(C.ROW2_PRICE_FONT, C.ROW2_PRICE_FONT_SIZE), C.ROW2_PRICE_COLOR,
        tracking=C.ROW2_PRICE_LETTER_SPACING,
    )

    def _receipt_cell(cx, combo_discount=False):
        """접수대행 칸 (기본: 50,000 취소선 + 선착순 할인 적용 / 이벤트 종료: 50,000 일반 글씨)
        combo_discount=True 이고 이벤트 종료 ver 이면: 50,000 취소선 + '결합 할인 적용'
        """
        if event_ended and not combo_discount:
            _draw_center_tracked(
                draw, (cx, y), C.FIXED_RECEIPT_TOP,
                _font(C.ROW2_PRICE_FONT, C.ROW2_PRICE_FONT_SIZE), C.ROW2_PRICE_COLOR,
                tracking=C.ROW2_PRICE_LETTER_SPACING,
            )
            return
        draw_vertical_pair(draw, cx, y, C.ROW2_FIXED_GAP, [
            {"text": C.FIXED_RECEIPT_TOP, "font": _font(C.ROW2_FIXED_TOP_FONT, C.ROW2_FIXED_TOP_FONT_SIZE),
             "fill": C.COLOR_GRAY60, "tracking": C.ROW2_FIXED_TOP_LETTER_SPACING,
             "strike": True, "line_width": C.ROW2_FIXED_TOP_STRIKE_WIDTH},
            {"text": C.FIXED_COMBO_BOTTOM if (combo_discount and event_ended) else C.FIXED_RECEIPT_BOTTOM,
             "font": _font(C.ROW2_FIXED_BOTTOM_FONT, C.ROW2_FIXED_BOTTOM_FONT_SIZE),
             "fill": C.COLOR_RED, "tracking": C.ROW2_FIXED_BOTTOM_LETTER_SPACING},
        ])

    # 3) 사전점검 접수대행 (고정)
    _receipt_cell(xs[2])

    # 4) 사후점검 (고정 금액)
    _draw_center_tracked(
        draw, (xs[3], y), C.FIXED_AFTERCHECK,
        _font(C.ROW2_PRICE_FONT, C.ROW2_PRICE_FONT_SIZE), C.ROW2_PRICE_COLOR,
        tracking=C.ROW2_PRICE_LETTER_SPACING,
    )

    # 5) 사후점검 접수대행 (고정) - 이벤트 종료 ver 에서는 '50,000'(취소선) + '결합 할인 적용'
    _receipt_cell(xs[4], combo_discount=True)

    # 6) 프로모션 = 취소선(전체총합, J열) + 최종가(굵고 큰 파랑, M열)
    #    이벤트 종료 ver: 최종가 = 전체총합 - 5만원 (위 합산 금액은 그대로)
    promo_price = (row["total_before"] - C.RECEIPT_FEE) if event_ended else row["promo_final"]
    draw_vertical_pair(draw, xs[5], y, C.ROW2_PROMO_GAP, [
        {"text": _money(row["total_before"]), "font": _font(C.ROW2_STRIKE_FONT, C.ROW2_STRIKE_FONT_SIZE),
         "fill": C.ROW2_STRIKE_COLOR, "tracking": C.ROW2_STRIKE_LETTER_SPACING,
         "strike": True, "line_width": C.ROW2_STRIKE_WIDTH},
        {"text": _money(promo_price), "font": _font(C.ROW2_PROMO_FONT, C.ROW2_PROMO_FONT_SIZE),
         "fill": C.ROW2_PROMO_COLOR, "tracking": C.ROW2_PROMO_LETTER_SPACING},
    ])

    return img


def _fit_font_size(draw: ImageDraw.ImageDraw, text: str, weight: str, max_size: int, min_size: int,
                    tracking: float, max_width: float) -> int:
    """텍스트가 max_width(px) 안에 들어올 때까지 폰트 크기를 1px씩 줄여서 맞는 크기를 반환.
    min_size까지 줄여도 안 들어가면 min_size를 그대로 반환(그 이상은 줄이지 않음)."""
    size = max_size
    while size > min_size:
        f = _font(weight, size)
        w = _tracked_width(draw, text, f, tracking)
        if w <= max_width:
            return size
        size -= 1
    return min_size


def render_header(complex_name: str) -> Image.Image:
    img = Image.open(C.TEMPLATE_1).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # 단지명이 길면 지정된 최대 폭(COMPLEX_NAME_MAX_WIDTH) 안에 들어오도록 폰트 크기를 자동으로 축소
    fit_size = _fit_font_size(
        draw, complex_name, C.COMPLEX_NAME_FONT,
        C.COMPLEX_NAME_FONT_SIZE, C.COMPLEX_NAME_MIN_FONT_SIZE,
        C.COMPLEX_NAME_LETTER_SPACING, C.COMPLEX_NAME_MAX_WIDTH,
    )
    _draw_center_tracked(
        draw, C.COMPLEX_NAME_POS, complex_name,
        _font(C.COMPLEX_NAME_FONT, fit_size), C.COMPLEX_NAME_COLOR,
        tracking=C.COMPLEX_NAME_LETTER_SPACING,
    )
    return img


def build_price_table(rows: list, event_ended: bool = False) -> Image.Image:
    """전체 단가표 이미지를 조립해서 반환.

    event_ended=False : 기본 ver (선착순 할인 적용 표기)
    event_ended=True  : 이벤트 종료 ver (50,000 취소선/선착순 할인 적용 제거, 가격 재계산)
    """
    if not rows:
        raise ValueError("rows가 비어 있습니다.")

    complex_name = rows[0]["complex_name"]

    header = render_header(complex_name)
    footer = Image.open(C.TEMPLATE_5).convert("RGBA")
    section2_header = Image.open(C.TEMPLATE_3).convert("RGBA")

    row1_imgs = [render_row1(r, event_ended) for r in rows]
    row2_imgs = [render_row2(r, event_ended) for r in rows]

    width = header.width
    total_height = (
        header.height
        + sum(im.height for im in row1_imgs)
        + section2_header.height
        + sum(im.height for im in row2_imgs)
        + footer.height
    )

    canvas = Image.new("RGBA", (width, total_height), (255, 255, 255, 255))

    y = 0
    canvas.paste(header, (0, y), header)
    y += header.height

    for im in row1_imgs:
        canvas.paste(im, (0, y), im)
        y += im.height

    canvas.paste(section2_header, (0, y), section2_header)
    y += section2_header.height

    for im in row2_imgs:
        canvas.paste(im, (0, y), im)
        y += im.height

    canvas.paste(footer, (0, y), footer)
    y += footer.height

    return canvas.convert("RGB")


def draw_debug_grid(img: Image.Image, step: int = 50) -> Image.Image:
    """좌표를 눈으로 가늠할 수 있도록 50px 간격 눈금을 그려서 반환 (좌표 조정용)."""
    img = img.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font = _font("regular", 12)
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=(255, 0, 0), width=1)
        draw.text((x + 2, 2), str(x), font=font, fill=(255, 0, 0))
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=(0, 150, 0), width=1)
        draw.text((2, y + 2), str(y), font=font, fill=(0, 150, 0))
    return img
