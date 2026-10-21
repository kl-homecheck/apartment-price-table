# -*- coding: utf-8 -*-
"""
아파트 사전점검 단가표 자동 생성기 (Streamlit 웹앱)

실행 방법:
    streamlit run app.py

구글 시트에서 복사한 여러 행(탭으로 구분된 텍스트)을 붙여넣고
버튼을 누르면, 이미지 렌더링 로직(parser.py / renderer.py / config.py)은
그대로 사용해서 완성된 단가표 이미지를 만들어 화면에 보여주고
다운로드할 수 있게 해주는 웹페이지입니다.

※ 이미지 렌더링 로직(Pillow 좌표/폰트 설정)은 전혀 손대지 않았습니다.
※ 화면 표시 방식만 변경: 잠자던 앱이 깨어난 뒤 그림이 깨져 보이던 문제를
   막기 위해, 이미지를 서버 임시 파일이 아니라 페이지 안에 직접 심어서 보여줍니다.
"""

import base64
import io

import streamlit as st

from parser import ParseError, parse_sheet_text
from renderer import build_price_table

st.set_page_config(page_title="아파트 사전점검 단가표 자동 생성기", page_icon="🏢", layout="centered")

st.title("🏢 아파트 사전점검 단가표 자동 생성기")
st.write("구글 시트에서 행(들)을 복사한 뒤 아래에 그대로 붙여넣고 버튼을 누르면, 완성된 단가표 이미지를 만들어드려요.")

sheet_text = st.text_area(
    "구글 시트 데이터를 복사해서 붙여넣으세요",
    height=220,
    placeholder="힐스테이트메디알레\t주관사\t프리미엄\t20\t51\t304,500\t239,000\t-\t191,000\t376,000\t-\t-\t276,000\n...",
)

generate_clicked = st.button("이미지 생성하기", type="primary", use_container_width=True)

if generate_clicked:
    if not sheet_text.strip():
        st.session_state.pop("result", None)
        st.warning("먼저 시트에서 복사한 데이터를 붙여넣어 주세요.")
    else:
        try:
            with st.spinner("이미지를 만들고 있어요..."):
                rows = parse_sheet_text(sheet_text)
                image = build_price_table(rows)
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                png_bytes = buf.getvalue()

            # 다운로드 버튼을 눌러 화면이 다시 그려져도 결과가 사라지지 않게 보관
            st.session_state["result"] = {
                "png": png_bytes,
                "name": rows[0]["complex_name"],
                "count": len(rows),
            }
        except ParseError as e:
            st.session_state.pop("result", None)
            st.error(f"데이터를 읽는 중 문제가 있어요: {e}")
        except Exception as e:  # noqa: BLE001
            st.session_state.pop("result", None)
            st.error(f"이미지 생성 중 오류가 발생했어요: {e}")

result = st.session_state.get("result")
if result:
    st.success(f"'{result['name']}' 단가표가 완성되었어요! (총 {result['count']}개 타입)")

    # 이미지를 페이지 안에 직접 심기 (임시 파일 주소를 쓰지 않아서 깨지지 않음)
    b64 = base64.b64encode(result["png"]).decode("ascii")
    st.markdown(
        f'<img src="data:image/png;base64,{b64}" style="width:100%;height:auto;" alt="단가표">',
        unsafe_allow_html=True,
    )

    st.download_button(
        label="⬇️ 이미지 다운로드",
        data=result["png"],
        file_name=f"{result['name']}_단가표.png",
        mime="image/png",
        use_container_width=True,
    )

with st.expander("붙여넣기 형식이 궁금하다면 (예시 보기)"):
    st.code(
        "힐스테이트메디알레\t주관사\t프리미엄\t20\t51\t304,500\t239,000\t-\t191,000\t376,000\t-\t-\t276,000\n"
        "힐스테이트메디알레\t주관사\t프리미엄\t24\t59\t333,500\t249,000\t-\t199,000\t384,000\t-\t-\t284,000",
        language="text",
    )
    st.caption("헤더(컬럼명) 줄은 있어도 없어도 자동으로 처리돼요. 평형 개수만큼 이미지 세로 길이가 자동으로 늘어나요.")
