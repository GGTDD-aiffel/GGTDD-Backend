from datetime import datetime

def convert_firebase_timestamp(firebase_datetime):
    """
    Firebase에서 가져온 타임스탬프를 datetime 객체로 변환합니다.
    
    Args:
        firebase_datetime: Firebase 타임스탬프, datetime 객체, 문자열 또는 None
        
    Returns:
        datetime 객체 또는 None
    """
    if firebase_datetime is None:
        return None
    
    # firebase_datetime이 이미 datetime 객체인지 확인
    if isinstance(firebase_datetime, datetime):
        return firebase_datetime
    
    # 문자열인 경우 처리 (여러 형식 지원)
    if isinstance(firebase_datetime, str):
        try:
            # ISO 형식 (YYYY-MM-DD)
            return datetime.fromisoformat(firebase_datetime.replace('Z', '+00:00'))
        except ValueError:
            try:
                # 일반적인 날짜 형식들
                for format_str in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S'):
                    try:
                        return datetime.strptime(firebase_datetime, format_str)
                    except ValueError:
                        continue
                
                # 날짜 변환 실패
                print(f"Warning: Could not parse date string '{firebase_datetime}'")
                return None
            except Exception as e:
                print(f"Error parsing date string: {e}")
                return None
    
    # DatetimeWithNanoseconds 변환 시도
    try:
        return datetime(
            year=firebase_datetime.year,
            month=firebase_datetime.month,
            day=firebase_datetime.day,
            hour=firebase_datetime.hour,
            minute=firebase_datetime.minute,
            second=firebase_datetime.second,
            microsecond=firebase_datetime.microsecond
        )
    except AttributeError as e:
        print(f"Error converting firebase timestamp: {e}, type: {type(firebase_datetime)}")
        return None

def convert_firebase_MBTI(mbti_str):
    """
    MBTI 문자열(예: 'INTP')을 전체 용어 리스트로 변환합니다.
    예: 'INTP' -> ['Introverted', 'Intuitive', 'Thinking', 'Perceiving']
    
    Args:
        mbti_str: MBTI 유형을 나타내는 문자열
        
    Returns:
        문자열 리스트: 각 MBTI 차원의 전체 용어
    """
    if not mbti_str or not isinstance(mbti_str, str):
        return []
    
    # 입력 문자열 표준화
    mbti = mbti_str.upper().strip()
    
    # 유효성 검사
    if len(mbti) != 4:
        return []
    
    # MBTI 변환 매핑
    dimension_1 = {'E': 'Extraverted', 'I': 'Introverted'}
    dimension_2 = {'S': 'Sensing', 'N': 'Intuitive'}
    dimension_3 = {'T': 'Thinking', 'F': 'Feeling'}
    dimension_4 = {'J': 'Judging', 'P': 'Perceiving'}
    
    dimensions = [dimension_1, dimension_2, dimension_3, dimension_4]
    result = []
    
    # 각 차원 변환
    for i, char in enumerate(mbti):
        if i < len(dimensions) and char in dimensions[i]:
            result.append(dimensions[i][char])
        else:
            # 유효하지 않은 문자 발견
            return []
    
    return result

def clear_paraphrases_collection(firebase_repo, recognition_id):
    """
    특정 recognition_id에 대한 paraphrase 컬렉션을 삭제합니다.
    
    Args:
        firebase_repo: FirebaseRepository 인스턴스
        recognition_id: 삭제할 paraphrase의 recognition_id
    """
    # 해당 recognition_id를 가진 모든 paraphrase 문서 가져오기
    docs = firebase_repo.db.collection('paraphrases').where('recognition_id', '==', recognition_id).get()
    
    # 각 문서 삭제
    for doc in docs:
        doc.reference.delete()