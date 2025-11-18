# AI Museum Portfolio

## 개요
실제 미술관(MET) 오픈데이터와 사용자가 생성한 AI 예술을 결합한 전시형 포트폴리오입니다.
주요 기능:
- MET The Met Museum Open Access API에서 작품 메타/이미지 불러오기
- OpenAI(LLM)를 이용한 ‘전문 큐레이터’ 해설 자동 생성
- Streamlit 기반 갤러리 (실존 작품 + 업로드한 생성 작품)
- Plotly 대시보드 (연도 분포 등) 및 업로드 이미지의 색상(RGB) 분포 3D 시각화

## 실행 방법
1. 가상환경 생성 및 활성화
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\\Scripts\\activate    # Windows (PowerShell)
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."    # macOS / Linux
setx OPENAI_API_KEY "sk-..."      # Windows (새 콘솔 필요)
streamlit run streamlit_app.py
ai-museum-portfolio/
├─ streamlit_app.py
├─ requirements.txt
├─ README.md
├─ src/
│  ├─ met_api.py
│  ├─ curator.py
│  ├─ viz.py
│  └─ generator.py
├─ prompts/
│  └─ curator_prompts.md
├─ data/
│  └─ generated_catalog.json
