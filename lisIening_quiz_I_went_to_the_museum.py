import streamlit as st
from openai import OpenAI
import random
import base64

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_question():
    answer1 = random.choice([" I went to the history museum.", "I played badminton.", " I watched a movie."," I went to the space center."," I made a car.","I went fishing.","I went shopping","I went to the park.","I went to the library.","I went to the museum.","I played soccer","I played basketball", "I played baseball","I played tennis"])       
    question_format = (                          
 f'''
대화를 듣고 {answer1}에 관해 묻는 질문,
예시:
 ''')
    
    key_expression = (f'''
A:What did you do yesterday?
B:{answer1}
A:What did you do there?
B:I learned about Korean history
''')
    prompt = f"""{key_expression}과 같은 구문을 사용 하는 CEFR A1 수준의 간단한 영어 대화를 생성해주세요. 
    영어 대화를 생성할 때, 마지막 대화 내용은 알려주지 말고대화 내용에 관한 객관식 질문으로 만들어야 합니다. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.  
    조건: 문제의 정답은 1개 입니다. 
    A와 B가 대화할 때 상대방의 이름을 부르면서 대화를 합니다. 
    영어 대화는 A와 B가 각각 1번 또는 2번 말하고 끝납니다.
    형식:
    [영어 대화]
    A: ...
    B: ...
    A: ...
    B: ...

    [한국어 질문]
    조건: {question_format}을 만들어야 합니다. 영어 대화에서 생성된 A와 B의 이름 중 필요한 것을 골라서 질문에 사용해야 합니다.
    질문: (한국어로 된 질문) 이 때, 선택지는 영어로 제공됩니다.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    audio_bytes = response.content
    
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    
    return audio_tag

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링👱🏾‍♂️")
st.markdown("**❓어제 한 일에 대한 퀴즈**")
st.divider()

#확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ [재생]▶ 버튼을 누르고 대화를 들어보기.<br> 
    3️⃣ [녹음 시작] 버튼을 다시 눌러 대답하고 이어서 바로 질문하기.<br>
    4️⃣ 1~3번을 반복하기. 말문이 막힐 땐 [잠깐 멈춤] 버튼을 누르기.<br>
    <br>
    🙏 잉글링은 완벽하게 이해하거나 제대로 대답하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [처음부터 다시하기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)
    st.divider()
    st.write("다음 보기 중 골라서 잉글링에게 질문해 보세요.")
    st.markdown('''
    🔸 Are you happy? (아 유 해피?)<br>
    🔸 Are you sad? (아 유 새드?)<br>
    🔸 Are you angry? (아 유 앵그리?)<br>
    🔸 Are you hungry? (아 유 헝그리?)<br>
    🔸 Are you thirsty? (아 유 떨스티?)<br>
    🔸 Are you tired? (아 유 다이얼드?)
    ''', unsafe_allow_html=True)
    st.divider()
    st.write("잉글링의 질문을 듣고, 다음 보기 중 골라서 대답해 보세요.")
    st.markdown('''
    🔸 Yes, I am.(예스 아이 앰.)<br>
    🔸 No, I'm not.(노 아임 낫.)
    ''', unsafe_allow_html=True)

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 만들기"):
    # 세션 상태 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    full_content = generate_question()
    
    dialogue, question_part = full_content.split("[한국어 질문]")
    
    question_lines = question_part.strip().split("\n")
    question = question_lines[0].replace("질문:", "").strip() if question_lines else ""
    options = question_lines[1:5] if len(question_lines) > 1 else []
    correct_answer = ""
    
    for line in question_lines:
        if line.startswith("정답:"):
            correct_answer = line.replace("정답:", "").strip()
            break
    
    st.session_state.question = question
    st.session_state.dialogue = dialogue.strip()
    st.session_state.options = options
    st.session_state.correct_answer = correct_answer
    st.session_state.question_generated = True
    
    # 새 대화에 대한 음성 생성
    st.session_state.audio_tag = text_to_speech(st.session_state.dialogue)
    
    # 페이지 새로고침
    st.rerun()

if 'question_generated' in st.session_state and st.session_state.question_generated:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    # 저장된 음성 태그 사용
    st.markdown("### 대화")
    st.markdown(st.session_state.audio_tag, unsafe_allow_html=True)
    
   
    #st.text(st.session_state.dialogue)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                #st.info(f"정답: {st.session_state.correct_answer}")  # 정답 출력
                # 공백 제거 후 비교
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                    st.text(st.session_state.dialogue)
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
                    st.text(st.session_state.dialogue)
            else:
                st.warning("답을 선택해주세요.")
