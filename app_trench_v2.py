"""
트렌치코트 전략 분석 Streamlit 대시보드

인터랙티브 시각화 및 필터 기능 제공
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import warnings

warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="트렌치코트 출시 전략 대시보드",
    page_icon="🧥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 경로
DATA_DIR = "data_ipchun"

# 캐싱을 통한 데이터 로드 최적화
@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    try:
        # 1. 전체 비교 데이터
        full_comparison = pd.read_csv(f"{DATA_DIR}/ipchun_full_comparison.csv")
        full_comparison['period'] = pd.to_datetime(full_comparison['period'])
        full_comparison['ratio'] = pd.to_numeric(full_comparison['ratio'], errors='coerce')
        
        # 2. 쇼핑 아이템 데이터
        shopping_items = pd.read_csv(f"{DATA_DIR}/trench_shopping_items.csv")
        if 'lprice' in shopping_items.columns:
            shopping_items['lprice'] = pd.to_numeric(shopping_items['lprice'], errors='coerce')
        
        # 3. 확장 키워드 v2
        expansion_v2 = pd.read_csv(f"{DATA_DIR}/ipchun_trench_v2_expansion.csv")
        expansion_v2['period'] = pd.to_datetime(expansion_v2['period'])
        expansion_v2['ratio'] = pd.to_numeric(expansion_v2['ratio'], errors='coerce')
        
        # 4. 핵심 트렌드
        core_trend = pd.read_csv(f"{DATA_DIR}/ipchun_core_trend.csv")
        core_trend['period'] = pd.to_datetime(core_trend['period'])
        core_trend['ratio'] = pd.to_numeric(core_trend['ratio'], errors='coerce')
        
        # 5. 세그먼트
        segments = pd.read_csv(f"{DATA_DIR}/ipchun_trench_segments.csv")
        segments['period'] = pd.to_datetime(segments['period'])
        segments['ratio'] = pd.to_numeric(segments['ratio'], errors='coerce')
        
        return full_comparison, shopping_items, expansion_v2, core_trend, segments
    
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None, None, None, None, None


def main():
    """메인 대시보드"""
    
    # 타이틀
    st.title("🧥 트렌치코트 2026 봄 시즌 출시 전략 대시보드")
    st.markdown("---")
    
    # 데이터 로드
    full_comparison, shopping_items, expansion_v2, core_trend, segments = load_data()
    
    if full_comparison is None:
        st.error("데이터를 로드할 수 없습니다.")
        return
    
    # 사이드바 필터
    st.sidebar.header("📊 필터 설정")
    
    # 날짜 범위 필터
    min_date = core_trend['period'].min().date()
    max_date = core_trend['period'].max().date()
    
    date_range = st.sidebar.date_input(
        "날짜 범위 선택",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 입춘 날짜 표시
    ipchun_date = pd.to_datetime('2025-02-03')
    st.sidebar.info(f"📅 입춘: {ipchun_date.strftime('%Y-%m-%d')}")
    
    # 메인 컨텐츠
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 시장 경쟁력", 
        "🔍 키워드 분석", 
        "💰 가격 분석", 
        "📊 트렌드 분석",
        "🎯 런칭 전략"
    ])
    
    # Tab 1: 시장 경쟁력
    with tab1:
        st.header("시장 경쟁력 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 카테고리별 평균 성장률
            category_growth = full_comparison.groupby('keyword')['ratio'].mean().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=category_growth.values,
                y=category_growth.index,
                orientation='h',
                title="카테고리별 평균 성장률 Top 15",
                labels={'x': '평균 성장률', 'y': '카테고리'},
                color=category_growth.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 트렌치코트 vs 전체 시장
            trench_data = full_comparison[
                full_comparison['keyword'].str.contains('트렌치|코트', na=False)
            ]
            
            if len(trench_data) > 0:
                trench_avg = float(trench_data['ratio'].mean())
                market_avg = float(full_comparison['ratio'].mean())
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['트렌치코트', '전체 시장'],
                    y=[trench_avg, market_avg],
                    marker_color=['#FF6B6B', '#4ECDC4'],
                    text=[f'{trench_avg:.2f}', f'{market_avg:.2f}'],
                    textposition='auto'
                ))
                fig.update_layout(
                    title="트렌치코트 vs 전체 시장 평균 성장률",
                    yaxis_title="평균 성장률",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 시각화 이미지 경로 설정
                IMAGE_PATH = "images/trench"
                if not os.path.exists(IMAGE_PATH):
                    os.makedirs(IMAGE_PATH, exist_ok=True)
                # 인사이트
                if trench_avg > market_avg:
                    st.success(f"✅ 트렌치코트 성장률({trench_avg:.2f})이 전체 시장 평균({market_avg:.2f})을 상회합니다!")
                else:
                    st.warning(f"⚠️ 트렌치코트 성장률({trench_avg:.2f})이 전체 시장 평균({market_avg:.2f})을 하회합니다.")
    
    # Tab 2: 키워드 분석
    with tab2:
        st.header("키워드 확장 분석")
        
        # 키워드별 Total Demand
        keyword_demand = expansion_v2.groupby('keyword')['ratio'].sum().sort_values(ascending=False)
        total_demand = keyword_demand.sum()
        keyword_pct = (keyword_demand / total_demand * 100).round(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상위 15개 키워드 막대그래프
            top_keywords = keyword_pct.head(15)
            
            fig = px.bar(
                x=top_keywords.values,
                y=top_keywords.index,
                orientation='h',
                title="키워드별 Total Demand 비율 Top 15",
                labels={'x': '비율 (%)', 'y': '키워드'},
                color=top_keywords.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 파이 차트
            top_10_keywords = keyword_pct.head(10)
            
            fig = px.pie(
                values=top_10_keywords.values,
                names=top_10_keywords.index,
                title="키워드별 Total Demand 비율 Top 10"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # 키워드 테이블
        st.subheader("키워드 상세 정보")
        keyword_df = pd.DataFrame({
            '키워드': keyword_pct.index,
            '비율 (%)': keyword_pct.values
        }).head(20)
        st.dataframe(keyword_df, use_container_width=True)
    
    # Tab 3: 가격 분석
    with tab3:
        st.header("가격 분석")
        
        if 'lprice' in shopping_items.columns:
            prices = shopping_items['lprice'].dropna()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 가격 분포 히스토그램
                fig = px.histogram(
                    prices,
                    nbins=50,
                    title="가격 분포 및 누적 분포",
                    labels={'value': '가격 (원)', 'count': '상품 수'},
                    color_discrete_sequence=['#95E1D3'],
                    cumulative=False
                )
                
                # 누적 분포 추가 선택
                show_cumulative = st.checkbox("누적 히스토그램으로 보기", value=False)
                if show_cumulative:
                    fig = px.histogram(
                        prices,
                        nbins=50,
                        title="가격 누적 분포",
                        labels={'value': '가격 (원)', 'count': '누적 상품 수'},
                        color_discrete_sequence=['#F38181'],
                        cumulative=True
                    )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # 기술통계
                st.subheader("가격 기술통계")
                price_stats = prices.describe()
                stats_df = pd.DataFrame({
                    '통계량': ['평균', '중앙값', '표준편차', '최소값', '최대값', '1사분위수', '3사분위수'],
                    '값 (원)': [
                        f"{price_stats['mean']:,.0f}",
                        f"{price_stats['50%']:,.0f}",
                        f"{price_stats['std']:,.0f}",
                        f"{price_stats['min']:,.0f}",
                        f"{price_stats['max']:,.0f}",
                        f"{price_stats['25%']:,.0f}",
                        f"{price_stats['75%']:,.0f}"
                    ]
                })
                st.dataframe(stats_df, use_container_width=True)
            
            with col2:
                # 가격대별 분포
                price_bins = [0, 50000, 100000, 150000, 200000, 300000, float('inf')]
                price_labels = ['~5만원', '5~10만원', '10~15만원', '15~20만원', '20~30만원', '30만원~']
                shopping_items['price_range'] = pd.cut(
                    shopping_items['lprice'], 
                    bins=price_bins, 
                    labels=price_labels
                )
                
                price_dist = shopping_items['price_range'].value_counts().sort_index()
                
                fig = px.pie(
                    values=price_dist.values,
                    names=price_dist.index,
                    title="가격대별 상품 분포"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # 가격 책정 제안
                st.subheader("💡 가격 책정 제안")
                median_price = price_stats['50%']
                q1 = price_stats['25%']
                q3 = price_stats['75%']
                
                st.info(f"""
                **권장 가격대**: {q1:,.0f}원 ~ {q3:,.0f}원
                
                **최적 가격**: {median_price:,.0f}원 (중앙값 기준)
                
                **가장 많은 상품 가격대**: {price_dist.idxmax()}
                """)
    
    # Tab 4: 트렌드 분석
    with tab4:
        st.header("트렌드 분석")
        
        # 날짜 필터 적용
        if len(date_range) == 2:
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            filtered_trend = core_trend[
                (core_trend['period'] >= start_date) & 
                (core_trend['period'] <= end_date)
            ]
        else:
            filtered_trend = core_trend
        
        # 키워드 선택
        available_keywords = filtered_trend['keyword'].unique().tolist()
        selected_keywords = st.multiselect(
            "표시할 키워드 선택",
            options=available_keywords,
            default=available_keywords[:5] if len(available_keywords) >= 5 else available_keywords
        )
        
        if selected_keywords:
            # 트렌드 라인 그래프
            filtered_data = filtered_trend[filtered_trend['keyword'].isin(selected_keywords)]
            
            fig = px.line(
                filtered_data,
                x='period',
                y='ratio',
                color='keyword',
                title="입춘 전후 트렌드 변화",
                labels={'period': '날짜', 'ratio': '검색 비율', 'keyword': '키워드'}
            )
            
            # 입춘 날짜 표시
            fig.add_vline(
                x=ipchun_date.timestamp() * 1000,
                line_dash="dash",
                line_color="red",
                annotation_text="입춘",
                annotation_position="top"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # 성별&연령 히트맵 분석 (Step 3 요구사항)
            st.divider()
            st.subheader("👥 성별 & 연령별 관심도 히트맵")
            
            if segments is not None and len(segments) > 0:
                # 피봇 테이블 생성
                # segments 데이터 구조: period, ratio, segment (또는 keyword)
                idx_name = 'segment' if 'segment' in segments.columns else 'keyword'
                
                pivot_segments = segments.pivot_table(
                    values='ratio',
                    index=idx_name,
                    columns='period',
                    aggfunc='mean'
                )
                
                # 날짜 형식 변경 (X축 가독성)
                pivot_segments.columns = [d.strftime('%m-%d') for d in pivot_segments.columns]
                
                fig_hm = px.imshow(
                    pivot_segments,
                    color_continuous_scale='YlOrRd',
                    title="날짜별 세그먼트 클릭 관심도 히트맵",
                    labels=dict(x="날짜", y="세그먼트", color="비율")
                )
                fig_hm.update_layout(height=600)
                st.plotly_chart(fig_hm, use_container_width=True)
                
                st.caption("※ 성별/연령대별 클릭 비율 데이터를 시각화한 결과입니다.")
            else:
                st.warning("세그먼트 데이터를 로드할 수 없어 히트맵을 표시할 수 없습니다.")

            # 골든 타임 분석
            st.subheader("📅 마케팅 골든 타임")
            golden_start = ipchun_date
            golden_end = ipchun_date + pd.Timedelta(days=14)
            
            golden_period = filtered_trend[
                (filtered_trend['period'] >= golden_start) &
                (filtered_trend['period'] <= golden_end)
            ]
            
            if len(golden_period) > 0:
                avg_ratio = float(golden_period['ratio'].mean())
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("골든 타임 기간", f"{golden_start.strftime('%m/%d')} ~ {golden_end.strftime('%m/%d')}")
                with col2:
                    st.metric("평균 검색 비율", f"{avg_ratio:.2f}")
                with col3:
                    campaign_start = golden_start - pd.Timedelta(days=7)
                    st.metric("캠페인 시작 권장일", campaign_start.strftime('%Y-%m-%d'))
        else:
            st.warning("키워드를 선택해주세요.")
    
    # Tab 5: 런칭 전략
    with tab5:
        st.header("🎯 2026 봄 시즌 런칭 전략")
        
        # 핵심 인사이트
        st.subheader("💡 핵심 인사이트")
        
        trench_data = full_comparison[
            full_comparison['keyword'].str.contains('트렌치|코트', na=False)
        ]
        
        if len(trench_data) > 0:
            trench_avg = float(trench_data['ratio'].mean())
            market_avg = float(full_comparison['ratio'].mean())
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **시장 경쟁력**
                
                트렌치코트 성장률({trench_avg:.2f})이 전체 시장 평균({market_avg:.2f})을 
                {'상회' if trench_avg > market_avg else '하회'}하여 
                {'높은' if trench_avg > market_avg else '낮은'} 시장 경쟁력을 보임
                """)
            
            with col2:
                if 'lprice' in shopping_items.columns:
                    prices = shopping_items['lprice'].dropna()
                    median_price = prices.median()
                    
                    price_bins = [0, 50000, 100000, 150000, 200000, 300000, float('inf')]
                    price_labels = ['~5만원', '5~10만원', '10~15만원', '15~20만원', '20~30만원', '30만원~']
                    shopping_items['price_range'] = pd.cut(
                        shopping_items['lprice'], 
                        bins=price_bins, 
                        labels=price_labels
                    )
                    price_dist = shopping_items['price_range'].value_counts()
                    
                    st.info(f"""
                    **가격 전략**
                    
                    중앙값 가격은 {median_price:,.0f}원이며,
                    가장 많은 상품이 속한 가격대는 {price_dist.idxmax()}
                    """)
        
        # 상품 스펙 제안
        st.subheader("🛍️ 상품 스펙 제안")
        
        top_keywords = expansion_v2.groupby('keyword')['ratio'].sum().sort_values(ascending=False).head(10)
        
        spec_df = pd.DataFrame({
            '키워드': top_keywords.index,
            '검색 강도': top_keywords.values.round(2)
        })
        
        st.dataframe(spec_df, use_container_width=True)
        
        st.markdown("""
        **제안 사항:**
        - **기장**: Short와 Long 기장을 모두 준비 (각각 26.35%, 17.21%)
        - **핏**: Loose 핏 중심 (7.37%)
        - **색상**: Black, Navy, Khaki, Beige 순으로 우선순위 설정
        """)
        
        # 마케팅 타이밍
        st.subheader("📅 마케팅 타이밍 전략")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "캠페인 시작",
                "입춘 1주 전",
                "2025-01-27"
            )
        
        with col2:
            st.metric(
                "골든 타임",
                "입춘 후 2주",
                "2025-02-03 ~ 02-17"
            )
        
        with col3:
            st.metric(
                "집중 마케팅",
                "입춘 당일부터",
                "2주간"
            )
        
        # 다운로드 버튼
        st.subheader("📥 리포트 다운로드")
        
        try:
            with open("TRENCH_ANALYSIS_REPORT.md", "r", encoding="utf-8") as f:
                report_content = f.read()
            
            st.download_button(
                label="📄 분석 리포트 다운로드 (Markdown)",
                data=report_content,
                file_name="TRENCH_ANALYSIS_REPORT.md",
                mime="text/markdown"
            )
        except:
            st.warning("분석 리포트 파일을 찾을 수 없습니다.")
    
    # 푸터
    st.markdown("---")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}")


if __name__ == "__main__":
    main()
