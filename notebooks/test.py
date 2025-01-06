import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # 시스템에서 설치된 폰트 경로 확인
font_prop = fm.FontProperties(fname=font_path)  # FontProperties 생성

# matplotlib에 폰트 설정
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def create_pie_chart(title, sizes, labels, colors, text_size, title_size, save_path):
    # 기본 폰트 설정
    new_font_prop = font_prop.copy()
    new_font_prop.set_size(text_size)

    # 파이 차트 생성
    wedges, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        colors=colors, 
        autopct="%.1f%%", 
        startangle=90, 
        wedgeprops={"width": 0.4}, 
        textprops={"fontproperties": new_font_prop}  # 폰트 크기 적용 완료
    )

    # 퍼센트 텍스트 위치를 바깥쪽으로 조정
    for autotext in autotexts:
        x, y = autotext.get_position()
        autotext.set_fontweight("bold")
        autotext.set_position((x * 1.3, y * 1.3))  # 바깥쪽으로 이동

    # 범례 폰트 크기 설정
    legend_font_prop = font_prop.copy()
    legend_font_prop.set_size(text_size)

    # 범례 추가
    plt.legend(wedges, labels, prop=legend_font_prop, loc="upper right")

    # 제목 폰트 크기 설정
    title_font_prop = font_prop.copy()
    title_font_prop.set_size(title_size)

    # 그래프 제목 설정
    plt.title("온라인 설문 참여 현황", fontproperties=title_font_prop, fontweight="bold")

    # 그래프 저장 및 출력
    plt.tight_layout()
    plt.savefig(f"{save_path}/{title}.png", dpi=300, bbox_inches="tight")


def plot_data(data, title):
    departments = data['부서명'].tolist()
    num_people = data['인원'].tolist()
    participation_rate = data['참여율'].tolist()  # 참여율은 이미 소수로 처리됨

    x = np.arange(len(departments))

    # 그래프 생성
    fig, ax1 = plt.subplots(figsize=(15, 6))

    # 막대 그래프 (인원)
    bar_width = 0.6
    ax1.bar(x, num_people, color='#1246FF', alpha=0.7, label="인원", width=bar_width)
    ax1.set_xlabel("부서명", fontsize=text_size)
    ax1.set_ylabel("인원", color='#1246FF', fontsize=text_size)
    ax1.tick_params(axis='y', labelcolor='#1246FF', labelsize=text_size)
    ax1.set_xticks(x)
    ax1.set_xticklabels(departments, rotation=90, ha="right", fontsize=text_size)

    # 선 그래프 (참여율)
    ax2 = ax1.twinx()
    ax2.plot(x, participation_rate, color='#0AA00A', marker='o', label="참여율")
    ax2.set_ylabel("참여율", color='#0AA00A', fontsize=text_size)
    ax2.tick_params(axis='y', labelcolor='#0AA00A', labelsize=text_size)
    ax2.set_ylim(0, 1)  # 참여율(%) 범위 조정

    # 범례 추가
    fig.legend(loc="upper right", bbox_to_anchor=(1.1, 1), fontsize=text_size)

    # 제목 설정
    plt.title(title, fontsize=title_size, pad=20)

    # 그래프 출력
    plt.tight_layout()
    plt.savefig(f"{save_path}/{title}.png", dpi=300, bbox_inches="tight")
    plt.show()


def main():
    save_path = "./plots"
    title_size = 24
    text_size = 17

    title = "온라인 설문 참여 현황"
    labels = ['참여자', '미참여자']
    sizes = [133 + 127 + 47, 95 + 263 + 45]
    colors = ["#39C039", "#868e96"]

    create_pie_chart(title, sizes, labels, colors, text_size, title_size, save_path)

if __name__ == "__main__":
    main()