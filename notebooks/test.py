import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# 한글 폰트 경로 설정 (확인된 유효한 경로 사용)
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # 시스템 폰트 경로
font_name = fm.FontProperties(fname=font_path).get_name()

# matplotlib에 폰트 설정
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 데이터프레임 생성
data = {
    "인사하위영역": ["본사", "센터", "역"],
    "전체인력": [228, 390, 92],
    "검사자": [133, 127, 47],
    "미응답": [95, 263, 45],
    "응답율": [58.3, 32.6, 51.1]
}

df = pd.DataFrame(data)

# 스타일 설정
sns.set_theme(style="whitegrid")

# 막대그래프 생성 및 저장
plt.figure(figsize=(10, 6))
ax = sns.barplot(x="인사하위영역", y="응답율", data=df, palette="pastel", edgecolor=".6")
ax.set_title("인사하위영역별 응답율", fontsize=16, fontweight='bold')
ax.set_ylabel("응답율 (%)", fontsize=12)
ax.set_xlabel("인사하위영역", fontsize=12)

# 응답율 값 표시
for i, v in enumerate(df["응답율"]):
    ax.text(i, v + 1, f"{v}%", ha="center", fontsize=11)

plt.tight_layout()
plt.savefig("barplot_응답율.png", dpi=300, bbox_inches='tight')  # 그래프 저장
plt.show()

# 도넛형 그래프 생성 및 저장
total_participants = df["검사자"].sum()
total_non_participants = df["미응답"].sum()

labels = ["참여자", "미참여자"]
sizes = [total_participants, total_non_participants]
colors = sns.color_palette("pastel")[0:2]

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, colors=colors, autopct='%.1f%%', startangle=90, 
        wedgeprops=dict(width=0.4), textprops={'fontsize': 14})
plt.title("온라인 설문 참여 현황", fontsize=16, fontweight='bold')

plt.tight_layout()
plt.savefig("donut_chart_참여현황.png", dpi=300, bbox_inches='tight')  # 그래프 저장
plt.show()